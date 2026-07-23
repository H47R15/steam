"""FastMCP adapter for :mod:`steam.mcp`.

One entry point — :func:`register_steam_tools` — that binds every
tool defined in :mod:`steam.mcp.tools` onto a FastMCP-compatible
server.  Works with the official MCP SDK
(``mcp.server.fastmcp.FastMCP``) as well as the standalone
``fastmcp`` package — both expose the same ``@server.tool()``
decorator API.

The adapter creates one wrapper function per tool binding.  Each
wrapper:

1. Accepts the tool's Pydantic input as positional args (matching
   FastMCP's signature-based schema generation).
2. Validates the input by constructing the Pydantic model.
3. Awaits the tool's async handler with the pre-bound client.
4. Returns the output as a plain dict (framework serialises to
   the MCP wire format).
5. Maps ``AsyncSteamError`` / ``SteamToolError`` to structured
   FastMCP tool errors so the model sees a stable
   ``{"error": {"code": …}}`` shape instead of a generic 500.

The FastMCP dependency is imported lazily inside
:func:`register_steam_tools` — importing :mod:`steam.mcp` on a
system without FastMCP won't crash.
"""
from __future__ import annotations

import inspect
from typing import Any, Iterable, List, Optional

from ..aio.client import AsyncSteamClient
from .tools import (
    SteamToolBinding,
    SteamToolError,
    _classify_error,
    build_steam_tool_bindings,
)


def register_steam_tools(
    server: Any,
    client: AsyncSteamClient,
    *,
    bindings: Optional[Iterable[SteamToolBinding]] = None,
    prefix: str = "",
) -> List[str]:
    """Bind every tool in ``bindings`` (or the default set) onto
    ``server``.  Returns the list of tool names that were
    registered.

    Parameters
    ----------
    server:
        A FastMCP-compatible server instance — anything that has a
        ``@server.tool(name=…, description=…)`` decorator that
        accepts an async function.
    client:
        The :class:`AsyncSteamClient` the tools should hit.  Must
        be started (``await client.start()``) BEFORE the server
        starts serving — the tool handlers don't lazy-init.
    bindings:
        Override the default tool set.  Useful for filtering
        (``[b for b in build_steam_tool_bindings() if b.name != "steam.send_um"]``)
        or extending.
    prefix:
        Optional prefix prepended to every tool name.  Handy when
        one server exposes multiple Steam accounts under distinct
        namespaces (``prefix="alice."`` → ``"alice.steam.status"``).
    """
    if bindings is None:
        bindings = build_steam_tool_bindings()

    registered: List[str] = []

    for binding in bindings:
        _register_one(server, client, binding, prefix)
        registered.append(f"{prefix}{binding.name}")

    return registered


def _register_one(
    server: Any,
    client: AsyncSteamClient,
    binding: SteamToolBinding,
    prefix: str,
) -> None:
    """Build one FastMCP tool wrapper for ``binding`` and register
    it on ``server``.  Extracted so the loop body in
    :func:`register_steam_tools` stays flat."""

    input_model = binding.input_model
    handler = binding.handler
    tool_name = f"{prefix}{binding.name}"

    # FastMCP inspects the wrapper's signature to derive the tool's
    # JSON schema.  Rather than reflecting Pydantic → inspect at
    # runtime (fragile across Pydantic / FastMCP versions), we
    # expose the input as a single Pydantic-typed ``params``
    # parameter — FastMCP recognises Pydantic models and inlines
    # their fields into the tool schema.  That gives the model a
    # clean per-field parameter list without us having to
    # dynamically generate positional args.
    async def _tool_impl(
        params: input_model,  # type: ignore[valid-type]
    ) -> dict:
        try:
            result = await handler(client, params)
        except SteamToolError:
            raise
        except BaseException as exc:  # noqa: BLE001
            raise _classify_error(exc) from exc
        # ``result`` is a Pydantic BaseModel — ``model_dump`` on v2,
        # ``dict()`` on v1.
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result.dict()  # type: ignore[attr-defined]

    _tool_impl.__name__ = tool_name.replace(".", "_")
    _tool_impl.__doc__ = binding.description
    # Preserve the async signature so FastMCP's inspection works.
    _tool_impl.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        parameters=[
            inspect.Parameter(
                "params",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=input_model,
            ),
        ],
        return_annotation=dict,
    )

    # FastMCP's ``@server.tool()`` decorator returns the (possibly
    # wrapped) callable — we don't need the return value, just the
    # side-effect of registration.
    server.tool(name=tool_name, description=binding.description)(_tool_impl)


__all__ = ["register_steam_tools"]

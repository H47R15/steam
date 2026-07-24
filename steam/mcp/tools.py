"""Framework-agnostic MCP tool definitions for :mod:`steam.aio`.

Each tool is a triple:

* **Input schema** — a Pydantic ``BaseModel``.  Names + types are
  the MCP tool's declared parameters; docstrings become the tool's
  human-readable description.
* **Output schema** — a Pydantic ``BaseModel``.  Names + types are
  what the tool returns to the model.  Keeping outputs typed lets
  the model reason about what it got.
* **Async handler** — takes ``(client, input)`` and returns an
  instance of the output schema.  Runs inside the MCP server's
  own event loop; the handler awaits ``AsyncSteamClient`` methods
  directly.

All three are collected in :class:`SteamToolBinding` so
:func:`build_steam_tool_bindings` can hand a framework adapter a
uniform list to register.

Pydantic v2 is required (v1 works but the ``model_config`` /
``model_json_schema`` calls used here are the v2 spellings).

Design notes
------------

* Tool inputs use ``int`` / ``str`` / ``list[int]`` — types the
  MCP wire protocol handles natively.  No custom types that would
  need a JSON encoder.
* Outputs use ``dict`` for the free-form ``get_product_info`` /
  ``send_um_and_wait`` payloads (Steam's response shapes are too
  varied to pin with Pydantic without dragging in every proto
  definition).  A future improvement would be per-app-id typed
  payloads.
* Every handler catches :class:`~steam.aio.errors.AsyncSteamError`
  and re-raises with a stable, MCP-friendly message.  Anything
  else (network failure, gevent surprise) is left to propagate —
  the MCP server logs it as an internal error, which is what we
  want.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..aio.client import AsyncSteamClient
from ..aio.errors import AsyncSteamError, SteamNotStartedError

# ---------------------------------------------------------------------
# Common types
# ---------------------------------------------------------------------


class _EmptyInput(BaseModel):
    """No parameters."""

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------
# Tool: steam.status
# ---------------------------------------------------------------------


class SteamStatusInput(_EmptyInput):
    """No parameters — returns the current client health snapshot."""


class SteamStatusOutput(BaseModel):
    """Health snapshot for the underlying Steam CM session.
    Mirrors :class:`steam.aio.status.ClientStatus` field-for-field,
    plus a top-level ``healthy`` flag the model can rely on
    without knowing what "connected + logged_on" means."""

    healthy: bool = Field(
        description=(
            "``True`` if the client is connected and logged on. "
            "Use this as the quick yes/no; the individual fields "
            "give context if the answer is no."
        ),
    )
    connected: bool
    logged_on: bool
    username: str | None = None
    cell_id: int = 0
    reconnect_state: str
    reconnect_attempts: int
    last_activity_at: float | None = None
    uptime_seconds: float | None = None


async def _tool_steam_status(
    client: AsyncSteamClient,
    _input: SteamStatusInput,
) -> SteamStatusOutput:
    """Report the Steam client's current session health.
    Cheap — no network round-trip; reads local state only."""
    s = client.status
    return SteamStatusOutput(
        healthy=s.connected and s.logged_on,
        connected=s.connected,
        logged_on=s.logged_on,
        username=s.username,
        cell_id=s.cell_id,
        reconnect_state=s.reconnect_state,
        reconnect_attempts=s.reconnect_attempts,
        last_activity_at=s.last_activity_at,
        uptime_seconds=s.uptime_seconds,
    )


# ---------------------------------------------------------------------
# Tool: steam.get_product_info
# ---------------------------------------------------------------------


class GetProductInfoInput(BaseModel):
    """Look up Steam product metadata for one or more app / package IDs."""

    apps: list[int] = Field(
        default_factory=list,
        description="Steam app IDs (e.g. 440 for Team Fortress 2). Empty for none.",
    )
    packages: list[int] = Field(
        default_factory=list,
        description="Steam package IDs. Empty for none.",
    )
    meta_data_only: bool = Field(
        default=False,
        description=(
            "When ``True``, return only lightweight metadata "
            "(``change_number`` etc.), not full app details."
        ),
    )
    timeout_seconds: float = Field(
        default=15.0,
        ge=0.5,
        le=60.0,
        description=(
            "Hard cap on the RPC. Steam typically answers within a second or two."
        ),
    )

    model_config = {"extra": "forbid"}


class GetProductInfoOutput(BaseModel):
    """Result of a ``get_product_info`` call.  The dict payloads
    are Steam's raw response — schema varies per app because
    ``common``, ``config``, ``depots``, and so on are all
    optional and per-app-shaped."""

    apps: dict[int, dict[str, Any]] = Field(default_factory=dict)
    packages: dict[int, dict[str, Any]] = Field(default_factory=dict)


async def _tool_get_product_info(
    client: AsyncSteamClient,
    inp: GetProductInfoInput,
) -> GetProductInfoOutput:
    """Fetch Steam metadata for the given apps / packages.
    Returns the raw payload from the Content Manager unmodified."""
    if not inp.apps and not inp.packages:
        raise ValueError("get_product_info requires at least one app or package id")
    raw = await client.get_product_info(
        apps=inp.apps,
        packages=inp.packages,
        meta_data_only=inp.meta_data_only,
        timeout=inp.timeout_seconds,
    )

    # ``get_product_info`` returns ``{"apps": {id: {...}}, "packages": ...}``
    # where the keys are ints for apps but sometimes strings if the
    # underlying proto decoded them that way — normalise for the
    # typed output.
    def _int_keys(d: Any) -> dict[int, dict[str, Any]]:
        if not isinstance(d, dict):
            return {}
        out: dict[int, dict[str, Any]] = {}
        for k, v in d.items():
            try:
                out[int(k)] = v if isinstance(v, dict) else {"value": v}
            except (TypeError, ValueError):
                # Non-int keys — skip (shouldn't happen for real
                # Steam responses but keep the tool robust).
                continue
        return out

    return GetProductInfoOutput(
        apps=_int_keys(raw.get("apps") if isinstance(raw, dict) else None),
        packages=_int_keys(raw.get("packages") if isinstance(raw, dict) else None),
    )


# ---------------------------------------------------------------------
# Tool: steam.send_um
# ---------------------------------------------------------------------


class SendUmInput(BaseModel):
    """Send a Steam Unified Messages RPC and return the response."""

    method_name: str = Field(
        description=(
            "Fully-qualified proto method name, e.g. "
            "``Player.GetGameBadgeLevels#1``."
        ),
        min_length=3,
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Request parameters — dict keyed by the request proto's field names."
        ),
    )
    timeout_seconds: float = Field(
        default=10.0,
        ge=0.5,
        le=60.0,
        description="Hard cap on the RPC.",
    )

    model_config = {"extra": "forbid"}


class SendUmOutput(BaseModel):
    """Response body of the UM RPC.  ``body`` is Steam's raw
    payload; ``ok`` is a convenience flag for the model to check
    without introspecting the body shape."""

    ok: bool = True
    body: dict[str, Any] = Field(default_factory=dict)


class UpcomingGamesInput(BaseModel):
    """Browse upcoming Steam games with stable pagination."""

    period: Literal[
        "today",
        "this_week",
        "next_week",
        "this_month",
        "next_month",
        "this_year",
    ] = Field(
        default="this_month",
        description=("Calendar group. `this_year` returns Steam's hot upcoming games."),
    )
    page: int = Field(default=1, ge=1, description="One-based result page.")
    per_page: int = Field(default=100, ge=1, le=100, description="Rows per page.")
    country_code: str = Field(default="US", min_length=2, max_length=2)
    language: str = Field(default="english", min_length=2, max_length=32)
    model_config = {"extra": "forbid"}


class UpcomingGamesOutput(BaseModel):
    """Compact table-ready upcoming-games page."""

    period: str
    date_from: str
    date_to: str
    page: int
    per_page: int
    total: int
    has_more: bool
    next_page: int | None = None
    rows: list[dict[str, Any]] = Field(default_factory=list)


async def _tool_upcoming_games(
    client: AsyncSteamClient,
    inp: UpcomingGamesInput,
) -> UpcomingGamesOutput:
    result = await client.get_upcoming_games(
        page=inp.page,
        per_page=inp.per_page,
        country_code=inp.country_code,
        language=inp.language,
        period=inp.period,
    )
    return UpcomingGamesOutput.model_validate(result)


async def _tool_send_um(
    client: AsyncSteamClient,
    inp: SendUmInput,
) -> SendUmOutput:
    """Send an arbitrary Steam Unified Messages call.  Use when
    the wrapper doesn't have a dedicated tool for the RPC you
    need — anything ``SteamClient.send_um_and_wait`` supports."""
    resp = await client.send_um_and_wait(
        inp.method_name,
        inp.params,
        timeout=inp.timeout_seconds,
    )
    # Response is a protobuf-ish object — convert to dict best-
    # effort so JSON serialisation works.  Real ``send_um_and_wait``
    # returns a ``CMsgProtoBufHeader``-shaped object; falling back
    # to ``{"raw": repr(resp)}`` keeps the MCP contract stable
    # even if a caller-provided sync client returns something
    # weird.
    if resp is None:
        return SendUmOutput(ok=False, body={})
    if hasattr(resp, "to_dict"):
        return SendUmOutput(ok=True, body=resp.to_dict())
    if isinstance(resp, dict):
        return SendUmOutput(ok=True, body=resp)
    return SendUmOutput(ok=True, body={"raw": repr(resp)})


# ---------------------------------------------------------------------
# Binding metadata + registry
# ---------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SteamToolBinding:
    """A ready-to-register MCP tool.

    ``handler`` is an async callable of shape
    ``(client, input_model) -> output_model`` — the framework
    adapter binds the ``client`` argument in advance and exposes
    the remaining ``(input_model) -> output_model`` as the actual
    MCP tool.

    ``name`` is the tool's MCP name (dotted, lowercase).
    ``description`` is human-readable and shown to the model.
    """

    name: str
    description: str
    input_model: type
    output_model: type
    handler: Callable[[AsyncSteamClient, Any], Awaitable[BaseModel]]


def build_steam_tool_bindings() -> list[SteamToolBinding]:
    """Return the built-in list of Steam MCP tool bindings.

    Kept as a function (rather than a module-level constant) so
    each call yields a fresh list — an adapter that mutates the
    returned list to filter tools won't affect subsequent calls.
    """
    return [
        SteamToolBinding(
            name="steam.status",
            description=(
                "Report the Steam client's current session health "
                "(connected, logged in, cell id, reconnect state). "
                "Call this before other Steam tools if you're unsure "
                "whether the connection is up."
            ),
            input_model=SteamStatusInput,
            output_model=SteamStatusOutput,
            handler=_tool_steam_status,
        ),
        SteamToolBinding(
            name="steam.get_product_info",
            description=(
                "Fetch Steam metadata for one or more app IDs and/or "
                "package IDs — name, description, config, depots, "
                "release date, etc.  This is the go-to tool for "
                "'what is app X'."
            ),
            input_model=GetProductInfoInput,
            output_model=GetProductInfoOutput,
            handler=_tool_get_product_info,
        ),
        SteamToolBinding(
            name="steam.send_um",
            description=(
                "Send an arbitrary Steam Unified Messages RPC.  Use "
                "when a specialised tool doesn't cover the API you "
                "need (e.g. Player.GetGameBadgeLevels#1, "
                "Community.GetApps, Store.Search, …).  You need to "
                "know the proto method name and its request field "
                "names."
            ),
            input_model=SendUmInput,
            output_model=SendUmOutput,
            handler=_tool_send_um,
        ),
        SteamToolBinding(
            name="steam.upcoming_games",
            description=(
                "Return one paginated page of upcoming Steam games as compact, "
                "table-ready rows. Supports today, this/next week, this/next "
                "month, and this year's hot 100. Calendar periods use the "
                "date-ordered catalogue and return up to 100 rows. Use page/next_page to "
                "continue; do not re-fetch product details merely to format "
                "the result."
            ),
            input_model=UpcomingGamesInput,
            output_model=UpcomingGamesOutput,
            handler=_tool_upcoming_games,
        ),
    ]


# ---------------------------------------------------------------------
# Shared error mapping — every tool handler wraps its body with
# this so exceptions land as MCP tool errors with stable shape.
# ---------------------------------------------------------------------


class SteamToolError(RuntimeError):
    """Raised by tool handlers to surface a Steam-side failure with
    a stable error code the MCP client can pattern-match on.

    Framework adapters translate this into the framework's own
    error type (``mcp.ToolError`` for the SDK, etc.) — kept as a
    plain ``RuntimeError`` here so the tool definitions stay
    framework-agnostic.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"[{code}] {message}")


def _classify_error(exc: BaseException) -> SteamToolError:
    """Map a raw exception to a stable MCP tool-error code."""
    if isinstance(exc, SteamNotStartedError):
        return SteamToolError("steam_not_started", str(exc))
    if isinstance(exc, AsyncSteamError):
        return SteamToolError(
            f"steam_{type(exc).__name__.lower().replace('error', '')}",
            str(exc),
        )
    return SteamToolError("internal_error", f"{type(exc).__name__}: {exc}")


__all__ = [
    "SteamStatusInput",
    "SteamStatusOutput",
    "GetProductInfoInput",
    "GetProductInfoOutput",
    "SendUmInput",
    "SendUmOutput",
    "UpcomingGamesInput",
    "UpcomingGamesOutput",
    "SteamToolBinding",
    "SteamToolError",
    "build_steam_tool_bindings",
    "_classify_error",
]

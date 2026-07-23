"""Model Context Protocol (MCP) bindings for :mod:`steam.aio`.

Exposes ``pysteam-client``'s async facade as MCP tools an LLM agent
can call.  Framework-agnostic at the core (tool definitions =
plain async functions + Pydantic schemas) with a thin adapter for
the official MCP SDK / FastMCP so users can plug this into any
MCP server they already have.

Two-layer API:

* :mod:`steam.mcp.tools` — the raw definitions.  If you're
  building your own MCP server, import the schemas + async
  callables and wire them however your framework wants.
* :mod:`steam.mcp.server` — the FastMCP adapter.  One call —
  ``register_steam_tools(mcp_server, client)`` — and every tool
  is bound to your existing server.

Neither module imports the MCP SDK at module-load time — the
SDK import happens inside :func:`register_steam_tools` so the base
package stays MCP-optional.

Example
-------

::

    from mcp.server.fastmcp import FastMCP
    from steam.aio import AsyncSteamClient
    from steam.mcp import register_steam_tools

    server = FastMCP("Steam")
    client = AsyncSteamClient()
    await client.start()
    await client.anonymous_login()

    register_steam_tools(server, client)
    # server.run() as usual
"""
from .server import register_steam_tools
from .tools import (
    SteamStatusInput,
    SteamStatusOutput,
    GetProductInfoInput,
    GetProductInfoOutput,
    SendUmInput,
    SendUmOutput,
    SteamToolBinding,
    build_steam_tool_bindings,
)

__all__ = [
    "register_steam_tools",
    "SteamStatusInput",
    "SteamStatusOutput",
    "GetProductInfoInput",
    "GetProductInfoOutput",
    "SendUmInput",
    "SendUmOutput",
    "SteamToolBinding",
    "build_steam_tool_bindings",
]

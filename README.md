<p align="center">
  <img src="https://raw.githubusercontent.com/H47R15/steam/master/.github/cover.png" alt="pysteam-client">
</p>

<p align="center">
  <a href="https://github.com/H47R15/steam/actions/workflows/testing_initiative.yml"><img alt="CI" src="https://github.com/H47R15/steam/actions/workflows/testing_initiative.yml/badge.svg?branch=master"></a>
  <a href="https://github.com/H47R15/steam/actions/workflows/codeql.yml"><img alt="CodeQL" src="https://github.com/H47R15/steam/actions/workflows/codeql.yml/badge.svg?branch=master"></a>
  <a href="https://api.securityscorecards.dev/projects/github.com/H47R15/steam"><img alt="OpenSSF Scorecard" src="https://api.securityscorecards.dev/projects/github.com/H47R15/steam/badge"></a>
  <a href="https://pypi.org/project/pysteam-client/"><img alt="PyPI" src="https://img.shields.io/pypi/v/pysteam-client.svg"></a>
  <a href="https://pypi.org/project/pysteam-client/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/pysteam-client.svg"></a>
  <a href="https://github.com/H47R15/steam/wiki/MCP"><img alt="MCP tools" src="https://img.shields.io/badge/MCP-tools_included-8A2BE2?logo=anthropic&logoColor=white"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/pysteam-client.svg"></a>
</p>

# pysteam-client

Modern Python client for the Steam network — CM protocol, PICS, CDN, WebAuth, Web API, Steam Guard, SteamIDs — plus a fully-async facade for FastAPI / TaskIQ and an MCP tool set for LLM agents.

Maintained fork of [ValvePython/steam](https://github.com/ValvePython/steam) for Python 3.13+ and current Steam wire protocols. Full docs in the [Wiki](https://github.com/H47R15/steam/wiki).

## Install

```bash
pip install pysteam-client[client]
```

`[client]` pulls in the gevent-based `SteamClient` (login, PICS, CDN). Without it, the `requests`-only subset (WebAPI / WebAuth / SteamID / master-server query) still works.

## Architecture

```mermaid
flowchart TB
    subgraph asyncio["Your process (asyncio)"]
        APP["FastAPI / TaskIQ /<br/>MCP server / your code"]
        MCP["steam.mcp<br/>LLM tool wrappers"]
        AIO["steam.aio<br/>AsyncSteamClient · Pool · Metrics"]
        APP --> AIO
        APP --> MCP
        MCP --> AIO
    end
    subgraph thread["Background daemon thread (gevent hub)"]
        SYNC["steam.client.SteamClient<br/>recv loop · heartbeat · auto-reconnect"]
    end
    AIO -.libev async watcher.-> SYNC
    SYNC ==CM protocol · WebAPI · CDN==> STEAM[(Steam network)]
```

## Quick start

**Sync** (script, CLI, batch jobs):

```python
from steam.client import SteamClient

client = SteamClient()
client.anonymous_login()
info = client.get_product_info(apps=[440], timeout=15)
print(info["apps"][440]["common"]["name"])
client.logout()
```

**Async** (FastAPI, TaskIQ, any asyncio app):

```python
from steam.aio import AsyncSteamClient

async with AsyncSteamClient() as client:
    await client.anonymous_login()
    info = await client.get_product_info(apps=[440])
```

**MCP** (expose to an LLM agent):

```python
from mcp.server.fastmcp import FastMCP
from steam.aio import AsyncSteamClient
from steam.mcp import register_steam_tools

server = FastMCP("Steam")
client = AsyncSteamClient()
await client.start()
await client.anonymous_login()
register_steam_tools(server, client)   # steam.status, steam.get_product_info, steam.send_um
```

## Documentation

Full documentation lives in the [**Wiki**](https://github.com/H47R15/steam/wiki):

**Getting started** — [Installation](https://github.com/H47R15/steam/wiki/Installation) · [First script](https://github.com/H47R15/steam/wiki/First-script)

**Client APIs** — [SteamClient](https://github.com/H47R15/steam/wiki/SteamClient) · [PICS](https://github.com/H47R15/steam/wiki/PICS) · [CDNClient](https://github.com/H47R15/steam/wiki/CDNClient) · [WebAuth](https://github.com/H47R15/steam/wiki/WebAuth) · [WebAPI](https://github.com/H47R15/steam/wiki/WebAPI) · [SteamAuthenticator](https://github.com/H47R15/steam/wiki/SteamAuthenticator) · [SteamID](https://github.com/H47R15/steam/wiki/SteamID) · [Master Server Queries](https://github.com/H47R15/steam/wiki/Master-Server-Queries)

**Async / FastAPI / MCP** *(new in 1.6)* — [AsyncSteamClient](https://github.com/H47R15/steam/wiki/AsyncSteamClient) · [Pool](https://github.com/H47R15/steam/wiki/Pool) · [FastAPI Integration](https://github.com/H47R15/steam/wiki/FastAPI-Integration) · [TaskIQ Integration](https://github.com/H47R15/steam/wiki/TaskIQ-Integration) · [MCP](https://github.com/H47R15/steam/wiki/MCP)

**Advanced** — [Regenerating Protobufs](https://github.com/H47R15/steam/wiki/Regenerating-Protobufs) · [Type Checking](https://github.com/H47R15/steam/wiki/Type-Checking) · [Contributing](https://github.com/H47R15/steam/wiki/Contributing) · [Fork Changes](https://github.com/H47R15/steam/wiki/Fork-Changes) · [FAQ](https://github.com/H47R15/steam/wiki/FAQ)

## Security

Every push, PR, and release runs eight independent gates before any wheel ships to PyPI: `ruff` + `black` (style), `mypy --strict` (types on `steam.aio` + `steam.mcp`), `pytest`, `deptry` (deps hygiene), `bandit` (Python SAST), `pip-audit` (CVEs), CodeQL (cross-file SAST), OpenSSF Scorecard (repo posture). A failing gate blocks the publish step.

**Report a vulnerability**: use [GitHub Security Advisories](https://github.com/H47R15/steam/security/advisories/new) (preferred, private, coordinated disclosure). Full policy in [SECURITY.md](SECURITY.md). **Do NOT open a public GitHub issue for security reports.**

## License

MIT — see [LICENSE](LICENSE). Unchanged from upstream.

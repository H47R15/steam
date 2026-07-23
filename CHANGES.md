## 1.7.1

### Added
- **CI quality gates** — the ``Publish`` workflow now runs
  ruff + black + mypy (strict, on ``steam.aio`` + ``steam.mcp``)
  + deptry + pip-audit BEFORE building the wheel.  A failing
  lint / type-check / test blocks the PyPI upload.
- The ``CI`` workflow (renamed from the old ``Tests`` workflow)
  runs the same gates on every push + PR as four independent
  jobs, so the GitHub UI shows which specific gate failed.
  Concurrency-cancel is on — pushing a fix doesn't wait for
  the previous build.
- ``[tool.black]`` / ``[tool.ruff]`` / ``[tool.mypy]`` sections
  in ``pyproject.toml``, scoped to the new modules so we can
  ratchet toward strict lint incrementally without rewriting the
  whole legacy tree in one go.
- ``ruff``, ``black``, ``mypy``, ``pip-audit`` added as dev
  dependencies so ``poetry install --with dev`` bootstraps
  everything CI runs.
- Cover image at the top of README.rst — rendered on both GitHub
  and PyPI via the absolute ``raw.githubusercontent.com`` URL.
- CI quality gates …

### Changed
- ``steam.aio.integrations.taskiq`` now registers its
  startup / shutdown handlers with ``TaskiqEvents.WORKER_STARTUP``
  / ``TaskiqEvents.WORKER_SHUTDOWN`` (the correct enum), not
  the bare ``"startup"`` / ``"shutdown"`` strings.  Fixes a
  latent bug — the string form was rejected by newer TaskIQ
  versions.  Test updated to match.
- Every ``steam/aio/**/*.py`` and ``steam/mcp/**/*.py`` file
  now passes ``mypy --strict`` and ``ruff check`` / ``black
  --check``.  Type annotations tightened (generic params on
  ``list`` / ``dict`` / ``Queue`` / ``Future`` / ``itertools.cycle``,
  narrowed return types in the FastAPI ``Depends`` providers).
- New black formatting applied to ``steam/aio`` + ``steam/mcp``
  + async tests.  No functional change; diffs are purely
  whitespace + import ordering.

## 1.7.0

### Added
- **Production hardening for `steam.aio`**:
  - `client.status` — JSON-serialisable `ClientStatus` dataclass
    (connected, logged_on, cell_id, reconnect state / attempts,
    last_activity_at, uptime). Safe to return from a FastAPI
    `/health` handler directly.
  - `metrics_hook=` constructor argument on `AsyncSteamClient`
    firing on `client.started` / `client.closed` / `cm.connected`
    / `cm.disconnected` / `reconnect.started` /
    `reconnect.succeeded` / `reconnect.failed` / `rpc.started` /
    `rpc.succeeded` / `rpc.failed`. Callback-based — the library
    stays free of Prometheus / StatsD deps. A raising hook is
    caught + logged so a broken metrics implementation never
    takes down the RPC path.
  - `prometheus_hook()` factory in `steam.aio.status` — one call
    returns a ready-made `MetricsHook` backed by
    `prometheus_client` counters + histograms. `prometheus_client`
    imported lazily.
  - `asyncio` cancellation now kills the underlying gevent
    greenlet — a cancelled `asyncio.wait_for(client.get_product_info(...))`
    actually stops the sync work instead of orphaning a socket
    read.
- **`steam.aio.AsyncSteamPool`** — multi-account pool.
  Concurrent bringup, round-robin selection, `acquire(account_id)`,
  per-member failure isolation, `replace_member()` for post-start
  recovery. `AsyncSteamPool` + `PoolMember` + `PoolMemberStatus`
  exported from `steam.aio`.
- **`steam.aio.integrations.fastapi`** — `steam_client_lifespan`
  / `steam_pool_lifespan` context managers + `get_steam_client`
  / `get_steam_pool` `Depends` providers. FastAPI imported
  lazily.
- **`steam.aio.integrations.taskiq`** — `register_steam_client` /
  `register_steam_pool` wire startup + shutdown hooks onto a
  TaskIQ broker and return a sync dependency function for
  `TaskiqDepends`. TaskIQ imported lazily.
- **`steam.mcp` package** — expose `AsyncSteamClient` as
  Model-Context-Protocol tools an LLM agent can call.
  Framework-agnostic tool definitions (Pydantic input / output
  schemas + async handlers) at `steam.mcp.tools`; FastMCP
  adapter at `steam.mcp.server`. Three built-in tools:
  `steam.status`, `steam.get_product_info`, `steam.send_um`.
  Adapter works with the official `mcp` SDK
  (`mcp.server.fastmcp.FastMCP`) and the standalone `fastmcp`
  package — both imported lazily.
- Extensive new test coverage — status snapshot, metrics hook
  fires on the right events, hook exceptions don't kill RPCs,
  cancellation kills the greenlet, pool concurrent bringup /
  round-robin / failure isolation, FastAPI lifespan wiring,
  TaskIQ dependency registration, MCP tool schemas + FastMCP
  registration. 120 mocked + 1 live smoke test.
- Wiki pages: `AsyncSteamClient`, `Pool`, `FastAPI-Integration`,
  `TaskIQ-Integration`, `MCP`.

### Changed
- `AsyncSteamClient` public API grew — new `status` property,
  `metrics_hook=` kwarg. No breaking changes to existing methods.
- `_require_ready()` now runs BEFORE dereferencing `self._sync`
  in every public method, so a call before `start()` raises the
  typed `SteamNotStartedError` instead of `AttributeError`.
- README updated with async / FastAPI / MCP quick-start snippets
  and a fresh source-tree layout.

## 1.6.0

### Added
- New `steam.aio` package — asyncio facade for use inside FastAPI /
  Starlette / any asyncio app. The sync gevent client runs on a
  dedicated daemon thread with its own isolated gevent hub; the
  asyncio process is never monkey-patched, so `httpx` / `uvicorn` /
  `motor` keep working. Public surface:
  - `AsyncSteamClient` — `start`, `anonymous_login`, `login`,
    `logout`, `disconnect`, `get_product_info`, `send_um_and_wait`,
    `close`, plus `logged_on` / `connected` / `username` / `cell_id`
    proxy properties. Full async context manager support.
  - `ReconnectPolicy` — auto-reconnect + relogin on CM disconnect,
    with exponential-backoff retry and observability events
    (`aio.reconnecting` / `aio.reconnected` / `aio.reconnect_failed`).
    Enabled by default; disable with
    `AsyncSteamClient(reconnect=ReconnectPolicy(enabled=False))`.
  - Async event bridge: `await client.wait_event(name, timeout=...)`
    for single-shot waits, `async for evt in client.events(*names)`
    for streaming subscription with bounded internal buffer.
  - Typed exception hierarchy (`steam.aio.errors`):
    `AsyncSteamError`, `SteamNotStartedError`, `SteamClosedError`,
    `SteamLoginError` (carries `EResult`), `SteamReconnectError`
    (carries attempt count), `SteamRPCTimeoutError` (carries
    deadline). Backwards-compatible with pre-1.6 callers catching
    `RuntimeError` / `TimeoutError`.
- Live-network integration smoke test (`tests/test_aio_integration.py`),
  gated by `RUN_LIVE=1` — anonymous login + `get_product_info(apps=[440])`
  against a real Steam CM. Skipped in normal CI, catches upstream
  Steam protocol changes on demand.

### Fixed
- Silence false-positive Pylance `reportArgumentType` warning on
  the generated `_builder.BuildServices(...)` call in every
  `*_pb2.py`. Type-check-only change; runtime behaviour is
  unchanged. The `pb_compile` post-processor now applies the
  suppression automatically on future protobuf rebuilds.

## 1.6.0

### Added
- `steam.aio.AsyncSteamClient` — asyncio facade around
  `SteamClient` for use inside FastAPI / Starlette / any asyncio
  app. Runs the sync client on a dedicated daemon thread with
  its own isolated gevent hub; the asyncio process is never
  monkey-patched, so `httpx` / `uvicorn` / `motor` keep working.
  Covers `anonymous_login`, `login`, `logout`, `disconnect`,
  `get_product_info`, and `close`, plus `logged_on` / `connected`
  / `username` / `cell_id` proxy properties. Full async context
  manager support (`async with AsyncSteamClient() as client:`).
  Background greenlets (recv loop, CM heartbeat) keep running
  between requests — the connection stays warm without any
  polling on the caller side.

### Fixed
- Silence false-positive Pylance `reportArgumentType` warning on
  the generated `_builder.BuildServices(...)` call in every
  `*_pb2.py`. Type-check-only change; runtime behaviour is
  unchanged. The `pb_compile` post-processor now applies the
  suppression automatically on future protobuf rebuilds.

## 1.5.1

### Fixed
- Silence false-positive Pylance `reportArgumentType` warning on
  the generated `_builder.BuildServices(...)` call in every
  `*_pb2.py`. Type-check-only change; runtime behaviour is
  unchanged. The `pb_compile` post-processor now applies the
  suppression automatically.


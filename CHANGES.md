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


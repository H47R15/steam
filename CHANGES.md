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


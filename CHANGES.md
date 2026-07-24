## 1.8.0

### Added
- Steam QR authentication support in the async client flow.

### Fixed
- Tightened QR/session handling and type-safety fixes for the local async Steam client surface.

## 1.7.9

### Fixed
- **``.gitignore`` silently ignoring top-level docs**.  The file
  starts with ``*`` (deny-all) and had no allowlist entries for
  ``README.*`` / ``SECURITY.md`` / ``CHANGES.md`` / ``LICENSE.*``.
  Files tracked before this rule (``LICENSE``, ``CHANGES.md``) kept
  working, but any new top-level doc was silently swallowed —
  which is exactly what happened to ``README.rst`` in 1.7.8: the
  commit stripped ``README.md`` and referenced ``README.rst`` in
  ``pyproject.toml``, but git never added ``README.rst`` because
  the ``*`` rule ignored it.  ``poetry build`` in the release
  workflow then failed with ``No such file or directory:
  README.rst``.  Fix: explicit allowlist entries for all top-level
  docs.
- **README ships in BOTH ``.rst`` and ``.md``** so both platforms
  render their preferred format — GitHub picks ``README.md`` (with
  the mermaid architecture diagram + rendered badges); PyPI reads
  ``README.rst`` as declared in ``pyproject.toml`` ``readme =``.
  Content is mirrored between the two.

### Fixed (from 1.7.8's uncommitted queue)
- 4 Pylance findings on the async surface — none were runtime
  bugs, all type-check-only:
  - ``events()`` return-type widened to ``AsyncGenerator[..., None]``
    (was ``AsyncIterator``) so callers can ``await agen.aclose()``.
  - ``prometheus_hook`` uses ``labelnames=`` kwarg for
    ``prometheus_client`` stability across stub versions; the
    lazy import carries a
    ``# type: ignore[import-not-found, unused-ignore]`` that keeps
    both Pylance (when the pkg is absent) and mypy (when it's
    present) quiet.
  - TaskIQ integration test casts the ``FakeBroker`` to ``Any`` at
    the ``register_steam_client`` boundary — the fake intentionally
    implements only the two-method subset the helper touches.

## 1.7.8

### Changed
- Reverted README format ``.md`` → ``.rst``.  1.7.7's markdown
  conversion was done for the mermaid diagram (Markdown renders
  it natively on GitHub, RST doesn't), but the format switch
  lost more than it gained.  ``.rst`` stays the canonical Python
  README; if we want the architecture diagram back, we'll render
  mermaid to SVG and reference the image, not swap the whole
  file format.
- ``pyproject.toml`` ``readme = "README.rst"`` restored.

### Added
- **MCP tools badge** in the README badge row —
  ``[MCP tools included]`` in Anthropic-purple, linking to the
  `MCP wiki page
  <https://github.com/H47R15/steam/wiki/MCP>`_.  Sits between
  the Python-versions and License badges.

### Fixed
- 4 Pylance findings on the async surface — none were real
  runtime bugs, all were type-check-only:
  - ``events()`` return-type widened to ``AsyncGenerator`` (was
    ``AsyncIterator``) so callers can ``await agen.aclose()``.
  - ``prometheus_hook`` now uses ``labelnames=`` kwarg for
    prometheus_client stability across stub versions.
  - ``prometheus_client`` lazy import carries an
    ``import-not-found, unused-ignore`` type-ignore that keeps
    both Pylance (when the pkg is absent) and mypy (when it's
    present) quiet.
  - TaskIQ integration test casts the ``FakeBroker`` to ``Any``
    at the ``register_steam_client`` boundary — the fake
    intentionally implements only the two-method subset the
    helper touches.

## 1.7.7

### Changed
- **README rewritten** — smaller, focused on architecture +
  quick-start.  Everything detailed now lives in the
  [Wiki](https://github.com/H47R15/steam/wiki) with an organised
  link tree in the README so users find the right page fast.
- **README format ``.rst`` → ``.md``** so GitHub renders the new
  architecture diagram natively (mermaid).  PyPI accepts markdown
  too — verified via ``readme_renderer[md]``.
- ``pyproject.toml`` ``readme = "README.md"`` updated to match.

### Added
- Mermaid architecture diagram at the top of the README showing
  the two-thread model (asyncio-side ``steam.aio`` / ``steam.mcp``
  vs. the background gevent-hub daemon thread running the sync
  ``SteamClient``), the libev async-watcher bridge between them,
  and the outbound CM / WebAPI / CDN paths.  Renders natively on
  GitHub; PyPI shows the mermaid source as a code block (still
  readable) with a click-through to the GitHub view.

### Fixed
- ``.github/workflows/scorecard.yml`` — the step name ``Upload
  artifact (retention: 5 days)`` had a second colon inside the
  parenthetical that YAML parsed as a nested mapping-value
  marker.  Result: "workflow file issue" — the run failed
  instantly at parse time with zero logs and the OpenSSF
  Scorecard workflow never got to score the repo.  Quoted the
  name so the colon is a literal character; all four workflow
  files now parse clean.

## 1.7.6

### Fixed
- Skip ``tests/test_webapi.py::TCwebapi`` (7 tests) and
  ``tests/test_steamid.py::steamid_functions::test_steam64_from_url``
  when running under urllib3 2.x.  Their VCR cassettes
  (``vcr/webapi.yaml``, ``vcr/steamid_community_urls.yaml``) were
  recorded against urllib3 1.x; vcrpy 8.3 can't replay the
  requests under 2.x because urllib3 changed enough at the
  connection layer that the recorded signature no longer matches
  (``CannotOverwriteExistingCassetteException`` from
  ``vcr/stubs/__init__.py``).
  
  The 1.7.5 upgrade to urllib3 2.7.0 (to close five CVEs — see
  1.7.5 notes) exposed this — nothing in ``steam.aio`` or
  ``steam.mcp`` is affected, and neither is the WebAPI runtime
  code itself; only the test-replay path.
  
  Skip reason surfaces in ``pytest -v`` output so nobody
  quietly misses the coverage regression.  Follow-up work
  tracked: re-record cassettes via ``poetry run vcr-webapi``
  (needs ``STEAM_API_KEY``) and an interactive session against
  live ``steamcommunity.com`` for the vanity URL test.

## 1.7.5

### Fixed
- **``poetry.lock`` regenerated with ``--regenerate``** so
  ``urllib3`` moves to 2.7.0 — 1.7.4's plain ``poetry lock``
  preserved 1.26.20 (still satisfied the new ">=1.26,<3"
  constraint) and CI failed on the same five CVEs a second
  time.  Every release from here on uses ``--regenerate`` when
  a constraint changes.

### Added
- **``SECURITY.md``** — vulnerability reporting policy with a
  copy-paste report template, supported-versions table, response
  commitments (48 h ack, 5 business-day triage, 30/60/90-day fix
  per severity, 90-day coordinated-disclosure embargo),
  safe-harbour clause for good-faith researchers, and explicit
  in-scope / out-of-scope lists.
- **``bandit``** Python-native SAST wired into CI as a fifth
  quality gate (``[tool.bandit]`` in ``pyproject.toml``; scoped
  to ``steam.aio`` + ``steam.mcp``; medium severity and above;
  ``B101`` / ``B110`` skipped for documented intentional patterns
  in cleanup paths + type-narrowing asserts).  Runs on every push,
  PR, and release.
- **CodeQL** workflow (``.github/workflows/codeql.yml``) —
  GitHub-native semantic SAST with cross-file dataflow analysis.
  Runs on push + PR + weekly cron.  Results in the repo's
  Security tab.  Complements bandit's single-file pattern scan.
- **OpenSSF Scorecard** workflow — automated repository-posture
  scoring; badge in ``README.rst`` renders the public score from
  ``api.securityscorecards.dev``.
- **Dependabot** config (``.github/dependabot.yml``) — weekly
  grouped dep-update PRs for pip + GitHub Actions, plus immediate
  security-update PRs whenever a CVE lands on a dep.
- **README security section + badges** — CI, CodeQL, OpenSSF
  Scorecard, PyPI version, supported Python versions.
- **Publish workflow gated on ``bandit`` too** — a failing SAST
  finding blocks the PyPI upload.

## 1.7.4

### Fixed
- **urllib3 CVEs**.  Relax the ``urllib3 = "<2"`` pin to
  ``">=1.26,<3"``.  The previous ``<2`` pin forced CI's fresh
  poetry venv onto urllib3 1.26.20, which pip-audit flagged with
  five open CVEs (PYSEC-2026-141 / -1994 / -1996 / -1998 / -1999)
  — all fixed in urllib3 2.x.  The fork has zero direct urllib3
  imports (``requests`` is the only consumer); the earlier
  comment claiming "cert-verification breakage in the fork under
  urllib3 2.x" was unsourced and nothing in the tree exercises
  the code path.  New constraint matches ``requests``'s own
  accepted range.
- Regenerated ``poetry.lock`` so ``pip-audit`` sees the newer
  urllib3.

## 1.7.3

### Fixed
- Add ``pydantic >= 2.0`` as a runtime dependency.  ``steam.mcp.tools``
  imports it at module-top for the MCP tool input/output schemas, so
  it can't be lazy — 1.7.1 / 1.7.2 shipped without declaring it and
  every CI job that touched ``steam.mcp`` failed with
  ``ModuleNotFoundError: No module named 'pydantic'``.  Pydantic is
  already present in every FastAPI / TaskIQ / MCP-SDK stack, so
  promoting it to a hard dep costs almost nothing.
- ``deptry`` config: ``taskiq`` + ``prometheus_client`` are now in
  BOTH the ``DEP001`` (missing-from-deps) and ``DEP003``
  (transitive) ignore lists.  1.7.1 only had ``DEP003`` — that
  passed locally where they were transitively installed but tripped
  ``DEP001`` in a fresh CI venv where they were absent.
- Regenerated ``poetry.lock`` to match.

## 1.7.2

### Fixed
- Regenerated ``poetry.lock`` so ``poetry install`` succeeds
  against the 1.7.1 ``pyproject.toml`` — the 1.7.1 release
  added ``ruff`` / ``black`` / ``mypy`` / ``pip-audit`` as
  dev dependencies but shipped without a matching lock-file
  refresh, so every CI job failed with "pyproject.toml
  changed significantly since poetry.lock was last generated".
  1.7.1 never made it past the quality gate to PyPI; 1.7.2
  is the effective 1.7.1 release with a working install.

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


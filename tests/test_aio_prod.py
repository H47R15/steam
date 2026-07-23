"""Tests for the production-hardening additions to :mod:`steam.aio`:

* status snapshot + metrics hook
* asyncio cancellation → gevent greenlet kill
* :class:`AsyncSteamPool`
* FastAPI + TaskIQ integration helpers
* :mod:`steam.mcp` tools + FastMCP adapter

Pure-Python; no live network.  The shared ``_FakeEmitter`` /
``_OK`` stubs from :mod:`test_aio_client` are re-imported so the
tests in this file compose with the same test doubles the earlier
suite established.
"""

from __future__ import annotations

import asyncio
import time
import unittest
from collections.abc import Callable
from typing import Any, cast
from unittest import mock

from tests.test_aio_client import _OK, _FakeEmitter, _run

# ----------------------------------------------------------------------
# Status + metrics hook
# ----------------------------------------------------------------------


class StatusMetricsTests(unittest.TestCase):
    def test_status_reflects_lifecycle(self) -> None:
        """Fresh client is not-started; after ``start`` + login it
        reports connected + logged_on + a real ``uptime_seconds``;
        after ``close`` it reports closed."""

        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False
                self.username = None
                self.cell_id = 0

            def anonymous_login(self) -> _OK:
                self.connected = True
                self.logged_on = True
                self.cell_id = 5
                return _OK()

            def disconnect(self) -> None:
                self.connected = False

        async def _main() -> tuple:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                client = AsyncSteamClient()
                pre = client.status
                await client.start()
                await client.anonymous_login()
                live = client.status
                await client.close()
                post = client.status
                return pre, live, post

        pre, live, post = _run(_main())
        self.assertFalse(pre.started)
        self.assertFalse(pre.connected)

        self.assertTrue(live.started)
        self.assertTrue(live.connected)
        self.assertTrue(live.logged_on)
        self.assertEqual(live.cell_id, 5)
        self.assertIsNotNone(live.uptime_seconds)
        self.assertGreater(live.uptime_seconds or 0, 0)
        self.assertIsNotNone(live.last_activity_at)

        self.assertTrue(post.closed)

    def test_metrics_hook_fires_on_lifecycle_and_rpc(self) -> None:
        """The hook receives ``client.started``, ``rpc.started``,
        ``rpc.succeeded`` (with ``duration_ms``), and
        ``client.closed`` in the right order for a normal call."""

        events: list = []

        def hook(event: str, tags: dict) -> None:
            events.append((event, dict(tags)))

        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()

            def anonymous_login(self) -> _OK:
                # Cheap fake CM latency so ``duration_ms`` is > 0.
                time.sleep(0.005)
                return _OK()

            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                client = AsyncSteamClient(metrics_hook=hook)
                await client.start()
                await client.anonymous_login()
                await client.close()

        _run(_main())

        names = [e for e, _tags in events]
        self.assertIn("client.started", names)
        self.assertIn("rpc.started", names)
        self.assertIn("rpc.succeeded", names)
        self.assertIn("client.closed", names)

        # rpc.succeeded carries method + numeric duration_ms
        rpc_end = [tags for e, tags in events if e == "rpc.succeeded"][0]
        self.assertEqual(rpc_end["method"], "anonymous_login")
        self.assertGreaterEqual(rpc_end["duration_ms"], 0)

    def test_metrics_hook_that_raises_does_not_kill_rpc(self) -> None:
        """A broken hook implementation must not take down the
        request path — we swallow its exceptions and keep going."""

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> _OK:
                return _OK()

            def disconnect(self) -> None:
                pass

        def hook(event: str, tags: dict) -> None:
            raise RuntimeError("someone's Prometheus is broken")

        async def _main() -> Any:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient(metrics_hook=hook) as client:
                    # Should complete despite the hook raising on every event.
                    return await client.anonymous_login()

        result = _run(_main())
        self.assertEqual(getattr(result, "name", None), "OK")


# ----------------------------------------------------------------------
# Cancellation → greenlet kill
# ----------------------------------------------------------------------


class CancellationTests(unittest.TestCase):
    def test_wait_for_timeout_kills_running_greenlet(self) -> None:
        """A ``asyncio.wait_for`` timeout on an in-flight RPC must
        (a) raise ``TimeoutError`` on the awaiter, AND (b) actually
        stop the gevent greenlet running the sync work — otherwise
        the runner thread accumulates zombie greenlets on every
        cancelled request."""

        # Track whether the sync work actually terminated via
        # GreenletExit (kill) or ran to completion.
        state = {"finished_normally": False, "killed": False}

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> _OK:
                # A cooperative long sleep gevent can interrupt.
                # Real ``login`` blocks on ``wait_msg`` which does
                # the same thing internally.
                import gevent

                try:
                    gevent.sleep(5.0)
                    state["finished_normally"] = True
                except BaseException:
                    state["killed"] = True
                    raise
                return _OK()

            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    with self.assertRaises(asyncio.TimeoutError):
                        await asyncio.wait_for(
                            client.anonymous_login(),
                            timeout=0.1,
                        )
                    # Give the kill a moment to land on the runner thread.
                    await asyncio.sleep(0.3)

        _run(_main())
        self.assertTrue(
            state["killed"],
            "greenlet was not killed after asyncio cancellation " f"(state={state!r})",
        )
        self.assertFalse(state["finished_normally"])


# ----------------------------------------------------------------------
# AsyncSteamPool
# ----------------------------------------------------------------------


class PoolTests(unittest.TestCase):
    def _stub_class(
        self,
        anon_result: Any = None,
        anon_raises: bool = False,
    ) -> type:
        """Build a fresh Stub class per test — the pool creates one
        SteamClient per member, so a shared Stub class with mutable
        state would leak between members."""

        _result = anon_result if anon_result is not None else _OK()

        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False

            def anonymous_login(self) -> Any:
                if anon_raises:
                    raise RuntimeError("login refused")
                self.connected = True
                self.logged_on = True
                return _result

            def disconnect(self) -> None:
                self.connected = False

        return Stub

    def test_pool_starts_all_members_concurrently(self) -> None:
        from steam.aio import AsyncSteamPool, PoolMember

        Stub = self._stub_class()

        async def _login(c: Any) -> None:
            await c.anonymous_login()

        async def _main() -> list:
            with mock.patch("steam.client.SteamClient", Stub):
                pool = AsyncSteamPool(
                    [
                        PoolMember(account_id="alice", login=_login),
                        PoolMember(account_id="bob", login=_login),
                        PoolMember(account_id="carol", login=_login),
                    ]
                )
                await pool.start()
                try:
                    return pool.status()
                finally:
                    await pool.close()

        statuses = _run(_main())
        self.assertEqual(
            [s.account_id for s in statuses],
            ["alice", "bob", "carol"],
        )
        self.assertTrue(all(s.ready for s in statuses))
        self.assertTrue(all(s.failure is None for s in statuses))

    def test_pool_round_robin_returns_all_members_in_order(self) -> None:
        from steam.aio import AsyncSteamPool, PoolMember

        Stub = self._stub_class()

        async def _login(c: Any) -> None:
            await c.anonymous_login()

        async def _main() -> list:
            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamPool(
                    [
                        PoolMember(account_id="a", login=_login),
                        PoolMember(account_id="b", login=_login),
                        PoolMember(account_id="c", login=_login),
                    ]
                ) as pool:
                    picks: list = []
                    for _ in range(6):
                        picks.append(pool.round_robin())
                    return picks

        picks = _run(_main())
        # Two full rotations across the three members, in
        # ``sorted(account_ids)`` order.
        self.assertEqual(len(picks), 6)
        # Each pick is a client instance — verify we cycled by
        # comparing distinct ids in the first 3 picks.
        self.assertEqual(len({id(c) for c in picks[:3]}), 3)
        # Second rotation is the same trio in the same order.
        self.assertEqual([id(c) for c in picks[:3]], [id(c) for c in picks[3:]])

    def test_pool_isolates_member_failure(self) -> None:
        """One member that fails to log in does not abort the pool
        — the other members come up, and the failed one shows up
        in ``status()`` with a populated ``failure``.

        Failure lives in each member's per-``login`` callable
        rather than in a rotating ``SteamClient`` factory — the
        pool starts members concurrently, so factory-order is
        non-deterministic and can't be relied on to pick which
        member sees which stub.
        """

        from steam.aio import AsyncSteamPool, PoolMember

        Stub = self._stub_class()

        async def _login_ok(c: Any) -> None:
            await c.anonymous_login()

        async def _login_fail(c: Any) -> None:
            raise RuntimeError("login refused")

        async def _main() -> list:
            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamPool(
                    [
                        PoolMember(account_id="good", login=_login_ok),
                        PoolMember(account_id="bad", login=_login_fail),
                        PoolMember(account_id="also_good", login=_login_ok),
                    ]
                ) as pool:
                    return pool.status()

        statuses = _run(_main())
        by_id = {s.account_id: s for s in statuses}
        self.assertTrue(by_id["good"].ready)
        self.assertTrue(by_id["also_good"].ready)
        self.assertFalse(by_id["bad"].ready)
        self.assertIsNotNone(by_id["bad"].failure)
        self.assertIn("login refused", by_id["bad"].failure or "")

    def test_pool_acquire_by_id(self) -> None:
        from steam.aio import AsyncSteamPool, PoolMember

        Stub = self._stub_class()

        async def _login(c: Any) -> None:
            await c.anonymous_login()

        async def _main() -> tuple:
            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamPool(
                    [
                        PoolMember(account_id="alice", login=_login),
                    ]
                ) as pool:
                    a = pool.acquire("alice")
                    try:
                        pool.acquire("nobody")
                    except KeyError as e:
                        raised_key = str(e)
                    else:
                        raised_key = None
                    return a, raised_key

        a, raised = _run(_main())
        self.assertIsNotNone(a)
        self.assertIsNotNone(raised)
        self.assertIn("unknown pool member", raised or "")


# ----------------------------------------------------------------------
# FastAPI integration
# ----------------------------------------------------------------------


class FastAPIIntegrationTests(unittest.TestCase):
    def test_lifespan_attaches_client_to_state_and_closes_on_exit(self) -> None:
        try:
            from fastapi import FastAPI
        except ImportError:
            self.skipTest("fastapi not installed")

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> _OK:
                return _OK()

            def disconnect(self) -> None:
                pass

        async def _main() -> tuple:
            from steam.aio import AsyncSteamClient
            from steam.aio.integrations.fastapi import steam_client_lifespan

            with mock.patch("steam.client.SteamClient", Stub):
                app = FastAPI()
                client = AsyncSteamClient()

                async def _login(c: Any) -> None:
                    await c.anonymous_login()

                async with steam_client_lifespan(
                    app,
                    client,
                    on_start=_login,
                ):
                    inside = getattr(app.state, "steam", None)
                    inside_id = id(inside)
                    inside_ready = inside is not None and inside is client
                outside = getattr(app.state, "steam", "MISSING")
                closed = client._closed  # noqa: SLF001
                return inside_ready, inside_id, id(client), outside, closed

        inside_ready, inside_id, client_id, outside, closed = _run(_main())
        self.assertTrue(inside_ready)
        self.assertEqual(inside_id, client_id)
        # After lifespan exit, state attr is cleared and client is closed.
        self.assertIsNone(outside)
        self.assertTrue(closed)


# ----------------------------------------------------------------------
# TaskIQ integration
# ----------------------------------------------------------------------


class TaskIQIntegrationTests(unittest.TestCase):
    def test_register_wires_startup_shutdown_and_returns_dep(self) -> None:
        try:
            import taskiq  # noqa: F401
        except ImportError:
            self.skipTest("taskiq not installed")

        # Minimal broker double — the helper only needs an
        # ``add_event_handler`` method.  Using a fake keeps this
        # test off the network / redis.
        class FakeBroker:
            def __init__(self) -> None:
                self.handlers: dict = {}

            def add_event_handler(
                self,
                name: str,
                handler: Callable[..., Any],
            ) -> None:
                self.handlers[name] = handler

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> _OK:
                return _OK()

            def disconnect(self) -> None:
                pass

        async def _main() -> tuple:
            from steam.aio import AsyncSteamClient
            from steam.aio.integrations.taskiq import register_steam_client

            with mock.patch("steam.client.SteamClient", Stub):
                broker = FakeBroker()
                client = AsyncSteamClient()

                async def _login(c: Any) -> None:
                    await c.anonymous_login()

                # ``FakeBroker`` implements the two-method subset of
                # ``AsyncBroker`` (``add_event_handler``) that
                # ``register_steam_client`` actually touches — a full
                # ``AsyncBroker`` would need a redis / whatever backing
                # and defeat the whole point of a unit test.  Cast to
                # ``Any`` at the boundary so Pylance / mypy don't flag
                # the structural mismatch.
                dep = register_steam_client(
                    cast(Any, broker),
                    client,
                    on_start=_login,
                )
                # Startup handler was registered — run it.  The key
                # is the ``TaskiqEvents`` enum (not the bare string
                # "startup") because that's what the helper feeds
                # into ``broker.add_event_handler`` — matching what
                # taskiq itself requires.
                from taskiq import TaskiqEvents

                await broker.handlers[TaskiqEvents.WORKER_STARTUP]()
                depped = dep()
                started = client._sync is not None  # noqa: SLF001
                await broker.handlers[TaskiqEvents.WORKER_SHUTDOWN]()
                closed = client._closed  # noqa: SLF001
                return depped is client, started, closed

        depped_is_client, started, closed = _run(_main())
        self.assertTrue(depped_is_client)
        self.assertTrue(started)
        self.assertTrue(closed)


# ----------------------------------------------------------------------
# steam.mcp
# ----------------------------------------------------------------------


class MCPToolTests(unittest.TestCase):
    def test_tool_bindings_have_stable_names(self) -> None:
        from steam.mcp import build_steam_tool_bindings

        names = {b.name for b in build_steam_tool_bindings()}
        # These are the names the LLM contract commits to — a
        # rename is a breaking change for existing MCP clients.
        self.assertEqual(
            names,
            {"steam.status", "steam.get_product_info", "steam.send_um"},
        )

    def test_steam_status_tool_returns_healthy_snapshot(self) -> None:
        from steam.mcp.tools import (
            SteamStatusInput,
            _tool_steam_status,
        )

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> _OK:
                self.connected = True
                self.logged_on = True
                return _OK()

            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False
                self.username = None
                self.cell_id = 0

            def disconnect(self) -> None:
                pass

        async def _main() -> Any:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    await client.anonymous_login()
                    out = await _tool_steam_status(client, SteamStatusInput())
                    return out

        out = _run(_main())
        self.assertTrue(out.healthy)
        self.assertTrue(out.connected)
        self.assertTrue(out.logged_on)

    def test_get_product_info_tool_forwards_apps_and_returns_typed_output(self) -> None:
        from steam.mcp.tools import (
            GetProductInfoInput,
            _tool_get_product_info,
        )

        received: dict = {}

        class Stub(_FakeEmitter):
            def get_product_info(self, **kw: Any) -> dict:
                received.update(kw)
                return {
                    "apps": {440: {"common": {"name": "Team Fortress 2"}}},
                    "packages": {},
                }

            def disconnect(self) -> None:
                pass

        async def _main() -> Any:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    return await _tool_get_product_info(
                        client,
                        GetProductInfoInput(apps=[440]),
                    )

        out = _run(_main())
        self.assertIn(440, out.apps)
        self.assertEqual(out.apps[440]["common"]["name"], "Team Fortress 2")
        self.assertEqual(received["apps"], [440])

    def test_get_product_info_rejects_empty_input(self) -> None:
        """The tool must reject requests with no ids — otherwise
        the model can ask 'get info' with no target and burn a CM
        call for nothing."""

        from steam.mcp.tools import (
            GetProductInfoInput,
            _tool_get_product_info,
        )

        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    await _tool_get_product_info(
                        client,
                        GetProductInfoInput(),
                    )

        with self.assertRaises(ValueError):
            _run(_main())

    def test_register_steam_tools_on_fastmcp(self) -> None:
        try:
            from mcp.server.fastmcp import FastMCP
        except ImportError:
            self.skipTest("mcp SDK not installed")

        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> list:
            from steam.aio import AsyncSteamClient
            from steam.mcp import register_steam_tools

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    server = FastMCP("SteamTest")
                    return register_steam_tools(server, client)

        registered = _run(_main())
        self.assertEqual(
            sorted(registered),
            ["steam.get_product_info", "steam.send_um", "steam.status"],
        )


if __name__ == "__main__":
    unittest.main()

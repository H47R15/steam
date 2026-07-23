"""Unit tests for :mod:`steam.aio`.

Pure Python, no live network.  Verifies:

* The gevent runner thread boots, dispatches work, and shuts down
  cleanly without leaking a thread.  Critically: background greenlets
  keep making progress between asyncio submissions — that's why we
  own a hub instead of using ``run_in_executor(None, sync_call)``.
* The public :class:`AsyncSteamClient` facade forwards its methods
  onto a stub ``SteamClient`` correctly (arg passthrough, exception
  propagation, kwargs).
* Auto-reconnect fires on a synthetic ``'disconnected'`` event,
  replays the last-known login, and gives up per :class:`ReconnectPolicy`.
* The event bridge (``wait_event`` / ``events``) delivers sync-side
  events to the asyncio thread with timeout + streaming semantics.
* Typed exceptions from :mod:`steam.aio.errors` are raised in the
  right places (start / close / login failure / timeout).

Tests use plain ``asyncio.run`` — no ``pytest-asyncio`` dependency
so they run under the repo's default test config.
"""

from __future__ import annotations

import asyncio
import time
import unittest
from collections.abc import Callable
from typing import Any
from unittest import mock


def _run(coro: Any) -> Any:
    """Tiny ``asyncio.run`` wrapper — keeps the test bodies free of
    the ``asyncio.new_event_loop`` boilerplate that older test
    runners sometimes need."""
    return asyncio.run(coro)


# ----------------------------------------------------------------------
# Test doubles
# ----------------------------------------------------------------------


class _OK:
    """Stands in for :class:`steam.enums.EResult.OK` — the facade
    checks ``.name == "OK"`` so any object with that attribute
    passes the login gate.  Avoids importing the real EResult (and
    thereby pulling gevent) into the test process.
    """

    name = "OK"

    def __repr__(self) -> str:
        return "_OK()"


class _FakeEmitter:
    """Minimal ``EventEmitter``-shaped mixin for stub sync clients.
    The real ``SteamClient`` extends ``gevent_eventemitter.EventEmitter``;
    for tests, we only need ``on`` / ``emit`` / ``remove_listener``.
    """

    def __init__(self) -> None:
        self._listeners: dict = {}

    def on(self, name: str, callback: Callable[..., Any]) -> None:
        self._listeners.setdefault(name, []).append(callback)

    def emit(self, name: str, *args: Any) -> None:
        for cb in list(self._listeners.get(name, ())):
            try:
                cb(*args)
            except Exception:  # noqa: BLE001
                # Real EventEmitter swallows listener errors; do the
                # same so a broken subscriber doesn't cascade into
                # test failures unrelated to the assertion.
                pass

    def remove_listener(self, name: str, callback: Callable[..., Any]) -> None:
        try:
            self._listeners.get(name, []).remove(callback)
        except ValueError:
            pass


# ----------------------------------------------------------------------
# GeventRunner
# ----------------------------------------------------------------------


class GeventRunnerTests(unittest.TestCase):
    def test_start_then_submit_returns_result(self) -> None:
        from steam.aio.runner import GeventRunner

        runner = GeventRunner()
        runner.start()
        try:
            fut = runner.submit(lambda: 21 * 2)
            self.assertEqual(fut.result(timeout=5), 42)
        finally:
            runner.stop()

    def test_submit_propagates_exception(self) -> None:
        from steam.aio.runner import GeventRunner

        class Boom(RuntimeError):
            pass

        runner = GeventRunner()
        runner.start()
        try:
            fut = runner.submit(lambda: (_ for _ in ()).throw(Boom("nope")))
            with self.assertRaises(Boom):
                fut.result(timeout=5)
        finally:
            runner.stop()

    def test_submit_after_stop_raises(self) -> None:
        from steam.aio.runner import GeventRunner

        runner = GeventRunner()
        runner.start()
        runner.stop()
        with self.assertRaises(RuntimeError):
            runner.submit(lambda: None)

    def test_stop_is_idempotent(self) -> None:
        from steam.aio.runner import GeventRunner

        runner = GeventRunner()
        runner.start()
        runner.stop()
        runner.stop()  # second call must not raise

    def test_thread_is_daemon(self) -> None:
        from steam.aio.runner import GeventRunner

        runner = GeventRunner()
        runner.start()
        try:
            self.assertTrue(runner._thread.daemon)  # noqa: SLF001
        finally:
            runner.stop()

    def test_background_greenlets_keep_running_between_submits(self) -> None:
        """The whole reason we run our own hub (instead of
        ``run_in_executor(None, sync_call)``) is that background
        greenlets need to make progress between calls — otherwise
        the CM heartbeat stops and the connection dies at 30s.
        """
        from steam.aio.runner import GeventRunner

        runner = GeventRunner()
        runner.start()
        try:
            counter = {"n": 0}

            def _install_ticker() -> None:
                import gevent

                def _tick() -> None:
                    while True:
                        counter["n"] += 1
                        gevent.sleep(0.05)

                gevent.spawn(_tick)

            runner.submit(_install_ticker).result(timeout=5)
            time.sleep(0.3)
            self.assertGreaterEqual(
                counter["n"],
                3,
                f"background greenlet only ticked {counter['n']} times — "
                "the gevent hub is stalling between submits",
            )
        finally:
            runner.stop()


# ----------------------------------------------------------------------
# AsyncSteamClient — happy paths
# ----------------------------------------------------------------------


class AsyncSteamClientTests(unittest.TestCase):
    def _run_with_stub(self, coro_factory: Any, stub_cls: Any) -> Any:
        async def _main() -> Any:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", stub_cls):
                async with AsyncSteamClient() as client:
                    return await coro_factory(client)

        return _run(_main())

    def test_anonymous_login_roundtrips(self) -> None:
        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False

            def anonymous_login(self) -> _OK:
                self.connected = True
                self.logged_on = True
                return _OK()

            def disconnect(self) -> None:
                self.connected = False

        async def _do(c: Any) -> Any:
            result = await c.anonymous_login()
            return getattr(result, "name", None)

        self.assertEqual(self._run_with_stub(_do, Stub), "OK")

    def test_get_product_info_forwards_kwargs(self) -> None:
        received: dict = {}

        class Stub(_FakeEmitter):
            def get_product_info(self, **kw: Any) -> dict:
                received.update(kw)
                return {"apps": {440: {"common": {"name": "Team Fortress 2"}}}}

            def disconnect(self) -> None:
                pass

        async def _do(c: Any) -> dict:
            return await c.get_product_info(
                apps=[440],
                meta_data_only=True,
                timeout=7.5,
            )

        result = self._run_with_stub(_do, Stub)
        self.assertIn("apps", result)
        self.assertEqual(received["apps"], [440])
        self.assertEqual(received["packages"], [])
        self.assertTrue(received["meta_data_only"])
        self.assertEqual(received["timeout"], 7.5)

    def test_send_um_and_wait_forwards_kwargs(self) -> None:
        received: dict = {}

        class Stub(_FakeEmitter):
            def send_um_and_wait(
                self,
                method_name: str,
                params: dict,
                *,
                timeout: float,
                raises: bool,
            ) -> dict:
                received["method_name"] = method_name
                received["params"] = params
                received["timeout"] = timeout
                received["raises"] = raises
                return {"ok": True, "level": 5}

            def disconnect(self) -> None:
                pass

        async def _do(c: Any) -> dict:
            return await c.send_um_and_wait(
                "Player.GetGameBadgeLevels#1",
                {"appid": 730},
                timeout=8.0,
            )

        result = self._run_with_stub(_do, Stub)
        self.assertEqual(result, {"ok": True, "level": 5})
        self.assertEqual(received["method_name"], "Player.GetGameBadgeLevels#1")
        self.assertEqual(received["params"], {"appid": 730})
        self.assertEqual(received["timeout"], 8.0)
        self.assertFalse(received["raises"])

    def test_exception_from_sync_client_propagates(self) -> None:
        class Boom(RuntimeError):
            pass

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> Any:
                raise Boom("CM refused")

            def disconnect(self) -> None:
                pass

        async def _do(c: Any) -> None:
            await c.anonymous_login()

        with self.assertRaises(Boom):
            self._run_with_stub(_do, Stub)

    def test_close_before_start_is_safe(self) -> None:
        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            client = AsyncSteamClient()
            await client.close()  # must not raise

        _run(_main())

    def test_runner_thread_dies_within_close(self) -> None:
        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> Any:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                client = AsyncSteamClient()
                await client.start()
                thread = client._runner._thread  # noqa: SLF001
                await client.close()
                return thread

        thread = _run(_main())
        deadline = time.time() + 3.0
        while thread.is_alive() and time.time() < deadline:
            time.sleep(0.05)
        self.assertFalse(
            thread.is_alive(),
            "runner thread did not exit within 3s of close()",
        )


# ----------------------------------------------------------------------
# AsyncSteamClient — typed errors
# ----------------------------------------------------------------------


class TypedErrorTests(unittest.TestCase):
    def test_not_started_error_on_method_call(self) -> None:
        from steam.aio import AsyncSteamClient, SteamNotStartedError

        async def _main() -> None:
            client = AsyncSteamClient()
            with self.assertRaises(SteamNotStartedError):
                await client.anonymous_login()

        _run(_main())

    def test_closed_error_after_close(self) -> None:
        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient, SteamClosedError

            with mock.patch("steam.client.SteamClient", Stub):
                client = AsyncSteamClient()
                await client.start()
                await client.close()
                with self.assertRaises(SteamClosedError):
                    await client.disconnect()

        _run(_main())

    def test_login_error_on_non_ok_eresult(self) -> None:
        class Rejected:
            name = "InvalidPassword"

            def __repr__(self) -> str:
                return "EResult.InvalidPassword"

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> Rejected:
                return Rejected()

            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient, SteamLoginError

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    with self.assertRaises(SteamLoginError) as ctx:
                        await client.anonymous_login()
                    self.assertEqual(
                        getattr(ctx.exception.eresult, "name", None),
                        "InvalidPassword",
                    )

        _run(_main())

    def test_login_error_can_be_suppressed(self) -> None:
        """Callers who need the raw EResult can opt out of the raise."""

        class Rejected:
            name = "InvalidPassword"

        class Stub(_FakeEmitter):
            def anonymous_login(self) -> Rejected:
                return Rejected()

            def disconnect(self) -> None:
                pass

        async def _main() -> str:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    result = await client.anonymous_login(raise_on_error=False)
                    return result.name

        self.assertEqual(_run(_main()), "InvalidPassword")


# ----------------------------------------------------------------------
# Event bridge
# ----------------------------------------------------------------------


class EventBridgeTests(unittest.TestCase):
    def test_wait_event_returns_args_tuple(self) -> None:
        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> tuple:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    # Schedule the emit to happen shortly after the
                    # wait starts.  We drive it from the runner thread
                    # so the asyncio side actually blocks on the queue.
                    async def _fire() -> None:
                        await asyncio.sleep(0.05)
                        client._runner.submit(  # noqa: SLF001
                            lambda: client._sync.emit(  # noqa: SLF001
                                "channel_secured",
                                "arg-a",
                                "arg-b",
                            ),
                        )

                    fire_task = asyncio.create_task(_fire())
                    result = await client.wait_event("channel_secured", timeout=2.0)
                    await fire_task
                    return result

        name, args = _run(_main())
        self.assertEqual(name, "channel_secured")
        self.assertEqual(args, ("arg-a", "arg-b"))

    def test_wait_event_timeout_raises_typed_error(self) -> None:
        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient, SteamRPCTimeoutError

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    with self.assertRaises(SteamRPCTimeoutError):
                        await client.wait_event("never_emitted", timeout=0.1)

        _run(_main())

    def test_events_iterator_yields_multiple(self) -> None:
        class Stub(_FakeEmitter):
            def disconnect(self) -> None:
                pass

        async def _main() -> list:
            from steam.aio import AsyncSteamClient

            collected: list = []
            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:

                    async def _consume() -> None:
                        # ``channel_secured`` / ``logged_on`` are real
                        # Steam event names that do NOT trigger the
                        # auto-reconnect machinery — subscribing to
                        # ``disconnected`` here would spawn a reconnect
                        # greenlet on the runner thread (a documented
                        # feature; see the reconnect tests) and add
                        # unrelated churn to this test.
                        agen = client.events("channel_secured", "logged_on")
                        try:
                            async for evt in agen:
                                collected.append(evt)
                                if len(collected) >= 2:
                                    break
                        finally:
                            await agen.aclose()

                    consumer = asyncio.create_task(_consume())
                    # Give the consumer a tick to install its listeners
                    # before we fire events on the runner thread.
                    await asyncio.sleep(0.05)
                    client._runner.submit(  # noqa: SLF001
                        lambda: client._sync.emit("channel_secured"),  # noqa: SLF001
                    )
                    client._runner.submit(  # noqa: SLF001
                        lambda: client._sync.emit("logged_on"),  # noqa: SLF001
                    )
                    await asyncio.wait_for(consumer, timeout=2.0)
            return collected

        collected = _run(_main())
        names = [n for n, _args in collected]
        self.assertEqual(names, ["channel_secured", "logged_on"])


# ----------------------------------------------------------------------
# Auto-reconnect
# ----------------------------------------------------------------------


class ReconnectTests(unittest.TestCase):
    def test_disconnect_triggers_reconnect_and_replays_anonymous_login(self) -> None:
        """Baseline reconnect: emit ``'disconnected'`` on the sync
        client, verify ``sync.reconnect()`` is invoked once and
        ``anonymous_login`` is replayed."""

        calls = {"reconnect": 0, "anon_login": 0}

        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False
                self.username = None
                self.login_key = None
                self.relogin_available = False

            def anonymous_login(self) -> _OK:
                calls["anon_login"] += 1
                self.connected = True
                self.logged_on = True
                return _OK()

            def reconnect(self, maxdelay: int = 30) -> bool:
                calls["reconnect"] += 1
                self.connected = True
                return True

            def disconnect(self) -> None:
                self.connected = False

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    await client.anonymous_login()
                    self.assertEqual(calls["anon_login"], 1)
                    # Fire a disconnect on the runner thread —
                    # ``_on_sync_disconnect`` runs there and spawns
                    # the reconnect greenlet.
                    reconnected_evt = asyncio.create_task(
                        client.wait_event("aio.reconnected", timeout=3.0),
                    )
                    # Small delay so the subscriber lands before we
                    # emit the disconnect that ultimately fires
                    # ``aio.reconnected``.
                    await asyncio.sleep(0.05)
                    client._runner.submit(  # noqa: SLF001
                        lambda: client._sync.emit("disconnected"),  # noqa: SLF001
                    )
                    name, args = await reconnected_evt
                    self.assertEqual(name, "aio.reconnected")
                    self.assertEqual(args, (1,))  # attempt count
                    self.assertEqual(calls["reconnect"], 1)
                    self.assertEqual(calls["anon_login"], 2)  # replayed

        _run(_main())

    def test_reconnect_gives_up_after_max_attempts(self) -> None:
        """Reconnect that never succeeds should emit
        ``aio.reconnect_failed`` after ``max_attempts`` and stop."""

        calls = {"reconnect": 0}

        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False
                self.username = None

            def anonymous_login(self) -> _OK:
                return _OK()

            def reconnect(self, maxdelay: int = 30) -> bool:
                calls["reconnect"] += 1
                return False

            def disconnect(self) -> None:
                pass

        async def _main() -> None:
            from steam.aio import AsyncSteamClient, ReconnectPolicy

            with mock.patch("steam.client.SteamClient", Stub):
                policy = ReconnectPolicy(max_attempts=3, max_delay=1)
                async with AsyncSteamClient(reconnect=policy) as client:
                    await client.anonymous_login()
                    failed = asyncio.create_task(
                        client.wait_event("aio.reconnect_failed", timeout=3.0),
                    )
                    await asyncio.sleep(0.05)
                    client._runner.submit(  # noqa: SLF001
                        lambda: client._sync.emit("disconnected"),  # noqa: SLF001
                    )
                    name, args = await failed
                    self.assertEqual(name, "aio.reconnect_failed")
                    self.assertEqual(args[0], 3)  # attempts
                    self.assertEqual(calls["reconnect"], 3)

        _run(_main())

    def test_intentional_disconnect_does_not_trigger_reconnect(self) -> None:
        """Calling ``disconnect()`` / ``logout()`` sets the
        ``_intentional_disconnect`` flag — a subsequent
        ``'disconnected'`` event must NOT spawn a reconnect."""

        calls = {"reconnect": 0}

        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False

            def anonymous_login(self) -> _OK:
                return _OK()

            def reconnect(self, maxdelay: int = 30) -> bool:
                calls["reconnect"] += 1
                return True

            def disconnect(self) -> None:
                self.connected = False
                # Real client emits 'disconnected' from within disconnect().
                self.emit("disconnected")

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", Stub):
                async with AsyncSteamClient() as client:
                    await client.anonymous_login()
                    await client.disconnect()
                    # Give the runner a beat in case a rogue reconnect
                    # greenlet is about to fire.
                    await asyncio.sleep(0.1)
                    self.assertEqual(calls["reconnect"], 0)

        _run(_main())


if __name__ == "__main__":
    unittest.main()

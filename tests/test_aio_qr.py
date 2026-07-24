"""Unit tests for :mod:`steam.aio.qr`.

Pure-Python; the underlying ``AsyncSteamClient.send_um_and_wait`` is
patched with a scripted queue of responses so tests exercise the
polling / expiry / rotation branches deterministically without a
live CM connection.
"""

from __future__ import annotations

import base64
import time
import unittest
from typing import Any
from unittest import mock

from tests.test_aio_client import _FakeEmitter, _run


class _Body(dict):
    """Dict + ``.body`` self-alias — mirrors what ``send_um_and_wait``
    would hand back for a real response (``.body`` attribute holding
    the parsed proto), without needing a full proto stub."""

    @property
    def body(self):  # noqa: D401 — property, not a description
        return self


def _make_client_with_scripted_um(responses: list[Any]):
    """Return an async context manager that yields an AsyncSteamClient
    whose ``send_um_and_wait`` pops from a fixed list of scripted
    responses.  ``responses`` may hold ``_Body`` dicts, ``None``
    (empty body), or exceptions (raised at call time)."""

    class Stub(_FakeEmitter):
        def disconnect(self):
            pass

    async def _make():
        from steam.aio import AsyncSteamClient

        client = AsyncSteamClient()
        # Bypass real gevent + CM connect — the tests only exercise
        # the QR helpers which route through ``send_um_and_wait``,
        # which we override immediately below.
        with mock.patch("steam.client.SteamClient", Stub):
            await client.start()

        async def _fake_send_um(
            method_name: str,
            params: dict | None = None,
            *,
            timeout: float = 10.0,
            raises: bool = False,
        ) -> Any:
            if not responses:
                raise AssertionError(
                    f"scripted responses exhausted — extra call to {method_name!r}",
                )
            entry = responses.pop(0)
            if isinstance(entry, BaseException):
                raise entry
            return entry

        client.send_um_and_wait = _fake_send_um  # type: ignore[assignment]
        return client

    return _make


class QRLoginSessionTests(unittest.TestCase):
    def test_begin_returns_session_populated_from_response(self) -> None:
        raw_request_id = b"\x01\x02\x03\x04"
        make = _make_client_with_scripted_um(
            [
                _Body(
                    {
                        "client_id": 12345,
                        "request_id": raw_request_id,
                        "challenge_url": "steam://qr/abcdef",
                        "interval": 5.0,
                        "version": 1,
                    }
                ),
            ]
        )

        async def _main():
            client = await make()
            try:
                session = await client.begin_qr_login(
                    device_friendly_name="test-client",
                    website_id="Community",
                )
                return session
            finally:
                await client.close()

        session = _run(_main())
        self.assertEqual(session.client_id, 12345)
        # request_id is base64-encoded on the session so it JSON-serialises.
        self.assertEqual(
            base64.b64decode(session.request_id),
            raw_request_id,
        )
        self.assertEqual(session.challenge_url, "steam://qr/abcdef")
        self.assertEqual(session.interval, 5.0)
        self.assertEqual(session.version, 1)
        self.assertGreater(session.started_at, 0)

    def test_poll_returns_none_while_pending(self) -> None:
        make = _make_client_with_scripted_um(
            [
                _Body(
                    {
                        "client_id": 1,
                        "request_id": b"x",
                        "challenge_url": "steam://qr/x",
                        "interval": 5.0,
                        "version": 1,
                    }
                ),
                _Body({}),  # empty poll → still pending
            ]
        )

        async def _main():
            client = await make()
            try:
                session = await client.begin_qr_login()
                return await client.poll_qr_status(session)
            finally:
                await client.close()

        self.assertIsNone(_run(_main()))

    def test_poll_returns_tokens_when_confirmed(self) -> None:
        make = _make_client_with_scripted_um(
            [
                _Body(
                    {
                        "client_id": 1,
                        "request_id": b"x",
                        "challenge_url": "steam://qr/x",
                        "interval": 5.0,
                        "version": 1,
                    }
                ),
                _Body(
                    {
                        "refresh_token": "refresh-abc",
                        "access_token": "access-xyz",
                        "account_name": "someone",
                        "new_guard_data": "guard-blob",
                        "had_remote_interaction": True,
                    }
                ),
            ]
        )

        async def _main():
            client = await make()
            try:
                session = await client.begin_qr_login()
                return await client.poll_qr_status(session)
            finally:
                await client.close()

        result = _run(_main())
        self.assertIsNotNone(result)
        assert result is not None  # for mypy
        self.assertEqual(result.refresh_token, "refresh-abc")
        self.assertEqual(result.access_token, "access-xyz")
        self.assertEqual(result.account_name, "someone")
        self.assertEqual(result.guard_data, "guard-blob")
        self.assertTrue(result.had_remote_interaction)

    def test_wait_confirmation_polls_until_tokens_land(self) -> None:
        # Three empty polls (still pending) then a token-carrying
        # response.  Interval overridden to 0.01s so the test
        # doesn't sit around for ~15s.
        make = _make_client_with_scripted_um(
            [
                _Body(
                    {
                        "client_id": 1,
                        "request_id": b"x",
                        "challenge_url": "steam://qr/x",
                        "interval": 5.0,
                        "version": 1,
                    }
                ),
                _Body({}),
                _Body({}),
                _Body({}),
                _Body(
                    {
                        "refresh_token": "final-token",
                        "access_token": "access-token",
                        "account_name": "sig",
                    }
                ),
            ]
        )

        async def _main():
            client = await make()
            try:
                session = await client.begin_qr_login()
                return await client.wait_qr_confirmation(
                    session,
                    interval_override=0.01,
                    timeout=5.0,
                )
            finally:
                await client.close()

        result = _run(_main())
        self.assertEqual(result.refresh_token, "final-token")

    def test_wait_raises_qr_expired_on_challenge_rotation(self) -> None:
        make = _make_client_with_scripted_um(
            [
                _Body(
                    {
                        "client_id": 1,
                        "request_id": b"x",
                        "challenge_url": "steam://qr/x",
                        "interval": 5.0,
                        "version": 1,
                    }
                ),
                _Body(
                    {
                        # Steam rotated the QR — surface as expired so the
                        # caller regenerates rather than silently loops.
                        "new_challenge_url": "steam://qr/rotated",
                    }
                ),
            ]
        )

        async def _main():
            from steam.aio import QRSignInExpired

            client = await make()
            try:
                session = await client.begin_qr_login()
                with self.assertRaises(QRSignInExpired):
                    await client.wait_qr_confirmation(
                        session,
                        interval_override=0.01,
                        timeout=5.0,
                    )
            finally:
                await client.close()

        _run(_main())

    def test_wait_raises_qr_expired_on_deadline(self) -> None:
        # Timeout is clamped to a 5s floor inside
        # ``_wait_for_confirmation`` so we can't test with less
        # than that — but we CAN pre-age the session by handing
        # ``_wait_for_confirmation`` a QRLoginSession whose
        # ``started_at`` is already past the deadline horizon.
        # First poll then sees remaining <= 0 and raises.
        from steam.aio.qr import QRLoginSession, _wait_for_confirmation

        aged_session = QRLoginSession(
            client_id=1,
            request_id="",
            challenge_url="steam://qr/x",
            interval=5.0,
            version=1,
            # 1000s in the past — well beyond any sane timeout.
            started_at=time.monotonic() - 1000.0,
        )

        make = _make_client_with_scripted_um(
            [
                # No begin() call — we're jumping straight to
                # _wait_for_confirmation with a hand-built session.
                # Include a couple of "still pending" polls in case
                # the deadline check somehow lets one through.
                _Body({}),
                _Body({}),
            ]
        )

        async def _main():
            from steam.aio import QRSignInExpired

            client = await make()
            try:
                with self.assertRaises(QRSignInExpired):
                    await _wait_for_confirmation(
                        client,
                        session=aged_session,
                        timeout=5.0,
                        interval_override=0.01,
                    )
            finally:
                await client.close()

        _run(_main())

    def test_wait_survives_single_rpc_timeout(self) -> None:
        # A transient SteamRPCTimeoutError on one poll should NOT
        # kill the wait — the loop retries on the next tick.
        from steam.aio.errors import SteamRPCTimeoutError

        make = _make_client_with_scripted_um(
            [
                _Body(
                    {
                        "client_id": 1,
                        "request_id": b"x",
                        "challenge_url": "steam://qr/x",
                        "interval": 5.0,
                        "version": 1,
                    }
                ),
                SteamRPCTimeoutError(15.0, "poll timed out"),
                _Body(
                    {
                        "refresh_token": "post-retry-token",
                        "access_token": "post-retry-access",
                        "account_name": "resilient",
                    }
                ),
            ]
        )

        async def _main():
            client = await make()
            try:
                session = await client.begin_qr_login()
                return await client.wait_qr_confirmation(
                    session,
                    interval_override=0.01,
                    timeout=5.0,
                )
            finally:
                await client.close()

        result = _run(_main())
        self.assertEqual(result.refresh_token, "post-retry-token")

    def test_interval_clamped_to_sane_range(self) -> None:
        # Absurd values from the server get clamped so we don't
        # poll every millisecond or wait an hour between polls.
        from steam.aio.qr import _clamp_interval

        self.assertEqual(_clamp_interval(0), 5.0)  # 0 → fallback
        self.assertEqual(_clamp_interval(-1), 5.0)  # negative → fallback
        self.assertEqual(_clamp_interval("bad"), 5.0)  # non-numeric → fallback
        self.assertEqual(_clamp_interval(0.001), 1.0)  # too small → floor
        self.assertEqual(_clamp_interval(600.0), 30.0)  # too large → ceiling
        self.assertEqual(_clamp_interval(5.0), 5.0)  # in-range → unchanged


if __name__ == "__main__":
    unittest.main()

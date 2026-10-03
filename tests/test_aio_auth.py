"""Unit tests for :mod:`steam.aio.auth` and the token login.

The credentials sign-in is driven against a scripted
``send_um_and_wait`` (the same harness as :mod:`tests.test_aio_qr`),
answering with real ``steammessages_auth`` protos where the code reads
nested messages, so the parsing is exercised against the shapes the
CM actually sends.  The password key is a real RSA key generated
here, which lets the tests decrypt what was sent and check it is the
password.
"""

from __future__ import annotations

import base64
import json
import unittest
from typing import Any
from unittest import mock

from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA

from steam.enums import EResult
from steam.protobufs import steammessages_auth_pb2 as auth_pb2
from tests.test_aio_client import _OK, _FakeEmitter, _run
from tests.test_aio_qr import _make_client_with_scripted_um

_KEY = RSA.generate(1024)
_PASSWORD = "correct horse battery staple"


class _Header:
    def __init__(self, eresult: int, error_message: str = "") -> None:
        self.eresult = eresult
        self.error_message = error_message


class _Reply:
    """What ``send_um_and_wait`` hands back: a header carrying Steam's
    ``eresult`` and the response body."""

    def __init__(self, body: Any = None, eresult: int = EResult.OK) -> None:
        self.header = _Header(int(eresult))
        self.body = body if body is not None else {}


def _key_reply() -> _Reply:
    return _Reply(
        {
            "publickey_mod": format(_KEY.n, "x"),
            "publickey_exp": format(_KEY.e, "x"),
            "timestamp": 58305950000,
        }
    )


def _begin_reply(*kinds: int, hint: str = "") -> _Reply:
    return _Reply(
        auth_pb2.CAuthentication_BeginAuthSessionViaCredentials_Response(
            client_id=4242,
            request_id=b"\x01\x02\x03",
            interval=5.0,
            steamid=76561198000000001,
            allowed_confirmations=[
                auth_pb2.CAuthentication_AllowedConfirmation(
                    confirmation_type=kind,
                    associated_message=hint,
                )
                for kind in kinds
            ],
        )
    )


def _tokens_reply() -> _Reply:
    return _Reply(
        {
            "refresh_token": "eyJ.refresh",
            "access_token": "eyJ.access",
            "account_name": "gaben",
            "new_guard_data": "guard-blob",
            "had_remote_interaction": True,
        }
    )


def _session(*kinds: int) -> Any:
    from steam.aio import CredentialsLoginSession, GuardOption, SteamGuard

    return CredentialsLoginSession(
        client_id=4242,
        request_id=base64.b64encode(b"\x01\x02\x03").decode(),
        steam_id=76561198000000001,
        account_name="gaben",
        interval=0.01,
        guards=tuple(GuardOption(kind=SteamGuard(k)) for k in kinds),
    )


def _drive(responses: list[Any], step: Any, calls: list[Any] | None = None) -> Any:
    """Run ``step(client)`` on a client whose RPCs answer ``responses``."""
    make = _make_client_with_scripted_um(responses, calls)

    async def _main() -> Any:
        client = await make()
        try:
            return await step(client)
        finally:
            await client.close()

    return _run(_main())


class BeginCredentialsLoginTests(unittest.TestCase):
    def test_encrypts_the_password_with_the_accounts_key(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []
        _drive(
            [_key_reply(), _begin_reply(1)],
            lambda c: c.begin_credentials_login("gaben", _PASSWORD),
            calls,
        )
        self.assertEqual(
            [name for name, _ in calls],
            [
                "Authentication.GetPasswordRSAPublicKey#1",
                "Authentication.BeginAuthSessionViaCredentials#1",
            ],
        )
        self.assertEqual(calls[0][1], {"account_name": "gaben"})
        begin = calls[1][1]
        sealed = base64.b64decode(begin["encrypted_password"])
        opened = PKCS1_v1_5.new(_KEY).decrypt(sealed, None)
        self.assertEqual(opened, _PASSWORD.encode())
        self.assertEqual(begin["encryption_timestamp"], 58305950000)

    def test_asks_for_a_remembered_steam_client_token(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []
        _drive(
            [_key_reply(), _begin_reply(1)],
            lambda c: c.begin_credentials_login(
                "gaben", _PASSWORD, device_friendly_name="shop sync"
            ),
            calls,
        )
        begin = calls[1][1]
        self.assertTrue(begin["remember_login"])
        self.assertEqual(begin["persistence"], 1)  # Persistent
        self.assertEqual(begin["website_id"], "Client")
        self.assertEqual(
            begin["device_details"],
            {"device_friendly_name": "shop sync", "platform_type": 1},
        )
        self.assertNotIn("guard_data", begin)

    def test_passes_guard_data_from_an_earlier_sign_in(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []
        _drive(
            [_key_reply(), _begin_reply(6)],
            lambda c: c.begin_credentials_login("gaben", _PASSWORD, guard_data="blob"),
            calls,
        )
        self.assertEqual(calls[1][1]["guard_data"], "blob")

    def test_returns_the_session_and_its_guards(self) -> None:
        from steam.aio import GuardOption, SteamGuard

        session = _drive(
            [_key_reply(), _begin_reply(2, hint="gmail.com")],
            lambda c: c.begin_credentials_login("gaben", _PASSWORD),
        )
        self.assertEqual(session.client_id, 4242)
        self.assertEqual(base64.b64decode(session.request_id), b"\x01\x02\x03")
        self.assertEqual(session.steam_id, 76561198000000001)
        self.assertEqual(session.account_name, "gaben")
        self.assertEqual(session.interval, 5.0)
        self.assertEqual(
            session.guards, (GuardOption(SteamGuard.EMAIL_CODE, "gmail.com"),)
        )
        self.assertTrue(session.needs_guard)
        self.assertEqual(session.code_kind, SteamGuard.EMAIL_CODE)

    def test_the_session_never_holds_the_password(self) -> None:
        session = _drive(
            [_key_reply(), _begin_reply(3, 4)],
            lambda c: c.begin_credentials_login("gaben", _PASSWORD),
        )
        self.assertNotIn(_PASSWORD, json.dumps(session.to_dict()))
        self.assertNotIn(_PASSWORD, repr(session))

    def test_wrong_password_is_a_login_error_carrying_the_eresult(self) -> None:
        from steam.aio import SteamLoginError

        with self.assertRaises(SteamLoginError) as caught:
            _drive(
                [_key_reply(), _Reply(eresult=EResult.InvalidPassword)],
                lambda c: c.begin_credentials_login("gaben", _PASSWORD),
            )
        self.assertEqual(caught.exception.eresult, EResult.InvalidPassword)
        self.assertIn("InvalidPassword", str(caught.exception))
        self.assertNotIn(_PASSWORD, str(caught.exception))

    def test_throttling_is_a_login_error_too(self) -> None:
        from steam.aio import SteamLoginError

        with self.assertRaises(SteamLoginError) as caught:
            _drive(
                [_Reply(eresult=EResult.RateLimitExceeded)],
                lambda c: c.begin_credentials_login("gaben", _PASSWORD),
            )
        self.assertEqual(caught.exception.eresult, EResult.RateLimitExceeded)

    def test_an_unusable_key_is_said_without_the_password(self) -> None:
        from steam.aio import SteamLoginError

        with self.assertRaises(SteamLoginError) as caught:
            _drive(
                [_Reply({"publickey_mod": "zz", "publickey_exp": "010001"})],
                lambda c: c.begin_credentials_login("gaben", _PASSWORD),
            )
        self.assertNotIn(_PASSWORD, str(caught.exception))


class GuardTests(unittest.TestCase):
    def test_no_guard_or_a_vouched_machine_needs_nobody(self) -> None:
        self.assertFalse(_session(1).needs_guard)
        self.assertFalse(_session(6).needs_guard)
        self.assertTrue(_session(4, 3).needs_guard)
        self.assertTrue(_session(5).needs_guard)

    def test_the_apps_code_comes_before_the_emailed_one(self) -> None:
        from steam.aio import SteamGuard

        self.assertEqual(_session(4, 3).code_kind, SteamGuard.DEVICE_CODE)
        self.assertEqual(_session(2).code_kind, SteamGuard.EMAIL_CODE)
        self.assertIsNone(_session(4).code_kind)
        self.assertIsNone(_session(5).code_kind)

    def test_a_guard_kind_steam_adds_later_is_unknown_not_a_crash(self) -> None:
        from steam.aio import SteamGuard

        self.assertIs(SteamGuard(99), SteamGuard.UNKNOWN)


class SessionSerialisationTests(unittest.TestCase):
    def test_round_trips_through_json(self) -> None:
        from steam.aio import CredentialsLoginSession, GuardOption, SteamGuard

        session = CredentialsLoginSession(
            client_id=4242,
            request_id="AQID",
            steam_id=76561198000000001,
            account_name="gaben",
            interval=5.0,
            guards=(GuardOption(SteamGuard.EMAIL_CODE, "gmail.com"),),
        )
        again = CredentialsLoginSession.from_dict(
            json.loads(json.dumps(session.to_dict()))
        )
        self.assertEqual(again, session)

    def test_refuses_what_to_dict_could_not_have_written(self) -> None:
        from steam.aio import CredentialsLoginSession

        for bad in (
            {},
            {"client_id": "x"},
            {
                "client_id": 0,
                "request_id": "",
                "steam_id": 1,
                "account_name": "a",
                "interval": 5,
                "guards": [],
            },
            {
                "client_id": 1,
                "request_id": "AQID",
                "steam_id": 1,
                "account_name": "a",
                "interval": 5,
                "guards": [{"kind": 2}],
            },
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                CredentialsLoginSession.from_dict(bad)


class SubmitCodeTests(unittest.TestCase):
    def test_sends_the_code_as_the_kind_the_session_takes(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []
        _drive(
            [_Reply()],
            lambda c: c.submit_steam_guard_code(_session(4, 3), " 7K2P9 \n"),
            calls,
        )
        self.assertEqual(
            calls,
            [
                (
                    "Authentication.UpdateAuthSessionWithSteamGuardCode#1",
                    {
                        "client_id": 4242,
                        "steamid": 76561198000000001,
                        "code": "7K2P9",
                        "code_type": 3,
                    },
                )
            ],
        )

    def test_a_wrong_code_is_a_login_error(self) -> None:
        from steam.aio import SteamLoginError

        with self.assertRaises(SteamLoginError) as caught:
            _drive(
                [_Reply(eresult=EResult.TwoFactorCodeMismatch)],
                lambda c: c.submit_steam_guard_code(_session(3), "AAAAA"),
            )
        self.assertEqual(caught.exception.eresult, EResult.TwoFactorCodeMismatch)

    def test_a_code_that_already_went_in_is_fine(self) -> None:
        _drive(
            [_Reply(eresult=EResult.DuplicateRequest)],
            lambda c: c.submit_steam_guard_code(_session(2), "AAAAA"),
        )

    def test_a_closed_session_is_expired(self) -> None:
        from steam.aio import SignInExpired

        with self.assertRaises(SignInExpired):
            _drive(
                [_Reply(eresult=EResult.Expired)],
                lambda c: c.submit_steam_guard_code(_session(2), "AAAAA"),
            )

    def test_a_session_without_a_code_takes_none(self) -> None:
        with self.assertRaises(ValueError):
            _drive([], lambda c: c.submit_steam_guard_code(_session(4), "AAAAA"))


class PollAndWaitTests(unittest.TestCase):
    def test_pending_is_none(self) -> None:
        result = _drive([_Reply({})], lambda c: c.poll_credentials_login(_session(4)))
        self.assertIsNone(result)

    def test_hands_over_the_tokens(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []
        result = _drive(
            [_tokens_reply()],
            lambda c: c.poll_credentials_login(_session(4)),
            calls,
        )
        self.assertEqual(
            calls[0],
            (
                "Authentication.PollAuthSessionStatus#1",
                {"client_id": 4242, "request_id": b"\x01\x02\x03"},
            ),
        )
        self.assertEqual(result.refresh_token, "eyJ.refresh")
        self.assertEqual(result.access_token, "eyJ.access")
        self.assertEqual(result.account_name, "gaben")
        self.assertEqual(result.guard_data, "guard-blob")

    def test_a_session_steam_no_longer_has_is_expired(self) -> None:
        from steam.aio import SignInExpired

        with self.assertRaises(SignInExpired):
            _drive(
                [_Reply(eresult=EResult.FileNotFound)],
                lambda c: c.poll_credentials_login(_session(4)),
            )

    def test_wait_polls_until_the_tokens_arrive(self) -> None:
        from steam.aio import SteamRPCTimeoutError

        result = _drive(
            [_Reply({}), SteamRPCTimeoutError(15.0), _tokens_reply()],
            lambda c: c.wait_credentials_login(_session(4), timeout=5),
        )
        self.assertEqual(result.refresh_token, "eyJ.refresh")

    def test_wait_gives_back_none_when_patience_runs_out(self) -> None:
        result = _drive(
            [_Reply({}), _Reply({}), _Reply({})],
            lambda c: c.wait_credentials_login(_session(4), timeout=0.015),
        )
        self.assertIsNone(result)


class SignInResultTests(unittest.TestCase):
    def test_repr_keeps_the_tokens_out(self) -> None:
        from steam.aio import SignInResult

        result = SignInResult(
            refresh_token="eyJ.refresh",
            access_token="eyJ.access",
            account_name="gaben",
            guard_data="guard-blob",
        )
        text = repr(result)
        self.assertIn("gaben", text)
        for secret in ("eyJ.refresh", "eyJ.access", "guard-blob"):
            self.assertNotIn(secret, text)


class LoginWithTokenTests(unittest.TestCase):
    def _stub(self, calls: list[tuple[Any, ...]]) -> type:
        class Stub(_FakeEmitter):
            def __init__(self) -> None:
                super().__init__()
                self.connected = False
                self.logged_on = False
                self.username = None
                self.relogin_available = False

            def login_with_token(
                self, username: str, token: str, login_id: int | None = None
            ) -> _OK:
                calls.append((username, token, login_id))
                self.connected = True
                self.logged_on = True
                return _OK()

            def reconnect(self, maxdelay: int = 30) -> bool:
                self.connected = True
                return True

            def disconnect(self) -> None:
                self.connected = False

        return Stub

    def test_forwards_and_can_replay_without_the_password(self) -> None:
        calls: list[tuple[Any, ...]] = []

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", self._stub(calls)):
                async with AsyncSteamClient() as client:
                    self.assertFalse(client.relogin_available)
                    await client.login_with_token("gaben", "eyJ.refresh")
                    self.assertEqual(calls, [("gaben", "eyJ.refresh", None)])
                    self.assertTrue(client.relogin_available)
                    self.assertNotIn("eyJ.refresh", repr(client._last_login))

        _run(_main())

    def test_reconnect_replays_the_token_login(self) -> None:
        import asyncio

        calls: list[tuple[Any, ...]] = []

        async def _main() -> None:
            from steam.aio import AsyncSteamClient

            with mock.patch("steam.client.SteamClient", self._stub(calls)):
                async with AsyncSteamClient() as client:
                    await client.login_with_token("gaben", "eyJ.refresh")
                    reconnected = asyncio.create_task(
                        client.wait_event("aio.reconnected", timeout=3.0),
                    )
                    await asyncio.sleep(0.05)
                    client._runner.submit(  # noqa: SLF001
                        lambda: client._sync.emit("disconnected"),  # noqa: SLF001
                    )
                    await reconnected
                    self.assertEqual(
                        calls,
                        [("gaben", "eyJ.refresh", None)] * 2,
                    )

        _run(_main())


class SyncLoginWithTokenTests(unittest.TestCase):
    """``SteamClient.login_with_token`` builds the ``ClientLogon``
    Steam's own client sends: the refresh token as ``access_token``,
    no password, no login key."""

    def test_sends_the_token_as_access_token(self) -> None:
        from steam.client import SteamClient

        client = SteamClient()
        sent: list[Any] = []
        ok = mock.Mock()
        ok.body.eresult = EResult.OK
        with (
            mock.patch.object(client, "_pre_login", return_value=EResult.OK),
            mock.patch.object(client, "send", side_effect=sent.append),
            mock.patch.object(client, "wait_msg", return_value=ok),
            mock.patch.object(client, "sleep"),
        ):
            result = client.login_with_token("gaben", "eyJ.refresh", login_id=7)

        self.assertEqual(result, EResult.OK)
        self.assertEqual(client.username, "gaben")
        (message,) = sent
        body = message.body
        self.assertEqual(body.account_name, "gaben")
        self.assertEqual(body.access_token, "eyJ.refresh")
        self.assertTrue(body.should_remember_password)
        self.assertEqual(body.obfuscated_private_ip.v4, 7)
        self.assertFalse(body.HasField("password"))
        self.assertFalse(body.HasField("login_key"))

    def test_login_still_sends_the_password(self) -> None:
        from steam.client import SteamClient

        client = SteamClient()
        sent: list[Any] = []
        ok = mock.Mock()
        ok.body.eresult = EResult.OK
        with (
            mock.patch.object(client, "_pre_login", return_value=EResult.OK),
            mock.patch.object(client, "send", side_effect=sent.append),
            mock.patch.object(client, "wait_msg", return_value=ok),
            mock.patch.object(client, "sleep"),
            mock.patch.object(client, "get_sentry", return_value=None),
        ):
            client.login("gaben", "hunter2", login_id=7)

        (message,) = sent
        self.assertEqual(message.body.password, "hunter2")
        self.assertFalse(message.body.HasField("access_token"))


if __name__ == "__main__":
    unittest.main()

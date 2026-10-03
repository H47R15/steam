"""Username + password sign-in via the CM ``Authentication`` service.

Since 2023 this is how Steam signs an account in.  The legacy
``CMsgClientLogon`` password logon behind :meth:`AsyncSteamClient.login`
is on its way out, and Steam no longer hands out the ``login_key`` that
``relogin()`` replays; Steam's own client, SteamKit2 and node-steam-user
all sign in like this now:

1. :meth:`AsyncSteamClient.begin_credentials_login` fetches the
   account's RSA key (``GetPasswordRSAPublicKey``), encrypts the
   password with it and opens an auth session
   (``BeginAuthSessionViaCredentials``).  A wrong password fails here,
   as :class:`~steam.aio.errors.SteamLoginError`.  The returned
   :class:`CredentialsLoginSession` lists the Steam Guard options
   Steam accepts for this sign-in.
2. When the account wants a code — the one Steam e-mails, or the
   Steam Mobile app's — :meth:`AsyncSteamClient.submit_steam_guard_code`.
   A confirmation instead (approving the sign-in in the mobile app, or
   the link in Steam's e-mail) needs nothing from the caller but
   waiting.
3. :meth:`AsyncSteamClient.poll_credentials_login` or
   :meth:`AsyncSteamClient.wait_credentials_login` until Steam hands
   over the tokens, as a :data:`SignInResult`.
4. :meth:`AsyncSteamClient.login_with_token` with its refresh token —
   now, and on any later run for about 200 days, without the password.

Design notes
------------

* Every step is one Unified Messages RPC through ``send_um_and_wait``
  on an anonymous CM session, the same route as :mod:`steam.aio.qr`.
  Nothing here holds a connection between steps, and a
  :class:`CredentialsLoginSession` is plain data
  (:meth:`~CredentialsLoginSession.to_dict`), so the steps may run in
  different processes: a web form's sign-in and the code typed into it
  a minute later rarely land on the same worker.
* The password is used once, to encrypt it for Steam, and kept
  nowhere: not on the session, not in an error message.
* Steam refuses a step through the reply header's ``eresult`` and an
  empty body.  Each refusal is raised as
  :class:`~steam.aio.errors.SteamLoginError` carrying that
  ``EResult`` — ``InvalidPassword``, ``InvalidLoginAuthCode``,
  ``TwoFactorCodeMismatch``, ``RateLimitExceeded`` — so a caller
  words its own message without parsing ours.  A session Steam has
  closed is :class:`SignInExpired`.
"""

from __future__ import annotations

import asyncio
import base64
import dataclasses
import enum
import time
from collections.abc import Iterable, Mapping
from typing import Any

from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA

from ..enums import EResult
from .errors import AsyncSteamError, SteamLoginError, SteamRPCTimeoutError
from .qr import (
    QRLoginResult,
    _clamp_interval,
    _decode_request_id,
    _extract_request_id,
    _response_body,
)

#: What a finished sign-in hands back.  A QR sign-in ends with the same
#: ``PollAuthSessionStatus`` answer, so it is the same class, under a
#: name that doesn't say QR.
SignInResult = QRLoginResult

#: How long :meth:`AsyncSteamClient.wait_credentials_login` waits by
#: default for a confirmation in the mobile app or a click in the
#: e-mail.  The auth session itself stays open for longer; waiting
#: again after ``None`` picks it up where this left off.
DEFAULT_SIGN_IN_WAIT_SECONDS = 120.0

#: Per-RPC deadline.  Each step is a single CM round trip.
_RPC_TIMEOUT = 15.0

#: ``k_EAuthTokenPlatformType_SteamClient``: the token is for a CM
#: logon.  A WebBrowser token has the wrong audience for
#: :meth:`AsyncSteamClient.login_with_token`.
_PLATFORM_STEAM_CLIENT = 1

#: ``k_ESessionPersistence_Persistent``: a "Remember me" session, the
#: kind whose refresh token lives for months rather than for one run.
_PERSISTENT = 1

#: What Steam answers about an auth session it no longer has: past its
#: lifetime, or never known.
_SESSION_GONE = frozenset({EResult.Expired, EResult.FileNotFound})


class SteamGuard(enum.IntEnum):
    """A way to confirm a sign-in — Steam's ``EAuthSessionGuardType``."""

    #: A value this release doesn't know.
    UNKNOWN = 0
    #: The account has no Steam Guard: nothing to confirm.
    NONE = 1
    #: The code Steam e-mails.
    EMAIL_CODE = 2
    #: The code in the Steam Mobile app.
    DEVICE_CODE = 3
    #: Approving the sign-in in the Steam Mobile app.
    DEVICE_CONFIRMATION = 4
    #: The link in the e-mail Steam sends.
    EMAIL_CONFIRMATION = 5
    #: The guard data an earlier sign-in handed back, passed in again.
    MACHINE_TOKEN = 6
    LEGACY_MACHINE_AUTH = 7

    @classmethod
    def _missing_(cls, value: object) -> SteamGuard:
        # Steam adds guard types now and then; one this release has
        # never heard of must not make the whole sign-in unreadable.
        return cls.UNKNOWN


@dataclasses.dataclass(frozen=True)
class GuardOption:
    """One way Steam accepts to confirm this sign-in."""

    kind: SteamGuard
    #: Steam's hint for it, where it gives one: for an e-mailed code,
    #: the domain of the address it went to (``gmail.com``).
    hint: str = ""


class SignInExpired(AsyncSteamError, TimeoutError):
    """Steam closed the auth session before it finished: past its
    lifetime, or not one Steam knows.  Start again with
    :meth:`AsyncSteamClient.begin_credentials_login`."""


@dataclasses.dataclass(frozen=True)
class CredentialsLoginSession:
    """An auth session opened with a username and password.

    Immutable, and plain data on purpose: :meth:`to_dict` and
    :meth:`from_dict` round-trip it through JSON so a later step can
    run in another process.  It holds no password — only the handles
    Steam gave out for this sign-in.  Treat it as secret anyway: once
    the sign-in is confirmed, whoever holds it can poll for the tokens.

    Attributes
    ----------
    client_id:
        Steam's handle for the auth session.
    request_id:
        The session's request id, base64 — bytes on the wire.
    steam_id:
        The SteamID64 of the account signing in.
    account_name:
        The account name the sign-in was started with.
    interval:
        How often to poll, in seconds, as Steam advertises it.
    guards:
        The ways Steam accepts to confirm this sign-in.
    """

    client_id: int
    request_id: str
    steam_id: int
    account_name: str
    interval: float
    guards: tuple[GuardOption, ...]

    @property
    def needs_guard(self) -> bool:
        """Whether someone has to confirm the sign-in: ``False`` for an
        account without Steam Guard, or one whose guard data vouched
        for this machine."""
        kinds = {guard.kind for guard in self.guards}
        return not kinds & {SteamGuard.NONE, SteamGuard.MACHINE_TOKEN}

    @property
    def code_kind(self) -> SteamGuard | None:
        """The code this sign-in takes, if it takes one.  The mobile
        app's before the e-mailed one: an account with the app gets its
        codes there."""
        kinds = {guard.kind for guard in self.guards}
        for kind in (SteamGuard.DEVICE_CODE, SteamGuard.EMAIL_CODE):
            if kind in kinds:
                return kind
        return None

    def to_dict(self) -> dict[str, Any]:
        """JSON-safe form, for :meth:`from_dict`."""
        return {
            "client_id": self.client_id,
            "request_id": self.request_id,
            "steam_id": self.steam_id,
            "account_name": self.account_name,
            "interval": self.interval,
            "guards": [{"kind": int(g.kind), "hint": g.hint} for g in self.guards],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CredentialsLoginSession:
        """Inverse of :meth:`to_dict`.  Raises :class:`ValueError` on
        anything :meth:`to_dict` could not have written."""
        try:
            guards = tuple(
                GuardOption(kind=SteamGuard(int(g["kind"])), hint=str(g["hint"]))
                for g in data["guards"]
            )
            session = cls(
                client_id=int(data["client_id"]),
                request_id=str(data["request_id"]),
                steam_id=int(data["steam_id"]),
                account_name=str(data["account_name"]),
                interval=_clamp_interval(data["interval"]),
                guards=guards,
            )
        except (KeyError, TypeError, ValueError) as err:
            raise ValueError(f"not a CredentialsLoginSession: {err}") from None
        if not session.client_id or not session.request_id:
            raise ValueError(
                "not a CredentialsLoginSession: no client_id or request_id"
            )
        return session


def _eresult(value: int) -> EResult | int:
    """``EResult`` for a value this release knows, else the bare int."""
    try:
        return EResult(value)
    except ValueError:
        return value


async def _call(
    client: Any,
    method: str,
    params: dict[str, Any],
    *,
    doing: str,
) -> dict[str, Any]:
    """One ``Authentication`` RPC: the reply's body, once Steam says OK.

    A refusal comes back as the header's ``eresult`` over an empty
    body; it is raised as :class:`SteamLoginError`, or
    :class:`SignInExpired` for a session Steam no longer has.
    ``raises=True`` turns a missing reply into
    :class:`SteamRPCTimeoutError` instead of a ``None`` that reads as
    an empty answer.
    """
    response = await client.send_um_and_wait(
        method,
        params,
        timeout=_RPC_TIMEOUT,
        raises=True,
    )
    header = response.header
    eresult = _eresult(int(header.eresult))
    if eresult != EResult.OK:
        name = eresult.name if isinstance(eresult, EResult) else str(eresult)
        detail = str(getattr(header, "error_message", "") or "")
        message = f"Steam refused {doing}: {name}" + (f" ({detail})" if detail else "")
        if eresult in _SESSION_GONE:
            raise SignInExpired(message)
        raise SteamLoginError(eresult, message)
    return _response_body(response)


def _encrypt_password(password: str, modulus_hex: str, exponent_hex: str) -> str:
    """The password as Steam takes it: RSA PKCS#1 v1.5 under the key
    ``GetPasswordRSAPublicKey`` gave out for this account, base64."""
    key = RSA.construct((int(modulus_hex, 16), int(exponent_hex, 16)))
    sealed = PKCS1_v1_5.new(key).encrypt(password.encode("utf-8"))
    return base64.b64encode(sealed).decode("ascii")


def _guard_options(raw: Iterable[Any]) -> tuple[GuardOption, ...]:
    return tuple(
        GuardOption(
            kind=SteamGuard(int(item.confirmation_type)),
            hint=str(item.associated_message or ""),
        )
        for item in raw
    )


async def _rpc_begin(
    client: Any,
    *,
    account_name: str,
    password: str,
    device_friendly_name: str,
    website_id: str,
    guard_data: str | None,
) -> CredentialsLoginSession:
    """``GetPasswordRSAPublicKey#1`` then
    ``BeginAuthSessionViaCredentials#1``."""
    key = await _call(
        client,
        "Authentication.GetPasswordRSAPublicKey#1",
        {"account_name": account_name},
        doing="the password key",
    )
    try:
        encrypted = _encrypt_password(
            password,
            str(key["publickey_mod"]),
            str(key["publickey_exp"]),
        )
    except (KeyError, ValueError) as err:
        raise SteamLoginError(
            EResult.Fail,
            f"Steam's password key was unusable: {err!r}",
        ) from err
    params: dict[str, Any] = {
        "account_name": account_name,
        "encrypted_password": encrypted,
        "encryption_timestamp": int(key.get("timestamp") or 0),
        "remember_login": True,
        "persistence": _PERSISTENT,
        "website_id": website_id,
        "device_details": {
            # Shown in the account's Steam Guard device list — the name
            # the account holder will look for when they review it.
            "device_friendly_name": device_friendly_name,
            "platform_type": _PLATFORM_STEAM_CLIENT,
        },
    }
    if guard_data:
        params["guard_data"] = guard_data
    body = await _call(
        client,
        "Authentication.BeginAuthSessionViaCredentials#1",
        params,
        doing="the sign-in",
    )
    return CredentialsLoginSession(
        client_id=int(body.get("client_id") or 0),
        request_id=_extract_request_id(body.get("request_id")),
        steam_id=int(body.get("steamid") or 0),
        account_name=account_name,
        interval=_clamp_interval(body.get("interval")),
        guards=_guard_options(body.get("allowed_confirmations") or ()),
    )


async def _rpc_submit_code(
    client: Any,
    *,
    session: CredentialsLoginSession,
    code: str,
) -> None:
    """``UpdateAuthSessionWithSteamGuardCode#1`` with the kind of code
    the session takes."""
    kind = session.code_kind
    if kind is None:
        raise ValueError("this sign-in takes no Steam Guard code")
    try:
        await _call(
            client,
            "Authentication.UpdateAuthSessionWithSteamGuardCode#1",
            {
                "client_id": session.client_id,
                "steamid": session.steam_id,
                "code": code.strip(),
                "code_type": int(kind),
            },
            doing="the Steam Guard code",
        )
    except SteamLoginError as err:
        # The code already went in — a double submit, or a retry after a
        # reply that got lost.  The session is where the caller wants it.
        if err.eresult != EResult.DuplicateRequest:
            raise


async def _rpc_poll(
    client: Any,
    *,
    session: CredentialsLoginSession,
) -> SignInResult | None:
    """One ``PollAuthSessionStatus#1``: the tokens once the sign-in is
    confirmed, ``None`` while it still waits on someone."""
    body = await _call(
        client,
        "Authentication.PollAuthSessionStatus#1",
        {
            "client_id": session.client_id,
            "request_id": _decode_request_id(session.request_id),
        },
        doing="the sign-in status",
    )
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return None
    guard_raw = body.get("new_guard_data")
    return SignInResult(
        refresh_token=str(refresh_token),
        access_token=str(body.get("access_token") or ""),
        account_name=str(body.get("account_name") or session.account_name),
        guard_data=guard_raw if isinstance(guard_raw, str) and guard_raw else None,
        had_remote_interaction=bool(body.get("had_remote_interaction", False)),
    )


async def _wait(
    client: Any,
    *,
    session: CredentialsLoginSession,
    timeout: float,
) -> SignInResult | None:
    """Poll at ``session.interval`` until Steam hands over the tokens,
    or ``None`` once ``timeout`` passes first.

    ``None`` rather than an error: running out of patience here doesn't
    close Steam's session, and a caller behind a web page waits in
    slices — each request waits a little, the page asks again.
    """
    deadline = time.monotonic() + max(timeout, 0.0)
    while True:
        try:
            result = await _rpc_poll(client, session=session)
        except SteamRPCTimeoutError:
            # One slow reply is not the end of the sign-in; the next
            # poll asks again.
            result = None
        if result is not None:
            return result
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        await asyncio.sleep(min(session.interval, remaining))


__all__ = [
    "CredentialsLoginSession",
    "DEFAULT_SIGN_IN_WAIT_SECONDS",
    "GuardOption",
    "SignInExpired",
    "SignInResult",
    "SteamGuard",
]

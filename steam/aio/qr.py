"""QR sign-in via the CM ``Authentication`` service.

Wraps two Unified Messages RPCs — ``BeginAuthSessionViaQR#1`` and
``PollAuthSessionStatus#1`` — into an ergonomic asyncio flow that
matches how the desktop Steam client renders its "Or sign in with
QR" panel:

1. Caller invokes :meth:`AsyncSteamClient.begin_qr_login` — returns
   a :class:`QRLoginSession` carrying the ``challenge_url`` (a
   ``steam://`` URL the mobile app understands) plus the polling
   ``interval`` and a ``client_id`` handle to resume the session.
2. The caller renders ``challenge_url`` as a QR code in their UI.
   The user scans it with the Steam mobile app and confirms the
   sign-in on their phone.
3. Caller invokes :meth:`AsyncSteamClient.wait_qr_confirmation`
   (or the manual :meth:`QRLoginSession.poll_once` if they want
   to drive the polling loop themselves).  Once Steam sees the
   mobile confirmation, the poll returns a
   :class:`QRLoginResult` carrying the ``refresh_token`` +
   ``access_token`` pair the caller then feeds into
   :meth:`AsyncSteamClient.login_with_token`.

Design notes
------------

* No new import at the module level in this file that isn't
  already in the base package — everything routes through
  ``send_um_and_wait`` so we can drop this feature into a running
  ``AsyncSteamClient`` without adding to the runtime dep list.
* The polling loop is asyncio-native (``asyncio.sleep``), so it
  runs on the caller's event loop, not the gevent worker — the
  network round-trip is on the runner thread via
  ``send_um_and_wait`` but the *wait between polls* stays on
  asyncio where cancellation is well-behaved.
* Polling honours the ``interval`` Steam returns in
  :class:`QRLoginSession` — Steam advertises 5 seconds today, but
  we trust whatever the server hands us so the client doesn't need
  a code change if Steam ever tunes it.
"""

from __future__ import annotations

import asyncio
import dataclasses
import time
from collections.abc import Iterable
from typing import Any, cast

from .errors import SteamRPCTimeoutError

#: Default cap on how long :meth:`AsyncSteamClient.wait_qr_confirmation`
#: will poll before giving up.  Steam's own client waits ~2 minutes
#: before offering a "generate new code" affordance — we match that
#: default so a user who walks away for a coffee doesn't come back
#: to a stalled login.
DEFAULT_QR_TIMEOUT_SECONDS = 120.0

#: Fallback polling interval used when the server response omits an
#: interval or hands back something absurd.  Steam typically
#: advertises 5 seconds; we clamp to a sensible range to prevent
#: pathological loops.
_MIN_POLL_INTERVAL = 1.0
_MAX_POLL_INTERVAL = 30.0
_FALLBACK_POLL_INTERVAL = 5.0


@dataclasses.dataclass(frozen=True)
class QRLoginSession:
    """Represents an in-flight QR sign-in handshake.

    Immutable snapshot returned by
    :meth:`AsyncSteamClient.begin_qr_login`.  The caller renders
    ``challenge_url`` as a QR code and then either polls manually
    with :meth:`AsyncSteamClient.poll_qr_status` or lets
    :meth:`AsyncSteamClient.wait_qr_confirmation` handle the loop.

    Attributes
    ----------
    client_id:
        Server-assigned handle; passed back on every subsequent
        poll so Steam can correlate the polls with the challenge.
    request_id:
        Opaque request identifier the server hands back — echoed
        on each poll.  Bytes on the wire; base64-encoded on our
        side so JSON-serialising the session is trivial.
    challenge_url:
        The ``steam://`` URL the mobile Steam app expects to see
        encoded in the QR image.  Any QR encoder that produces a
        scan-able image will do — Steam's own client feeds it into
        a stock QR renderer, no custom encoding.
    interval:
        How often to poll ``PollAuthSessionStatus``, in seconds.
        Advertised by the server; clamped to a sensible range.
    version:
        Protocol version handed back by the server — echoed on
        subsequent polls if the server asks for it later.
    started_at:
        Monotonic timestamp of the ``begin`` call — used by
        :meth:`AsyncSteamClient.wait_qr_confirmation` to detect
        overall timeout without depending on wall-clock jumps.
    """

    client_id: int
    request_id: str
    challenge_url: str
    interval: float
    version: int
    started_at: float


@dataclasses.dataclass(frozen=True)
class QRLoginResult:
    """Terminal outcome of a QR sign-in flow.

    Attributes
    ----------
    refresh_token:
        Long-lived Steam OAuth refresh token.  Persist this — it's
        the equivalent of Steam's own "Remember me" and can be
        replayed to log in without another QR scan.  Rotate via
        the ``RevokeRefreshToken`` service if compromised.
    access_token:
        Short-lived access token derived from the refresh token.
        Steam re-issues it on demand via
        ``GenerateAccessTokenForApp``; callers usually don't need
        to hold on to this one.
    account_name:
        Steam login handle of the account that confirmed the
        sign-in on the mobile app.  Useful for a "signed in as X"
        chip in the caller's UI.
    guard_data:
        New Steam Guard machine data blob (base64) the server
        wants us to remember so we don't re-challenge on the same
        device next time.  Optional — some accounts don't hand it
        back.
    had_remote_interaction:
        ``True`` if Steam saw a mobile-app confirmation during
        this session.  Almost always ``True`` at the point we
        get here (a poll that returns tokens without a
        confirmation would only happen on a machine already
        trusted by Steam).
    """

    refresh_token: str
    access_token: str
    account_name: str
    guard_data: str | None = None
    had_remote_interaction: bool = True


class QRSignInExpired(TimeoutError):
    """Raised when a QR sign-in session times out without the user
    scanning + confirming on their mobile app."""


def _clamp_interval(value: Any) -> float:
    """Normalise the ``interval`` field on a
    ``BeginAuthSessionViaQR`` response into the range we're willing
    to poll at.  Servers occasionally advertise 0 (poll as fast as
    possible) or absurd upper bounds; clamp both."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return _FALLBACK_POLL_INTERVAL
    if parsed <= 0:
        return _FALLBACK_POLL_INTERVAL
    if parsed < _MIN_POLL_INTERVAL:
        return _MIN_POLL_INTERVAL
    if parsed > _MAX_POLL_INTERVAL:
        return _MAX_POLL_INTERVAL
    return parsed


def _extract_request_id(raw: Any) -> str:
    """The wire type of ``request_id`` is ``bytes``; base64-encode
    for a JSON-safe representation so :class:`QRLoginSession` can
    round-trip through a WebSocket / HTTP callback without a
    custom encoder."""
    import base64

    if isinstance(raw, bytes):
        return base64.b64encode(raw).decode("ascii")
    if isinstance(raw, str):
        return raw
    return ""


def _decode_request_id(encoded: str) -> bytes:
    """Inverse of :func:`_extract_request_id` — accepts either a
    pre-encoded string OR (defensively) raw bytes for callers who
    already have the untransformed value from a fresh
    :class:`QRLoginSession`."""
    import base64

    if isinstance(encoded, bytes):
        return encoded
    if not encoded:
        return b""
    return base64.b64decode(encoded)


# ---------------------------------------------------------------------
# Helpers used by AsyncSteamClient to invoke the two UM RPCs.  Kept
# module-level so tests can patch them without reaching into the
# client class.
# ---------------------------------------------------------------------


async def _rpc_begin(
    client: Any,
    *,
    device_friendly_name: str,
    website_id: str,
) -> QRLoginSession:
    """Wrapper around ``Authentication.BeginAuthSessionViaQR#1``.
    Returns a fresh :class:`QRLoginSession` populated from the
    server's response."""
    params: dict[str, Any] = {
        "device_friendly_name": device_friendly_name,
        # ``k_EAuthTokenPlatformType_WebBrowser = 2`` — matches the
        # web-client sign-in flow, which is the closest fit for a
        # browser-rendered QR panel.
        "platform_type": 2,
        "website_id": website_id,
    }
    response = await client.send_um_and_wait(
        "Authentication.BeginAuthSessionViaQR#1",
        params,
        timeout=15.0,
    )
    body = _response_body(response)
    return QRLoginSession(
        client_id=int(body.get("client_id", 0) or 0),
        request_id=_extract_request_id(body.get("request_id")),
        challenge_url=str(body.get("challenge_url") or ""),
        interval=_clamp_interval(body.get("interval")),
        version=int(body.get("version", 0) or 0),
        started_at=time.monotonic(),
    )


async def _rpc_poll(
    client: Any,
    *,
    session: QRLoginSession,
) -> QRLoginResult | None:
    """One iteration of ``Authentication.PollAuthSessionStatus#1``.
    Returns ``None`` while Steam is still waiting for the mobile
    confirmation, or a :class:`QRLoginResult` once tokens are
    ready.

    A response with a non-empty ``new_challenge_url`` means Steam
    rotated the QR (rare, but possible if the mobile app rejects
    the initial challenge).  We surface this by raising
    :class:`QRSignInExpired` so the caller can generate a fresh
    session — auto-refreshing under the hood would silently change
    the QR the user is looking at.
    """
    params: dict[str, Any] = {
        "client_id": session.client_id,
        "request_id": _decode_request_id(session.request_id),
    }
    response = await client.send_um_and_wait(
        "Authentication.PollAuthSessionStatus#1",
        params,
        timeout=15.0,
    )
    body = _response_body(response)

    # Steam rotated the challenge — treat as an expired session so
    # the caller generates a fresh one instead of a stale-QR loop.
    new_challenge = body.get("new_challenge_url")
    if isinstance(new_challenge, str) and new_challenge:
        raise QRSignInExpired(
            "Steam rotated the QR challenge — generate a new session",
        )

    refresh_token = body.get("refresh_token")
    access_token = body.get("access_token")
    if not refresh_token:
        # Still waiting for the mobile confirmation — Steam
        # returns an empty ``refresh_token`` field on
        # not-yet-confirmed polls.
        return None
    guard_raw = body.get("new_guard_data")
    guard_data = guard_raw if isinstance(guard_raw, str) and guard_raw else None
    return QRLoginResult(
        refresh_token=str(refresh_token),
        access_token=str(access_token or ""),
        account_name=str(body.get("account_name") or ""),
        guard_data=guard_data,
        had_remote_interaction=bool(body.get("had_remote_interaction", True)),
    )


async def _wait_for_confirmation(
    client: Any,
    *,
    session: QRLoginSession,
    timeout: float,
    interval_override: float | None = None,
) -> QRLoginResult:
    """Poll ``PollAuthSessionStatus`` at ``session.interval`` until
    the mobile app confirms or the overall ``timeout`` elapses.

    Uses ``asyncio.sleep`` between polls so the wait honours
    ``asyncio.wait_for`` / ``Task.cancel`` cleanly — cancelling
    the wait cancels the coroutine at the sleep boundary without
    stranding the RPC.
    """
    deadline = session.started_at + max(timeout, 5.0)
    poll_interval = interval_override if interval_override else session.interval
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise QRSignInExpired(
                "QR sign-in was not confirmed on the mobile app "
                f"within {timeout:.0f}s",
            )
        try:
            result = await _rpc_poll(client, session=session)
        except SteamRPCTimeoutError:
            # A single poll timing out is not fatal — Steam may
            # be slow during the mobile-side round-trip.  Retry
            # on the next tick.
            result = None
        if result is not None:
            return result
        # Sleep at most until the deadline so we don't over-shoot.
        await asyncio.sleep(min(poll_interval, remaining))


def _response_body(response: Any) -> dict[str, Any]:
    """Uniform accessor for whatever ``send_um_and_wait`` hands
    back.  The runtime wraps the response protobuf in different
    shapes depending on which underlying transport fired — the
    ``.body.<field>`` form is the common one, but tests may
    substitute a plain ``dict`` for convenience."""
    if response is None:
        return {}
    body = getattr(response, "body", None)
    if body is None:
        # Some transports return the proto message directly; treat
        # as a body if it has an ``ListFields`` / iteration
        # protocol.  Fall through to attribute access below.
        body = response
    # Coerce to a dict — descriptor iteration if it's a proto,
    # ``dict(body)`` if it's already dict-like.
    if isinstance(body, dict):
        return body
    listed = getattr(body, "ListFields", None)
    if callable(listed):
        list_fields = listed()
        if isinstance(list_fields, Iterable):
            return {
                desc.name: value
                for desc, value in cast(Iterable[tuple[Any, Any]], list_fields)
            }
    # Last resort — accessor by known field names.
    return {
        name: getattr(body, name, None)
        for name in (
            "client_id",
            "request_id",
            "challenge_url",
            "interval",
            "version",
            "refresh_token",
            "access_token",
            "account_name",
            "new_guard_data",
            "had_remote_interaction",
            "new_challenge_url",
        )
    }


__all__ = [
    "QRLoginSession",
    "QRLoginResult",
    "QRSignInExpired",
    "DEFAULT_QR_TIMEOUT_SECONDS",
]

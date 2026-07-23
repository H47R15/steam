"""Typed exception hierarchy for :mod:`steam.aio`.

Every failure surfaced by :class:`~steam.aio.AsyncSteamClient` derives
from :class:`AsyncSteamError`, so callers (including a future MCP
tool server) can distinguish structured, expected errors from bare
``RuntimeError``\\s that indicate a real bug.

Hierarchy::

    AsyncSteamError
    ├── SteamNotStartedError    (called a method before start())
    ├── SteamClosedError        (called a method after close())
    ├── SteamLoginError         (login rejected — carries the EResult)
    ├── SteamReconnectError     (auto-reconnect gave up — carries attempt count)
    └── SteamRPCTimeoutError    (an await hit its timeout — carries the timeout)

An MCP tool wrapper can pattern-match on the concrete type and emit
structured JSON, e.g. ``{"error": "login_failed", "eresult": 5}`` for
``SteamLoginError``, without regex-parsing an ``str(exc)``.
"""

from __future__ import annotations

from typing import Any


class AsyncSteamError(Exception):
    """Base class for every :mod:`steam.aio` error."""


class SteamNotStartedError(AsyncSteamError, RuntimeError):
    """Raised when a method is called before :meth:`AsyncSteamClient.start`.

    Multi-inherits from :class:`RuntimeError` so existing callers
    catching ``RuntimeError`` (the pre-1.6 API) still work.
    """


class SteamClosedError(AsyncSteamError, RuntimeError):
    """Raised when a method is called after :meth:`AsyncSteamClient.close`.

    Multi-inherits from :class:`RuntimeError` for backwards compat
    with the pre-1.6 API.
    """


class SteamLoginError(AsyncSteamError):
    """Raised when :meth:`AsyncSteamClient.login` /
    :meth:`AsyncSteamClient.anonymous_login` returns a non-OK
    :class:`~steam.enums.EResult`.

    ``eresult`` is the raw ``EResult`` value from the CM so the
    caller can distinguish e.g. ``AccountLoginDeniedNeedTwoFactor``
    from ``InvalidPassword`` without string-matching.
    """

    def __init__(self, eresult: Any, message: str | None = None) -> None:
        self.eresult = eresult
        super().__init__(message or f"Steam login failed: {eresult!r}")


class SteamReconnectError(AsyncSteamError):
    """Raised when the auto-reconnect loop gives up after exhausting
    its retry budget.

    ``attempts`` is the number of connect attempts made; ``last_error``
    is the final underlying exception (if any).
    """

    def __init__(
        self,
        attempts: int,
        last_error: BaseException | None = None,
    ) -> None:
        self.attempts = attempts
        self.last_error = last_error
        msg = f"Steam reconnect gave up after {attempts} attempts"
        if last_error is not None:
            msg = f"{msg}: {last_error!r}"
        super().__init__(msg)


class SteamRPCTimeoutError(AsyncSteamError, TimeoutError):
    """Raised when a blocking RPC (``get_product_info``,
    ``send_um_and_wait``) exceeds its timeout.

    Multi-inherits from :class:`TimeoutError` so callers that only
    care that "something timed out" can catch either.  ``timeout``
    is the deadline in seconds so error messages/telemetry can
    report the exact contract that failed.
    """

    def __init__(self, timeout: float, message: str | None = None) -> None:
        self.timeout = timeout
        super().__init__(message or f"Steam RPC timed out after {timeout}s")


__all__ = [
    "AsyncSteamError",
    "SteamNotStartedError",
    "SteamClosedError",
    "SteamLoginError",
    "SteamReconnectError",
    "SteamRPCTimeoutError",
]

"""Asyncio facade around the gevent-based ``steam.client.SteamClient``.

Use this from FastAPI / Starlette / any ``asyncio``-based app.  The
underlying sync client runs on a dedicated daemon thread with its
own gevent hub — the asyncio event loop is never monkey-patched, so
``httpx`` / ``uvicorn`` / ``motor`` / any other stdlib-socket user
keeps working.

Quick start::

    from steam.aio import AsyncSteamClient

    async with AsyncSteamClient() as client:
        await client.anonymous_login()
        info = await client.get_product_info(apps=[440])

Public names
------------

* :class:`~steam.aio.client.AsyncSteamClient` — the facade.
* :class:`~steam.aio.client.ReconnectPolicy` — reconnect config.
* Typed errors from :mod:`steam.aio.errors`
  (:class:`AsyncSteamError` and subclasses).

Module layout (organised so a future ``steam.mcp`` server can
compose these pieces):

* :mod:`steam.aio.runner` — the cross-thread gevent runner
  (reusable by anything that needs to drive the sync client from
  async code).
* :mod:`steam.aio.client` — the ``SteamClient`` facade + reconnect
  loop + event bridge.
* :mod:`steam.aio.errors` — the typed exception hierarchy.
"""

from .client import AsyncSteamClient, ReconnectPolicy
from .errors import (
    AsyncSteamError,
    SteamClosedError,
    SteamLoginError,
    SteamNotStartedError,
    SteamReconnectError,
    SteamRPCTimeoutError,
)
from .pool import AsyncSteamPool, PoolLogin, PoolMember, PoolMemberStatus
from .qr import (
    DEFAULT_QR_TIMEOUT_SECONDS,
    QRLoginResult,
    QRLoginSession,
    QRSignInExpired,
)
from .status import (
    RECONNECT_FAILED,
    RECONNECT_IDLE,
    RECONNECT_RECONNECTING,
    ClientStatus,
    MetricsHook,
    prometheus_hook,
)

__all__ = [
    "AsyncSteamClient",
    "ReconnectPolicy",
    "AsyncSteamError",
    "SteamClosedError",
    "SteamLoginError",
    "SteamNotStartedError",
    "SteamReconnectError",
    "SteamRPCTimeoutError",
    "ClientStatus",
    "MetricsHook",
    "prometheus_hook",
    "RECONNECT_IDLE",
    "RECONNECT_RECONNECTING",
    "RECONNECT_FAILED",
    "AsyncSteamPool",
    "PoolMember",
    "PoolLogin",
    "PoolMemberStatus",
    "QRLoginSession",
    "QRLoginResult",
    "QRSignInExpired",
    "DEFAULT_QR_TIMEOUT_SECONDS",
]

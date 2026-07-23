"""FastAPI integration helpers for :mod:`steam.aio`.

Everything here is optional — the base ``steam.aio`` package works
inside a FastAPI app perfectly well without this module.  These
helpers just remove the boilerplate that everyone would otherwise
write.

Two shapes:

* :func:`steam_client_lifespan` — an ``@asynccontextmanager``
  factory that starts a client on app boot and closes it on app
  shutdown.  Attaches the client to ``app.state.steam`` so
  request handlers can reach it via :func:`get_steam_client`.

* :func:`steam_pool_lifespan` — same shape but for an
  :class:`~steam.aio.pool.AsyncSteamPool`.  Attaches to
  ``app.state.steam_pool``.

* :func:`get_steam_client` / :func:`get_steam_pool` — dependency
  functions for use with ``Depends``.

FastAPI is imported lazily (only when the caller actually calls
one of these functions) so the base ``steam.aio`` package doesn't
grow a FastAPI dep.

Example — single client::

    from contextlib import asynccontextmanager
    from fastapi import Depends, FastAPI
    from steam.aio import AsyncSteamClient
    from steam.aio.integrations.fastapi import (
        get_steam_client, steam_client_lifespan,
    )

    client = AsyncSteamClient()

    async def _login(c: AsyncSteamClient) -> None:
        await c.anonymous_login()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with steam_client_lifespan(app, client, on_start=_login):
            yield

    app = FastAPI(lifespan=lifespan)

    @app.get("/product/{app_id}")
    async def product(
        app_id: int,
        steam: AsyncSteamClient = Depends(get_steam_client),
    ):
        return await steam.get_product_info(apps=[app_id])

    @app.get("/health")
    async def health(steam: AsyncSteamClient = Depends(get_steam_client)):
        return steam.status.__dict__

Example — pool::

    pool = AsyncSteamPool([...])

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with steam_pool_lifespan(app, pool):
            yield

    @app.get("/product/{app_id}")
    async def product(
        app_id: int,
        pool: AsyncSteamPool = Depends(get_steam_pool),
    ):
        return await pool.round_robin().get_product_info(apps=[app_id])
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Awaitable, Callable, Optional, TYPE_CHECKING

from ..client import AsyncSteamClient
from ..pool import AsyncSteamPool


if TYPE_CHECKING:
    # ``fastapi.FastAPI`` and ``fastapi.Request`` are only needed
    # for type hints — importing them at runtime would force a
    # fastapi install on every ``steam.aio`` user.  ``TYPE_CHECKING``
    # keeps them out of the module import graph.
    from fastapi import FastAPI, Request


_STATE_CLIENT_ATTR = "steam"
_STATE_POOL_ATTR = "steam_pool"


# ---------------------------------------------------------------------
# Lifespan managers
# ---------------------------------------------------------------------


@asynccontextmanager
async def steam_client_lifespan(
    app: "FastAPI",
    client: AsyncSteamClient,
    *,
    on_start: Optional[Callable[[AsyncSteamClient], Awaitable[Any]]] = None,
    state_attr: str = _STATE_CLIENT_ATTR,
) -> AsyncIterator[AsyncSteamClient]:
    """Start ``client`` at app boot, close it at app shutdown, and
    stash it on ``app.state.<state_attr>`` (default: ``steam``).

    ``on_start`` runs AFTER ``client.start()`` — it's the natural
    place to do login (anonymous or credentialed) so a request
    handler is guaranteed to find a logged-in client.  A failure
    inside ``on_start`` propagates out and prevents the app from
    coming up — that's on purpose; a Steam-dependent service
    should not accept traffic if it can't reach Steam.
    """
    await client.start()
    if on_start is not None:
        try:
            await on_start(client)
        except BaseException:
            # Best-effort teardown of the started client so we don't
            # leak the runner thread when startup fails.
            await client.close()
            raise
    setattr(app.state, state_attr, client)
    try:
        yield client
    finally:
        setattr(app.state, state_attr, None)
        await client.close()


@asynccontextmanager
async def steam_pool_lifespan(
    app: "FastAPI",
    pool: AsyncSteamPool,
    *,
    state_attr: str = _STATE_POOL_ATTR,
) -> AsyncIterator[AsyncSteamPool]:
    """Same shape as :func:`steam_client_lifespan` but for a pool.
    The pool's members carry their own ``login`` callables (see
    :class:`~steam.aio.pool.PoolMember`), so there's no ``on_start``
    parameter here — logins are per-member.
    """
    await pool.start()
    setattr(app.state, state_attr, pool)
    try:
        yield pool
    finally:
        setattr(app.state, state_attr, None)
        await pool.close()


# ---------------------------------------------------------------------
# Depends providers
# ---------------------------------------------------------------------


def get_steam_client(
    request: "Request",
    *,
    state_attr: str = _STATE_CLIENT_ATTR,
) -> AsyncSteamClient:
    """FastAPI dependency — returns the ``AsyncSteamClient``
    attached by :func:`steam_client_lifespan`.

    Kept synchronous (not ``async``) because reading from
    ``app.state`` doesn't need to be — FastAPI will happily inject
    a sync dependency into an async handler.

    Wrap with ``Depends(...)`` at the handler::

        from steam.aio import AsyncSteamClient
        from steam.aio.integrations.fastapi import get_steam_client

        @app.get("/…")
        async def handler(
            steam: AsyncSteamClient = Depends(get_steam_client),
        ):
            ...
    """
    client = getattr(request.app.state, state_attr, None)
    if client is None:
        raise RuntimeError(
            f"No AsyncSteamClient on app.state.{state_attr}. "
            "Did you set up ``steam_client_lifespan`` in your "
            "FastAPI lifespan?",
        )
    return client


def get_steam_pool(
    request: "Request",
    *,
    state_attr: str = _STATE_POOL_ATTR,
) -> AsyncSteamPool:
    """FastAPI dependency — returns the ``AsyncSteamPool``
    attached by :func:`steam_pool_lifespan`.
    """
    pool = getattr(request.app.state, state_attr, None)
    if pool is None:
        raise RuntimeError(
            f"No AsyncSteamPool on app.state.{state_attr}. "
            "Did you set up ``steam_pool_lifespan`` in your "
            "FastAPI lifespan?",
        )
    return pool


__all__ = [
    "steam_client_lifespan",
    "steam_pool_lifespan",
    "get_steam_client",
    "get_steam_pool",
]

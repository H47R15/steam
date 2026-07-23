"""TaskIQ integration helpers for :mod:`steam.aio`.

TaskIQ is asyncio-native, so :class:`AsyncSteamClient` drops in
naturally.  The idiomatic wiring is:

1. Start the client in a broker startup hook.
2. Expose it through TaskIQ's dependency-injection system so tasks
   can grab it with ``TaskiqDepends(get_steam_client)``.
3. Close it in a broker shutdown hook.

This module packages that boilerplate.

Example
-------

::

    from steam.aio import AsyncSteamClient
    from steam.aio.integrations.taskiq import register_steam_client
    from taskiq import TaskiqDepends
    from taskiq_redis import ListQueueBroker

    broker = ListQueueBroker(url="redis://localhost:6379")
    client = AsyncSteamClient()

    async def _login(c: AsyncSteamClient) -> None:
        await c.anonymous_login()

    get_client = register_steam_client(broker, client, on_start=_login)

    @broker.task
    async def sync_app(app_id: int, steam=TaskiqDepends(get_client)):
        return await steam.get_product_info(apps=[app_id])

The returned ``get_client`` is the dependency function to pass to
``TaskiqDepends``.  Pool variant :func:`register_steam_pool` works
the same way but yields the pool.

TaskIQ is imported lazily so users who don't have it aren't forced
to install it.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Optional, TYPE_CHECKING

from ..client import AsyncSteamClient
from ..pool import AsyncSteamPool


if TYPE_CHECKING:
    from taskiq import AsyncBroker


def register_steam_client(
    broker: "AsyncBroker",
    client: AsyncSteamClient,
    *,
    on_start: Optional[Callable[[AsyncSteamClient], Awaitable[Any]]] = None,
) -> Callable[[], AsyncSteamClient]:
    """Wire ``client`` into the broker's lifecycle and return a
    dependency function suitable for :class:`TaskiqDepends`.

    * On broker startup — starts the client, then awaits
      ``on_start(client)`` if provided (typical: login).
    * On broker shutdown — closes the client.

    A partial startup failure (either ``client.start()`` or the
    ``on_start`` hook) tears the client back down before
    re-raising, so a failed broker startup doesn't leak a runner
    thread.

    The returned dependency function is a plain sync callable —
    TaskIQ accepts sync deps in async tasks and this is cheaper
    than an async one that only reads a captured local.
    """

    async def _startup() -> None:
        await client.start()
        if on_start is not None:
            try:
                await on_start(client)
            except BaseException:
                await client.close()
                raise

    async def _shutdown() -> None:
        await client.close()

    broker.add_event_handler("startup", _startup)  # type: ignore[attr-defined]
    broker.add_event_handler("shutdown", _shutdown)  # type: ignore[attr-defined]

    def _dep() -> AsyncSteamClient:
        return client

    return _dep


def register_steam_pool(
    broker: "AsyncBroker",
    pool: AsyncSteamPool,
) -> Callable[[], AsyncSteamPool]:
    """Pool variant of :func:`register_steam_client`.  Members
    carry their own ``login`` callables (see
    :class:`~steam.aio.pool.PoolMember`), so no ``on_start``
    parameter here.
    """

    async def _startup() -> None:
        await pool.start()

    async def _shutdown() -> None:
        await pool.close()

    broker.add_event_handler("startup", _startup)  # type: ignore[attr-defined]
    broker.add_event_handler("shutdown", _shutdown)  # type: ignore[attr-defined]

    def _dep() -> AsyncSteamPool:
        return pool

    return _dep


__all__ = [
    "register_steam_client",
    "register_steam_pool",
]

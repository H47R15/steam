"""Multi-account pool for :class:`AsyncSteamClient`.

Rationale
---------

Each ``AsyncSteamClient`` == one CM connection == one Steam account.
For workloads that need multiple accounts (a TaskIQ worker
farming out ``get_product_info`` calls across several licensed
accounts, an MCP server exposing tools for different personas, a
FastAPI app juggling scraper accounts), a pool is the right shape:

* One client per account, all brought up concurrently at startup.
* Cheap round-robin selector for stateless RPCs where any account
  will do.
* Named ``acquire(account_id)`` for stateful RPCs that must land on
  a specific account (chat, market listings, inventory).
* Per-client isolation on failure — one dead session doesn't take
  the pool down; ``status()`` surfaces the health of every member
  so a load-balancer / health-check endpoint can drain a bad node.

Not a connection pool in the DB sense — you don't check clients out
and back in.  Each ``get`` returns a shared handle; concurrent
``await`` calls on the same client are serialised inside the
gevent hub (see :class:`AsyncSteamClient` docstring for the
concurrency model).

Example
-------

::

    from steam.aio import AsyncSteamPool, PoolMember

    pool = AsyncSteamPool([
        PoolMember(account_id="alice", login=lambda c: c.anonymous_login()),
        PoolMember(account_id="bob",   login=lambda c: c.anonymous_login()),
    ])
    await pool.start()
    try:
        client = pool.round_robin()
        info = await client.get_product_info(apps=[440])
    finally:
        await pool.close()
"""

from __future__ import annotations

import asyncio
import dataclasses
import itertools
from collections.abc import Awaitable, Callable, Iterable
from typing import Any

from .client import AsyncSteamClient, ReconnectPolicy
from .status import ClientStatus, MetricsHook, _noop_hook

#: Signature of a "how to log this member in" callable.  Runs
#: after ``AsyncSteamClient.start()`` and BEFORE the pool
#: reports the member as ready.  The pool passes the freshly-
#: started client; the callable does whatever login (anonymous,
#: credentialed, custom pre-flight).  Returning normally = ready;
#: raising = the member is marked failed and left out of the
#: round-robin rotation (but still surfaced in ``status``).
PoolLogin = Callable[[AsyncSteamClient], Awaitable[Any]]


@dataclasses.dataclass(frozen=True)
class PoolMember:
    """Configuration for one client in an :class:`AsyncSteamPool`.

    ``login`` is a coroutine factory — the pool calls
    ``await member.login(client)`` after ``start()``.  Callers
    provide the login flavour themselves rather than the pool
    guessing, because credentialed login needs 2FA / mail-code
    orchestration that isn't the pool's business.

    ``metrics_hook`` overrides the pool-level hook on a per-member
    basis (rare — mostly useful when you want Prometheus labels
    to carry ``account_id`` and can't easily map that after the fact).
    """

    account_id: str
    login: PoolLogin
    reconnect: ReconnectPolicy = dataclasses.field(default_factory=ReconnectPolicy)
    metrics_hook: MetricsHook = _noop_hook


@dataclasses.dataclass(frozen=True)
class PoolMemberStatus:
    """Snapshot of one pool member.  ``failure`` is populated iff
    ``ready`` is ``False`` AND ``start`` / ``login`` raised — a
    healthy member that's mid-reconnect stays ``ready=True`` and
    the reconnect state is visible via ``client_status``.
    """

    account_id: str
    ready: bool
    failure: str | None
    client_status: ClientStatus | None


class AsyncSteamPool:
    """Manages N :class:`AsyncSteamClient` instances.

    Lifecycle
    ---------

    * ``AsyncSteamPool(members, metrics_hook=None)`` — construct.
      No I/O.
    * ``await pool.start()`` — spawn all clients concurrently.
      Each member goes through its own ``login`` coroutine.
      Individual failures are recorded in ``status()`` but don't
      abort the pool's startup; the pool is usable as long as ≥1
      member came up.
    * ``await pool.close()`` — close every member concurrently.
      Idempotent.

    Selection
    ---------

    * :meth:`acquire` — get a client by ``account_id``.  Raises
      ``KeyError`` if unknown, ``RuntimeError`` if the member
      failed to start.
    * :meth:`round_robin` — get the next ready client.  Skips
      failed / closed members automatically.  Raises
      ``RuntimeError`` if no clients are ready.
    * :meth:`ready_clients` — the current list of ready clients
      (useful for ``asyncio.gather`` fan-out).

    Health
    ------

    * :meth:`status` — snapshot of every member's state.  Safe
      to serialise for a ``/health`` endpoint.

    Design notes
    ------------

    The pool doesn't try to auto-heal a permanently-failed member —
    it's not the pool's business to know whether "invalid password"
    is temporary or the operator revoking access.  Callers can
    ``pool.replace_member(config)`` after fixing the config.  A
    healthy member that just lost its CM connection is different:
    its :class:`AsyncSteamClient` runs its own auto-reconnect loop,
    so the pool never sees the transient failure.
    """

    def __init__(
        self,
        members: Iterable[PoolMember],
        *,
        metrics_hook: MetricsHook = _noop_hook,
    ) -> None:
        self._configs: dict[str, PoolMember] = {}
        for m in members:
            if m.account_id in self._configs:
                raise ValueError(
                    f"duplicate account_id {m.account_id!r} in pool",
                )
            self._configs[m.account_id] = m
        if not self._configs:
            raise ValueError("AsyncSteamPool needs at least one member")
        self._default_metrics_hook = metrics_hook
        self._clients: dict[str, AsyncSteamClient] = {}
        self._failures: dict[str, str] = {}  # account_id → failure repr
        self._round_robin_cycle: itertools.cycle[str] | None = None
        self._started = False
        self._closed = False
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Bring up every member concurrently.  Idempotent."""
        if self._started:
            return
        self._started = True

        async def _bring_up_one(cfg: PoolMember) -> None:
            hook = (
                cfg.metrics_hook
                if cfg.metrics_hook is not _noop_hook
                else self._default_metrics_hook
            )
            client = AsyncSteamClient(
                reconnect=cfg.reconnect,
                metrics_hook=hook,
            )
            try:
                await client.start()
                await cfg.login(client)
            except BaseException as e:  # noqa: BLE001
                # Best-effort teardown of a partially-started client
                # so we don't leak the runner thread.
                try:
                    await client.close()
                except Exception:  # noqa: BLE001
                    pass
                self._failures[cfg.account_id] = f"{type(e).__name__}: {e}"
                return
            self._clients[cfg.account_id] = client

        await asyncio.gather(
            *(_bring_up_one(cfg) for cfg in self._configs.values()),
            return_exceptions=False,
        )
        self._rebuild_cycle()

    async def close(self) -> None:
        """Close every member concurrently.  Idempotent."""
        if self._closed:
            return
        self._closed = True
        clients = list(self._clients.values())
        self._clients.clear()
        self._round_robin_cycle = None
        await asyncio.gather(
            *(c.close() for c in clients),
            return_exceptions=True,
        )

    async def __aenter__(self) -> AsyncSteamPool:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def acquire(self, account_id: str) -> AsyncSteamClient:
        """Get the client for ``account_id``.  ``KeyError`` if
        unknown, ``RuntimeError`` if that member failed to start."""
        if account_id not in self._configs:
            raise KeyError(
                f"unknown pool member {account_id!r} "
                f"(known: {sorted(self._configs)!r})",
            )
        client = self._clients.get(account_id)
        if client is None:
            failure = self._failures.get(account_id, "not started")
            raise RuntimeError(
                f"pool member {account_id!r} is not ready: {failure}",
            )
        return client

    def round_robin(self) -> AsyncSteamClient:
        """Get the next ready client in cyclic order.
        ``RuntimeError`` if no clients are ready."""
        if self._round_robin_cycle is None or not self._clients:
            raise RuntimeError("no ready pool members")
        # ``itertools.cycle`` doesn't drop items mid-cycle, so we
        # scan through it until we find a still-alive client.
        # Worst case is O(N) — trivial for pool sizes we care
        # about (typically <20).
        for _ in range(len(self._configs) + 1):
            candidate_id = next(self._round_robin_cycle)
            client = self._clients.get(candidate_id)
            if client is not None:
                return client
        raise RuntimeError("no ready pool members")

    def ready_clients(self) -> list[AsyncSteamClient]:
        """Snapshot of every currently-ready client.  Useful for
        ``asyncio.gather`` fan-out."""
        return list(self._clients.values())

    def _rebuild_cycle(self) -> None:
        # Rebuild the round-robin cycle whenever the member list
        # changes — cycles created from an outdated list would
        # keep yielding stale ids.
        if self._clients:
            self._round_robin_cycle = itertools.cycle(sorted(self._clients))
        else:
            self._round_robin_cycle = None

    # ------------------------------------------------------------------
    # Mutation — add / remove members after start()
    # ------------------------------------------------------------------

    async def replace_member(self, cfg: PoolMember) -> None:
        """Swap or add a member.  If the account_id already exists,
        the old client is closed first.  Useful for recovering a
        member that failed on ``start()`` after fixing its config
        without restarting the whole pool.
        """
        async with self._lock:
            existing = self._clients.pop(cfg.account_id, None)
            self._failures.pop(cfg.account_id, None)
            self._configs[cfg.account_id] = cfg
            if existing is not None:
                try:
                    await existing.close()
                except Exception:  # noqa: BLE001
                    pass
            hook = (
                cfg.metrics_hook
                if cfg.metrics_hook is not _noop_hook
                else self._default_metrics_hook
            )
            client = AsyncSteamClient(
                reconnect=cfg.reconnect,
                metrics_hook=hook,
            )
            try:
                await client.start()
                await cfg.login(client)
            except BaseException as e:  # noqa: BLE001
                try:
                    await client.close()
                except Exception:  # noqa: BLE001
                    pass
                self._failures[cfg.account_id] = f"{type(e).__name__}: {e}"
                self._rebuild_cycle()
                return
            self._clients[cfg.account_id] = client
            self._rebuild_cycle()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def status(self) -> list[PoolMemberStatus]:
        """Per-member snapshot.  Ordered by ``account_id`` for
        stable output (useful for tests and diff-friendly
        ``/health`` responses)."""
        out: list[PoolMemberStatus] = []
        for account_id in sorted(self._configs):
            client = self._clients.get(account_id)
            failure = self._failures.get(account_id)
            out.append(
                PoolMemberStatus(
                    account_id=account_id,
                    ready=client is not None,
                    failure=failure,
                    client_status=client.status if client is not None else None,
                )
            )
        return out


__all__ = [
    "AsyncSteamPool",
    "PoolMember",
    "PoolLogin",
    "PoolMemberStatus",
]

"""Async facade for :class:`steam.client.SteamClient`.

See :mod:`steam.aio` for the design overview.  This module is the
public entry point — the load-bearing cross-thread bridge lives in
:mod:`steam.aio.runner`, typed errors in :mod:`steam.aio.errors`.

Public surface
--------------

* :class:`AsyncSteamClient` — the async facade.  Instantiate,
  ``await client.start()``, use as an async context manager, or
  wire into FastAPI's ``lifespan``.

Backwards compatibility
-----------------------

Pre-1.6 code that imported ``from steam.aio.client import
AsyncSteamClient`` continues to work.  The private ``_GeventRunner``
name is preserved as a re-export from :mod:`steam.aio.runner` so
early adopters who reached in for it aren't broken by the split.
"""

from __future__ import annotations

import asyncio
import dataclasses
import logging
import threading
import time
from collections.abc import AsyncGenerator, Callable
from concurrent.futures import Future
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    # ``QRLoginSession`` / ``QRLoginResult`` are only referenced in
    # the method signatures on this class — the actual runtime
    # import happens inside the methods (see the ``from .qr import
    # ...`` lines) so the QR module stays lazy-loaded and the two
    # files don't develop a circular import.  ``TYPE_CHECKING``
    # gives mypy / Pylance the names they need for annotations
    # without paying the import cost at module load.
    from .qr import QRLoginResult, QRLoginSession

from .errors import (
    AsyncSteamError,
    SteamClosedError,
    SteamLoginError,
    SteamNotStartedError,
    SteamReconnectError,
    SteamRPCTimeoutError,
)
from .runner import GeventRunner
from .status import (
    RECONNECT_FAILED,
    RECONNECT_IDLE,
    RECONNECT_RECONNECTING,
    ClientStatus,
    MetricsHook,
    _invoke_hook,
    _noop_hook,
)

# Re-export the internal name so early adopters who imported it
# directly aren't broken by the module split.  New code should use
# :class:`steam.aio.runner.GeventRunner`.
_GeventRunner = GeventRunner


_log = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Reconnect policy + credential replay
# ----------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ReconnectPolicy:
    """Configures :class:`AsyncSteamClient`'s auto-reconnect loop.

    Attributes
    ----------
    enabled:
        Master switch.  ``False`` = a disconnect is terminal;
        pending awaits will typically raise once the sync client
        gives up.  ``True`` (default) = try to reconnect + relogin
        transparently.
    max_delay:
        Cap on the exponential backoff (passed through to
        :meth:`SteamClient.reconnect`, which does its own jittered
        backoff internally).  30s matches the sync client's default.
    max_attempts:
        Hard cap on connect attempts before giving up and raising
        :class:`SteamReconnectError` on the next call.  ``None``
        means retry forever — appropriate for long-lived FastAPI
        processes.  A finite value (e.g. 10) is safer during
        development.
    """

    enabled: bool = True
    max_delay: int = 30
    max_attempts: int | None = None


@dataclasses.dataclass
class _LastLogin:
    """Cached login invocation.  Replayed after a successful CM
    reconnect so pending awaits see a re-established session.
    ``anonymous`` is the fast path (no credentials cached, no
    security cost); credentialed logins fall back to
    ``SteamClient.relogin()`` when the CM handed out a
    ``login_key`` — see :attr:`AsyncSteamClient.relogin_available`.
    Passwords are NEVER cached here.
    """

    kind: str  # "anonymous" | "credentialed"
    username: str = ""
    # 2FA / mail codes are one-shot by definition — replaying them
    # doesn't make sense, so we don't cache them either.  If a
    # session dies mid-2FA flow, the caller has to redrive login.
    login_id: int | None = None


class AsyncSteamClient:
    """Async facade around :class:`steam.client.SteamClient`.

    Safe for use inside a FastAPI process — the underlying gevent
    machinery runs on a dedicated background thread and never
    monkey-patches the asyncio process's sockets.

    Typical FastAPI wiring::

        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from steam.aio import AsyncSteamClient

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            client = AsyncSteamClient()
            await client.start()
            await client.anonymous_login()
            app.state.steam = client
            try:
                yield
            finally:
                await client.close()

        app = FastAPI(lifespan=lifespan)

        @app.get("/product/{app_id}")
        async def product(app_id: int):
            return await app.state.steam.get_product_info(apps=[app_id])

    Reconnect
    ---------

    A dropped CM connection is transparently reconnected + re-logged-in
    by default (see :class:`ReconnectPolicy`).  Callers can observe
    the state machine via :meth:`wait_event` / :meth:`events` —
    the client re-emits three events beyond the sync client's own:

    * ``'aio.reconnecting'`` — reconnect loop just started
    * ``'aio.reconnected'`` — reconnect + relogin succeeded
    * ``'aio.reconnect_failed'`` — gave up per policy

    Concurrency
    -----------

    Concurrent ``await`` calls on the same client are serialised by
    gevent (single hub = single greenlet-scheduler) but the asyncio
    loop is never blocked — awaiting many operations concurrently
    is fine, they just execute in gevent's fair round-robin.
    """

    #: Sentinel used for the event bridge overflow warning path.
    _EVENT_QUEUE_MAX = 256

    def __init__(
        self,
        *,
        reconnect: ReconnectPolicy = ReconnectPolicy(),
        metrics_hook: MetricsHook = _noop_hook,
    ) -> None:
        self._runner = GeventRunner(name="pysteam-cm")
        self._sync: Any = None
        self._closed = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._reconnect_policy = reconnect
        self._metrics_hook = metrics_hook
        # State the reconnect loop needs.  ``_last_login`` remembers
        # WHAT to replay; ``_intentional_disconnect`` marks the
        # brief window during ``close()`` where a ``'disconnected'``
        # event MUST NOT trigger a reconnect.
        self._last_login: _LastLogin | None = None
        self._intentional_disconnect = False
        self._reconnect_greenlet: Any = None
        # Reconnect state + activity + uptime bookkeeping for
        # :attr:`status`.  Every value defaults to a "cold" state
        # so :attr:`status` on an unstarted client is safe.
        self._reconnect_state = RECONNECT_IDLE
        self._reconnect_attempts = 0
        self._last_activity_at: float | None = None
        self._started_at: float | None = None
        # Event bridge: (event_name → set[asyncio.Queue]) maps
        # active subscribers.  All access is from the runner thread
        # via the sync client's ``.on(...)`` callback + the
        # ``events()`` async iterator on the asyncio thread.  The
        # mutex protects the dict shape from concurrent
        # mutation across the two threads.
        self._subscribers_lock = threading.Lock()
        self._subscribers: dict[str, set[asyncio.Queue[Any]]] = {}
        # Sync-side listeners we registered (event_name → callback)
        # so ``close()`` can detach them cleanly.
        self._sync_listeners: list[tuple[str, Callable[..., Any]]] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Bring up the runner thread and construct the underlying
        ``SteamClient`` on it.  Idempotent — calling twice is a
        no-op.
        """
        if self._sync is not None:
            return
        self._loop = asyncio.get_running_loop()
        # ``_runner.start`` blocks up to 5s waiting for the gevent
        # hub — run it in the default asyncio executor so we don't
        # freeze the event loop during boot.
        await self._loop.run_in_executor(None, self._runner.start)

        def _make_sync() -> Any:
            # Import inside the runner thread so ``steam.client``'s
            # gevent-touching init happens on the right hub.  Typed
            # ``Any`` because ``SteamClient`` isn't mypy-typed
            # upstream — the ``no-untyped-call`` warning is genuine
            # but unavoidable until upstream ships stubs; we keep
            # the boundary here.
            from steam.client import SteamClient

            return SteamClient()  # type: ignore[no-untyped-call]

        self._sync = await self._await_fut(self._runner.submit(_make_sync))
        self._started_at = time.monotonic()
        # Register the CM disconnect handler — this is what drives
        # auto-reconnect.  It runs on the runner thread inside the
        # sync client's greenlet, which is exactly where
        # ``reconnect()`` / ``relogin()`` need to run.
        self._install_sync_listener("disconnected", self._on_sync_disconnect)
        # Additional sync listeners fire the metrics hook — CM
        # connect / disconnect are noisy in prod, so users usually
        # want them as counters.  Emitting from a listener keeps
        # the hooks decoupled from the RPC path (a broken hook
        # can't break login).
        self._install_sync_listener("connected", self._on_metric_connected)
        self._install_sync_listener("disconnected", self._on_metric_disconnected)
        _invoke_hook(self._metrics_hook, "client.started", {})

    # ------------------------------------------------------------------
    # Metrics glue — sync-side listeners installed at start().
    # Live on the runner thread; keep them cheap so they don't
    # steal time from the recv/heartbeat greenlets.
    # ------------------------------------------------------------------

    def _on_metric_connected(self, *_a: Any) -> None:
        _invoke_hook(self._metrics_hook, "cm.connected", {})

    def _on_metric_disconnected(self, *_a: Any) -> None:
        _invoke_hook(
            self._metrics_hook,
            "cm.disconnected",
            {"intentional": bool(self._intentional_disconnect)},
        )

    async def _await_fut(self, cfut: Future[Any]) -> Any:
        """Bridge a ``concurrent.futures.Future`` into the current
        loop as an awaitable.  ``asyncio.wrap_future`` handles the
        callback registration and cancellation semantics.
        """
        loop = self._loop or asyncio.get_running_loop()
        return await asyncio.wrap_future(cfut, loop=loop)

    def _require_ready(self) -> None:
        if self._sync is None:
            raise SteamNotStartedError(
                "AsyncSteamClient is not started; call `await client.start()` "
                "or use it as an async context manager.",
            )
        if self._closed:
            raise SteamClosedError("AsyncSteamClient is closed")

    async def _call(
        self,
        fn: Callable[[], Any],
        *,
        method: str | None = None,
    ) -> Any:
        """Submit ``fn`` to the runner and await the result — the
        one funnel every public method routes through, so lifecycle
        checks, cancellation, metrics, and future-bridging live in
        one place.

        Cancellation
        ------------

        If the awaiting coroutine is cancelled (e.g. via
        ``asyncio.wait_for`` timeout or a client disconnect from
        FastAPI), we kill the backing gevent greenlet through
        :meth:`GeventRunner.cancel_future` so the sync work stops
        instead of orphaning a socket read.  The greenlet's
        ``GreenletExit`` propagates back into the future as an
        exception — we ignore it here because the caller has
        already cancelled and doesn't need to see it.
        """
        self._require_ready()
        cfut = self._runner.submit(fn)
        start_ts = time.monotonic()
        if method:
            _invoke_hook(self._metrics_hook, "rpc.started", {"method": method})
        try:
            result = await self._await_fut(cfut)
        except asyncio.CancelledError:
            # Best-effort kill; safe even if the greenlet has
            # already completed.  We DON'T await the kill — the
            # canceller is on its way out and doesn't care about
            # confirmation.
            self._runner.cancel_future(cfut)
            if method:
                duration_ms = (time.monotonic() - start_ts) * 1000.0
                _invoke_hook(
                    self._metrics_hook,
                    "rpc.failed",
                    {
                        "method": method,
                        "duration_ms": duration_ms,
                        "error": "cancelled",
                    },
                )
            raise
        except BaseException as e:  # noqa: BLE001
            if method:
                duration_ms = (time.monotonic() - start_ts) * 1000.0
                _invoke_hook(
                    self._metrics_hook,
                    "rpc.failed",
                    {
                        "method": method,
                        "duration_ms": duration_ms,
                        "error": type(e).__name__,
                    },
                )
            raise
        else:
            self._last_activity_at = time.time()
            if method:
                duration_ms = (time.monotonic() - start_ts) * 1000.0
                _invoke_hook(
                    self._metrics_hook,
                    "rpc.succeeded",
                    {"method": method, "duration_ms": duration_ms},
                )
            return result

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def anonymous_login(self, *, raise_on_error: bool = True) -> Any:
        """Log in as an anonymous user (no username / password).

        Returns the raw ``EResult`` from the sync client.  When
        ``raise_on_error`` (the default), a non-OK result raises
        :class:`SteamLoginError` — this is the idiom most callers
        want (no more ``if result != EResult.OK`` boilerplate) but
        can be turned off for callers that need the raw enum.
        """
        # ``_require_ready`` runs BEFORE touching ``self._sync``
        # because dereferencing ``self._sync.anonymous_login`` while
        # ``_sync`` is ``None`` would raise ``AttributeError``
        # instead of the typed :class:`SteamNotStartedError` callers
        # expect.  Same pattern applies to every method below that
        # reads a bound method off the sync client for submission.
        self._require_ready()
        result = await self._call(
            self._sync.anonymous_login,
            method="anonymous_login",
        )
        self._last_login = _LastLogin(kind="anonymous")
        self._raise_login_if_needed(result, raise_on_error)
        return result

    async def login(
        self,
        username: str,
        password: str = "",
        *,
        login_key: str | None = None,
        auth_code: str | None = None,
        two_factor_code: str | None = None,
        login_id: int | None = None,
        raise_on_error: bool = True,
    ) -> Any:
        """Log in with credentials.  See ``SteamClient.login`` for
        the returned ``EResult`` values and 2FA / mail-code
        semantics.

        Passwords are NOT cached here — see :attr:`relogin_available`
        for how the auto-reconnect loop replays a credentialed
        login safely (it relies on the ``login_key`` Steam issues
        after a successful password login).
        """
        self._require_ready()
        sync = self._sync

        def _do_login() -> Any:
            return sync.login(
                username,
                password,
                login_key=login_key,
                auth_code=auth_code,
                two_factor_code=two_factor_code,
                login_id=login_id,
            )

        result = await self._call(_do_login, method="login")
        self._last_login = _LastLogin(
            kind="credentialed",
            username=username,
            login_id=login_id,
        )
        self._raise_login_if_needed(result, raise_on_error)
        return result

    def _raise_login_if_needed(self, result: Any, raise_on_error: bool) -> None:
        if not raise_on_error:
            return
        # Sync client returns an ``EResult`` enum; compare by name
        # rather than importing the enum (keeps this module import-
        # cheap and avoids a hard dep on ``steam.enums`` from the
        # asyncio thread).
        ok = getattr(result, "name", None) == "OK" or result is True
        if not ok:
            raise SteamLoginError(result)

    async def logout(self) -> None:
        """Send ``ClientLogOff`` and wait for the CM to acknowledge
        (up to 5s in the sync client).  Falls through to
        ``disconnect`` internally if the ack doesn't come.

        Sets the "intentional disconnect" flag so the auto-reconnect
        loop doesn't fire while we tear down.
        """
        self._require_ready()
        self._intentional_disconnect = True
        try:
            await self._call(self._sync.logout, method="logout")
        finally:
            # Leave the flag on — callers typically follow ``logout``
            # with ``close()``; if they want to re-login on the
            # same client instance, the next successful
            # ``anonymous_login`` / ``login`` clears it.
            pass

    async def disconnect(self) -> None:
        """Tear down the socket and kill background greenlets on
        the sync client.  Does not stop the runner thread — call
        :meth:`close` for full teardown.

        Marks the disconnect as intentional so the auto-reconnect
        loop doesn't fire.
        """
        self._require_ready()
        self._intentional_disconnect = True
        await self._call(self._sync.disconnect, method="disconnect")

    # ------------------------------------------------------------------
    # RPC — call-and-return methods
    # ------------------------------------------------------------------

    async def get_product_info(
        self,
        apps: list[int] | None = None,
        packages: list[int] | None = None,
        *,
        meta_data_only: bool = False,
        raw: bool = False,
        auto_access_tokens: bool = True,
        timeout: float = 15.0,
    ) -> Any:
        """Fetch product info for the given app / package IDs.
        Passthrough to ``SteamClient.get_product_info`` with the
        same kwargs — see the sync docstring for the return shape.

        Raises :class:`SteamRPCTimeoutError` if the underlying
        gevent-side call times out (the sync client raises
        ``gevent.Timeout`` in that case).
        """
        self._require_ready()
        sync = self._sync
        _apps = apps or []
        _packages = packages or []

        def _do_get() -> Any:
            return sync.get_product_info(
                apps=_apps,
                packages=_packages,
                meta_data_only=meta_data_only,
                raw=raw,
                auto_access_tokens=auto_access_tokens,
                timeout=timeout,
            )

        try:
            return await self._call(_do_get, method="get_product_info")
        except BaseException as e:  # noqa: BLE001
            if _is_gevent_timeout(e):
                raise SteamRPCTimeoutError(timeout) from e
            raise

    async def send_um_and_wait(
        self,
        method_name: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float = 10.0,
        raises: bool = False,
    ) -> Any:
        """Send a Steam Unified Messages RPC and wait for the reply.

        ``method_name`` is the fully-qualified proto method name
        (e.g. ``"Player.GetGameBadgeLevels#1"``); ``params`` is a
        dict matching the request proto's field names.  Returns the
        response ``CMsgProtoBufHeader`` — see the sync client's
        ``send_um_and_wait`` docstring for details.

        Raises :class:`SteamRPCTimeoutError` on gevent timeout.
        """
        self._require_ready()
        sync = self._sync
        _params = params or {}

        def _do_send() -> Any:
            return sync.send_um_and_wait(
                method_name,
                _params,
                timeout=timeout,
                raises=raises,
            )

        try:
            return await self._call(_do_send, method="send_um_and_wait")
        except BaseException as e:  # noqa: BLE001
            if _is_gevent_timeout(e):
                raise SteamRPCTimeoutError(timeout) from e
            raise

    # ------------------------------------------------------------------
    # QR sign-in — mirror of the desktop client's "Or sign in with QR"
    # panel.  See :mod:`steam.aio.qr` for the full flow + design notes.
    # ------------------------------------------------------------------

    async def begin_qr_login(
        self,
        *,
        device_friendly_name: str = "pysteam-client",
        website_id: str = "Community",
    ) -> QRLoginSession:
        """Start a QR sign-in handshake with Steam.

        Returns a :class:`~steam.aio.qr.QRLoginSession` carrying the
        ``challenge_url`` you'd render as a QR image plus a
        ``client_id`` handle to resume the session on subsequent
        polls.  The client stays connected in its current state
        during this — no session churn on the CM side, no login
        state change.

        The default ``device_friendly_name`` shows up in the user's
        Steam account settings under "Authorized devices"; override
        with something operator-recognisable if this client is one
        of many talking to the same account.
        """
        self._require_ready()
        from .qr import _rpc_begin

        return await _rpc_begin(
            self,
            device_friendly_name=device_friendly_name,
            website_id=website_id,
        )

    async def poll_qr_status(
        self,
        session: QRLoginSession,
    ) -> QRLoginResult | None:
        """One-shot poll for a QR sign-in session.

        Returns ``None`` while Steam is still waiting for the
        mobile confirmation, or a :class:`~steam.aio.qr.QRLoginResult`
        once the mobile app confirms and tokens are ready.  Raises
        :class:`~steam.aio.qr.QRSignInExpired` if Steam rotates the
        challenge (call :meth:`begin_qr_login` again).

        Use this when driving the polling loop yourself (e.g.
        surfacing per-tick progress in a UI); use
        :meth:`wait_qr_confirmation` for the fire-and-forget
        version that loops internally.
        """
        self._require_ready()
        from .qr import _rpc_poll

        return await _rpc_poll(self, session=session)

    async def wait_qr_confirmation(
        self,
        session: QRLoginSession,
        *,
        timeout: float | None = None,
        interval_override: float | None = None,
    ) -> QRLoginResult:
        """Poll ``PollAuthSessionStatus`` at ``session.interval``
        until the mobile app confirms or ``timeout`` elapses.

        ``timeout`` defaults to
        :data:`~steam.aio.qr.DEFAULT_QR_TIMEOUT_SECONDS` (120s) —
        matches the desktop Steam client's own "generate new code"
        cutoff.  Raises :class:`~steam.aio.qr.QRSignInExpired` when
        the deadline passes without a mobile confirmation.
        """
        self._require_ready()
        from .qr import (
            DEFAULT_QR_TIMEOUT_SECONDS,
            _wait_for_confirmation,
        )

        return await _wait_for_confirmation(
            self,
            session=session,
            timeout=timeout if timeout is not None else DEFAULT_QR_TIMEOUT_SECONDS,
            interval_override=interval_override,
        )

    # ------------------------------------------------------------------
    # Event bridge — asyncio-side subscribers on top of the sync
    # client's gevent EventEmitter.
    # ------------------------------------------------------------------

    async def wait_event(
        self,
        name: str,
        timeout: float | None = None,
    ) -> tuple[Any, ...]:
        """Wait for a single occurrence of ``name`` from the sync
        client's event emitter and return its args as a tuple.
        On timeout raises :class:`SteamRPCTimeoutError`.

        Names include ``'connected'``, ``'disconnected'``,
        ``'reconnect'``, ``'logged_on'``, ``'channel_secured'``,
        ``'error'``, plus the client's own reconnect lifecycle
        events (``'aio.reconnecting'``, ``'aio.reconnected'``,
        ``'aio.reconnect_failed'``).  Arbitrary ``EMsg`` values also
        work — pass the integer id as a string per the sync
        client's convention.
        """
        self._require_ready()
        q: asyncio.Queue[Any] = asyncio.Queue(maxsize=1)
        self._add_subscriber(name, q)
        try:
            if timeout is None:
                item: tuple[Any, ...] = await q.get()
                return item
            try:
                item = await asyncio.wait_for(q.get(), timeout=timeout)
                return item
            except TimeoutError as e:
                raise SteamRPCTimeoutError(
                    timeout,
                    f"Timed out waiting for event {name!r}",
                ) from e
        finally:
            self._remove_subscriber(name, q)

    async def events(
        self,
        *names: str,
        buffer_size: int = _EVENT_QUEUE_MAX,
    ) -> AsyncGenerator[tuple[str, tuple[Any, ...]], None]:  # noqa: UP043
        """Async iterator over the given event names.  Yields
        ``(name, args_tuple)`` pairs.  Loop teardown detaches the
        listeners.

        The internal per-subscriber queue is bounded (default 256
        events); on overflow we drop the OLDEST event and log a
        warning — reasonable for an observer that fell behind.
        Callers who can't tolerate drops should size ``buffer_size``
        to their expected burst OR consume in a background task
        that stays close to real-time.
        """
        self._require_ready()
        if not names:
            raise ValueError("events() requires at least one event name")
        q: asyncio.Queue[Any] = asyncio.Queue(maxsize=buffer_size)
        # A single queue serves all names — each event pushed
        # carries its own name in the tuple so the iterator can
        # tell them apart.  Multiplexing keeps the queue count
        # bounded at 1 per iterator regardless of subscription
        # width.
        for name in names:
            self._add_subscriber(name, q)
        try:
            while True:
                item = await q.get()
                yield item  # ``(name, args_tuple)``
        finally:
            for name in names:
                self._remove_subscriber(name, q)

    def _add_subscriber(self, name: str, q: asyncio.Queue[Any]) -> None:
        with self._subscribers_lock:
            fresh_name = name not in self._subscribers
            self._subscribers.setdefault(name, set()).add(q)
        if fresh_name:
            # First subscriber for this name — register a sync-side
            # listener that fans events out to whichever asyncio
            # queues are currently subscribed.  Later
            # subscribe/unsubscribe calls just mutate the set; we
            # never register more than one sync listener per name.
            self._install_sync_listener(name, self._make_forwarder(name))

    def _remove_subscriber(self, name: str, q: asyncio.Queue[Any]) -> None:
        with self._subscribers_lock:
            queues = self._subscribers.get(name)
            if queues is None:
                return
            queues.discard(q)
            if not queues:
                del self._subscribers[name]
        # We deliberately leave the sync listener registered even
        # when the last subscriber leaves — re-registering per
        # subscriber flap would race with in-flight events on the
        # runner thread.  The forwarder becomes a no-op when
        # ``_subscribers[name]`` is empty (see :meth:`_make_forwarder`).

    def _make_forwarder(self, name: str) -> Callable[..., None]:
        """Build the sync-side callback that forwards ``name``
        events onto every currently-subscribed asyncio queue.
        Runs on the runner thread, so it uses
        ``loop.call_soon_threadsafe`` to hand each event to the
        asyncio loop.
        """

        def _forward(*args: Any) -> None:
            with self._subscribers_lock:
                queues = list(self._subscribers.get(name, ()))
            if not queues:
                return
            loop = self._loop
            if loop is None or loop.is_closed():
                return
            payload = (name, args)
            for q in queues:
                loop.call_soon_threadsafe(self._enqueue, q, payload, name)

        return _forward

    @staticmethod
    def _enqueue(q: asyncio.Queue[Any], payload: Any, name: str) -> None:
        """Put ``payload`` on ``q`` from the asyncio thread; on
        overflow drop the oldest event and log a warning."""
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            try:
                q.get_nowait()  # drop oldest
            except asyncio.QueueEmpty:
                pass
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                # A concurrent producer beat us to the space; the
                # event is dropped.  Very unlikely with a single
                # producer, but treat as best-effort.
                pass
            _log.warning(
                "aio event queue overflow for %r — dropped oldest event",
                name,
            )

    def _install_sync_listener(
        self,
        name: str,
        callback: Callable[..., Any],
    ) -> None:
        """Register a listener on the sync client's EventEmitter.
        Must be called from the runner thread (that's where the
        emitter's internal set lives)."""

        def _register() -> None:
            self._sync.on(name, callback)

        # Submit and don't await — event subscription doesn't need
        # to complete before the caller returns; the runner will
        # process it well before any event of interest fires.
        self._runner.submit(_register)
        self._sync_listeners.append((name, callback))

    # ------------------------------------------------------------------
    # Auto-reconnect
    # ------------------------------------------------------------------

    def _on_sync_disconnect(self, *_args: Any) -> None:
        """Sync-side callback fired on the runner thread when the
        CM connection drops.  Spawns the reconnect loop unless the
        disconnect was intentional (``logout`` / ``disconnect`` /
        ``close``) or reconnect is disabled by policy.
        """
        if self._closed or self._intentional_disconnect:
            return
        if not self._reconnect_policy.enabled:
            return
        if self._reconnect_greenlet is not None:
            # Already reconnecting — sync client emits several
            # 'disconnected' events in a row during a bad flap; we
            # only want one worker.
            greenlet_alive = (
                getattr(
                    self._reconnect_greenlet,
                    "dead",
                    True,
                )
                is False
            )
            if greenlet_alive:
                return
        import gevent

        self._reconnect_greenlet = gevent.spawn(self._reconnect_loop)

    def _reconnect_loop(self) -> None:
        """Runs on the runner thread in a greenlet.  Retries
        ``sync.reconnect()`` + replay-login until success or
        policy-cap; emits ``aio.reconnecting`` / ``aio.reconnected``
        / ``aio.reconnect_failed`` events at each state transition."""
        sync = self._sync
        policy = self._reconnect_policy
        max_attempts = policy.max_attempts
        attempt = 0
        last_error: BaseException | None = None
        self._reconnect_state = RECONNECT_RECONNECTING
        self._reconnect_attempts = 0
        sync.emit("aio.reconnecting")
        _invoke_hook(self._metrics_hook, "reconnect.started", {})
        while True:
            attempt += 1
            self._reconnect_attempts = attempt
            if max_attempts is not None and attempt > max_attempts:
                self._reconnect_state = RECONNECT_FAILED
                sync.emit(
                    "aio.reconnect_failed",
                    attempt - 1,
                    last_error,
                )
                _invoke_hook(
                    self._metrics_hook,
                    "reconnect.failed",
                    {"attempts": attempt - 1},
                )
                _log.error(
                    "aio: reconnect gave up after %d attempts (last=%r)",
                    attempt - 1,
                    last_error,
                )
                return
            try:
                # ``reconnect`` has its own jittered exponential
                # backoff internally, capped at ``max_delay``.
                connected = sync.reconnect(maxdelay=policy.max_delay)
            except BaseException as e:  # noqa: BLE001
                last_error = e
                connected = False
                # ``AttributeError`` / ``TypeError`` from missing or
                # mis-signatured ``reconnect`` are bugs, not transient
                # network faults — retrying them accomplishes nothing
                # and would loop forever under the default
                # ``max_attempts=None`` policy.  Bail out fast so the
                # error surfaces to the caller instead of stalling
                # the runner thread.
                if isinstance(e, (AttributeError, TypeError)):
                    self._reconnect_state = RECONNECT_FAILED
                    sync.emit("aio.reconnect_failed", attempt, e)
                    _invoke_hook(
                        self._metrics_hook,
                        "reconnect.failed",
                        {"attempts": attempt},
                    )
                    _log.error(
                        "aio: reconnect bailed on non-recoverable error %r "
                        "(this is a bug or a mocked-out SteamClient — real "
                        "reconnect() should never raise these)",
                        e,
                    )
                    return
            if not connected:
                continue
            # Reconnected — replay whichever login we last did.
            try:
                self._replay_login()
            except BaseException as e:  # noqa: BLE001
                # Login itself failed.  Treat this as an
                # attempt-failure and loop (the CM may be
                # transiently rejecting).  If it's permanent
                # (bad password / banned) the caller will see it
                # once ``max_attempts`` is hit.
                last_error = e
                _log.warning(
                    "aio: relogin after reconnect failed: %r",
                    e,
                )
                continue
            self._reconnect_state = RECONNECT_IDLE
            self._reconnect_attempts = 0
            sync.emit("aio.reconnected", attempt)
            _invoke_hook(
                self._metrics_hook,
                "reconnect.succeeded",
                {"attempts": attempt},
            )
            _log.info("aio: reconnected + relogged in after %d attempts", attempt)
            return

    def _replay_login(self) -> None:
        """Runs on the runner thread inside the reconnect loop.
        Replays the last login using the safest available path:
        anonymous → ``anonymous_login``; credentialed →
        ``relogin()`` if the sync client cached a ``login_key``,
        else no-op (caller must re-authenticate — password isn't
        cached here for security).
        """
        sync = self._sync
        last = self._last_login
        if last is None:
            return
        if last.kind == "anonymous":
            sync.anonymous_login()
            return
        if last.kind == "credentialed":
            if getattr(sync, "relogin_available", False):
                sync.relogin()
            else:
                _log.warning(
                    "aio: no cached login_key for %r; skipping relogin — "
                    "caller must re-authenticate",
                    last.username,
                )

    @property
    def relogin_available(self) -> bool:
        """Whether the sync client has a cached ``login_key`` that
        auto-reconnect can use to replay a credentialed login
        without needing the password again."""
        return bool(getattr(self._sync, "relogin_available", False))

    # ------------------------------------------------------------------
    # Introspection — proxy attributes off the sync client
    # ------------------------------------------------------------------

    @property
    def logged_on(self) -> bool:
        """Whether the CM session is currently logged in."""
        return bool(getattr(self._sync, "logged_on", False))

    @property
    def connected(self) -> bool:
        """Whether the underlying TCP connection is up."""
        return bool(getattr(self._sync, "connected", False))

    @property
    def username(self) -> str | None:
        """Currently-logged-in username, or ``None`` if anonymous / logged out."""
        return getattr(self._sync, "username", None)

    @property
    def cell_id(self) -> int:
        """Steam cell id we're routed to (0 until the CM assigns one)."""
        return int(getattr(self._sync, "cell_id", 0) or 0)

    @property
    def status(self) -> ClientStatus:
        """A JSON-serialisable snapshot of session state, suitable
        for a FastAPI ``/health`` endpoint or an MCP status tool.
        Cheap — builds a fresh dataclass each call, no caching."""
        uptime = (
            time.monotonic() - self._started_at
            if self._started_at is not None
            else None
        )
        return ClientStatus(
            started=self._sync is not None,
            closed=self._closed,
            connected=self.connected,
            logged_on=self.logged_on,
            username=self.username,
            cell_id=self.cell_id,
            reconnect_state=self._reconnect_state,
            reconnect_attempts=self._reconnect_attempts,
            last_activity_at=self._last_activity_at,
            uptime_seconds=uptime,
        )

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Full teardown: disconnect the CM session and stop the
        runner thread.  Idempotent; safe to call from a FastAPI
        ``lifespan`` finaliser or ``__aexit__``.

        Uses ``asyncio.wait_for`` around each cross-thread await
        so a wedged sync client can't hang the shutdown — after
        the (generous) timeout we fall through to stopping the
        runner, which will terminate the daemon thread regardless.
        """
        if self._closed:
            return
        self._closed = True
        self._intentional_disconnect = True
        if self._sync is not None and self._runner.is_alive:
            try:
                await asyncio.wait_for(
                    self._await_fut(
                        self._runner.submit(self._detach_and_disconnect),
                    ),
                    timeout=5.0,
                )
            except (TimeoutError, Exception):  # noqa: BLE001
                # Runner may be slow or wedged — the ``runner.stop``
                # call below will kill the thread with prejudice.
                pass
        loop = self._loop or asyncio.get_running_loop()
        await loop.run_in_executor(None, self._runner.stop)
        _invoke_hook(self._metrics_hook, "client.closed", {})

    def _detach_and_disconnect(self) -> None:
        """Runs on the runner thread during ``close()`` — remove
        every sync-side listener we installed, then disconnect."""
        sync = self._sync
        for name, callback in self._sync_listeners:
            try:
                sync.remove_listener(name, callback)
            except Exception:  # noqa: BLE001
                pass
        self._sync_listeners.clear()
        with self._subscribers_lock:
            self._subscribers.clear()
        try:
            sync.disconnect()
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> AsyncSteamClient:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> None:
        await self.close()


def _is_gevent_timeout(exc: BaseException) -> bool:
    """Detect ``gevent.Timeout`` without importing gevent on the
    asyncio thread.  We can't ``isinstance`` against a class we
    haven't imported, so walk the MRO by name — good enough.
    """
    for cls in type(exc).__mro__:
        if cls.__module__.startswith("gevent") and cls.__name__ == "Timeout":
            return True
    return False


__all__ = [
    "AsyncSteamClient",
    "ReconnectPolicy",
    # Re-exports for callers who reach for typed errors from here.
    "AsyncSteamError",
    "SteamNotStartedError",
    "SteamClosedError",
    "SteamLoginError",
    "SteamReconnectError",
    "SteamRPCTimeoutError",
]

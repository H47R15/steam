"""Cross-thread bridge from ``asyncio`` to ``gevent``.

Owns a dedicated daemon thread with an isolated gevent :class:`Hub`.
The asyncio side submits callables and awaits a
``concurrent.futures.Future`` — the runner thread wakes its hub via
a libev/libuv **async watcher** (``hub.loop.async_()``), spawns a
greenlet per work item, and writes the result back through the
future.  ``asyncio.wrap_future`` translates the completion into an
awaitable on the asyncio loop.

The runner's main greenlet blocks forever on a ``gevent.event.Event``
so background greenlets (recv loop, CM heartbeat, per-message
handlers) keep making progress between asyncio submissions.  Handing
the thread back to a ``ThreadPoolExecutor`` between calls would
starve those loops and let the CM kill the connection at 30s
``cm_stale_seconds``.

Not part of the public API — an implementation detail of
:class:`steam.aio.client.AsyncSteamClient`, factored out so a future
``steam.mcp`` server (or any other async surface) can reuse it
without also importing the full client facade.
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from concurrent.futures import Future
from typing import Any


class _ShutdownSentinel:
    """Distinct from ``None`` so a legitimate ``None`` work-item
    can't be mistaken for the stop signal.  Named for readability
    in tracebacks."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "_ShutdownSentinel()"


_SHUTDOWN = _ShutdownSentinel()


class GeventRunner:
    """Owns a gevent hub on a dedicated daemon thread.

    Lifecycle
    ---------

    * :meth:`start` boots the thread and returns once the hub +
      async watcher are ready to accept work.  Raises whatever the
      runner raised during setup, or ``RuntimeError`` on timeout.
    * :meth:`submit` pushes a callable onto the internal queue and
      wakes the hub; returns a ``concurrent.futures.Future``.
      Callable runs inside a ``gevent.spawn``ed greenlet on the
      runner thread — long-running work is fine, other greenlets
      (heartbeat etc.) keep running underneath.
    * :meth:`stop` sends a shutdown sentinel and joins the thread.
      Idempotent; blocks up to ``timeout`` seconds.  A daemon
      thread will die with the process regardless.

    Thread safety
    -------------

    * :meth:`submit` is safe from any thread — pushing onto a stdlib
      :class:`queue.Queue` is protected by the queue's own mutex,
      and ``watcher.send()`` is documented safe from foreign threads
      (it just flips a byte in the eventfd/pipe backing the watcher).
    * :meth:`stop` is safe from any thread.
    * DO NOT call other methods concurrently with :meth:`start` on
      a fresh runner — start must complete before submissions land.
    """

    def __init__(self, name: str = "pysteam-runner") -> None:
        self._name = name
        # ``_ready`` flips once the hub is set up AND the async
        # watcher is registered — submitting before that would push
        # onto the queue but never wake the hub.
        self._ready = threading.Event()
        self._stopped = threading.Event()
        self._init_error: BaseException | None = None
        # Populated inside the runner thread once the gevent hub
        # exists; the caller thread only ever reads them, and
        # ``_ready.wait()`` establishes happens-before with the
        # assignments inside ``_run``.
        self._async_watcher: Any = None
        self._done: Any = None
        self._work_queue: queue.Queue[Any] = queue.Queue()
        self._thread = threading.Thread(
            target=self._run,
            name=name,
            daemon=True,
        )
        # ``id(future) -> greenlet`` for in-flight submissions.
        # Written by ``_exec_one`` on the runner thread, read from
        # any thread by :meth:`cancel_future`.  Dict item ops in
        # CPython are atomic under the GIL, so no lock is needed
        # for get/set/pop of a single key — this is the same
        # rationale ``concurrent.futures`` itself relies on for
        # its internal state.
        self._greenlets: dict[int, Any] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self, timeout: float = 5.0) -> None:
        """Boot the runner thread.  Blocks until the hub is ready to
        accept work.  Raises whatever the runner raised during
        setup, or ``RuntimeError`` on timeout.
        """
        self._thread.start()
        if not self._ready.wait(timeout=timeout):
            raise RuntimeError(
                f"{self._name} failed to reach ready state within {timeout}s",
            )
        if self._init_error is not None:
            raise self._init_error

    def _run(self) -> None:
        try:
            # Local imports so ``gevent`` never enters the parent
            # process's ``sys.modules`` via this module — it's only
            # touched on the runner thread.
            import gevent
            import gevent.event
            from gevent.hub import get_hub

            hub = get_hub()
            self._async_watcher = hub.loop.async_()
            self._async_watcher.start(self._drain_queue)
            self._done = gevent.event.Event()
            self._ready.set()
            # Block the main greenlet forever.  The hub keeps
            # spinning underneath because the async watcher and any
            # greenlets we spawn inside ``_drain_queue`` share the
            # same libev loop.  ``_done.set()`` from the shutdown
            # path unblocks and we fall through to cleanup.
            self._done.wait()
        except BaseException as e:
            self._init_error = e
            self._ready.set()
        finally:
            try:
                if self._async_watcher is not None:
                    self._async_watcher.stop()
                    self._async_watcher.close()
            finally:
                self._stopped.set()

    def stop(self, timeout: float = 10.0) -> None:
        """Shut down the runner.  Idempotent; safe to call from any
        thread.  Blocks until the runner thread exits or the
        timeout elapses — a daemon thread will die with the
        process regardless, so a timeout here just means "we gave
        up waiting", not "the runner leaked".
        """
        if not self._thread.is_alive():
            return
        self._work_queue.put(_SHUTDOWN)
        watcher = self._async_watcher
        if watcher is not None:
            try:
                watcher.send()
            except Exception:  # noqa: BLE001
                # Watcher may already be torn down.
                pass
        self._stopped.wait(timeout=timeout)

    # ------------------------------------------------------------------
    # Work submission
    # ------------------------------------------------------------------

    def submit(self, fn: Callable[[], Any]) -> Future[Any]:
        """Enqueue ``fn`` for execution on the gevent thread.

        Returns a ``concurrent.futures.Future`` — bridge to
        asyncio with ``asyncio.wrap_future(fut)``.
        """
        if not self._ready.is_set():
            raise RuntimeError(f"{self._name} not started")
        if self._stopped.is_set():
            raise RuntimeError(f"{self._name} is stopped")
        fut: Future[Any] = Future()
        self._work_queue.put((fn, fut))
        watcher = self._async_watcher
        if watcher is not None:
            watcher.send()
        return fut

    def _drain_queue(self) -> None:
        """Called on the runner thread when ``.send()`` wakes the
        hub.  Drains everything currently on the queue and spawns
        one greenlet per work item — draining in a loop rather than
        one-per-wake means a burst of submissions doesn't require
        N watcher wake-ups.
        """
        import gevent

        while True:
            try:
                item = self._work_queue.get_nowait()
            except queue.Empty:
                return
            if item is _SHUTDOWN:
                if self._done is not None:
                    self._done.set()
                return
            fn, fut = item
            gevent.spawn(self._exec_one, fn, fut)

    def cancel_future(self, fut: Future[Any]) -> bool:
        """Kill the greenlet backing ``fut``, if any.  Safe from
        any thread; the kill is scheduled through a new submission
        so it happens on the runner thread (killing a greenlet
        from a foreign thread is not fully thread-safe on all
        gevent versions).

        Returns ``True`` if a live greenlet was found and a kill
        scheduled, ``False`` if the future has already completed
        or was never started.  Idempotent — a second call after
        the greenlet dies is a no-op.
        """
        greenlet = self._greenlets.get(id(fut))
        if greenlet is None:
            return False
        # Schedule the kill on the runner thread.  Using
        # ``submit`` also wakes the hub via the async watcher, so
        # the kill lands promptly even if no other work is queued.
        # ``block=False`` on ``.kill()`` returns immediately without
        # waiting for the target greenlet to unwind — good enough
        # because the future itself carries the ``GreenletExit``
        # exception once the target actually dies.
        try:

            def _kill(g: Any = greenlet) -> None:
                g.kill(block=False)

            self.submit(_kill)
        except RuntimeError:
            # Runner already stopped — greenlets on that hub are
            # already dead, so nothing to kill.
            return False
        return True

    def _exec_one(self, fn: Callable[[], Any], fut: Future[Any]) -> None:
        """Body of the per-work greenlet.  Runs ``fn`` synchronously
        on the gevent thread and writes the outcome into ``fut``.

        Records the current greenlet in ``_greenlets`` so
        :meth:`cancel_future` can kill it if the asyncio side
        cancels (e.g. via ``asyncio.wait_for`` timeout).  Entry is
        cleaned up in the ``finally`` block whether the callable
        completes normally, raises, or is killed by
        ``GreenletExit``.

        Catches ``BaseException`` (not just ``Exception``) so
        gevent-specific transports like ``gevent.Timeout`` — which
        subclasses ``BaseException`` in newer gevent releases —
        surface as awaited exceptions rather than hanging the
        ``asyncio.wrap_future`` forever.  ``GreenletExit`` (raised
        by ``kill()``) also flows through this path; the resulting
        exception is set on the future so the awaiting asyncio
        coroutine sees a real error rather than hanging on the
        already-cancelled ``wrap_future``.
        """
        import gevent

        self._greenlets[id(fut)] = gevent.getcurrent()
        try:
            try:
                result = fn()
            except BaseException as e:  # noqa: BLE001
                if not fut.done():
                    fut.set_exception(e)
            else:
                if not fut.done():
                    fut.set_result(result)
        finally:
            self._greenlets.pop(id(fut), None)

    # ------------------------------------------------------------------
    # Introspection (mostly for tests)
    # ------------------------------------------------------------------

    @property
    def is_alive(self) -> bool:
        """True if the runner thread is running and hasn't stopped."""
        return self._thread.is_alive() and not self._stopped.is_set()

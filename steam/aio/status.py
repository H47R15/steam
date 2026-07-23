"""Structured status + metrics-hook contract for :mod:`steam.aio`.

Two independent things live here because they're often used
together:

* :class:`ClientStatus` — a frozen dataclass that
  :attr:`AsyncSteamClient.status` returns.  Safe to serialise to
  JSON directly (all fields are primitives), so a FastAPI
  ``/health`` endpoint can just return it, and an MCP tool can
  expose it as-is.
* :class:`MetricsHook` — the callable protocol the client fires
  on interesting lifecycle events.  Users wire this to
  Prometheus / StatsD / OpenTelemetry / logs without the library
  taking a hard dep on any of those.

Neither module pulls in any framework; anyone can import
:mod:`steam.aio.status` from a request handler without adding
Prometheus to the process's dependency graph.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any

# ---------------------------------------------------------------------
# Status snapshot
# ---------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ClientStatus:
    """Point-in-time snapshot of an :class:`AsyncSteamClient`'s
    session state.  Cheap to compute; :attr:`AsyncSteamClient.status`
    builds a fresh instance every call rather than caching (the
    call is O(1) and callers shouldn't have to think about staleness).

    All fields are JSON-serialisable primitives so a FastAPI
    handler can do ``return client.status.__dict__`` directly or
    pass through as a Pydantic model.

    Attributes
    ----------
    started:
        ``True`` after :meth:`AsyncSteamClient.start` completes,
        ``False`` before and after :meth:`AsyncSteamClient.close`.
    closed:
        ``True`` once :meth:`AsyncSteamClient.close` has been
        invoked.  ``started AND closed`` is possible — the client
        was alive at some point but has been torn down.
    connected:
        Whether the underlying TCP connection to the CM is up.
    logged_on:
        Whether the CM has accepted our login.  Anonymous vs
        credentialed doesn't change this field — see :attr:`username`.
    username:
        Currently-logged-in username, or ``None`` for anonymous /
        logged out.
    cell_id:
        Steam cell id the CM assigned to us (0 before the CM has
        replied).  Useful for CDN routing.
    reconnect_state:
        One of ``"idle"``, ``"reconnecting"``, or ``"failed"``.
        ``"failed"`` means the auto-reconnect loop hit its
        ``max_attempts`` and gave up — the caller must decide what
        to do (usually: log an alert and rebuild the client).
    reconnect_attempts:
        Number of reconnect attempts made since the current
        disconnect event.  Resets to 0 on ``aio.reconnected``.
    last_activity_at:
        Unix timestamp of the last successful RPC call (login,
        get_product_info, send_um_and_wait, …), or ``None`` if
        nothing has succeeded yet.  Useful for stale-client
        detection.
    uptime_seconds:
        Seconds since :meth:`start` was called, or ``None`` if
        the client hasn't started yet.
    """

    started: bool
    closed: bool
    connected: bool
    logged_on: bool
    username: str | None
    cell_id: int
    reconnect_state: str
    reconnect_attempts: int
    last_activity_at: float | None
    uptime_seconds: float | None


# ---------------------------------------------------------------------
# Metrics hook
# ---------------------------------------------------------------------


#: Signature of the optional metrics hook.  The client invokes it
#: at every lifecycle transition and RPC boundary.  ``event`` is
#: a short kebab-case name; ``tags`` is a flat dict of primitives
#: describing the event, safe to pass straight into a Prometheus
#: label set or StatsD tag list.
#:
#: Events fired today:
#:
#: * ``"client.started"``            — start() completed.  ``tags={}``.
#: * ``"client.closed"``             — close() completed.  ``tags={}``.
#: * ``"cm.connected"``              — CM socket up.  ``tags={}``.
#: * ``"cm.disconnected"``           — CM socket dropped.
#:   ``tags={"intentional": bool}`` — ``True`` when we called
#:   ``.disconnect()`` / ``.logout()`` / ``.close()`` ourselves.
#: * ``"reconnect.started"``         — auto-reconnect loop began.
#: * ``"reconnect.succeeded"``       — reconnect + relogin worked.
#:   ``tags={"attempts": int}``.
#: * ``"reconnect.failed"``          — gave up.
#:   ``tags={"attempts": int}``.
#: * ``"rpc.started"``               — a blocking RPC began.
#:   ``tags={"method": str}``.
#: * ``"rpc.succeeded"``             — RPC returned.
#:   ``tags={"method": str, "duration_ms": float}``.
#: * ``"rpc.failed"``                — RPC raised.
#:   ``tags={"method": str, "duration_ms": float, "error": str}``.
#:
#: Hook implementations MUST NOT raise — the client catches and
#: logs, but a raising hook still costs latency on the hot path.
#: Hooks MUST be non-blocking (no network / disk / long CPU);
#: they run inline in the coroutine that logs them, so a slow
#: hook slows every request.
MetricsHook = Callable[[str, "dict[str, Any]"], None]


def _noop_hook(event: str, tags: dict[str, Any]) -> None:  # noqa: ARG001
    """Default hook — does nothing.  Named so it's visible in
    ``client._metrics_hook`` when debugging (``<function _noop_hook>``
    beats ``<lambda>``)."""
    return None


def _invoke_hook(hook: MetricsHook, event: str, tags: dict[str, Any]) -> None:
    """Call ``hook(event, tags)`` and swallow any exception — a
    broken metrics implementation must never take down the RPC
    path.  Errors are logged at debug level (higher would flood
    logs on a persistently-broken hook).
    """
    if hook is _noop_hook:
        return
    try:
        hook(event, tags)
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).debug(
            "metrics hook raised for event %r",
            event,
            exc_info=True,
        )


# ---------------------------------------------------------------------
# Reconnect state constants — kept as strings so status dicts
# serialise cleanly for JSON APIs / MCP tools without needing
# custom encoders.
# ---------------------------------------------------------------------

RECONNECT_IDLE = "idle"
RECONNECT_RECONNECTING = "reconnecting"
RECONNECT_FAILED = "failed"


__all__ = [
    "ClientStatus",
    "MetricsHook",
    "RECONNECT_IDLE",
    "RECONNECT_RECONNECTING",
    "RECONNECT_FAILED",
]


# ---------------------------------------------------------------------
# Convenience: a Prometheus-compatible hook factory.  Users who
# want Prometheus can call ``prometheus_hook(...)`` to get a
# ready-made hook — no library-side import of ``prometheus_client``
# unless the user actually uses it.
# ---------------------------------------------------------------------


def prometheus_hook(
    *,
    namespace: str = "pysteam",
    subsystem: str = "aio",
    registry: Any | None = None,
) -> MetricsHook:
    """Return a :data:`MetricsHook` backed by ``prometheus_client``
    counters + histograms.  Import happens inside this function so
    the base package stays free of the dep.

    Registers (once per (namespace, subsystem, registry) triple):

    * ``pysteam_aio_rpc_total{method, outcome}`` — counter
    * ``pysteam_aio_rpc_duration_seconds{method, outcome}`` — histogram
    * ``pysteam_aio_connect_events_total{event}`` — counter
    * ``pysteam_aio_reconnect_attempts`` — gauge (last attempt count)

    ``outcome`` is ``"success"`` for ``rpc.succeeded`` and the
    ``error`` tag value for ``rpc.failed``.
    """
    # Lazy — don't drag ``prometheus_client`` into the module graph
    # for users who don't want it.
    try:
        from prometheus_client import Counter, Gauge, Histogram
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "prometheus_hook requires ``prometheus_client``; "
            "install it or wire your own MetricsHook",
        ) from e

    kw: dict[str, Any] = {"namespace": namespace, "subsystem": subsystem}
    if registry is not None:
        kw["registry"] = registry

    rpc_total = Counter(
        "rpc_total",
        "pysteam.aio RPC calls",
        ["method", "outcome"],
        **kw,
    )
    rpc_duration = Histogram(
        "rpc_duration_seconds",
        "pysteam.aio RPC latency",
        ["method", "outcome"],
        **kw,
    )
    connect_events = Counter(
        "connect_events_total",
        "pysteam.aio CM connection events",
        ["event"],
        **kw,
    )
    reconnect_gauge = Gauge(
        "reconnect_attempts",
        "pysteam.aio reconnect attempts (last)",
        **kw,
    )

    def _hook(event: str, tags: dict[str, Any]) -> None:
        if event == "rpc.succeeded":
            method = tags.get("method", "unknown")
            duration = float(tags.get("duration_ms", 0)) / 1000.0
            rpc_total.labels(method=method, outcome="success").inc()
            rpc_duration.labels(method=method, outcome="success").observe(duration)
        elif event == "rpc.failed":
            method = tags.get("method", "unknown")
            duration = float(tags.get("duration_ms", 0)) / 1000.0
            outcome = str(tags.get("error", "error"))
            rpc_total.labels(method=method, outcome=outcome).inc()
            rpc_duration.labels(method=method, outcome=outcome).observe(duration)
        elif event in {"cm.connected", "cm.disconnected"}:
            connect_events.labels(event=event.split(".", 1)[1]).inc()
        elif event in {"reconnect.succeeded", "reconnect.failed"}:
            reconnect_gauge.set(int(tags.get("attempts", 0)))
            connect_events.labels(event=event.split(".", 1)[1]).inc()

    return _hook

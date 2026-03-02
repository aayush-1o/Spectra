"""
Spectra — Request Timing Middleware
Phase 5 observability: measures every request's wall-clock time, logs slow
requests (>200ms), adds X-Response-Time-Ms header, and maintains a rolling
window of the last 1000 request times for the /admin/metrics endpoint.

Design:
  - Uses collections.deque(maxlen=1000) for O(1) append and automatic eviction.
  - Thread-safe enough for asyncio — asyncio uses a single event loop thread,
    so concurrent coroutines don't race on the deque.
  - get_avg_request_time_ms() is a module-level function so admin.py can import
    it without creating a circular import through the middleware class.
"""

import logging
import time
from collections import deque
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ── Rolling window of request durations (ms), max 1000 entries ───────────────
_request_times: deque[float] = deque(maxlen=1000)

# Threshold above which a request is logged as slow
SLOW_REQUEST_THRESHOLD_MS: float = 200.0


def get_avg_request_time_ms() -> float:
    """
    Return the mean request time (ms) over the current rolling window.
    Returns 0.0 if no requests have been handled yet.
    """
    if not _request_times:
        return 0.0
    return round(sum(_request_times) / len(_request_times), 2)


def get_request_time_samples() -> int:
    """Return the number of samples in the current rolling window."""
    return len(_request_times)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that:
      1. Records wall-clock time for every request.
      2. Appends elapsed_ms to the module-level deque.
      3. Logs WARNING for requests that exceed SLOW_REQUEST_THRESHOLD_MS.
      4. Injects X-Response-Time-Ms header into the response.

    Mounted AFTER EthicsGuardMiddleware so its timing includes the guard but not
    CORS preflight overhead (CORS is an outer layer).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        t0 = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # Still record time and re-raise so FastAPI handles the 500
            elapsed_ms = (time.perf_counter() - t0) * 1000
            _request_times.append(elapsed_ms)
            raise

        elapsed_ms = (time.perf_counter() - t0) * 1000
        _request_times.append(elapsed_ms)

        if elapsed_ms > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                "SLOW REQUEST  method=%s  path=%s  duration=%.0fms",
                request.method,
                request.url.path,
                elapsed_ms,
            )

        # Attach timing header so frontend and load-balancers can observe it
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
        return response

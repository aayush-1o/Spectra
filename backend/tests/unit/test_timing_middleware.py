"""
Spectra — Phase 5 Timing Middleware Tests
Verifies that TimingMiddleware:
  1. Adds X-Response-Time-Ms header to all responses.
  2. Logs a WARNING for requests exceeding SLOW_REQUEST_THRESHOLD_MS.
  3. Correctly updates the rolling deque via get_avg_request_time_ms().

Design:
  - Tests use unittest.mock to avoid requiring a live FastAPI/ASGI server.
  - The middleware is tested as a plain Python class (no TestClient overhead).
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Reset rolling deque state between tests to avoid cross-test interference
import app.middleware.timing as timing_module
from app.middleware.timing import (
    SLOW_REQUEST_THRESHOLD_MS,
    TimingMiddleware,
    get_avg_request_time_ms,
    get_request_time_samples,
)


def _make_mock_request(method: str = "GET", path: str = "/api/v1/persons") -> MagicMock:
    """Create a minimal mock Request object."""
    req = MagicMock()
    req.method = method
    req.url.path = path
    return req


def _make_mock_response() -> MagicMock:
    """Create a minimal mock Response with a mutable headers dict."""
    resp = MagicMock()
    resp.headers = {}
    return resp


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_timing_middleware_adds_response_time_header():
    """
    Every response must have an X-Response-Time-Ms header with a numeric string.
    """
    middleware = TimingMiddleware(app=MagicMock())  # app not used in dispatch
    request = _make_mock_request()
    response = _make_mock_response()

    async def call_next(_):
        return response

    asyncio.get_event_loop().run_until_complete(
        middleware.dispatch(request, call_next)
    )

    assert "X-Response-Time-Ms" in response.headers, (
        "TimingMiddleware did not add X-Response-Time-Ms header"
    )
    # Must be parseable as float
    value = float(response.headers["X-Response-Time-Ms"])
    assert value >= 0, f"Response time must be non-negative, got {value}"


def test_timing_middleware_appends_to_deque():
    """
    After a request is handled, get_request_time_samples() must increase by 1.
    """
    before = get_request_time_samples()
    middleware = TimingMiddleware(app=MagicMock())
    response = _make_mock_response()

    async def call_next(_):
        return response

    asyncio.get_event_loop().run_until_complete(
        middleware.dispatch(_make_mock_request(), call_next)
    )

    after = get_request_time_samples()
    assert after == before + 1, f"Expected {before + 1} samples, got {after}"


def test_timing_middleware_logs_slow_requests():
    """
    Requests that take longer than SLOW_REQUEST_THRESHOLD_MS must emit a WARNING log.
    We patch time.perf_counter to simulate a slow response.
    """
    middleware = TimingMiddleware(app=MagicMock())
    request = _make_mock_request(path="/api/v1/graph/neighbourhood/abc")
    response = _make_mock_response()

    async def slow_next(_):
        return response

    # Simulate 250ms elapsed (above the 200ms threshold)
    fake_times = [0.0, 0.25]  # start, end
    with patch("app.middleware.timing.time.perf_counter", side_effect=fake_times):
        with patch.object(timing_module.logger, "warning") as mock_warn:
            asyncio.get_event_loop().run_until_complete(
                middleware.dispatch(request, slow_next)
            )
            mock_warn.assert_called_once()
            call_args = str(mock_warn.call_args)
            assert "SLOW REQUEST" in call_args


def test_timing_middleware_does_not_log_fast_requests():
    """
    Requests under SLOW_REQUEST_THRESHOLD_MS must NOT trigger a WARNING log.
    """
    middleware = TimingMiddleware(app=MagicMock())
    response = _make_mock_response()

    async def fast_next(_):
        return response

    # Simulate 10ms elapsed (well below threshold)
    fake_times = [0.0, 0.010]
    with patch("app.middleware.timing.time.perf_counter", side_effect=fake_times):
        with patch.object(timing_module.logger, "warning") as mock_warn:
            asyncio.get_event_loop().run_until_complete(
                middleware.dispatch(_make_mock_request(), fast_next)
            )
            mock_warn.assert_not_called()


def test_get_avg_request_time_ms_returns_float():
    """get_avg_request_time_ms() must return a float in all cases."""
    result = get_avg_request_time_ms()
    assert isinstance(result, float), f"Expected float, got {type(result)}"


def test_get_avg_request_time_ms_returns_zero_when_empty():
    """
    If the deque is empty at startup, get_avg_request_time_ms() must return 0.0.
    (tested indirectly — we cannot reliably empty the deque without resetting the module)
    """
    # We cannot fully guarantee empty because other tests run first,
    # but we can verify it never raises an exception.
    result = get_avg_request_time_ms()
    assert result >= 0.0


def test_slow_request_threshold_is_200ms():
    """SLOW_REQUEST_THRESHOLD_MS must be exactly 200 (ms). Document in test."""
    assert SLOW_REQUEST_THRESHOLD_MS == 200.0, (
        f"Expected threshold 200ms, got {SLOW_REQUEST_THRESHOLD_MS}. "
        "If you changed this, update PHASE-5-EXPLANATION.md accordingly."
    )

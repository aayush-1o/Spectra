"""
Spectra — Structured Logging Middleware
Phase 7: Emits one JSON log line per request with key observability fields.

In development: uses standard Python logging (human-readable).
In production:  emits JSON so Railway/Render/Datadog can parse structured fields.

Log fields per request:
  timestamp     ISO-8601 UTC
  method        HTTP method
  path          Request path (query string excluded for brevity)
  status_code   Response status
  duration_ms   Wall clock time (same source as TimingMiddleware)
  client_ip     X-Forwarded-For → fallback to direct client host
  environment   From settings
  error         Only present on 5xx — exception message
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger("spectra.access")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Access logging middleware.

    - Health / ready probes are logged at DEBUG level to avoid noise.
    - 5xx responses are logged at ERROR level so they surface in cloud dashboards.
    - All other responses are logged at INFO level.
    """

    QUIET_PATHS = {"/health", "/ready", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        t0 = time.perf_counter()
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        exc_detail: str | None = None
        try:
            response = await call_next(request)
        except Exception as exc:
            exc_detail = str(exc)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            self._emit(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=elapsed_ms,
                client_ip=client_ip,
                error=exc_detail,
            )
            raise

        elapsed_ms = (time.perf_counter() - t0) * 1000
        self._emit(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=elapsed_ms,
            client_ip=client_ip,
        )
        return response

    def _emit(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str,
        error: str | None = None,
    ) -> None:
        record: dict = {
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "method":      method,
            "path":        path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 1),
            "client_ip":   client_ip,
            "environment": settings.environment,
        }
        if error:
            record["error"] = error

        # Choose log level
        if status_code >= 500:
            level = logging.ERROR
        elif path in self.QUIET_PATHS:
            level = logging.DEBUG
        else:
            level = logging.INFO

        if settings.is_production:
            # Emit JSON line — parsed by Render/Railway log aggregators
            logger.log(level, json.dumps(record))
        else:
            # Human-readable for local dev
            logger.log(
                level,
                "%s %s → %d  (%.0fms)  ip=%s%s",
                method,
                path,
                status_code,
                duration_ms,
                client_ip,
                f"  error={error}" if error else "",
            )

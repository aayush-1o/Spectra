"""
Spectra — Structured Logging Middleware
Phase 7: Emits one JSON log line per request with key observability fields.

AUDIT FIX (Phase 7.1):
  - NEVER re-raise from dispatch() — this bypassed FastAPI's exception handler
    and caused uvicorn to return plain-text "Internal Server Error".
  - Instead, return a JSONResponse(500) so the client always gets JSON.
  - Log only type(exc).__name__ (not the full message) to avoid leaking
    internal SQL / file paths into production logs.

In development: uses standard Python logging (human-readable).
In production:  emits JSON so Railway/Render/Datadog can parse structured fields.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger("spectra.access")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Access logging middleware.

    - Health / ready probes are logged at DEBUG level to avoid noise.
    - 5xx responses are logged at ERROR level so they surface in cloud dashboards.
    - All other responses are logged at INFO level.
    - Exceptions are caught and returned as JSON 500 (never re-raised) so
      FastAPI's error handler chain is not bypassed.
    """

    QUIET_PATHS = {"/health", "/ready", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        t0 = time.perf_counter()
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            # ── AUDIT FIX: do NOT re-raise ────────────────────────────────────
            # Re-raising here bypasses FastAPI's exception handler and makes
            # uvicorn return plain-text "Internal Server Error" (text/plain).
            # We log the exception CLASS (not message) to avoid leaking SQL /
            # internal paths, then return a clean JSON 500.
            elapsed_ms = (time.perf_counter() - t0) * 1000
            exc_class = type(exc).__name__
            logger.exception(
                "Unhandled exception [%s] on %s %s",
                exc_class,
                request.method,
                request.url.path,
            )
            self._emit(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=elapsed_ms,
                client_ip=client_ip,
                error=exc_class,   # class only — NOT str(exc)
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )

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
            record["error"] = error   # exception class name, not message

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

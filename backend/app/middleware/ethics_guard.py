"""
Spectra — Ethics Guard Middleware
Blocks any POST/PUT request body that contains patterns matching real PII.

This is a FIRST-CLASS safety feature. Do NOT remove or disable.
⚠️ Spectra only accepts 100% synthetic (computer-generated) data.
"""

import json
import re
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ── Real PII patterns that must be rejected ────────────────────────────────────
_REAL_PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    # International phone numbers: +1, +44, +91, etc.
    ("real_phone_number", re.compile(r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{4}")),
    # US SSN: XXX-XX-XXXX
    ("real_ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    # Real email domains (free providers + common corporate)
    (
        "real_email_domain",
        re.compile(
            r"[a-zA-Z0-9._%+\-]+@(?:gmail|yahoo|outlook|hotmail|icloud|protonmail|"
            r"live|msn|aol|me|mac|googlemail)\.(?:com|co\.uk|in|net|org)",
            re.IGNORECASE,
        ),
    ),
    # Credit card numbers (basic 16-digit pattern)
    ("credit_card", re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b")),
    # Aadhaar (Indian national ID) — 12-digit number
    ("aadhaar", re.compile(r"\b[2-9]\d{3}[\s]?\d{4}[\s]?\d{4}\b")),
]

_REJECTION_MESSAGE = (
    "Real PII detected. Spectra only accepts synthetic data. "
    "This request has been blocked by the Spectra ethics guard."
)


class EthicsGuardMiddleware(BaseHTTPMiddleware):
    """
    Inspects POST and PUT request bodies for real PII patterns.
    Returns HTTP 400 with an explanation if any pattern is matched.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            body_bytes = await request.body()

            if body_bytes:
                try:
                    body_text = body_bytes.decode("utf-8", errors="replace")
                except Exception:
                    body_text = ""

                for pattern_name, pattern in _REAL_PII_PATTERNS:
                    if pattern.search(body_text):
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "ETHICS_VIOLATION",
                                "pattern_matched": pattern_name,
                                "message": _REJECTION_MESSAGE,
                            },
                        )

            # Re-attach body so downstream handlers can read it
            async def receive():
                return {"type": "http.request", "body": body_bytes}

            request._receive = receive

        return await call_next(request)

"""
Spectra — Ethics Guard Middleware
Blocks any POST/PUT/PATCH request body that contains patterns matching real PII.

This is a FIRST-CLASS safety feature. Do NOT remove or disable.
⚠️ Spectra only accepts 100% synthetic (computer-generated) data.

AUDIT FIXES (Phase 7.1):
  1. Body size cap: reject payloads > 1 MB before regex scan (anti-DoS).
  2. NFKC normalisation: collapses Unicode homoglyphs / full-width characters
     (e.g. ＋44 becomes +44) so bypass via non-ASCII lookalikes is impossible.
"""

import json
import re
import unicodedata
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ── Body size limit ────────────────────────────────────────────────────────────
# Spectra only processes synthetic data — real payloads are tiny JSON objects.
# Anything larger than 1 MB is rejected before pattern scanning (anti-DoS).
_MAX_BODY_BYTES = 1 * 1024 * 1024  # 1 MB

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
    Inspects POST, PUT, and PATCH request bodies for real PII patterns.
    Returns HTTP 400 with an explanation if any pattern is matched.
    Returns HTTP 413 if the body exceeds 1 MB.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in ("POST", "PUT", "PATCH"):
            body_bytes = await request.body()

            # ── 1. Reject oversized payloads (anti-DoS) ───────────────────────
            if len(body_bytes) > _MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "PAYLOAD_TOO_LARGE",
                        "message": (
                            "Request body exceeds 1 MB. "
                            "Spectra only accepts compact synthetic data payloads."
                        ),
                    },
                )

            if body_bytes:
                body_text = body_bytes.decode("utf-8", errors="replace")

                # ── 2. NFKC normalise to collapse Unicode homoglyphs ──────────
                # This prevents bypass via full-width chars like ＋44 → +44,
                # or full-width digits ０１２３ → 0123, etc.
                body_text = unicodedata.normalize("NFKC", body_text)

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

"""
Spectra — FastAPI Application Entry Point
Synthetic Intelligence & Movement Simulation for Analytics Training
⚠️ ALL DATA IS FAKE. No real people. No real surveillance. Educational only.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.ethics_guard import EthicsGuardMiddleware
from app.api.v1 import auth

app = FastAPI(
    title="Spectra API",
    description=(
        "⚠️ SYNTHETIC DATA ONLY — Spectra is an educational data analytics simulation. "
        "All data is computer-generated. No real people are tracked."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware (order matters: outermost wraps first) ──────────────────────────
app.add_middleware(EthicsGuardMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return service liveness status."""
    return {"status": "ok", "project": "Spectra"}

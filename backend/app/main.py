"""
Spectra — FastAPI Application Entry Point
Synthetic Intelligence & Movement Simulation for Analytics Training
⚠️ ALL DATA IS FAKE. No real people. No real surveillance. Educational only.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.ethics_guard import EthicsGuardMiddleware
from app.api.v1 import auth
from app.api.v1 import persons, locations, events
from app.api.v1 import graph as graph_router
from app.api.v1 import anomalies as anomalies_router
from app.db.neo4j import close_neo4j_driver


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown hooks."""
    yield
    # Gracefully close Neo4j driver on shutdown
    await close_neo4j_driver()


app = FastAPI(
    title="Spectra API",
    description=(
        "⚠️ SYNTHETIC DATA ONLY — Spectra is an educational data analytics simulation. "
        "All data is computer-generated. No real people are tracked."
    ),
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(graph_router.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(anomalies_router.router, prefix="/api/v1/anomalies", tags=["anomalies"])


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return service liveness status."""
    return {"status": "ok", "project": "Spectra", "phase": 3}

"""
Spectra — FastAPI Application Entry Point
Synthetic Intelligence & Movement Simulation for Analytics Training
⚠️ ALL DATA IS FAKE. No real people. No real surveillance. Educational only.

Phase 5 changes:
  - TimingMiddleware added (request duration logging + X-Response-Time-Ms header)
  - Neo4j startup indexes ensured in lifespan()
  - Redis pool opened/closed in lifespan()
  - Admin router registered at /api/v1/admin
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.ethics_guard import EthicsGuardMiddleware
from app.middleware.timing import TimingMiddleware
from app.api.v1 import auth
from app.api.v1 import persons, locations, events
from app.api.v1 import graph as graph_router
from app.api.v1 import anomalies as anomalies_router
from app.api.v1 import admin as admin_router
from app.db.neo4j import close_neo4j_driver, ensure_neo4j_indexes, get_neo4j_driver
from app.db.redis import close_redis_pool, get_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown hooks."""
    # ── Startup ────────────────────────────────────────────────────────────────
    # Warm up the Redis connection pool (first access creates it)
    get_redis_pool()

    # Create Neo4j indexes (non-fatal if Neo4j is temporarily unavailable)
    neo4j_driver = get_neo4j_driver()
    await ensure_neo4j_indexes(neo4j_driver)

    yield

    # ── Shutdown ───────────────────────────────────────────────────────────────
    await close_neo4j_driver()
    await close_redis_pool()


app = FastAPI(
    title="Spectra API",
    description=(
        "⚠️ SYNTHETIC DATA ONLY — Spectra is an educational data analytics simulation. "
        "All data is computer-generated. No real people are tracked."
    ),
    version="0.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware (order matters: outermost wraps innermost) ──────────────────────
# CORSMiddleware is outermost so preflight OPTIONS requests bypass all other middleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TimingMiddleware sits inside CORS so it only times actual API calls.
app.add_middleware(TimingMiddleware)

# EthicsGuard is innermost — it reads the request body before any handler.
app.add_middleware(EthicsGuardMiddleware)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(graph_router.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(anomalies_router.router, prefix="/api/v1/anomalies", tags=["anomalies"])
app.include_router(admin_router.router, prefix="/api/v1/admin", tags=["admin"])


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Return service liveness status."""
    return {"status": "ok", "project": "Spectra", "phase": 5}

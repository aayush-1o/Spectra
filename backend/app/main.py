"""
Spectra — FastAPI Application Entry Point
Synthetic Intelligence & Movement Simulation for Analytics Training
⚠️ ALL DATA IS FAKE. No real people. No real surveillance. Educational only.

Phase 5: TimingMiddleware, Redis pool lifecycle, Neo4j indexes, admin router
Phase 7: Deep /health + /ready endpoints, structured logging, docs disabled in prod,
         production config validation on startup.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.db.postgres import AsyncSessionLocal
from app.db.neo4j import close_neo4j_driver, ensure_neo4j_indexes, get_neo4j_driver
from app.db.redis import close_redis_pool, get_redis_pool
from app.middleware.ethics_guard import EthicsGuardMiddleware
from app.middleware.logging import StructuredLoggingMiddleware
from app.middleware.timing import TimingMiddleware
from app.api.v1 import auth, persons, locations, events
from app.api.v1 import graph as graph_router
from app.api.v1 import anomalies as anomalies_router
from app.api.v1 import admin as admin_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown hooks."""
    # ── Startup ────────────────────────────────────────────────────────────────
    # Phase 7: validate production config before anything else starts
    settings.validate_production()

    # Warm up the Redis connection pool (first access creates it)
    get_redis_pool()

    # Create Neo4j indexes (non-fatal if Neo4j is temporarily unavailable)
    neo4j_driver = get_neo4j_driver()
    await ensure_neo4j_indexes(neo4j_driver)

    logger.info(
        "Spectra started  env=%s  docs=%s  log_level=%s",
        settings.environment,
        settings.allow_docs,
        settings.log_level,
    )

    yield

    # ── Shutdown ───────────────────────────────────────────────────────────────
    await close_neo4j_driver()
    await close_redis_pool()


# ── OpenAPI docs: disabled in production ─────────────────────────────────────
_docs_url = "/docs" if settings.allow_docs else None
_redoc_url = "/redoc" if settings.allow_docs else None

app = FastAPI(
    title="Spectra API",
    description=(
        "⚠️ SYNTHETIC DATA ONLY — Spectra is an educational data analytics simulation. "
        "All data is computer-generated. No real people are tracked."
    ),
    version="0.7.0",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    lifespan=lifespan,
)

# ── Middleware (order matters: outermost wraps innermost) ──────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 7: structured JSON access logging in all environments
app.add_middleware(StructuredLoggingMiddleware)

# TimingMiddleware: slow request log + X-Response-Time-Ms header
app.add_middleware(TimingMiddleware)

# EthicsGuard is innermost — reads request body before any handler
app.add_middleware(EthicsGuardMiddleware)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router,            prefix="/api/v1/auth",      tags=["auth"])
app.include_router(persons.router,         prefix="/api/v1/persons",   tags=["persons"])
app.include_router(locations.router,       prefix="/api/v1/locations", tags=["locations"])
app.include_router(events.router,          prefix="/api/v1/events",    tags=["events"])
app.include_router(graph_router.router,    prefix="/api/v1/graph",     tags=["graph"])
app.include_router(anomalies_router.router,prefix="/api/v1/anomalies", tags=["anomalies"])
app.include_router(admin_router.router,    prefix="/api/v1/admin",     tags=["admin"])


# ── Health Endpoints ───────────────────────────────────────────────────────────

async def _check_postgres() -> dict[str, Any]:
    """Ping PostgreSQL with a trivial query."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


async def _check_redis() -> dict[str, Any]:
    """Ping Redis via the shared pool."""
    try:
        pool = get_redis_pool()
        client = aioredis.Redis(connection_pool=pool)
        await client.ping()
        await client.aclose()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


async def _check_neo4j() -> dict[str, Any]:
    """Ping Neo4j with a lightweight Cypher query."""
    try:
        driver = get_neo4j_driver()
        async with driver.session(database="neo4j") as session:
            await session.run("RETURN 1")
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@app.get("/health", tags=["health"])
async def health_check() -> JSONResponse:
    """
    Deep liveness probe — checks all three backing services.
    Returns 200 even if a dependency is degraded (liveness vs readiness).
    Render / Fly.io use this for container restart decisions.
    """
    checks = {
        "postgres": await _check_postgres(),
        "redis":    await _check_redis(),
        "neo4j":    await _check_neo4j(),
    }
    overall = "ok" if all(c["status"] == "ok" for c in checks.values()) else "degraded"
    return JSONResponse(content={
        "status":      overall,
        "project":     "Spectra",
        "version":     "0.7.0",
        "environment": settings.environment,
        "phase":       7,
        "services":    checks,
    })


@app.get("/ready", tags=["health"])
async def readiness_check() -> JSONResponse:
    """
    Readiness probe — returns 503 if ANY dependency is unreachable.
    Kubernetes / load-balancers use this to stop routing traffic to the pod.
    Render doesn't use this natively but it's useful for smoke-testing deploys.
    """
    checks = {
        "postgres": await _check_postgres(),
        "redis":    await _check_redis(),
        "neo4j":    await _check_neo4j(),
    }
    all_ok = all(c["status"] == "ok" for c in checks.values())
    code   = http_status.HTTP_200_OK if all_ok else http_status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=code,
        content={
            "ready":    all_ok,
            "services": checks,
        },
    )

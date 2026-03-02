"""
Spectra — Admin API (v1)
Phase 5: GET /api/v1/admin/metrics — system health + performance snapshot.

⚠️ All data is synthetic. No real persons tracked.

Metrics include:
  - total_persons          COUNT(*) from persons table
  - total_events           COUNT(*) from events table
  - total_anomalies        COUNT(*) from anomaly_records table
  - total_graph_nodes      COUNT from Neo4j (timeout-guarded)
  - cache_hits             redis hits since startup
  - cache_misses           redis misses since startup
  - cache_hit_rate         hits / (hits + misses)
  - cache_status           "available" | "unavailable"
  - avg_request_time_ms    rolling mean over last 1000 requests
  - slow_request_threshold_ms  200 ms (constant)
  - request_samples        number of timing samples in rolling window
"""

import json
import logging

import neo4j
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.db.neo4j import get_neo4j_session
from app.db.redis import CacheHelper, get_redis
from app.middleware.timing import SLOW_REQUEST_THRESHOLD_MS, get_avg_request_time_ms, get_request_time_samples
from app.models.anomaly import AnomalyRecord
from app.models.event import Event
from app.models.person import Person
from app.models.user import User
from app.services.anomaly_service import get_anomaly_count

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)
router = APIRouter()

_KPI_CACHE_KEY = "dashboard:kpis"
_KPI_TTL_SECONDS = 60


class MetricsResponse(BaseModel):
    """Structured response for GET /api/v1/admin/metrics."""
    total_persons: int
    total_events: int
    total_anomalies: int
    total_graph_nodes: int  # -1 = Neo4j unavailable
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    cache_status: str  # "available" | "unavailable"
    avg_request_time_ms: float
    slow_request_threshold_ms: float
    request_samples: int


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    redis_client: aioredis.Redis = Depends(get_redis),
    _current_user: User = Depends(get_current_user),
) -> MetricsResponse:
    """
    Return a snapshot of system performance metrics.

    KPI counts (persons, events, anomalies) are cached in Redis for 60s
    to keep this endpoint fast on repeated dashboard polls.
    """
    # ── Try KPI cache first ───────────────────────────────────────────────────
    cached = await CacheHelper.get(redis_client, _KPI_CACHE_KEY)
    if cached:
        kpis = json.loads(cached)
        total_persons = kpis["total_persons"]
        total_events = kpis["total_events"]
        total_anomalies = kpis["total_anomalies"]
    else:
        # Run 3 COUNT(*) queries concurrently via individual awaits
        # (asyncpg executes them on the same connection sequentially; true
        # concurrency would need multiple sessions — overkill here)
        persons_res = await db.execute(select(func.count()).select_from(Person))
        total_persons = persons_res.scalar_one()

        events_res = await db.execute(select(func.count()).select_from(Event))
        total_events = events_res.scalar_one()

        total_anomalies = await get_anomaly_count(db)

        # Cache KPI bundle
        await CacheHelper.set(
            redis_client,
            _KPI_CACHE_KEY,
            json.dumps({
                "total_persons": total_persons,
                "total_events": total_events,
                "total_anomalies": total_anomalies,
            }),
            _KPI_TTL_SECONDS,
        )

    # ── Neo4j node count (timeout-guarded) ────────────────────────────────────
    total_graph_nodes = -1
    try:
        result = await neo4j_session.run("MATCH (n) RETURN count(n) AS cnt")
        record = await result.single()
        if record:
            total_graph_nodes = record["cnt"]
    except Exception as exc:
        logger.warning("Could not query Neo4j node count: %s", exc)

    # ── Redis availability probe ───────────────────────────────────────────────
    cache_status = "unavailable"
    try:
        await redis_client.ping()
        cache_status = "available"
    except Exception:
        pass

    cache_stats = CacheHelper.stats()

    return MetricsResponse(
        total_persons=total_persons,
        total_events=total_events,
        total_anomalies=total_anomalies,
        total_graph_nodes=total_graph_nodes,
        cache_hits=cache_stats["hits"],
        cache_misses=cache_stats["misses"],
        cache_hit_rate=cache_stats["hit_rate"],
        cache_status=cache_status,
        avg_request_time_ms=get_avg_request_time_ms(),
        slow_request_threshold_ms=SLOW_REQUEST_THRESHOLD_MS,
        request_samples=get_request_time_samples(),
    )

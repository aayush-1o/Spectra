"""
Spectra — Graph API (v1)
Neighbourhood, centrality, shortest-path, and community detection endpoints.

Phase 5 optimisations:
  - Neighbourhood results cached in Redis (key: graph:neighbourhood:{id}:{hops}, TTL 120s).
  - CacheHelper is used for all Redis I/O — Redis failure degrades gracefully.

Phase 8:
  - GET /api/v1/graph/communities — Louvain community detection on Neo4j graph.
"""

import json
import logging

import neo4j
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_current_user
from app.db.neo4j import get_neo4j_session
from app.db.redis import CacheHelper, get_redis
from app.models.user import User
from app.schemas.graph import CentralityEntry, NeighbourhoodResponse, PathResponse
from app.services.community_service import detect_communities
from app.services.graph_service import GraphService

logger = logging.getLogger(__name__)
router = APIRouter()

_NEIGHBOURHOOD_TTL = 120  # seconds


def _neighbourhood_cache_key(person_id: str, hops: int) -> str:
    return f"graph:neighbourhood:{person_id}:{hops}"


@router.get("/neighbourhood/{person_id}", response_model=NeighbourhoodResponse)
async def get_neighbourhood(
    person_id: str,
    hops: int = Query(default=2, ge=1, le=5, description="Number of hops from the seed person"),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    redis_client: aioredis.Redis = Depends(get_redis),
    _current_user: User = Depends(get_current_user),
) -> NeighbourhoodResponse:
    """
    Return all nodes and edges within N hops of a given person.

    Cache: Redis key graph:neighbourhood:{person_id}:{hops}, TTL 120s.
    On cache hit the Neo4j query is skipped entirely. Requires Bearer JWT.
    """
    cache_key = _neighbourhood_cache_key(person_id, hops)

    # ── Cache hit path ────────────────────────────────────────────────────────
    cached = await CacheHelper.get(redis_client, cache_key)
    if cached:
        logger.debug("Graph cache HIT  key=%s", cache_key)
        data = json.loads(cached)
        return NeighbourhoodResponse(nodes=data["nodes"], edges=data["edges"])

    # ── Cache miss — query Neo4j ──────────────────────────────────────────────
    logger.debug("Graph cache MISS  key=%s", cache_key)
    svc = GraphService(neo4j_session)
    result = await svc.get_neighbourhood(person_id, hops)

    # Cache serialised result (both nodes and edges lists are JSON-safe)
    await CacheHelper.set(redis_client, cache_key, json.dumps(result), _NEIGHBOURHOOD_TTL)

    return NeighbourhoodResponse(nodes=result["nodes"], edges=result["edges"])


@router.get("/centrality", response_model=list[CentralityEntry])
async def get_centrality(
    top_n: int = Query(default=20, ge=1, le=100),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    _current_user: User = Depends(get_current_user),
) -> list[CentralityEntry]:
    """Return top-N persons ranked by degree centrality. Requires Bearer JWT."""
    svc = GraphService(neo4j_session)
    return await svc.get_centrality(top_n)


@router.get("/shortest-path", response_model=PathResponse)
async def get_shortest_path(
    from_id: str = Query(..., description="Source person ID"),
    to_id: str = Query(..., description="Target person ID"),
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    _current_user: User = Depends(get_current_user),
) -> PathResponse:
    """Find the shortest path between two persons. Requires Bearer JWT."""
    if from_id == to_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_id and to_id must be different persons.",
        )
    svc = GraphService(neo4j_session)
    path = await svc.get_shortest_path(from_id, to_id)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No path found between the two persons.",
        )
    return PathResponse(path=path)


@router.get("/communities")
async def get_communities(
    neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session),
    redis_client: aioredis.Redis = Depends(get_redis),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """
    Run Louvain community detection on the synthetic person interaction graph.
    Results are cached in Redis for 600 seconds.

    Returns:
        {
            "communities": {"person_id": community_id, ...},
            "community_count": int
        }
    Requires Bearer JWT.
    """
    return await detect_communities(neo4j_session, redis_client)

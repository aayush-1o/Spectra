"""
Spectra — Shared Redis Connection Pool
Phase 5 optimisation: replaces per-request throw-away clients with a shared pool.

Design decisions:
  - Module-level ConnectionPool created once, re-used across all requests.
  - CacheHelper wraps every call in try/except: a Redis outage degrades gracefully
    (returns None / skips set) without surfacing a 500 error to the client.
  - Cache hit/miss counts are tracked in-memory for the metrics endpoint.
  - Pool is closed via close_redis_pool() in main.py lifespan shutdown.

Redis Key Structure (Phase 5):
  ┌──────────────────────────────────────────────────┬───────┬──────────────────────────────────────────────┐
  │ Key pattern                                      │ TTL   │ Purpose                                      │
  ├──────────────────────────────────────────────────┼───────┼──────────────────────────────────────────────┤
  │ anomaly:last_run                                 │ 300s  │ Anomaly run summary (flagged count, ms)      │
  │ graph:neighbourhood:{person_id}:{hops}           │ 120s  │ Serialised NeighbourhoodResponse JSON        │
  │ dashboard:kpis                                   │  60s  │ Total persons / events / anomalies counts    │
  └──────────────────────────────────────────────────┴───────┴──────────────────────────────────────────────┘

Cache Invalidation Strategy:
  - All keys use short TTLs (60–300s) and expire naturally.
  - No explicit invalidation is needed for this workload because synthetic data
    changes only on explicit generate/reset admin calls — those calls should clear
    the relevant keys via CacheHelper.delete() (no-op if Redis is unavailable).
  - If you add write paths in the future, call CacheHelper.delete() after commits.
"""

import logging
from collections import deque
from typing import AsyncGenerator

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)

# ── Connection pool — constructed once at first access ────────────────────────
_pool: ConnectionPool | None = None

# ── In-memory hit/miss counters for the metrics endpoint ─────────────────────
_cache_hits: int = 0
_cache_misses: int = 0


def get_redis_pool() -> ConnectionPool:
    """Return (and lazily create) the shared Redis connection pool."""
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


async def close_redis_pool() -> None:
    """Disconnect the pool cleanly on application shutdown."""
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
        logger.info("Redis pool closed.")


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """
    FastAPI dependency — yields a Redis client backed by the shared pool.
    Usage:
        redis_client: aioredis.Redis = Depends(get_redis)
    """
    client = aioredis.Redis(connection_pool=get_redis_pool())
    try:
        yield client
    finally:
        await client.aclose()


class CacheHelper:
    """
    Thin wrapper around Redis calls that:
      1. Tracks hit/miss stats for the metrics endpoint.
      2. Swallows RedisError so cache failures degrade gracefully.
    All methods are static and accept the FastAPI-injected Redis client.
    """

    @staticmethod
    async def get(client: aioredis.Redis, key: str) -> str | None:
        """
        Get a cached string value.
        Returns None on cache miss OR when Redis is unavailable.
        """
        global _cache_hits, _cache_misses
        try:
            value = await client.get(key)
            if value is not None:
                _cache_hits += 1
                return value
            _cache_misses += 1
            return None
        except RedisError as exc:
            logger.debug("Redis GET failed for key=%s: %s", key, exc)
            _cache_misses += 1
            return None

    @staticmethod
    async def set(
        client: aioredis.Redis,
        key: str,
        value: str,
        ttl: int,
    ) -> None:
        """Set a key with TTL (seconds). No-op on RedisError."""
        try:
            await client.set(key, value, ex=ttl)
        except RedisError as exc:
            logger.debug("Redis SET failed for key=%s: %s", key, exc)

    @staticmethod
    async def delete(client: aioredis.Redis, *keys: str) -> None:
        """Delete one or more keys. No-op on RedisError."""
        try:
            if keys:
                await client.delete(*keys)
        except RedisError as exc:
            logger.debug("Redis DELETE failed for keys=%s: %s", keys, exc)

    @staticmethod
    def hit_rate() -> float:
        """Return cache hit rate in the range [0.0, 1.0]. Returns 0.0 if no requests yet."""
        total = _cache_hits + _cache_misses
        if total == 0:
            return 0.0
        return round(_cache_hits / total, 4)

    @staticmethod
    def stats() -> dict:
        """Return raw hit/miss counters and hit rate."""
        return {
            "hits": _cache_hits,
            "misses": _cache_misses,
            "hit_rate": CacheHelper.hit_rate(),
        }

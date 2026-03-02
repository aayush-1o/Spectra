"""
Spectra — Phase 5 Redis Fallback Tests
Verifies that CacheHelper degrades gracefully when Redis is unavailable.

Design:
  - Uses unittest.mock to simulate RedisError without requiring a live Redis.
  - All tests are synchronous (asyncio.get_event_loop().run_until_complete).
  - These tests guard against regressions where a Redis outage causes 500s.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import RedisError

from app.db.redis import CacheHelper


# ── CacheHelper graceful degradation ──────────────────────────────────────────

def test_cache_helper_get_returns_none_on_redis_error():
    """
    CacheHelper.get must return None when Redis raises RedisError,
    rather than propagating the exception to the caller.
    """
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=RedisError("connection refused"))

    result = asyncio.get_event_loop().run_until_complete(
        CacheHelper.get(mock_client, "some:key")
    )

    assert result is None, "Expected None on Redis error, got something else"


def test_cache_helper_set_is_noop_on_redis_error():
    """
    CacheHelper.set must silently swallow RedisError.
    The calling code must not need to handle exceptions from this method.
    """
    mock_client = AsyncMock()
    mock_client.set = AsyncMock(side_effect=RedisError("write failed"))

    # Must not raise
    asyncio.get_event_loop().run_until_complete(
        CacheHelper.set(mock_client, "some:key", "value", ttl=60)
    )


def test_cache_helper_delete_is_noop_on_redis_error():
    """
    CacheHelper.delete must silently swallow RedisError.
    """
    mock_client = AsyncMock()
    mock_client.delete = AsyncMock(side_effect=RedisError("delete failed"))

    asyncio.get_event_loop().run_until_complete(
        CacheHelper.delete(mock_client, "key1", "key2")
    )


def test_cache_helper_get_increments_hit_counter():
    """
    A successful cache GET should increment the hit counter,
    which drives the hit_rate metric.
    """
    import app.db.redis as redis_module

    initial_hits = redis_module._cache_hits
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value="cached_value")

    result = asyncio.get_event_loop().run_until_complete(
        CacheHelper.get(mock_client, "hit:key")
    )

    assert result == "cached_value"
    assert redis_module._cache_hits > initial_hits


def test_cache_helper_get_increments_miss_counter_on_none():
    """
    A cache miss (Redis returns None) should increment the miss counter.
    """
    import app.db.redis as redis_module

    initial_misses = redis_module._cache_misses
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=None)

    result = asyncio.get_event_loop().run_until_complete(
        CacheHelper.get(mock_client, "miss:key")
    )

    assert result is None
    assert redis_module._cache_misses > initial_misses


def test_cache_helper_hit_rate_is_between_0_and_1():
    """hit_rate() must always return a value in [0.0, 1.0]."""
    rate = CacheHelper.hit_rate()
    assert 0.0 <= rate <= 1.0, f"hit_rate() returned {rate} which is out of [0, 1]"


def test_cache_helper_stats_has_expected_keys():
    """stats() must return a dict with hits, misses, and hit_rate."""
    stats = CacheHelper.stats()
    assert "hits" in stats
    assert "misses" in stats
    assert "hit_rate" in stats
    assert isinstance(stats["hits"], int)
    assert isinstance(stats["misses"], int)
    assert isinstance(stats["hit_rate"], float)

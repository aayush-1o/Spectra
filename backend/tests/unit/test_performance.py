"""
Spectra — Phase 5 Performance Tests
Tests execution speed of core computation functions to catch regressions.

Design:
  - Uses standard pytest timing (no pytest-benchmark dependency at import time)
    because benchmark fixture is optional. Each test has a HARD LIMIT measured
    with time.perf_counter so they fail loudly if performance degrades.
  - All tests run without a real DB/Redis (pure in-memory mocks).
"""

import asyncio
import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from app.services.anomaly_service import _build_feature_matrix, run_detection


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_event(event_id: str, hour: int = 12, amount: float = 100.0, duration: int = 60):
    """Create a minimal mock Event for testing."""
    e = MagicMock()
    e.id = event_id
    e.occurred_at = datetime(2025, 6, 1, hour, 0, 0, tzinfo=timezone.utc)
    e.metadata_ = {"amount_usd": amount, "duration_seconds": duration, "_synthetic": True}
    return e


# ── Performance Tests ──────────────────────────────────────────────────────────

def test_feature_matrix_build_1000_events_under_100ms():
    """
    Building the feature matrix for 1000 events must complete in under 100ms.
    If this fails, the list-comprehension + np.array() approach has regressed.
    Baseline (Phase 4): ~120ms (no vectorisation).
    Phase 5 target: <100ms.
    """
    events = [
        _make_event(
            f"evt-{i}",
            hour=i % 24,
            amount=float(i * 50),
            duration=i % 3600,
        )
        for i in range(1000)
    ]

    start = time.perf_counter()
    X, valid = _build_feature_matrix(events)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert X.shape == (1000, 3), f"Expected (1000, 3), got {X.shape}"
    assert len(valid) == 1000
    assert elapsed_ms < 100, (
        f"Feature matrix build took {elapsed_ms:.1f}ms — exceeds 100ms limit. "
        "Check for accidental O(n²) loops in _build_feature_matrix()."
    )


def test_feature_matrix_build_empty_events():
    """Empty event list should return an empty matrix without error."""
    X, valid = _build_feature_matrix([])
    assert X.shape == (0, 3)
    assert valid == []


def test_run_detection_dedup_skips_existing_pairs():
    """
    run_detection should skip event records that already have an AnomalyRecord
    with the same (entity_id, algorithm) pair.

    This is the core Phase 5 deduplication requirement. We mock _load_existing_pairs
    to return pairs that cover ALL events, so no new records should be inserted.
    """
    from unittest.mock import patch

    # Create 20 events that would each be flagged
    events = [
        _make_event(f"evt-{i:03d}", hour=23, amount=500_000.0, duration=1)
        for i in range(20)
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = events

    # Existing pairs cover ALL events for isolation_forest and z_score
    existing_pairs = frozenset(
        [(e.id, "isolation_forest") for e in events] +
        [(e.id, "z_score") for e in events]
    )

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.add_all = MagicMock()
    mock_db.commit = AsyncMock()

    with patch(
        "app.services.anomaly_service._load_existing_pairs",
        AsyncMock(return_value=existing_pairs),
    ):
        result = asyncio.get_event_loop().run_until_complete(
            run_detection(mock_db, redis_client=None)
        )

    # No new records should have been committed
    assert result["flagged"] == 0, (
        f"Expected 0 flagged (all are duplicates), got {result['flagged']}"
    )
    mock_db.add_all.assert_not_called()


def test_run_detection_no_redis_still_returns_result():
    """
    Passing redis_client=None must NOT raise an exception.
    The service must degrade gracefully when Redis is unavailable.
    """
    from unittest.mock import patch

    events = [_make_event(f"evt-{i}", hour=12, amount=100.0) for i in range(5)]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = events

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.add_all = MagicMock()
    mock_db.commit = AsyncMock()

    with patch(
        "app.services.anomaly_service._load_existing_pairs",
        AsyncMock(return_value=frozenset()),
    ):
        result = asyncio.get_event_loop().run_until_complete(
            run_detection(mock_db, redis_client=None)
        )

    assert "flagged" in result
    assert "duration_ms" in result
    assert isinstance(result["duration_ms"], float)

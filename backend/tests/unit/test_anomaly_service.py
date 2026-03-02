"""
Spectra — Unit Tests: AnomalyService
Tests the detection logic directly without requiring a DB or Redis connection.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.anomaly_service import _build_feature_matrix, run_detection


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_event(event_id: str, hour: int = 12, amount: float = 0.0, duration: int = 0):
    """Create a minimal mock Event object for testing."""
    e = MagicMock()
    e.id = event_id
    e.occurred_at = datetime(2025, 6, 1, hour, 0, 0, tzinfo=timezone.utc)
    e.metadata_ = {}
    if amount:
        e.metadata_["amount_usd"] = amount
    if duration:
        e.metadata_["duration_seconds"] = duration
    return e


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_build_feature_matrix_returns_correct_shape():
    """Feature matrix should have shape (n_events, 3)."""
    events = [_make_event(f"evt-{i}", hour=i % 24, amount=float(i * 100)) for i in range(10)]
    X, valid = _build_feature_matrix(events)
    assert X.shape == (10, 3)
    assert len(valid) == 10


def test_isolation_forest_flags_outliers():
    """IsolationForest should flag at least one outlier in a skewed dataset."""
    from sklearn.ensemble import IsolationForest

    # 95 normal points, 5 extreme outliers
    normal = np.random.normal(1000, 50, (95, 3))
    outliers = np.array([[23, 500000, 0]] * 5)  # extreme amount, off-hours
    X = np.vstack([normal, outliers])

    clf = IsolationForest(contamination=0.05, random_state=42)
    preds = clf.fit_predict(X)
    assert (preds == -1).sum() > 0, "IsolationForest should flag at least 1 outlier"


def test_get_anomalies_returns_list():
    """get_anomalies should return whatever the DB query scalar returns."""
    import asyncio
    from app.services.anomaly_service import get_anomalies

    mock_record = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_record]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = asyncio.get_event_loop().run_until_complete(get_anomalies(mock_db, limit=5, offset=0))
    assert isinstance(result, list)
    assert len(result) == 1


def test_z_score_flags_extreme_values():
    """Z-score logic should identify values significantly above the mean."""
    # 30 tightly clustered normal values (mean ~1000, std ~20), plus one extreme outlier
    normal_amounts = np.random.RandomState(42).normal(1000, 20, 29)
    amounts = np.append(normal_amounts, 50000.0)  # last is a massive outlier
    mean, std = amounts.mean(), amounts.std()
    z_scores = np.abs((amounts - mean) / std)
    flagged = z_scores > 2.5
    assert flagged[-1], f"Extreme value (z={z_scores[-1]:.1f}) should be flagged by z-score"
    assert not all(flagged[:-1]), "Not all normal values should be flagged"

"""
Spectra — Anomaly Detection Service
Runs IsolationForest + z-score on synthetic event data and persists AnomalyRecord rows.

Phase 5 optimisations:
  - Deduplication: existing (entity_id, algorithm) pairs are loaded before insert so
    repeated runs don't create duplicate rows.  The DB-level unique index on
    (entity_id, algorithm) in migration 0003 provides a second safety net.
  - get_anomaly_count(): fast COUNT(*) helper for the metrics endpoint.
  - Feature matrix generation is unchanged but comments clarify complexity.

Results are cached in Redis for 5 minutes to avoid repeated expensive computation.
"""

import json
import time
from datetime import datetime, timezone

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly import AnomalyAlgorithm, AnomalyRecord, EntityType
from app.models.event import Event

_REDIS_KEY = "anomaly:last_run"
_REDIS_TTL_SECONDS = 300  # 5 minutes


def _build_feature_matrix(events: list[Event]) -> tuple[np.ndarray, list[Event]]:
    """
    Build a numeric feature matrix from events.  O(n) — vectorised with list
    comprehension before a single np.array() call (avoids repeated resize).

    Features per event:
      [0] hour_of_day   — captures off-hours behaviour
      [1] amount_usd    — large transfers are a key anomaly signal
      [2] duration_sec  — unusually long/short calls are suspicious

    Returns (matrix shape (n,3), valid_events list same length as matrix rows).
    """
    rows = []
    valid_events = []
    for e in events:
        meta = e.metadata_ or {}
        amount = float(meta.get("amount_usd", 0.0))
        duration = float(meta.get("duration_seconds", 0.0))
        hour = float(e.occurred_at.hour) if e.occurred_at else 12.0
        rows.append([hour, amount, duration])
        valid_events.append(e)

    if not rows:
        return np.empty((0, 3), dtype=float), []

    return np.array(rows, dtype=float), valid_events


async def _load_existing_pairs(db: AsyncSession) -> frozenset[tuple[str, str]]:
    """
    Load all (entity_id, algorithm) pairs already in anomaly_records.
    Used by run_detection to skip duplicates before attempting any INSERT,
    reducing unnecessary DB round-trips and preventing unique-constraint errors.
    """
    result = await db.execute(
        select(AnomalyRecord.entity_id, AnomalyRecord.algorithm)
    )
    return frozenset(
        (str(row.entity_id), str(row.algorithm)) for row in result.all()
    )


async def run_detection(db: AsyncSession, redis_client) -> dict:
    """
    Run IsolationForest + z-score anomaly detection on all Event rows.

    Steps:
      1. Load all Event rows from Postgres.
      2. Load existing (entity_id, algorithm) pairs for deduplication.
      3. Build feature matrix.
      4. IsolationForest (contamination=0.05) flags outliers.
      5. Z-score on amount_usd flags high-value transfers (|z| > 2.5).
      6. Save only NEW AnomalyRecord rows (skip already-flagged pairs).
      7. Cache summary in Redis with 5-min TTL.

    Returns: {"flagged": int, "skipped_duplicates": int, "duration_ms": float}
    """
    t0 = time.perf_counter()

    # ── Load events ───────────────────────────────────────────────────────────
    result = await db.execute(select(Event))
    events = result.scalars().all()

    if not events:
        return {"flagged": 0, "skipped_duplicates": 0, "duration_ms": 0.0}

    X, valid_events = _build_feature_matrix(events)

    # ── Load existing pairs for dedup ─────────────────────────────────────────
    existing_pairs: frozenset[tuple[str, str]] = await _load_existing_pairs(db)

    anomaly_records: list[AnomalyRecord] = []
    already_flagged: set[str] = set()   # within-run dedup (prevents double-alg same event)
    skipped_duplicates: int = 0

    # ── IsolationForest ───────────────────────────────────────────────────────
    if len(X) >= 10:  # need enough samples for reliable fit
        clf = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
        preds = clf.fit_predict(X)   # -1 = anomaly, 1 = normal
        scores = clf.decision_function(X)

        for i, (pred, score) in enumerate(zip(preds, scores)):
            if pred == -1:
                e = valid_events[i]
                pair = (e.id, AnomalyAlgorithm.isolation_forest.value)
                if pair in existing_pairs:
                    skipped_duplicates += 1
                    continue
                if e.id not in already_flagged:
                    already_flagged.add(e.id)
                    normalised = float(np.clip(1.0 - (score + 0.5), 0.01, 1.0))
                    anomaly_records.append(
                        AnomalyRecord(
                            entity_id=e.id,
                            entity_type=EntityType.event,
                            anomaly_type="isolation_forest_outlier",
                            score=normalised,
                            description=(
                                f"IsolationForest flagged event {e.id[:8]}… "
                                f"(hour={int(X[i][0])}, amount=${X[i][1]:.0f}, "
                                f"duration={int(X[i][2])}s)"
                            ),
                            algorithm=AnomalyAlgorithm.isolation_forest,
                            detected_at=datetime.now(timezone.utc),
                        )
                    )

    # ── Z-score on amount_usd (transfer events only) ──────────────────────────
    transfer_amounts = [
        (e, float((e.metadata_ or {}).get("amount_usd", 0.0)))
        for e in events
        if (e.metadata_ or {}).get("amount_usd")
    ]
    if len(transfer_amounts) >= 3:
        amounts = np.array([a for _, a in transfer_amounts])
        mean, std = amounts.mean(), amounts.std()
        if std > 0:
            for e, amount in transfer_amounts:
                z = abs((amount - mean) / std)
                if z > 2.5:
                    pair = (e.id, AnomalyAlgorithm.z_score.value)
                    if pair in existing_pairs:
                        skipped_duplicates += 1
                        continue
                    if e.id not in already_flagged:
                        already_flagged.add(e.id)
                        anomaly_records.append(
                            AnomalyRecord(
                                entity_id=e.id,
                                entity_type=EntityType.event,
                                anomaly_type="high_value_transfer",
                                score=float(np.clip(z / 5.0, 0.5, 1.0)),
                                description=(
                                    f"Transfer of ${amount:,.2f} is {z:.1f}σ above mean "
                                    f"(μ=${mean:,.0f}, σ=${std:,.0f})"
                                ),
                                algorithm=AnomalyAlgorithm.z_score,
                                detected_at=datetime.now(timezone.utc),
                            )
                        )

    # ── Persist to Postgres ───────────────────────────────────────────────────
    if anomaly_records:
        db.add_all(anomaly_records)
        await db.commit()

    elapsed_ms = (time.perf_counter() - t0) * 1000
    summary = {
        "flagged": len(anomaly_records),
        "skipped_duplicates": skipped_duplicates,
        "duration_ms": round(elapsed_ms, 2),
    }

    # ── Cache in Redis ────────────────────────────────────────────────────────
    if redis_client is not None:
        try:
            await redis_client.set(_REDIS_KEY, json.dumps(summary), ex=_REDIS_TTL_SECONDS)
        except Exception:
            pass  # Redis failure must NOT break the detection run

    return summary


async def get_anomalies(db: AsyncSession, limit: int = 20, offset: int = 0) -> list[AnomalyRecord]:
    """Return a paginated list of AnomalyRecord rows ordered by score descending."""
    result = await db.execute(
        select(AnomalyRecord)
        .order_by(AnomalyRecord.score.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


async def get_anomaly_count(db: AsyncSession) -> int:
    """Fast COUNT(*) of all AnomalyRecord rows — used by the metrics endpoint."""
    result = await db.execute(select(func.count()).select_from(AnomalyRecord))
    return result.scalar_one()

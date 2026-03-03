"""
Spectra — Anomaly Detection Service
Runs IsolationForest + z-score + DBSCAN + LOF + Night Owl Rule on synthetic event data.

Phase 5 optimisations:
  - Deduplication: existing (entity_id, algorithm) pairs are loaded before insert.
  - Idempotent INSERT ... ON CONFLICT DO NOTHING at DB level.

Phase 8 additions:
  - DBSCAN: cluster-based outlier detection (noise points = anomalies)
  - LOF: Local Outlier Factor density-based anomalies
  - Night Owl Rule: persons with >60% of events between 11pm–4am

Results are cached in Redis for 5 minutes.
"""

import json
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly import AnomalyAlgorithm, AnomalyRecord, EntityType
from app.models.event import Event

_REDIS_KEY = "anomaly:last_run"
_REDIS_TTL_SECONDS = 300  # 5 minutes


def _build_feature_matrix(events: list[Event]) -> tuple[np.ndarray, list[Event]]:
    """
    Build a numeric feature matrix from events.  O(n) — vectorised.

    Features per event:
      [0] hour_of_day   — captures off-hours behaviour
      [1] amount_usd    — large transfers are a key anomaly signal
      [2] duration_sec  — unusually long/short calls are suspicious
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
    """Load all (entity_id, algorithm) pairs already in anomaly_records."""
    result = await db.execute(
        select(AnomalyRecord.entity_id, AnomalyRecord.algorithm)
    )
    return frozenset(
        (str(row.entity_id), str(row.algorithm)) for row in result.all()
    )


async def run_detection(db: AsyncSession, redis_client) -> dict:
    """
    Run all anomaly detection algorithms on all Event rows.

    Algorithms: isolation_forest, z_score, dbscan, lof, night_owl_rule
    Returns counts per algorithm plus totals.
    """
    t0 = time.perf_counter()

    # ── Load events ───────────────────────────────────────────────────────────
    result = await db.execute(select(Event))
    events = result.scalars().all()

    if not events:
        return {"flagged": 0, "skipped_duplicates": 0, "duration_ms": 0.0, "by_algorithm": {}}

    X, valid_events = _build_feature_matrix(events)

    # ── Load existing pairs for dedup ─────────────────────────────────────────
    existing_pairs: frozenset[tuple[str, str]] = await _load_existing_pairs(db)

    anomaly_records: list[AnomalyRecord] = []
    already_flagged: set[str] = set()  # within-run dedup
    skipped_duplicates: int = 0
    by_algorithm: dict[str, int] = {}

    def _add_record(event_id: str, alg: AnomalyAlgorithm, anomaly_type: str, score: float, desc: str):
        nonlocal skipped_duplicates
        pair = (event_id, alg.value)
        if pair in existing_pairs:
            skipped_duplicates += 1
            return
        if event_id in already_flagged:
            return
        already_flagged.add(event_id)
        anomaly_records.append(
            AnomalyRecord(
                id=str(uuid.uuid4()),  # ← FIX: explicit UUID so bulk insert never gets NULL
                entity_id=event_id,
                entity_type=EntityType.event,
                anomaly_type=anomaly_type,
                score=float(np.clip(score, 0.01, 1.0)),
                description=desc,
                algorithm=alg,
                detected_at=datetime.now(timezone.utc),
            )
        )
        by_algorithm[alg.value] = by_algorithm.get(alg.value, 0) + 1

    # ── IsolationForest ───────────────────────────────────────────────────────
    if len(X) >= 10:
        clf = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
        preds = clf.fit_predict(X)
        scores = clf.decision_function(X)

        for i, (pred, score) in enumerate(zip(preds, scores)):
            if pred == -1:
                e = valid_events[i]
                normalised = float(np.clip(1.0 - (score + 0.5), 0.01, 1.0))
                _add_record(
                    e.id,
                    AnomalyAlgorithm.isolation_forest,
                    "isolation_forest_outlier",
                    normalised,
                    f"IsolationForest flagged event {e.id[:8]}… "
                    f"(hour={int(X[i][0])}, amount=${X[i][1]:.0f}, duration={int(X[i][2])}s)",
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
                    _add_record(
                        e.id,
                        AnomalyAlgorithm.z_score,
                        "high_value_transfer",
                        float(np.clip(z / 5.0, 0.5, 1.0)),
                        f"Transfer of ${amount:,.2f} is {z:.1f}σ above mean "
                        f"(μ=${mean:,.0f}, σ=${std:,.0f})",
                    )

    # ── DBSCAN — cluster-based outlier detection ───────────────────────────────
    if len(X) >= 10:
        # Normalise features for DBSCAN
        X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
        db_labels = DBSCAN(eps=0.8, min_samples=5).fit_predict(X_norm)

        for i, label in enumerate(db_labels):
            if label == -1:  # noise = outlier
                e = valid_events[i]
                _add_record(
                    e.id,
                    AnomalyAlgorithm.dbscan,
                    "dbscan_noise_point",
                    0.75,
                    f"DBSCAN: event {e.id[:8]}… is not part of any cluster "
                    f"(hour={int(X[i][0])}, amount=${X[i][1]:.0f})",
                )

    # ── LOF — Local Outlier Factor ────────────────────────────────────────────
    if len(X) >= 10:
        n_neighbors = min(20, len(X) - 1)
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=0.05)
        lof_preds = lof.fit_predict(X)
        lof_scores = -lof.negative_outlier_factor_  # higher = more anomalous

        for i, (pred, lof_score) in enumerate(zip(lof_preds, lof_scores)):
            if pred == -1:
                e = valid_events[i]
                pair = (e.id, AnomalyAlgorithm.lof.value)
                if pair in existing_pairs:
                    skipped_duplicates += 1
                    continue
                normalised = float(np.clip((lof_score - 1.0) / 5.0, 0.01, 1.0))
                anomaly_records.append(
                    AnomalyRecord(
                        id=str(uuid.uuid4()),  # ← FIX: explicit UUID
                        entity_id=e.id,
                        entity_type=EntityType.event,
                        anomaly_type="lof_density_outlier",
                        score=normalised,
                        description=(
                            f"LOF: event {e.id[:8]}… is a local density outlier "
                            f"(score={lof_score:.2f}, threshold≈1.5)"
                        ),
                        algorithm=AnomalyAlgorithm.lof,
                        detected_at=datetime.now(timezone.utc),
                    )
                )
                by_algorithm["lof"] = by_algorithm.get("lof", 0) + 1

    # ── Night Owl Rule — persons with >60% events between 11pm–4am ───────────
    person_events_map: dict[str, list[Event]] = defaultdict(list)
    for e in events:
        person_events_map[e.actor_id].append(e)
        person_events_map[e.target_id].append(e)

    for person_id, p_events in person_events_map.items():
        if len(p_events) < 5:
            continue
        night_count = sum(
            1 for e in p_events
            if e.occurred_at and (e.occurred_at.hour >= 23 or e.occurred_at.hour <= 4)
        )
        pct = night_count / len(p_events)
        if pct > 0.60:
            pair = (person_id, AnomalyAlgorithm.night_owl_rule.value)
            if pair in existing_pairs:
                skipped_duplicates += 1
                continue
            anomaly_records.append(
                AnomalyRecord(
                    id=str(uuid.uuid4()),  # ← FIX: explicit UUID
                    entity_id=person_id,
                    entity_type=EntityType.person,
                    anomaly_type="night_owl_activity",
                    score=float(np.clip(pct, 0.60, 1.0)),
                    description=(
                        f"Night Owl: {pct*100:.0f}% of {len(p_events)} events "
                        f"occurred between 11pm–4am (threshold: 60%)"
                    ),
                    algorithm=AnomalyAlgorithm.night_owl_rule,
                    detected_at=datetime.now(timezone.utc),
                )
            )
            by_algorithm["night_owl_rule"] = by_algorithm.get("night_owl_rule", 0) + 1

    # ── Persist to Postgres ────────────────────────────────────────────────────
    if anomaly_records:
        stmt = (
            pg_insert(AnomalyRecord)
            .values(
                [
                    {
                        "id":           rec.id,
                        "entity_id":    rec.entity_id,
                        "entity_type":  rec.entity_type,
                        "anomaly_type": rec.anomaly_type,
                        "score":        rec.score,
                        "description":  rec.description,
                        "algorithm":    rec.algorithm,
                        "detected_at":  rec.detected_at,
                        "created_at":   rec.detected_at,
                    }
                    for rec in anomaly_records
                ]
            )
            .on_conflict_do_nothing(
                index_elements=["entity_id", "algorithm"]
            )
        )
        await db.execute(stmt)
        await db.commit()

    elapsed_ms = (time.perf_counter() - t0) * 1000
    summary = {
        "flagged": len(anomaly_records),
        "skipped_duplicates": skipped_duplicates,
        "duration_ms": round(elapsed_ms, 2),
        "by_algorithm": by_algorithm,
    }

    # ── Cache in Redis ────────────────────────────────────────────────────────
    if redis_client is not None:
        try:
            await redis_client.set(_REDIS_KEY, json.dumps(summary), ex=_REDIS_TTL_SECONDS)
        except Exception:
            pass

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
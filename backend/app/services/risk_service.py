"""
Spectra — Risk Score Service
Computes a 0–100 risk score for each synthetic person based on their event activity.

Formula (max 100 points):
  volume (25pts)      — number of events relative to max observed
  off_hours (30pts)   — percentage of events occurring outside 9am–6pm
  transfer (25pts)    — max transfer amount relative to $50,000 cap
  anomaly (20pts)     — number of anomalies flagged for this person

⚠️ All data is synthetic. Scores have no real-world meaning.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly import AnomalyAlgorithm, AnomalyRecord, EntityType
from app.models.event import Event
from app.models.person import Person

logger = logging.getLogger(__name__)

_TRANSFER_CAP_USD = 50_000.0
_MAX_ANOMALY_SCORE_COUNT = 10  # clamp anomaly count at 10 for scoring


def compute_risk_score(
    event_count: int,
    off_hours_pct: float,
    max_transfer_usd: float,
    anomaly_count: int,
    *,
    max_event_count: int = 1,
) -> float:
    """
    Compute a scalar risk score in range [0.0, 100.0].

    Args:
        event_count:       Total number of events for this person.
        off_hours_pct:     Fraction of events outside 9am–6pm (0.0–1.0).
        max_transfer_usd:  USD value of the largest transfer event.
        anomaly_count:     Number of anomaly records flagged for this person.
        max_event_count:   Maximum event_count across all persons (used for normalisation).

    Returns:
        A float in [0.0, 100.0].
    """
    # Volume component: 25 points max
    # Normalise against the busiest person so relative activity is captured.
    max_ev = max(max_event_count, 1)
    volume_pts = 25.0 * min(event_count / max_ev, 1.0)

    # Off-hours component: 30 points max
    off_hours_pts = 30.0 * float(np.clip(off_hours_pct, 0.0, 1.0))

    # Transfer size component: 25 points max
    transfer_pts = 25.0 * float(np.clip(max_transfer_usd / _TRANSFER_CAP_USD, 0.0, 1.0))

    # Anomaly count component: 20 points max
    anomaly_pts = 20.0 * float(np.clip(anomaly_count / _MAX_ANOMALY_SCORE_COUNT, 0.0, 1.0))

    raw = volume_pts + off_hours_pts + transfer_pts + anomaly_pts
    return float(np.clip(raw, 0.0, 100.0))


async def compute_all_risk_scores(db: AsyncSession) -> dict:
    """
    Read all persons and their events from Postgres, compute a risk score for
    each, and update the risk_score column.

    Returns:
        {"updated": int, "skipped": int}
    """
    # ── Load all persons ──────────────────────────────────────────────────────
    persons_result = await db.execute(select(Person))
    persons = persons_result.scalars().all()

    if not persons:
        return {"updated": 0, "skipped": 0}

    # ── Load all events ───────────────────────────────────────────────────────
    events_result = await db.execute(select(Event))
    events = events_result.scalars().all()

    # ── Load all anomaly records ──────────────────────────────────────────────
    anomaly_result = await db.execute(
        select(AnomalyRecord).where(AnomalyRecord.entity_type == EntityType.event)
    )
    anomaly_records = anomaly_result.scalars().all()

    # Build lookup structures
    person_events: dict[str, list[Event]] = defaultdict(list)
    for e in events:
        person_events[e.actor_id].append(e)
        person_events[e.target_id].append(e)

    # Anomalies are keyed to events; we need to find which persons are connected
    anomalous_event_ids: set[str] = {rec.entity_id for rec in anomaly_records}
    person_anomaly_count: dict[str, int] = defaultdict(int)
    for e in events:
        if e.id in anomalous_event_ids:
            person_anomaly_count[e.actor_id] += 1
            person_anomaly_count[e.target_id] += 1

    # Maximum event count for normalisation
    max_event_count = max(
        (len(evs) for evs in person_events.values()),
        default=1,
    )

    # ── Compute and persist scores ────────────────────────────────────────────
    updated = 0
    for person in persons:
        evs = person_events.get(person.id, [])
        event_count = len(evs)

        # Off-hours: any event outside 9am–6pm
        off_hours = sum(
            1 for e in evs
            if e.occurred_at and (e.occurred_at.hour < 9 or e.occurred_at.hour >= 18)
        )
        off_hours_pct = off_hours / max(event_count, 1)

        # Max transfer USD
        max_transfer = max(
            (float((e.metadata_ or {}).get("amount_usd", 0.0)) for e in evs),
            default=0.0,
        )

        anomaly_count = person_anomaly_count.get(person.id, 0)

        score = compute_risk_score(
            event_count=event_count,
            off_hours_pct=off_hours_pct,
            max_transfer_usd=max_transfer,
            anomaly_count=anomaly_count,
            max_event_count=max_event_count,
        )

        person.risk_score = score
        updated += 1

    await db.commit()
    logger.info("Risk scores updated for %d persons", updated)
    return {"updated": updated, "skipped": 0}

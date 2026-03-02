"""
Spectra — Event Generator
Pairs persons into synthetic interaction events with realistic time distribution.
⚠️ All events are computer-generated. No real communications are modelled.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

import numpy as np

from app.data_gen.constants import EVENT_TYPES, EVENT_WEIGHTS
from app.models.event import Event, EventType
from app.models.location import Location
from app.models.person import Person

# Business hours bias: 9am–6pm (hours 9..17 inclusive = 9 hours out of 24)
_BUSINESS_HOUR_WEIGHT = 3.0  # 3× more likely than off-hours
_HOURS = list(range(24))
_HOUR_WEIGHTS = [
    _BUSINESS_HOUR_WEIGHT if 9 <= h <= 17 else 1.0
    for h in _HOURS
]
_HOUR_WEIGHTS_NORM = [w / sum(_HOUR_WEIGHTS) for w in _HOUR_WEIGHTS]


def _random_past_datetime(days: int = 365) -> datetime:
    """Return a timezone-aware UTC datetime within the past `days` days,
    weighted toward business hours."""
    now = datetime.now(timezone.utc)
    # Random day offset
    day_offset = random.randint(0, days - 1)
    # Weighted random hour
    hour = int(np.random.choice(_HOURS, p=_HOUR_WEIGHTS_NORM))
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    base = now - timedelta(days=day_offset)
    return base.replace(hour=hour, minute=minute, second=second, microsecond=0)


class EventGenerator:
    """Generate synthetic Event objects (not yet persisted to DB)."""

    def generate(
        self,
        persons: list[Person],
        locations: list[Location],
        n: int,
    ) -> list[Event]:
        """
        Return a list of *n* unsaved Event ORM objects.

        - Actor and target are always different persons (no self-events).
        - Event type is sampled using the weighted distribution from constants.
        - occurred_at is weighted toward business hours.
        - metadata_ includes event-specific fields plus _synthetic: True.
        """
        if len(persons) < 2:
            raise ValueError("Need at least 2 persons to generate events.")

        # Ensure every person has an id (SQLAlchemy column defaults only fire at
        # flush time; in unit tests no session exists, so ids may be None).
        for p in persons:
            if p.id is None:
                p.id = str(uuid.uuid4())
        for loc in locations:
            if loc.id is None:
                loc.id = str(uuid.uuid4())

        events: list[Event] = []

        for _ in range(n):
            actor, target = random.sample(persons, 2)
            event_type_str: str = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS, k=1)[0]
            event_type = EventType(event_type_str)
            location = random.choice(locations) if locations else None

            # Build event-type-specific metadata
            meta: dict = {"_synthetic": True}
            if event_type == EventType.call:
                meta["duration_seconds"] = random.randint(60, 3600)
            elif event_type == EventType.transfer:
                meta["amount_usd"] = round(random.uniform(10, 50000), 2)

            events.append(
                Event(
                    event_type=event_type,
                    actor_id=actor.id,
                    target_id=target.id,
                    location_id=location.id if location else None,
                    occurred_at=_random_past_datetime(),
                    metadata_=meta,
                )
            )

        return events

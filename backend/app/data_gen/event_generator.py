"""
Spectra — Event Generator
Pairs persons into synthetic interaction events with realistic time distribution.
⚠️ All events are computer-generated. No real communications are modelled.

Phase 8: Added channel, is_encrypted (call); content_hash, platform (message);
         currency, recipient_account (transfer); attendee_count, is_covert (meeting).
"""

import hashlib
import random
import uuid
from datetime import datetime, timedelta, timezone

import numpy as np

from app.data_gen.constants import (
    CALL_CHANNELS,
    EVENT_TYPES,
    EVENT_WEIGHTS,
    FAKE_PLATFORMS,
    TRANSFER_CURRENCIES,
)
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


def _fake_content_hash() -> str:
    """Generate a fake SHA256 hex string for message content."""
    random_bytes = uuid.uuid4().bytes + uuid.uuid4().bytes
    return hashlib.sha256(random_bytes).hexdigest()


def _fake_iban_style() -> str:
    """Generate a fake IBAN-style recipient account string."""
    country = random.choice(["MR", "VX", "CY", "DL", "NX"])
    digits = "".join([str(random.randint(0, 9)) for _ in range(18)])
    return f"{country}{digits}"


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

        Phase 8 additions per event type:
        - call: channel (voice/encrypted/unknown), is_encrypted (bool)
        - message: content_hash (fake SHA256), platform (NexusMail/etc)
        - transfer: currency (USD/EUR/MeridianCoin), recipient_account (fake IBAN)
        - meeting: attendee_count (2–10), is_covert (bool, 15% chance)
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
                meta["channel"] = random.choice(CALL_CHANNELS)
                meta["is_encrypted"] = meta["channel"] == "encrypted" or random.random() < 0.15
            elif event_type == EventType.message:
                meta["content_hash"] = _fake_content_hash()
                meta["platform"] = random.choice(FAKE_PLATFORMS)
            elif event_type == EventType.transfer:
                meta["amount_usd"] = round(random.uniform(10, 50000), 2)
                meta["currency"] = random.choice(TRANSFER_CURRENCIES)
                meta["recipient_account"] = _fake_iban_style()
            elif event_type == EventType.meeting:
                meta["attendee_count"] = random.randint(2, 10)
                meta["is_covert"] = random.random() < 0.15

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

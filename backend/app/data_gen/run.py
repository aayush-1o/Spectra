"""
Spectra — Data Generation CLI Entry Point  (Phase 11 — High-Volume Batch)

Usage:
    python -m app.data_gen.run --persons 5000 --events 50000
    docker exec spectra-backend python -m app.data_gen.run --persons 5000 --events 50000

Performance strategy:
  - SQLAlchemy Core bulk INSERT (insert().values()) instead of add_all()
  - Chunked processing: 500 rows per flush/commit cycle
  - Objects are NOT loaded into the ORM identity map — pure INSERT throughput
  - created_at/updated_at supplied explicitly (TimestampMixin uses Python defaults,
    not server_default, so Core INSERT must provide them)
"""

import argparse
import asyncio
import time
import uuid
from itertools import islice
from datetime import datetime, timezone
from typing import Any, Generator

from sqlalchemy import delete, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.data_gen.event_generator import EventGenerator
from app.data_gen.location_generator import LocationGenerator
from app.data_gen.person_generator import PersonGenerator
from app.db.postgres import get_async_session
from app.models.event import Event
from app.models.location import Location
from app.models.person import Person

CHUNK_SIZE = 500  # rows per DB round-trip


def _chunked(iterable, size: int) -> Generator[list, None, None]:
    """Yield successive chunks of `size` from an iterable."""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


_NOW = datetime.now(timezone.utc)  # single timestamp reused for all bulk inserts


def _person_to_dict(p: Person) -> dict[str, Any]:
    """Serialize a Person ORM object to a plain dict for Core bulk insert.
    Includes created_at/updated_at because TimestampMixin uses Python-side
    defaults (not server_default), so Core INSERT must supply them explicitly.
    The DB column is named "metadata" (the ORM attribute is metadata_).
    """
    return {
        "id": p.id or str(uuid.uuid4()),
        "fake_name": p.fake_name,
        "date_of_birth": p.date_of_birth,
        "occupation": p.occupation,
        "location_id": None,
        "fake_phone_primary": p.fake_phone_primary,
        "fake_phone_secondary": p.fake_phone_secondary,
        "fake_email": p.fake_email,
        "fake_nationality": p.fake_nationality,
        "fake_alias": p.fake_alias,
        "risk_category": p.risk_category,
        "group_memberships": p.group_memberships,
        "fake_id_number": p.fake_id_number,
        "risk_score": None,
        "last_seen_lat": p.last_seen_lat,
        "last_seen_lon": p.last_seen_lon,
        "last_seen_at": p.last_seen_at,
        "metadata": p.metadata_,
        "created_at": _NOW,
        "updated_at": _NOW,
    }


def _location_to_dict(loc: Location) -> dict[str, Any]:
    return {
        "id": loc.id or str(uuid.uuid4()),
        "fake_address": loc.fake_address,
        "lat": loc.lat,
        "lng": loc.lng,
        "location_type": (
            loc.location_type.value
            if hasattr(loc.location_type, "value")
            else loc.location_type
        ),
        "district": loc.district,
        "threat_level": loc.threat_level,
        "surveillance_coverage": loc.surveillance_coverage,
        "metadata": loc.metadata_,
        "created_at": _NOW,
        "updated_at": _NOW,
    }


def _event_to_dict(e: Event) -> dict[str, Any]:
    return {
        "id": e.id or str(uuid.uuid4()),
        "event_type": (
            e.event_type.value if hasattr(e.event_type, "value") else e.event_type
        ),
        "actor_id": e.actor_id,
        "target_id": e.target_id,
        "location_id": e.location_id,
        "occurred_at": e.occurred_at,
        "anomaly_score": None,
        "metadata": e.metadata_,
        "created_at": _NOW,
        "updated_at": _NOW,
    }



async def main(n_persons: int, n_events: int) -> None:
    t0 = time.perf_counter()
    n_locations = max(n_persons // 4, 50)

    print(
        f"[Spectra] Generating {n_persons:,} persons, "
        f"{n_locations:,} locations, {n_events:,} events …"
    )
    print(f"[Spectra] Chunk size: {CHUNK_SIZE} rows per flush")

    person_gen = PersonGenerator()
    location_gen = LocationGenerator()
    event_gen = EventGenerator()

    # ── 1. Generate all objects in memory (Python-only, fast) ─────────────────
    t_gen = time.perf_counter()
    persons = person_gen.generate(n_persons)
    # Assign UUIDs now so FK references in events are correct
    for p in persons:
        p.id = str(uuid.uuid4())

    locations = location_gen.generate(n_locations)
    for loc in locations:
        loc.id = str(uuid.uuid4())

    events = event_gen.generate(persons, locations, n_events)
    for e in events:
        e.id = str(uuid.uuid4())

    print(f"[Spectra]   ↳ Object generation: {time.perf_counter() - t_gen:.2f}s")

    # ── 2. Bulk-insert into Postgres using Core INSERT (chunked) ───────────────
    async for session in get_async_session():
        # Clear existing data (fresh seeding)
        t_clear = time.perf_counter()
        await session.execute(delete(Event))
        await session.execute(delete(Person))
        await session.execute(delete(Location))
        await session.commit()
        print(f"[Spectra]   ↳ Cleared old data: {time.perf_counter() - t_clear:.2f}s")

        # ── Insert persons ────────────────────────────────────────────────────
        t_persons = time.perf_counter()
        person_dicts = [_person_to_dict(p) for p in persons]
        for chunk in _chunked(person_dicts, CHUNK_SIZE):
            await session.execute(pg_insert(Person.__table__).values(chunk))
        await session.commit()
        print(
            f"[Spectra]   ↳ Inserted {n_persons:,} persons: "
            f"{time.perf_counter() - t_persons:.2f}s"
        )

        # ── Insert locations ──────────────────────────────────────────────────
        t_locs = time.perf_counter()
        loc_dicts = [_location_to_dict(loc) for loc in locations]
        for chunk in _chunked(loc_dicts, CHUNK_SIZE):
            await session.execute(pg_insert(Location.__table__).values(chunk))
        await session.commit()
        print(
            f"[Spectra]   ↳ Inserted {n_locations:,} locations: "
            f"{time.perf_counter() - t_locs:.2f}s"
        )

        # ── Insert events (chunked — largest set) ─────────────────────────────
        t_events = time.perf_counter()
        event_dicts = [_event_to_dict(e) for e in events]
        chunk_count = 0
        for chunk in _chunked(event_dicts, CHUNK_SIZE):
            await session.execute(pg_insert(Event.__table__).values(chunk))
            chunk_count += 1
            if chunk_count % 10 == 0:
                await session.commit()  # intermediate commits every 5,000 rows
                pct = min(100, round(chunk_count * CHUNK_SIZE / n_events * 100))
                print(f"[Spectra]     events …{pct}% ({chunk_count * CHUNK_SIZE:,}/{n_events:,})")
        await session.commit()
        print(
            f"[Spectra]   ↳ Inserted {n_events:,} events: "
            f"{time.perf_counter() - t_events:.2f}s"
        )

        # ── Re-index for search performance ───────────────────────────────────
        await session.execute(text("ANALYZE persons, events, locations;"))
        await session.commit()

        elapsed = time.perf_counter() - t0
        print(
            f"\n[Spectra] ✅ Done in {elapsed:.2f}s — "
            f"{n_persons:,} persons | {n_locations:,} locations | {n_events:,} events"
        )
        break  # generator yields one session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Spectra — high-volume synthetic data generation CLI"
    )
    parser.add_argument(
        "--persons", type=int, default=5000,
        help="Number of synthetic persons to generate (default: 5000)",
    )
    parser.add_argument(
        "--events", type=int, default=50000,
        help="Number of synthetic events to generate (default: 50000)",
    )
    args = parser.parse_args()
    asyncio.run(main(n_persons=args.persons, n_events=args.events))

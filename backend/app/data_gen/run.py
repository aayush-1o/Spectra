"""
Spectra — Data Generation CLI Entry Point

Usage:
    python -m app.data_gen.run --persons 200 --events 800
    docker exec spectra-backend python -m app.data_gen.run --persons 200 --events 800
"""

import argparse
import asyncio
import time

from sqlalchemy import text

from app.data_gen.event_generator import EventGenerator
from app.data_gen.location_generator import LocationGenerator
from app.data_gen.person_generator import PersonGenerator
from app.db.postgres import get_async_session


async def main(n_persons: int, n_events: int) -> None:
    t0 = time.perf_counter()

    person_gen = PersonGenerator()
    location_gen = LocationGenerator()
    event_gen = EventGenerator()

    # Use same number of locations as persons for variety
    n_locations = max(n_persons // 4, 10)

    print(f"[Spectra] Generating {n_persons} persons, {n_locations} locations, {n_events} events …")

    persons = person_gen.generate(n_persons)
    locations = location_gen.generate(n_locations)

    async for session in get_async_session():
        # ── Insert persons first so FK constraints on events resolve ─────────
        session.add_all(persons)
        await session.flush()  # assigns PKs without committing

        session.add_all(locations)
        await session.flush()  # assigns PKs for location → event FK

        # ── Generate events now that persons & locations have real IDs ────────
        events = event_gen.generate(persons, locations, n_events)
        session.add_all(events)

        await session.commit()

        elapsed = time.perf_counter() - t0
        print(
            f"[Spectra] ✅ Done in {elapsed:.2f}s — "
            f"{n_persons} persons | {n_locations} locations | {n_events} events inserted."
        )
        break  # generator yields one session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Spectra — synthetic data generation CLI"
    )
    parser.add_argument(
        "--persons",
        type=int,
        default=200,
        help="Number of synthetic persons to generate (default: 200)",
    )
    parser.add_argument(
        "--events",
        type=int,
        default=800,
        help="Number of synthetic events to generate (default: 800)",
    )
    args = parser.parse_args()
    asyncio.run(main(n_persons=args.persons, n_events=args.events))

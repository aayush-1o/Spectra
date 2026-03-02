"""
Spectra — Graph Builder CLI
Reads Person + Event rows from Postgres and writes edges to Neo4j.
Run AFTER `python -m app.data_gen.run` to populate the graph layer.

Usage:
    docker exec spectra-backend python -m app.data_gen.graph_builder
"""

import asyncio
import time

from sqlalchemy import select

from app.db.neo4j import get_neo4j_driver
from app.db.postgres import get_async_session
from app.models.event import Event, EventType
from app.models.person import Person
from app.models.location import Location


async def build_graph() -> None:
    t0 = time.perf_counter()
    driver = get_neo4j_driver()

    async for session in get_async_session():
        # ── Load all data from Postgres ───────────────────────────────────────
        persons_result = await session.execute(select(Person))
        persons = persons_result.scalars().all()

        locations_result = await session.execute(select(Location))
        locations = locations_result.scalars().all()

        events_result = await session.execute(select(Event))
        events = events_result.scalars().all()
        break  # single session

    print(f"[GraphBuilder] Loaded {len(persons)} persons, {len(locations)} locations, {len(events)} events from Postgres")

    # ── Write to Neo4j ────────────────────────────────────────────────────────
    async with driver.session(database="neo4j") as neo4j_sess:

        # 1. MERGE Person nodes
        await neo4j_sess.run(
            """
            UNWIND $persons AS p
            MERGE (n:Person {id: p.id})
            SET n.fake_name = p.fake_name,
                n.occupation = p.occupation
            """,
            persons=[
                {"id": p.id, "fake_name": p.fake_name, "occupation": p.occupation or ""}
                for p in persons
            ],
        )

        # 2. MERGE Location nodes
        await neo4j_sess.run(
            """
            UNWIND $locations AS loc
            MERGE (n:Location {id: loc.id})
            SET n.fake_address = loc.fake_address,
                n.location_type = loc.location_type
            """,
            locations=[
                {
                    "id": loc.id,
                    "fake_address": loc.fake_address,
                    "location_type": loc.location_type.value,
                }
                for loc in locations
            ],
        )

        # 3. Build event edges — batch by type for efficiency
        call_msg_events = [
            {
                "event_id": e.id,
                "actor_id": e.actor_id,
                "target_id": e.target_id,
                "ts": e.occurred_at.isoformat(),
            }
            for e in events
            if e.event_type in (EventType.call, EventType.message)
        ]

        transfer_events = [
            {
                "event_id": e.id,
                "actor_id": e.actor_id,
                "target_id": e.target_id,
                "ts": e.occurred_at.isoformat(),
                "amount_usd": e.metadata_.get("amount_usd", 0.0) if e.metadata_ else 0.0,
            }
            for e in events
            if e.event_type == EventType.transfer
        ]

        meeting_events = [
            {
                "event_id": e.id,
                "actor_id": e.actor_id,
                "location_id": e.location_id,
                "ts": e.occurred_at.isoformat(),
            }
            for e in events
            if e.event_type == EventType.meeting and e.location_id
        ]

        if call_msg_events:
            await neo4j_sess.run(
                """
                UNWIND $events AS e
                MATCH (a:Person {id: e.actor_id})
                MATCH (b:Person {id: e.target_id})
                MERGE (a)-[r:CONTACTED {event_id: e.event_id}]->(b)
                SET r.ts = e.ts
                """,
                events=call_msg_events,
            )

        if transfer_events:
            await neo4j_sess.run(
                """
                UNWIND $events AS e
                MATCH (a:Person {id: e.actor_id})
                MATCH (b:Person {id: e.target_id})
                MERGE (a)-[r:TRANSACTED {event_id: e.event_id}]->(b)
                SET r.ts = e.ts, r.amount_usd = e.amount_usd
                """,
                events=transfer_events,
            )

        if meeting_events:
            await neo4j_sess.run(
                """
                UNWIND $events AS e
                MATCH (a:Person {id: e.actor_id})
                MATCH (b:Location {id: e.location_id})
                MERGE (a)-[r:VISITED {event_id: e.event_id}]->(b)
                SET r.ts = e.ts
                """,
                events=meeting_events,
            )

    elapsed = time.perf_counter() - t0
    print(
        f"[GraphBuilder] ✅ Done in {elapsed:.2f}s — "
        f"{len(call_msg_events)} CONTACTED + {len(transfer_events)} TRANSACTED + {len(meeting_events)} VISITED edges written."
    )
    await driver.close()


if __name__ == "__main__":
    asyncio.run(build_graph())

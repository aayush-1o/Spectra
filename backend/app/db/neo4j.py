"""
Spectra — Neo4j Async Driver Singleton
Provides a shared AsyncDriver instance and a FastAPI-compatible session dependency.

Phase 5 addition: ensure_neo4j_indexes() creates B-tree indexes on Person.id and
Location.id at application startup, improving all neighbourhood/shortest-path lookups.
"""

import logging
from typing import AsyncGenerator

import neo4j
from neo4j import AsyncDriver, AsyncGraphDatabase

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level driver — created once, reused across all requests.
_driver: AsyncDriver | None = None


def get_neo4j_driver() -> AsyncDriver:
    """Return (and lazily create) the module-level async Neo4j driver."""
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
            max_connection_pool_size=50,
        )
    return _driver


async def close_neo4j_driver() -> None:
    """Cleanly close the driver on application shutdown."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def get_neo4j_session() -> AsyncGenerator[neo4j.AsyncSession, None]:
    """
    FastAPI dependency — yields an async Neo4j session.
    Usage:
        async def route(neo4j_session: neo4j.AsyncSession = Depends(get_neo4j_session)):
    """
    driver = get_neo4j_driver()
    async with driver.session(database="neo4j") as session:
        yield session


async def ensure_neo4j_indexes(driver: AsyncDriver) -> None:
    """
    Create Neo4j range indexes on Person.id and Location.id if they don't already
    exist.  These are the primary lookup keys for all neighbourhood and centrality
    queries — without them Neo4j does a full node-label scan on every request.

    Called once from main.py lifespan() on startup.  Failures are logged as
    warnings and do NOT prevent the application from starting.
    """
    index_statements = [
        "CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)",
        "CREATE INDEX location_id IF NOT EXISTS FOR (l:Location) ON (l.id)",
    ]
    try:
        async with driver.session(database="neo4j") as session:
            for stmt in index_statements:
                await session.run(stmt)
        logger.info("Neo4j indexes ensured: Person(id), Location(id)")
    except Exception as exc:
        # Neo4j may not yet be seeded — non-fatal at startup
        logger.warning("Could not create Neo4j indexes (non-fatal): %s", exc)

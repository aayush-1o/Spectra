"""
Spectra — Neo4j Async Driver Singleton
Provides a shared AsyncDriver instance and a FastAPI-compatible session dependency.
"""

from typing import AsyncGenerator

import neo4j
from neo4j import AsyncDriver, AsyncGraphDatabase

from app.config import settings

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

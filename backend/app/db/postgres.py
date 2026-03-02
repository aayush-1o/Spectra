"""
Spectra — Async PostgreSQL Engine + Session Factory

Phase 7: DATABASE_URL rewrite for Render compatibility.
Render Postgres gives a `postgresql://` connection string.
SQLAlchemy async requires `postgresql+asyncpg://`.
We normalise it here so both formats work.
"""

import re
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


def _normalise_db_url(url: str) -> str:
    """
    Rewrite postgresql:// → postgresql+asyncpg://
    Required because Render/Heroku-style DATABASE_URLs omit the driver.
    """
    return re.sub(r"^postgresql://", "postgresql+asyncpg://", url)


# ── Engine ─────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    _normalise_db_url(settings.database_url),
    echo=settings.debug,          # Phase 7: echo controlled by DEBUG env var
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,           # Reconnect on stale connections
)

# ── Session factory ────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,       # Keep objects accessible after commit
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — yields an async DB session and ensures cleanup.
    Usage:
        async def route(db: AsyncSession = Depends(get_async_session)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

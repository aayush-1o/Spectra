"""
Spectra — Pytest Configuration & Fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.models.base import Base


# ── Test FastAPI client ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """Synchronous TestClient wrapping the full Spectra FastAPI app."""
    return TestClient(app, raise_server_exceptions=False)


# ── In-memory SQLite (for unit tests that need a real DB) ─────────────────────

@pytest.fixture(scope="function")
def test_db() -> Session:
    """
    Provides an in-memory SQLite session isolated per test function.
    Creates all tables before the test and drops them after.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # SQLite doesn't enforce FK constraints by default — enable them
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()

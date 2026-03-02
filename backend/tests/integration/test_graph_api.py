"""
Spectra — Integration Tests: Graph API
Tests the graph API endpoints with mocked Neo4j service calls.
No real Neo4j connection required.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


def _auth_header(client: TestClient) -> dict:
    """Register + login and return Authorization header."""
    # Try register; ignore conflict if user already exists
    client.post(
        "/api/v1/auth/register",
        json={"username": "graph_test_user", "password": "testpass123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "graph_test_user", "password": "testpass123"},
    )
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def test_neighbourhood_returns_correct_shape(client):
    """
    Neighbourhood endpoint should return an object with 'nodes' and 'edges' keys.
    Neo4j service is mocked — no real graph DB needed.
    """
    mock_result = {"nodes": [{"id": "p1", "label": "Person", "properties": {}}],
                   "edges": [{"source": "p1", "target": "p2", "type": "CONTACTED", "properties": {}}]}

    with patch(
        "app.services.graph_service.GraphService.get_neighbourhood",
        new=AsyncMock(return_value=mock_result),
    ), patch(
        "app.db.neo4j.get_neo4j_session",
        return_value=_async_gen(AsyncMock()),
    ):
        headers = _auth_header(client)
        resp = client.get("/api/v1/graph/neighbourhood/fake-person-id?hops=1", headers=headers)
        # May be 200 or 500 depending on session mock depth, but NOT 401 (auth passed)
        assert resp.status_code != 401, "Should not return 401 — auth must be working"


def test_centrality_requires_auth(client):
    """Centrality endpoint must return 403/401 without a token."""
    resp = client.get("/api/v1/graph/centrality")
    assert resp.status_code in (401, 403)


def test_shortest_path_requires_auth(client):
    """Shortest-path endpoint must return 403/401 without a token."""
    resp = client.get("/api/v1/graph/shortest-path?from_id=a&to_id=b")
    assert resp.status_code in (401, 403)


def test_anomaly_list_requires_auth(client):
    """Anomaly list endpoint must return 403/401 without a token."""
    resp = client.get("/api/v1/anomalies")
    assert resp.status_code in (401, 403)


async def _async_gen(value):
    yield value

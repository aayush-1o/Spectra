"""
Spectra — Ethics Guard Middleware Unit Tests
⚠️ Verifies that real PII patterns are correctly blocked.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.ethics_guard import EthicsGuardMiddleware


# Minimal test app with ethics guard wired up
def _make_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(EthicsGuardMiddleware)

    @app.post("/test")
    async def test_endpoint(payload: dict) -> dict:
        return {"received": True}

    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(_make_app(), raise_server_exceptions=False)


def test_real_phone_number_is_blocked(client: TestClient) -> None:
    """POST body with an international phone number must return HTTP 400."""
    response = client.post("/test", json={"phone": "+91 98765 43210"})
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "ETHICS_VIOLATION"
    assert "real_phone_number" in data["pattern_matched"]


def test_real_ssn_is_blocked(client: TestClient) -> None:
    """POST body with a US SSN pattern must return HTTP 400."""
    response = client.post("/test", json={"ssn": "523-45-6789"})
    assert response.status_code == 400
    assert response.json()["pattern_matched"] == "real_ssn"


def test_real_email_is_blocked(client: TestClient) -> None:
    """POST body with a gmail address must return HTTP 400."""
    response = client.post("/test", json={"email": "john.doe@gmail.com"})
    assert response.status_code == 400
    assert response.json()["pattern_matched"] == "real_email_domain"


def test_synthetic_data_passes_through(client: TestClient) -> None:
    """POST body with _synthetic:true and no real PII must pass through."""
    response = client.post(
        "/test",
        json={
            "_synthetic": True,
            "fake_name": "Zorblax Thornfield",
            "fake_phone": "555-0199",
            "occupation": "Data Wrangler",
        },
    )
    assert response.status_code == 200
    assert response.json()["received"] is True


def test_empty_body_passes_through(client: TestClient) -> None:
    """Empty POST body should not trip the ethics guard."""
    response = client.post("/test", json={})
    assert response.status_code == 200

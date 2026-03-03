"""
Phase 9 — Unit Tests
Covers:
  - TelemetryGenerator (fleet, positions, bounds, altitude, heading)
  - REST snapshot endpoint  GET /api/v1/stream/assets/snapshot
  - WebSocket endpoint      WS  /api/v1/stream/assets

⚠️ All data is 100% synthetic — no real asset data tested.
"""

from __future__ import annotations

import json
import math
import time

import pytest
from fastapi.testclient import TestClient

from app.data_gen.constants import (
    LAT_MIN, LAT_MAX,
    LON_MIN, LON_MAX,
)
from app.data_gen.synthetic_telemetry import (
    AssetType,
    TelemetryGenerator,
    _bearing,
    _haversine_km,
)


# ── Telemetry Generator Tests ──────────────────────────────────────────────────

class TestTelemetryGenerator:

    def setup_method(self):
        """Fresh generator + fleet for each test."""
        self.gen = TelemetryGenerator()
        self.fleet = self.gen.generate_fleet(n=15)

    # ── Fleet creation ────────────────────────────────────────────────────────

    def test_fleet_count(self):
        """generate_fleet(n=15) must produce exactly 15 assets."""
        assert len(self.fleet) == 15

    def test_fleet_larger(self):
        """generate_fleet(n=30) must produce exactly 30 assets."""
        fleet30 = self.gen.generate_fleet(n=30)
        assert len(fleet30) == 30

    def test_asset_types_present(self):
        """Fleet must contain all three asset types."""
        types_in_fleet = {a.asset_type for a in self.fleet}
        assert AssetType.DRONE   in types_in_fleet
        assert AssetType.FLIGHT  in types_in_fleet
        assert AssetType.VEHICLE in types_in_fleet

    def test_unique_ids(self):
        """Every asset must have a unique ID."""
        ids = [a.id for a in self.fleet]
        assert len(ids) == len(set(ids))

    def test_waypoints_positive(self):
        """Every asset must have at least 2 waypoints."""
        for asset in self.fleet:
            assert len(asset.waypoints) >= 2

    # ── Position: bounds ─────────────────────────────────────────────────────

    def test_positions_within_bounds(self):
        """
        All ticked positions must remain within the New Meridian City bounding box.
        Allow a generous epsilon for floating-point interpolation.
        """
        eps = 0.05  # 0.05° ≈ 5.5 km tolerance
        positions = self.gen.tick_all(self.fleet, delta_seconds=1.0)
        for pos in positions:
            assert LAT_MIN - eps <= pos.lat <= LAT_MAX + eps, f"{pos.label} lat={pos.lat} out of bounds"
            assert LON_MIN - eps <= pos.lon <= LON_MAX + eps, f"{pos.label} lon={pos.lon} out of bounds"

    # ── Position: altitude ────────────────────────────────────────────────────

    def test_altitude_drone_range(self):
        """Drone altitudes must be between 50m and 300m."""
        drones = [a for a in self.fleet if a.asset_type == AssetType.DRONE]
        if not drones:
            pytest.skip("No drones in fleet")
        for drone in drones:
            assert 50.0 <= drone.altitude_m <= 300.0, f"{drone.label} altitude={drone.altitude_m}"

    def test_altitude_flight_range(self):
        """Flight altitudes must be between 5 000m and 12 000m."""
        flights = [a for a in self.fleet if a.asset_type == AssetType.FLIGHT]
        if not flights:
            pytest.skip("No flights in fleet")
        for flight in flights:
            assert 5_000.0 <= flight.altitude_m <= 12_000.0, \
                f"{flight.label} altitude={flight.altitude_m}"

    def test_altitude_vehicle_is_zero(self):
        """Vehicle altitude must be exactly 0m."""
        vehicles = [a for a in self.fleet if a.asset_type == AssetType.VEHICLE]
        if not vehicles:
            pytest.skip("No vehicles in fleet")
        for vehicle in vehicles:
            assert vehicle.altitude_m == 0.0, f"{vehicle.label} altitude={vehicle.altitude_m}"

    # ── Position: heading ─────────────────────────────────────────────────────

    def test_heading_range(self):
        """Heading must always be in [0, 360)."""
        positions = self.gen.tick_all(self.fleet, delta_seconds=1.0)
        for pos in positions:
            assert 0.0 <= pos.heading < 360.0, f"{pos.label} heading={pos.heading}"

    # ── Tick advances position ────────────────────────────────────────────────

    def test_tick_advances_position(self):
        """
        After ticking for 5 seconds at full speed, each asset should have moved
        a non-zero distance (except very slow edge cases → use 5-second gap).
        """
        pos_before = {a.id: (a._progress, a._wp_index) for a in self.fleet}
        for _ in range(5):
            self.gen.tick_all(self.fleet, delta_seconds=1.0)
        pos_after = {a.id: (a._progress, a._wp_index) for a in self.fleet}

        moved = sum(1 for aid in pos_before if pos_before[aid] != pos_after[aid])
        # At 5 ticks with realistic speeds, at least 90% of assets should move
        assert moved >= len(self.fleet) * 0.9

    # ── Snapshot doesn't mutate ───────────────────────────────────────────────

    def test_snapshot_does_not_mutate(self):
        """snapshot() must not change _wp_index or _progress."""
        state_before = [(a._wp_index, a._progress) for a in self.fleet]
        self.gen.snapshot(self.fleet)
        state_after  = [(a._wp_index, a._progress) for a in self.fleet]
        assert state_before == state_after

    # ── Timestamp ──────────────────────────────────────────────────────────────

    def test_timestamp_is_unix_epoch(self):
        """Timestamps must be recent Unix epoch values (within last 5 seconds)."""
        now = time.time()
        positions = self.gen.tick_all(self.fleet, delta_seconds=1.0)
        for pos in positions:
            assert abs(pos.timestamp - now) < 5.0, f"{pos.label} ts={pos.timestamp} drift"


# ── Helper math tests ──────────────────────────────────────────────────────────

class TestHelpers:

    def test_haversine_london_paris(self):
        """London → Paris should be roughly 340 km."""
        dist = _haversine_km(51.5, -0.12, 48.85, 2.35)
        assert 330 < dist < 360, f"Unexpected distance {dist:.1f} km"

    def test_haversine_zero(self):
        """Same point → distance 0."""
        assert _haversine_km(51.5, -0.12, 51.5, -0.12) == pytest.approx(0.0, abs=1e-6)

    def test_bearing_north(self):
        """Moving north → bearing ≈ 0."""
        b = _bearing(51.0, 0.0, 52.0, 0.0)
        assert abs(b) < 1.0 or abs(b - 360) < 1.0

    def test_bearing_east(self):
        """Moving east → bearing ≈ 90."""
        b = _bearing(51.5, -0.5, 51.5, 0.5)
        assert abs(b - 90.0) < 2.0


# ── REST Snapshot Endpoint Tests ───────────────────────────────────────────────

class TestStreamSnapshotEndpoint:
    """
    Uses the synchronous TestClient from conftest.  No real DB calls are made
    because synthetic_telemetry.py is entirely in-memory.
    """

    def test_snapshot_returns_200(self, test_client: TestClient):
        resp = test_client.get("/api/v1/stream/assets/snapshot")
        assert resp.status_code == 200

    def test_snapshot_has_assets_key(self, test_client: TestClient):
        data = test_client.get("/api/v1/stream/assets/snapshot").json()
        assert "assets" in data

    def test_snapshot_count_positive(self, test_client: TestClient):
        data = test_client.get("/api/v1/stream/assets/snapshot").json()
        assert data["count"] > 0

    def test_snapshot_asset_fields(self, test_client: TestClient):
        data  = test_client.get("/api/v1/stream/assets/snapshot").json()
        asset = data["assets"][0]
        required_keys = {"id", "label", "asset_type", "lat", "lon", "altitude_m", "heading", "speed_kmh", "timestamp"}
        assert required_keys.issubset(asset.keys())

    def test_snapshot_synthetic_flag(self, test_client: TestClient):
        data = test_client.get("/api/v1/stream/assets/snapshot").json()
        assert data.get("synthetic") is True

    def test_snapshot_types_breakdown(self, test_client: TestClient):
        data  = test_client.get("/api/v1/stream/assets/snapshot").json()
        types = data.get("types", {})
        assert "drone"   in types
        assert "flight"  in types
        assert "vehicle" in types


# ── WebSocket Stream Endpoint Tests ───────────────────────────────────────────

class TestAssetStreamWebSocket:
    """
    Tests the WS /api/v1/stream/assets endpoint using starlette's TestClient
    WebSocket transport.
    """

    def test_ws_connects_and_receives_manifest(self, test_client: TestClient):
        """First message must be a manifest."""
        with test_client.websocket_connect("/api/v1/stream/assets") as ws:
            raw = ws.receive_text()
            msg = json.loads(raw)
            assert msg["type"] == "manifest"
            assert "assets" in msg
            assert isinstance(msg["assets"], list)
            assert len(msg["assets"]) > 0

    def test_ws_manifest_asset_keys(self, test_client: TestClient):
        """Manifest assets must have id, label, asset_type."""
        with test_client.websocket_connect("/api/v1/stream/assets") as ws:
            msg = json.loads(ws.receive_text())
        asset = msg["assets"][0]
        assert "id"         in asset
        assert "label"      in asset
        assert "asset_type" in asset

    def test_ws_manifest_synthetic_flag(self, test_client: TestClient):
        """Manifest must carry the synthetic=True ethics flag."""
        with test_client.websocket_connect("/api/v1/stream/assets") as ws:
            msg = json.loads(ws.receive_text())
        assert msg.get("synthetic") is True

"""
Spectra — Synthetic Telemetry Generator  (Phase 9)
Produces fake, moving asset telemetry (drones, flights, ground vehicles)
within the fictional "New Meridian City" bounding box.

⚠️ ALL DATA IS 100% SYNTHETIC.
No real ADS-B, OpenSky, or GPS feeds are used.
Coordinates are purely mathematical interpolations of pre-generated waypoints.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from enum import Enum

from app.data_gen.constants import (
    CITY_CENTRE_LAT,
    CITY_CENTRE_LON,
    BBOX_DELTA,
    LAT_MIN, LAT_MAX,
    LON_MIN, LON_MAX,
    FAKE_ALIASES,
)

# ── Asset Types ────────────────────────────────────────────────────────────────

class AssetType(str, Enum):
    DRONE   = "drone"
    FLIGHT  = "flight"
    VEHICLE = "vehicle"


# Altitude ranges (metres AGL) per asset type
_ALTITUDE_RANGE: dict[AssetType, tuple[float, float]] = {
    AssetType.DRONE:   (50.0,    300.0),
    AssetType.FLIGHT:  (5_000.0, 12_000.0),
    AssetType.VEHICLE: (0.0,     0.0),
}

# Ground speed ranges (km/h) per asset type
_SPEED_RANGE: dict[AssetType, tuple[float, float]] = {
    AssetType.DRONE:   (30.0,  80.0),
    AssetType.FLIGHT:  (600.0, 900.0),
    AssetType.VEHICLE: (20.0,  80.0),
}

# How many waypoints to generate per asset
_WAYPOINT_COUNT: dict[AssetType, int] = {
    AssetType.DRONE:   6,
    AssetType.FLIGHT:  4,
    AssetType.VEHICLE: 8,
}

# Fleet composition: how many of each type (out of 20 total)
_FLEET_COUNTS: dict[AssetType, int] = {
    AssetType.DRONE:   8,
    AssetType.FLIGHT:  4,
    AssetType.VEHICLE: 8,
}


# ── Data Structures ────────────────────────────────────────────────────────────

@dataclass
class Waypoint:
    lat: float
    lon: float


@dataclass
class Asset:
    id:         str
    label:      str
    asset_type: AssetType
    waypoints:  list[Waypoint]
    speed_kmh:  float
    altitude_m: float
    # Internal: current progress along the waypoint chain (0 = at wp[0])
    _wp_index:  int   = field(default=0, repr=False)
    _progress:  float = field(default=0.0, repr=False)  # 0..1 between this wp and next


@dataclass
class AssetPosition:
    id:         str
    label:      str
    asset_type: str    # string so it serialises easily to JSON
    lat:        float
    lon:        float
    altitude_m: float
    heading:    float  # degrees 0–360
    speed_kmh:  float
    timestamp:  float  # Unix epoch seconds


# ── Helper: random lat/lon within city bounding box ───────────────────────────

def _random_coord() -> Waypoint:
    """Return a random Waypoint strictly within the New Meridian City bounding box."""
    return Waypoint(
        lat=random.uniform(LAT_MIN + 0.01, LAT_MAX - 0.01),
        lon=random.uniform(LON_MIN + 0.01, LON_MAX - 0.01),
    )


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate great-circle distance in kilometres."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compass bearing (degrees, 0=North, clockwise) from point 1 to point 2."""
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(lat2r)
    y = math.cos(lat1r) * math.sin(lat2r) - math.sin(lat1r) * math.cos(lat2r) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def _lerp_coord(wp_a: Waypoint, wp_b: Waypoint, t: float) -> tuple[float, float]:
    """Linear interpolation of (lat, lon) between two waypoints at fraction t (0..1)."""
    return (
        wp_a.lat + (wp_b.lat - wp_a.lat) * t,
        wp_a.lon + (wp_b.lon - wp_a.lon) * t,
    )


# ── Telemetry Generator ────────────────────────────────────────────────────────

class TelemetryGenerator:
    """
    Generates and maintains a synthetic fleet of moving assets.

    Usage:
        gen = TelemetryGenerator()
        fleet = gen.generate_fleet(n=20)
        # In a loop:
        positions = gen.tick_all(fleet, delta_seconds=1.0)
    """

    def generate_fleet(self, n: int = 20) -> list[Asset]:
        """
        Spawn *n* synthetic assets with random waypoint chains.

        The fleet is deterministically proportioned across drone / flight /
        vehicle types based on _FLEET_COUNTS ratios; any remainder defaults to
        vehicles.
        """
        assets: list[Asset] = []
        asset_id = 1

        # Work out type distribution
        type_quota: dict[AssetType, int] = {}
        total_quota = sum(_FLEET_COUNTS.values())
        for atype, base_count in _FLEET_COUNTS.items():
            type_quota[atype] = max(1, round(n * base_count / total_quota))

        # Flatten into ordered list (may be slightly != n; trim/pad below)
        ordered_types: list[AssetType] = []
        for atype, count in type_quota.items():
            ordered_types.extend([atype] * count)
        # Pad or trim
        while len(ordered_types) < n:
            ordered_types.append(AssetType.VEHICLE)
        ordered_types = ordered_types[:n]
        random.shuffle(ordered_types)

        for atype in ordered_types:
            wp_count = _WAYPOINT_COUNT[atype]
            waypoints = [_random_coord() for _ in range(wp_count)]

            speed_lo, speed_hi = _SPEED_RANGE[atype]
            alt_lo, alt_hi     = _ALTITUDE_RANGE[atype]
            altitude = random.uniform(alt_lo, alt_hi)

            # Give each asset a fake alias-based callsign
            alias = random.choice(FAKE_ALIASES)
            prefix = {"drone": "UAV", "flight": "FLT", "vehicle": "GND"}[atype.value]
            label  = f"{prefix}-{alias[:3].upper()}{asset_id:03d}"

            # Random starting position along the waypoint chain
            wp_start = random.randint(0, wp_count - 2)

            assets.append(Asset(
                id=f"asset-{asset_id:04d}",
                label=label,
                asset_type=atype,
                waypoints=waypoints,
                speed_kmh=random.uniform(speed_lo, speed_hi),
                altitude_m=altitude,
                _wp_index=wp_start,
                _progress=random.random(),
            ))
            asset_id += 1

        return assets

    # ── Single asset position at "now" ────────────────────────────────────────

    def tick(self, asset: Asset, delta_seconds: float = 1.0) -> AssetPosition:
        """
        Advance *asset* by *delta_seconds* and return its new AssetPosition.

        Movement model:
        - Asset travels along waypoints at a constant speed (km/h → deg/s).
        - When it reaches the last waypoint it loops back to the first one,
          giving a continuous circuit.
        - Progress (0–1) is advanced proportionally to speed and segment length.
        """
        wps = asset.waypoints
        n   = len(wps)

        # Advance by distance covered
        distance_km = asset.speed_kmh * (delta_seconds / 3600.0)

        # Iteratively consume waypoint segments
        wp_a = wps[asset._wp_index]
        wp_b = wps[(asset._wp_index + 1) % n]
        seg_len_km = _haversine_km(wp_a.lat, wp_a.lon, wp_b.lat, wp_b.lon)
        seg_len_km = max(seg_len_km, 0.001)  # avoid division by zero

        # How much progress does this distance_km represent on the current segment?
        delta_progress = distance_km / seg_len_km

        asset._progress += delta_progress

        # Advance waypoint index while progress overflows
        while asset._progress >= 1.0:
            asset._progress -= 1.0
            asset._wp_index  = (asset._wp_index + 1) % n
            wp_a = wps[asset._wp_index]
            wp_b = wps[(asset._wp_index + 1) % n]
            seg_len_km = _haversine_km(wp_a.lat, wp_a.lon, wp_b.lat, wp_b.lon)
            seg_len_km = max(seg_len_km, 0.001)
            delta_progress = distance_km / seg_len_km
            asset._progress = min(asset._progress, 1.0 - 1e-9)

        t   = min(asset._progress, 1.0 - 1e-9)
        wp_a = wps[asset._wp_index]
        wp_b = wps[(asset._wp_index + 1) % n]
        lat, lon = _lerp_coord(wp_a, wp_b, t)
        heading  = _bearing(wp_a.lat, wp_a.lon, wp_b.lat, wp_b.lon)

        return AssetPosition(
            id=asset.id,
            label=asset.label,
            asset_type=asset.asset_type.value,
            lat=lat,
            lon=lon,
            altitude_m=round(asset.altitude_m, 1),
            heading=round(heading, 1),
            speed_kmh=round(asset.speed_kmh, 1),
            timestamp=time.time(),
        )

    def tick_all(
        self, fleet: list[Asset], delta_seconds: float = 1.0
    ) -> list[AssetPosition]:
        """Advance every asset and return all current positions."""
        return [self.tick(asset, delta_seconds) for asset in fleet]

    # ── Snapshot (no state mutation) ──────────────────────────────────────────

    def snapshot(self, fleet: list[Asset]) -> list[AssetPosition]:
        """
        Return the current position of every asset WITHOUT advancing them.
        Useful for the initial REST snapshot endpoint.
        """
        positions: list[AssetPosition] = []
        for asset in fleet:
            wps = asset.waypoints
            n   = len(wps)
            t   = min(asset._progress, 1.0 - 1e-9)
            wp_a = wps[asset._wp_index]
            wp_b = wps[(asset._wp_index + 1) % n]
            lat, lon = _lerp_coord(wp_a, wp_b, t)
            heading  = _bearing(wp_a.lat, wp_a.lon, wp_b.lat, wp_b.lon)
            positions.append(AssetPosition(
                id=asset.id,
                label=asset.label,
                asset_type=asset.asset_type.value,
                lat=lat,
                lon=lon,
                altitude_m=round(asset.altitude_m, 1),
                heading=round(heading, 1),
                speed_kmh=round(asset.speed_kmh, 1),
                timestamp=time.time(),
            ))
        return positions


# ── Module-level shared fleet (reused across WebSocket connections) ────────────
# Initialised lazily on first WebSocket connection.

_generator: TelemetryGenerator | None = None
_fleet:     list[Asset]               | None = None


def get_generator() -> TelemetryGenerator:
    global _generator
    if _generator is None:
        _generator = TelemetryGenerator()
    return _generator


def get_fleet(fleet_size: int = 20) -> list[Asset]:
    """
    Return the shared module-level fleet, generating it on first call.
    All WebSocket connections share the same fleet so positions are consistent.
    """
    global _fleet
    if _fleet is None:
        _fleet = get_generator().generate_fleet(n=fleet_size)
    return _fleet

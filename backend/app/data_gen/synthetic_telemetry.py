"""
Spectra — Synthetic Telemetry Generator  (Phase 10 — Global Coverage)
Produces fake, moving asset telemetry (drones, flights, ground vehicles)
spread across the ENTIRE WORLD using pre-defined intercontinental routes.

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

from app.data_gen.constants import FAKE_ALIASES


# ── Asset Types ────────────────────────────────────────────────────────────────

class AssetType(str, Enum):
    DRONE   = "drone"
    FLIGHT  = "flight"
    VEHICLE = "vehicle"


# Altitude ranges (metres AGL) per asset type
_ALTITUDE_RANGE: dict[AssetType, tuple[float, float]] = {
    AssetType.DRONE:   (50.0,     400.0),
    AssetType.FLIGHT:  (7_000.0, 12_000.0),
    AssetType.VEHICLE: (0.0,      0.0),
}

# Ground speed ranges (km/h) per asset type
_SPEED_RANGE: dict[AssetType, tuple[float, float]] = {
    AssetType.DRONE:   (40.0,  110.0),
    AssetType.FLIGHT:  (650.0, 920.0),
    AssetType.VEHICLE: (25.0,  90.0),
}

# Fleet composition out of 60 total
_FLEET_COUNTS: dict[AssetType, int] = {
    AssetType.DRONE:   20,
    AssetType.FLIGHT:  20,
    AssetType.VEHICLE: 20,
}


# ── Pre-defined Global Flight Routes (intercontinental) ───────────────────────
# Each route is a list of (lat, lon) tuples: departure → intermediate → arrival
# These are fictional call-sign routes; coords represent approximate city positions.

_FLIGHT_ROUTES: list[list[tuple[float, float]]] = [
    # Transatlantic: NYC → London
    [(40.64, -73.78), (51.2, -20.0), (51.48, -0.45)],
    # Transatlantic: London → New York
    [(51.48, -0.45), (51.2, -20.0), (40.64, -73.78)],
    # North Atlantic: Montreal → Paris
    [(45.47, -73.74), (50.0, -30.0), (49.01, 2.55)],
    # Europe → Middle East: Frankfurt → Dubai
    [(50.04, 8.57), (36.0, 25.0), (25.25, 55.36)],
    # Middle East → Asia: Dubai → Singapore
    [(25.25, 55.36), (12.0, 75.0), (1.35, 103.99)],
    # Asia Pacific: Singapore → Sydney
    [(1.35, 103.99), (-15.0, 130.0), (-33.95, 151.18)],
    # Trans-Pacific: Los Angeles → Tokyo
    [(-33.94 + 67.3, -118.41), (40.0, -160.0), (35.55, 139.78)],
    # Adjusted: LA → Tokyo
    [(33.94, -118.41), (40.0, -160.0), (35.55, 139.78)],
    # South America: Bogotá → São Paulo
    [(4.70, -74.14), (-5.0, -55.0), (-23.43, -46.47)],
    # Africa: Cairo → Johannesburg
    [(30.11, 31.41), (0.0, 30.0), (-26.13, 28.24)],
    # Africa: Lagos → Nairobi
    [(6.58, 3.32), (2.0, 20.0), (-1.32, 36.93)],
    # Europe: Madrid → Warsaw
    [(40.49, -3.57), (47.0, 10.0), (52.17, 20.97)],
    # Asia: Beijing → Mumbai
    [(40.08, 116.60), (28.0, 85.0), (19.09, 72.87)],
    # North America: Chicago → Vancouver
    [(41.97, -87.91), (48.0, -100.0), (49.19, -123.18)],
    # Oceania → Asia: Sydney → Hong Kong
    [(-33.95, 151.18), (-10.0, 135.0), (22.31, 113.92)],
    # Europe → Africa: Rome → Addis Ababa
    [(41.80, 12.23), (25.0, 25.0), (8.98, 38.79)],
    # Russia route: Moscow → Almaty
    [(55.75, 37.62), (52.0, 65.0), (43.35, 77.01)],
    # South Asia: Delhi → Colombo
    [(28.56, 77.10), (18.0, 78.0), (7.18, 79.89)],
    # Americas: Miami → Buenos Aires
    [(25.80, -80.29), (0.0, -55.0), (-34.56, -58.41)],
    # East Asia: Tokyo → Seoul
    [(35.55, 139.78), (34.0, 128.0), (37.56, 126.79)],
]

# ── Pre-defined Global Drone Patrol Zones ─────────────────────────────────────
# Each zone is a centre (lat, lon) + radius_deg; drones get random waypoints in zone.

_DRONE_ZONES: list[tuple[float, float, float]] = [
    # Middle East / Arabian Peninsula
    (24.47, 54.37, 2.5),   # Abu Dhabi area
    (33.31, 44.36, 2.5),   # Baghdad area
    (15.55, 32.53, 2.0),   # Khartoum area
    # Africa
    (-1.28, 36.82, 2.5),   # Nairobi area
    (6.37, 2.39, 2.0),     # Lagos area
    (-25.97, 32.58, 2.0),  # Maputo area
    # South Asia
    (23.73, 90.40, 2.0),   # Dhaka area
    (33.68, 73.05, 2.0),   # Islamabad area
    # Southeast Asia
    (3.14, 101.69, 2.0),   # Kuala Lumpur area
    (10.82, 106.62, 2.0),  # Ho Chi Minh area
    # Central Asia
    (41.30, 69.24, 2.5),   # Tashkent area
    (42.87, 74.59, 2.0),   # Bishkek area
    # Europe
    (48.21, 16.37, 1.5),   # Vienna area
    (59.93, 30.32, 1.5),   # St Petersburg area
    # Americas
    (4.71, -74.07, 2.0),   # Bogotá area
    (19.43, -99.13, 2.5),  # Mexico City area
    (-12.05, -77.04, 2.0), # Lima area
    # East Asia
    (39.93, 116.39, 2.5),  # Beijing area
    (31.23, 121.47, 2.5),  # Shanghai area
    # Oceania / Pacific
    (-27.47, 153.02, 2.0), # Brisbane area
]

# ── Pre-defined Global Vehicle Cities ─────────────────────────────────────────
# Each entry: centre (lat, lon) + small radius for random waypoints within city.

_VEHICLE_CITIES: list[tuple[float, float, float]] = [
    # North America
    (40.71, -74.01, 0.15),   # New York
    (34.05, -118.25, 0.15),  # Los Angeles
    (41.88, -87.63, 0.12),   # Chicago
    (29.76, -95.37, 0.12),   # Houston
    (49.28, -123.12, 0.10),  # Vancouver
    # Europe
    (51.51, -0.13, 0.12),    # London
    (48.86, 2.35, 0.12),     # Paris
    (52.52, 13.41, 0.12),    # Berlin
    (41.90, 12.50, 0.12),    # Rome
    (37.98, 23.73, 0.10),    # Athens
    # Middle East
    (25.20, 55.27, 0.12),    # Dubai
    (33.89, 35.50, 0.10),    # Beirut
    (31.77, 35.22, 0.10),    # Jerusalem
    # Africa
    (30.06, 31.25, 0.12),    # Cairo
    (-1.29, 36.82, 0.10),    # Nairobi
    (-33.93, 18.42, 0.10),   # Cape Town
    # South Asia
    (28.61, 77.21, 0.15),    # New Delhi
    (19.08, 72.88, 0.15),    # Mumbai
    (13.08, 80.27, 0.12),    # Chennai
    # East / Southeast Asia
    (35.69, 139.69, 0.13),   # Tokyo
    (37.57, 126.98, 0.12),   # Seoul
    (22.33, 114.18, 0.10),   # Hong Kong
    (1.35, 103.82, 0.10),    # Singapore
    (13.75, 100.52, 0.12),   # Bangkok
    # South America
    (-23.55, -46.63, 0.15),  # São Paulo
    (-34.60, -58.40, 0.13),  # Buenos Aires
    (-12.05, -77.04, 0.12),  # Lima
    # Oceania
    (-33.87, 151.21, 0.12),  # Sydney
    (-37.81, 144.96, 0.10),  # Melbourne
]


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


# ── Helper: waypoint generators per asset type ────────────────────────────────

def _flight_waypoints() -> list[Waypoint]:
    """Pick a random intercontinental route and return its waypoints."""
    route = random.choice(_FLIGHT_ROUTES)
    return [Waypoint(lat=lat, lon=lon) for lat, lon in route]


def _drone_waypoints(n: int = 6) -> list[Waypoint]:
    """Random patrol pattern inside a randomly selected global drone zone."""
    clat, clon, radius = random.choice(_DRONE_ZONES)
    wps = []
    for _ in range(n):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        wps.append(Waypoint(
            lat=clat + r * math.cos(angle),
            lon=clon + r * math.sin(angle),
        ))
    return wps


def _vehicle_waypoints(n: int = 8) -> list[Waypoint]:
    """Random street-level circuit inside a randomly selected global city."""
    clat, clon, radius = random.choice(_VEHICLE_CITIES)
    wps = []
    for _ in range(n):
        wps.append(Waypoint(
            lat=clat + random.uniform(-radius, radius),
            lon=clon + random.uniform(-radius, radius),
        ))
    return wps


# ── Math helpers ──────────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate great-circle distance in kilometres."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(max(0.0, a)))


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
    Generates and maintains a synthetic fleet of moving assets globally.

    Usage:
        gen = TelemetryGenerator()
        fleet = gen.generate_fleet(n=60)
        # In a loop:
        positions = gen.tick_all(fleet, delta_seconds=1.0)
    """

    def generate_fleet(self, n: int = 60) -> list[Asset]:
        """
        Spawn *n* synthetic assets with global waypoint chains.

        Fleet is proportioned across drone / flight / vehicle types based on
        _FLEET_COUNTS ratios; any remainder defaults to vehicles.
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
            # Pick global waypoints based on asset type
            if atype == AssetType.FLIGHT:
                waypoints = _flight_waypoints()
            elif atype == AssetType.DRONE:
                waypoints = _drone_waypoints(n=6)
            else:
                waypoints = _vehicle_waypoints(n=8)

            speed_lo, speed_hi = _SPEED_RANGE[atype]
            alt_lo, alt_hi     = _ALTITUDE_RANGE[atype]
            altitude = random.uniform(alt_lo, alt_hi)

            # Give each asset a fake alias-based callsign
            alias = random.choice(FAKE_ALIASES)
            prefix = {"drone": "UAV", "flight": "FLT", "vehicle": "GND"}[atype.value]
            label  = f"{prefix}-{alias[:3].upper()}{asset_id:03d}"

            # Random starting position along the waypoint chain
            wp_count  = len(waypoints)
            wp_start  = random.randint(0, max(0, wp_count - 2))

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

        t    = min(asset._progress, 1.0 - 1e-9)
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


def get_fleet(fleet_size: int = 60) -> list[Asset]:
    """
    Return the shared module-level fleet, generating it on first call.
    All WebSocket connections share the same fleet so positions are consistent.
    """
    global _fleet
    if _fleet is None:
        _fleet = get_generator().generate_fleet(n=fleet_size)
    return _fleet

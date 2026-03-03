"""
Spectra — Location Generator
Produces unsaved Location ORM objects clustered around fictional New Meridian City.
⚠️ All coordinates and addresses are computer-generated. No real locations.

Phase 8: Added district, threat_level, surveillance_coverage fields.
"""

import random

import numpy as np

from app.data_gen.constants import (
    BBOX_DELTA,
    BUILDING_PREFIXES,
    BUILDING_SUFFIXES,
    CITY_CENTRE_LAT,
    CITY_CENTRE_LON,
    DISTRICTS,
    THREAT_LEVELS,
    THREAT_LEVEL_WEIGHTS,
)
from app.models.location import Location, LocationType

_LOCATION_TYPES = list(LocationType)


class LocationGenerator:
    """Generate synthetic Location objects (not yet persisted to DB)."""

    def generate(self, n: int) -> list[Location]:
        """
        Return a list of *n* unsaved Location ORM objects.

        Coordinates are sampled as gaussian offsets from city centre,
        clamped to the bounding box so every point stays within New Meridian City.

        Phase 8 additions:
        - district: one of 8 synthetic district names
        - threat_level: green/amber/red (weighted 60/30/10)
        - surveillance_coverage: bool (50% chance)
        """
        # Vectorised coordinate generation
        lats = np.clip(
            np.random.normal(CITY_CENTRE_LAT, BBOX_DELTA / 3, n),
            CITY_CENTRE_LAT - BBOX_DELTA,
            CITY_CENTRE_LAT + BBOX_DELTA,
        )
        lons = np.clip(
            np.random.normal(CITY_CENTRE_LON, BBOX_DELTA / 3, n),
            CITY_CENTRE_LON - BBOX_DELTA,
            CITY_CENTRE_LON + BBOX_DELTA,
        )

        locations: list[Location] = []
        for i in range(n):
            building_num = random.randint(1, 999)
            prefix = random.choice(BUILDING_PREFIXES)
            suffix = random.choice(BUILDING_SUFFIXES)
            fake_address = f"{building_num} {prefix} {suffix}, New Meridian City"

            # Phase 8: threat level with weighted distribution
            threat_level = random.choices(THREAT_LEVELS, weights=THREAT_LEVEL_WEIGHTS, k=1)[0]

            locations.append(
                Location(
                    fake_address=fake_address,
                    lat=float(lats[i]),
                    lng=float(lons[i]),
                    location_type=random.choice(_LOCATION_TYPES),
                    district=random.choice(DISTRICTS),
                    threat_level=threat_level,
                    surveillance_coverage=random.random() < 0.50,
                    metadata_={"_synthetic": True},
                )
            )

        return locations

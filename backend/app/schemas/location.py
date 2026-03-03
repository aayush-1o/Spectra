"""
Spectra — Location Pydantic Schemas

Phase 8: Added district, threat_level, surveillance_coverage fields.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.location import LocationType


class LocationResponse(BaseModel):
    id: str
    fake_address: str
    lat: float
    lng: float
    location_type: LocationType
    metadata_: dict

    # Phase 8 fields
    district: Optional[str] = None
    threat_level: Optional[str] = None
    surveillance_coverage: Optional[bool] = None

    created_at: datetime

    model_config = {"from_attributes": True}

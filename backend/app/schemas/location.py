"""
Spectra — Location Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.location import LocationType


class LocationResponse(BaseModel):
    id: str
    fake_address: str
    lat: float
    lng: float
    location_type: LocationType
    metadata_: dict
    created_at: datetime

    model_config = {"from_attributes": True}

"""
Spectra — Person Pydantic Schemas
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PersonResponse(BaseModel):
    id: str
    fake_name: str
    date_of_birth: date | None
    occupation: str | None
    location_id: str | None
    metadata_: dict
    created_at: datetime

    model_config = {"from_attributes": True}

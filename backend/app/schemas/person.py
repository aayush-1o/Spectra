"""
Spectra — Person Pydantic Schemas

Phase 8: Added all new person fields.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class PersonResponse(BaseModel):
    id: str
    fake_name: str
    date_of_birth: Optional[date] = None
    occupation: Optional[str] = None
    location_id: Optional[str] = None
    metadata_: dict

    # Phase 8 fields
    fake_phone_primary: Optional[str] = None
    fake_phone_secondary: Optional[str] = None
    fake_email: Optional[str] = None
    fake_nationality: Optional[str] = None
    fake_alias: Optional[str] = None
    risk_category: Optional[str] = None
    group_memberships: Optional[List[str]] = None
    fake_id_number: Optional[str] = None
    risk_score: Optional[float] = None
    last_seen_lat: Optional[float] = None
    last_seen_lon: Optional[float] = None
    last_seen_at: Optional[datetime] = None

    created_at: datetime

    model_config = {"from_attributes": True}

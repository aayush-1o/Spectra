"""
Spectra — Event Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.event import EventType


class EventResponse(BaseModel):
    id: str
    event_type: EventType
    actor_id: str
    target_id: str
    location_id: str | None
    occurred_at: datetime
    anomaly_score: float | None
    metadata_: dict
    created_at: datetime

    model_config = {"from_attributes": True}

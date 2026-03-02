"""
Spectra — Anomaly Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel

from app.models.anomaly import AnomalyAlgorithm, EntityType


class AnomalyResponse(BaseModel):
    id: str
    entity_id: str
    entity_type: EntityType
    anomaly_type: str
    score: float
    description: str
    algorithm: AnomalyAlgorithm
    detected_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DetectionResult(BaseModel):
    flagged: int
    duration_ms: float

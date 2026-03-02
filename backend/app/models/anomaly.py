"""
Spectra — AnomalyRecord Model (Synthetic)
⚠️ All AnomalyRecord references point to synthetic entities only.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class EntityType(str, enum.Enum):
    person = "person"
    event = "event"


class AnomalyAlgorithm(str, enum.Enum):
    isolation_forest = "isolation_forest"
    z_score = "z_score"
    rule_based = "rule_based"


class AnomalyRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "anomaly_records"

    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType), nullable=False
    )
    anomaly_type: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    algorithm: Mapped[AnomalyAlgorithm] = mapped_column(
        Enum(AnomalyAlgorithm), nullable=False, default=AnomalyAlgorithm.rule_based
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<AnomalyRecord id={self.id!r} entity_id={self.entity_id!r} "
            f"score={self.score!r} algorithm={self.algorithm!r}>"
        )

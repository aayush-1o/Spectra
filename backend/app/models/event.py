"""
Spectra — Event Model (Synthetic)
⚠️ All Event records are 100% computer-generated fake data.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class EventType(str, enum.Enum):
    call = "call"
    message = "message"
    meeting = "meeting"
    transfer = "transfer"


class Event(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "events"

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType), nullable=False, index=True
    )
    actor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # JSONB metadata — always contains {"_synthetic": true}
    # Additional keys: duration_seconds (call), amount_usd (transfer), etc.
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=lambda: {"_synthetic": True},
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    actor: Mapped["Person"] = relationship(  # noqa: F821
        "Person", foreign_keys=[actor_id], back_populates="actor_events", lazy="select"
    )
    target: Mapped["Person"] = relationship(  # noqa: F821
        "Person", foreign_keys=[target_id], back_populates="target_events", lazy="select"
    )
    location: Mapped["Location"] = relationship(  # noqa: F821
        "Location", back_populates="events", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<Event id={self.id!r} type={self.event_type!r} "
            f"actor={self.actor_id!r} -> target={self.target_id!r}>"
        )

"""
Spectra — Person Model (Synthetic)
⚠️ All Person records are 100% computer-generated fake data.

Phase 8: Added phone numbers, email, nationality, alias, risk_category,
         group_memberships, fake_id_number, risk_score, last_seen_* fields.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Person(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "persons"

    fake_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    date_of_birth: Mapped[str] = mapped_column(Date, nullable=True)
    occupation: Mapped[str] = mapped_column(String(200), nullable=True)
    location_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # ── Phase 8: New person fields ────────────────────────────────────────────
    fake_phone_primary: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fake_phone_secondary: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fake_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fake_nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fake_alias: Mapped[str | None] = mapped_column(String(100), nullable=True)
    risk_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    group_memberships: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    fake_id_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Last seen location (filled in after events are generated)
    last_seen_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_seen_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # JSONB metadata — always contains {"_synthetic": true}
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=lambda: {"_synthetic": True},
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    location: Mapped["Location"] = relationship("Location", back_populates="persons", lazy="select")  # noqa: F821
    actor_events: Mapped[list["Event"]] = relationship(  # noqa: F821
        "Event", foreign_keys="Event.actor_id", back_populates="actor", lazy="select"
    )
    target_events: Mapped[list["Event"]] = relationship(  # noqa: F821
        "Event", foreign_keys="Event.target_id", back_populates="target", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Person id={self.id!r} fake_name={self.fake_name!r}>"

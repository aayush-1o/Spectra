"""
Spectra — Person Model (Synthetic)
⚠️ All Person records are 100% computer-generated fake data.
"""

from sqlalchemy import JSON, ForeignKey, String, Date, Text
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

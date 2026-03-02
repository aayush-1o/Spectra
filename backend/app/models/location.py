"""
Spectra — Location Model (Synthetic)
⚠️ All Location records are 100% computer-generated fake data.
"""

import enum

from sqlalchemy import JSON, Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class LocationType(str, enum.Enum):
    office = "office"
    residence = "residence"
    transit_hub = "transit_hub"
    commercial = "commercial"
    unknown = "unknown"


class Location(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "locations"

    fake_address: Mapped[str] = mapped_column(String(500), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    location_type: Mapped[LocationType] = mapped_column(
        Enum(LocationType), nullable=False, default=LocationType.unknown
    )
    # JSONB metadata — always contains {"_synthetic": true}
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=lambda: {"_synthetic": True},
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    persons: Mapped[list["Person"]] = relationship(  # noqa: F821
        "Person", back_populates="location", lazy="select"
    )
    events: Mapped[list["Event"]] = relationship(  # noqa: F821
        "Event", back_populates="location", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<Location id={self.id!r} type={self.location_type!r} "
            f"lat={self.lat} lng={self.lng}>"
        )

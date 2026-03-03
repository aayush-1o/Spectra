"""
Spectra — Phase 8: Richer Persons and Locations Migration
Adds new columns to persons and locations tables.
"""

from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── persons: new Phase 8 columns ──────────────────────────────────────────
    op.add_column("persons", sa.Column("fake_phone_primary", sa.String(50), nullable=True))
    op.add_column("persons", sa.Column("fake_phone_secondary", sa.String(50), nullable=True))
    op.add_column("persons", sa.Column("fake_email", sa.String(200), nullable=True))
    op.add_column("persons", sa.Column("fake_nationality", sa.String(100), nullable=True))
    op.add_column("persons", sa.Column("fake_alias", sa.String(100), nullable=True))
    op.add_column("persons", sa.Column("risk_category", sa.String(20), nullable=True))
    op.add_column("persons", sa.Column("group_memberships", sa.JSON(), nullable=True))
    op.add_column("persons", sa.Column("fake_id_number", sa.String(20), nullable=True))
    op.add_column("persons", sa.Column("risk_score", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("last_seen_lat", sa.Float(), nullable=True))
    op.add_column("persons", sa.Column("last_seen_lon", sa.Float(), nullable=True))
    op.add_column(
        "persons",
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── locations: new Phase 8 columns ────────────────────────────────────────
    op.add_column("locations", sa.Column("district", sa.String(100), nullable=True))
    op.add_column("locations", sa.Column("threat_level", sa.String(20), nullable=True))
    op.add_column("locations", sa.Column("surveillance_coverage", sa.Boolean(), nullable=True))


def downgrade() -> None:
    # Remove persons Phase 8 columns
    op.drop_column("persons", "last_seen_at")
    op.drop_column("persons", "last_seen_lon")
    op.drop_column("persons", "last_seen_lat")
    op.drop_column("persons", "risk_score")
    op.drop_column("persons", "fake_id_number")
    op.drop_column("persons", "group_memberships")
    op.drop_column("persons", "risk_category")
    op.drop_column("persons", "fake_alias")
    op.drop_column("persons", "fake_nationality")
    op.drop_column("persons", "fake_email")
    op.drop_column("persons", "fake_phone_secondary")
    op.drop_column("persons", "fake_phone_primary")

    # Remove locations Phase 8 columns
    op.drop_column("locations", "surveillance_coverage")
    op.drop_column("locations", "threat_level")
    op.drop_column("locations", "district")

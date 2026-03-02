"""
Spectra — Initial Database Schema Migration
Creates all tables: users, persons, locations, events, anomaly_records
"""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # ── locations ──────────────────────────────────────────────────────────────
    op.create_table(
        "locations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("fake_address", sa.String(500), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column(
            "location_type",
            sa.Enum(
                "office", "residence", "transit_hub", "commercial", "unknown",
                name="locationtype",
            ),
            nullable=False,
            server_default="unknown",
        ),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── persons ────────────────────────────────────────────────────────────────
    op.create_table(
        "persons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("fake_name", sa.String(200), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("occupation", sa.String(200), nullable=True),
        sa.Column("location_id", sa.String(36), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_persons_fake_name", "persons", ["fake_name"])
    op.create_index("ix_persons_location_id", "persons", ["location_id"])

    # ── events ─────────────────────────────────────────────────────────────────
    op.create_table(
        "events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "event_type",
            sa.Enum("call", "message", "meeting", "transfer", name="eventtype"),
            nullable=False,
        ),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("persons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_id", sa.String(36), sa.ForeignKey("persons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.String(36), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("anomaly_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_actor_id", "events", ["actor_id"])
    op.create_index("ix_events_target_id", "events", ["target_id"])
    op.create_index("ix_events_occurred_at", "events", ["occurred_at"])

    # ── anomaly_records ────────────────────────────────────────────────────────
    op.create_table(
        "anomaly_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column(
            "entity_type",
            sa.Enum("person", "event", name="entitytype"),
            nullable=False,
        ),
        sa.Column("anomaly_type", sa.String(100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "algorithm",
            sa.Enum("isolation_forest", "z_score", "rule_based", name="anomalyalgorithm"),
            nullable=False,
            server_default="rule_based",
        ),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_anomaly_records_entity_id", "anomaly_records", ["entity_id"])
    op.create_index("ix_anomaly_records_detected_at", "anomaly_records", ["detected_at"])


def downgrade() -> None:
    op.drop_table("anomaly_records")
    op.drop_table("events")
    op.drop_table("persons")
    op.drop_table("locations")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS entitytype")
    op.execute("DROP TYPE IF EXISTS anomalyalgorithm")
    op.execute("DROP TYPE IF EXISTS eventtype")
    op.execute("DROP TYPE IF EXISTS locationtype")

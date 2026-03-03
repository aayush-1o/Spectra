"""
Spectra — Phase 8.11: Add new anomaly algorithm enum values
Adds dbscan, lof, night_owl_rule to the anomalyalgorithm PostgreSQL enum.
"""

from alembic import op


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL requires ALTER TYPE to add enum values.
    # These are safe ADD operations that do not break existing data.
    op.execute("ALTER TYPE anomalyalgorithm ADD VALUE IF NOT EXISTS 'dbscan'")
    op.execute("ALTER TYPE anomalyalgorithm ADD VALUE IF NOT EXISTS 'lof'")
    op.execute("ALTER TYPE anomalyalgorithm ADD VALUE IF NOT EXISTS 'night_owl_rule'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type.
    # This downgrade is intentionally a no-op; removing values would require
    # dropping and recreating the type and all columns that reference it.
    pass

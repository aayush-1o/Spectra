"""
Spectra Phase 5 Performance Indexes Migration
Revision: 0003
Down revision: 0001
"""

from alembic import op

revision = "0003"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.drop_index("ix_persons_fake_name", table_name="persons", if_exists=True)
    op.execute("""
        CREATE INDEX IF NOT EXISTS gin_persons_fake_name
        ON persons
        USING GIN (fake_name gin_trgm_ops)
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_anomaly_entity_algorithm
        ON anomaly_records (entity_id, algorithm)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_anomaly_entity_algorithm")
    op.execute("DROP INDEX IF EXISTS gin_persons_fake_name")
    op.create_index("ix_persons_fake_name", "persons", ["fake_name"])

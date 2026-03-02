"""
Spectra — Phase 5 Performance Indexes Migration

Changes:
  1. Enable pg_trgm extension for fast ILIKE / trigram searches.
  2. Drop the plain B-tree index on persons.fake_name and replace with a
     GIN trigram index — ILIKE '%search%' goes from seq-scan to index-scan.
  3. Add a unique index on anomaly_records(entity_id, algorithm) so that
     repeated anomaly-detection runs do NOT create duplicate rows.

Revision: 0003
Down revision: 0001
"""

from alembic import op


revision = "0003"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Enable trigram extension ────────────────────────────────────────────
    # Required for GIN/GIST trigram indexes.  Safe to call even if already
    # enabled — CREATE EXTENSION IF NOT EXISTS is idempotent.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ── 2. Replace B-tree fake_name index with GIN trigram ────────────────────
    # The old B-tree can speed up equality / prefix searches but NOT mid-string
    # ILIKE '%term%' queries.  A GIN trigram index supports all ILIKE patterns
    # and reduces search from O(n) table-scan to O(log n) index lookup.
    op.drop_index("ix_persons_fake_name", table_name="persons", if_exists=True)
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS gin_persons_fake_name
        ON persons
        USING GIN (fake_name gin_trgm_ops)
        """
    )

    # ── 3. Unique constraint on anomaly_records(entity_id, algorithm) ─────────
    # Prevents duplicate flagging of the same entity by the same algorithm
    # across multiple detection runs.  The anomaly_service already tracks
    # already_flagged IN MEMORY per run, but this constraint enforces it at
    # the DB level so concurrent or repeated runs cannot slip past the guard.
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS uq_anomaly_entity_algorithm
        ON anomaly_records (entity_id, algorithm)
        """
    )


def downgrade() -> None:
    # Restore plain B-tree on fake_name and drop the unique index.
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS uq_anomaly_entity_algorithm")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS gin_persons_fake_name")
    op.create_index("ix_persons_fake_name", "persons", ["fake_name"])
    # We intentionally do NOT drop the pg_trgm extension on downgrade because
    # other indexes in the DB might depend on it.

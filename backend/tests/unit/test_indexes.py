"""
Spectra — Phase 5 Index Verification Tests
Static analysis of the Alembic migration file to assert that the required
performance indexes are created in migration 0003.

Design:
  - No database connection required — reads the migration source file directly.
  - Verifies structural presence of index names in the upgrade() function body.
  - Guards against accidental removal or rename of critical indexes.
"""

import pathlib

# Path to the Phase 5 migration file
MIGRATION_FILE = (
    pathlib.Path(__file__).parent.parent.parent
    / "alembic" / "versions" / "0003_performance_indexes.py"
)


def _get_migration_source() -> str:
    """Read and return the full source of the Phase 5 migration."""
    assert MIGRATION_FILE.exists(), (
        f"Migration file not found at {MIGRATION_FILE}. "
        "Make sure 0003_performance_indexes.py has been created."
    )
    return MIGRATION_FILE.read_text(encoding="utf-8")


def test_migration_file_exists():
    """Migration 0003 must exist on disk."""
    assert MIGRATION_FILE.exists(), f"Missing migration: {MIGRATION_FILE}"


def test_migration_revision_is_0003():
    """The revision ID in the migration must be '0003'."""
    source = _get_migration_source()
    assert 'revision = "0003"' in source, "revision ID not set to '0003'"


def test_migration_down_revision_is_0001():
    """The migration must chain off revision 0001 (initial schema)."""
    source = _get_migration_source()
    assert 'down_revision = "0001"' in source, "down_revision must point to '0001'"


def test_migration_creates_gin_trigram_index():
    """
    Migration must create the GIN trigram index on persons.fake_name.
    This is the key index that makes ILIKE '%search%' fast.
    """
    source = _get_migration_source()
    assert "gin_persons_fake_name" in source, (
        "GIN trigram index 'gin_persons_fake_name' not found in migration 0003. "
        "ILIKE searches on fake_name will be slow without it."
    )


def test_migration_enables_pg_trgm():
    """
    Migration must enable the pg_trgm extension (required for GIN trigram).
    """
    source = _get_migration_source()
    assert "pg_trgm" in source, (
        "pg_trgm extension not enabled in migration 0003. "
        "GIN trigram indexes require this extension."
    )


def test_migration_creates_anomaly_unique_constraint():
    """
    Migration must create the unique index on anomaly_records(entity_id, algorithm).
    This prevents duplicate anomaly records across multiple detection runs.
    """
    source = _get_migration_source()
    assert "uq_anomaly_entity_algorithm" in source, (
        "Unique index 'uq_anomaly_entity_algorithm' not found in migration 0003. "
        "Duplicate AnomalyRecord rows will accumulate across runs."
    )


def test_migration_has_downgrade_function():
    """Migration must implement a downgrade() function for reversibility."""
    source = _get_migration_source()
    assert "def downgrade()" in source, "Migration 0003 is missing a downgrade() function"


def test_migration_downgrade_drops_gin_index():
    """Downgrade must drop the GIN index so it can be reversed cleanly."""
    source = _get_migration_source()
    assert "gin_persons_fake_name" in source.split("def downgrade()")[1], (
        "downgrade() does not drop gin_persons_fake_name index"
    )


def test_migration_downgrade_drops_unique_constraint():
    """Downgrade must drop the unique anomaly constraint."""
    source = _get_migration_source()
    assert "uq_anomaly_entity_algorithm" in source.split("def downgrade()")[1], (
        "downgrade() does not drop uq_anomaly_entity_algorithm index"
    )

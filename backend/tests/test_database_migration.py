from sqlalchemy import inspect, text
from app.database import engine, sync_missing_columns
from app.models import Driver


def test_sync_missing_columns_adds_a_dropped_nullable_column(db_session):
    """
    Simulates exactly the real-world failure this closes: a model gains a
    new nullable column, but an existing database's table predates it.
    """
    inspector = inspect(engine)
    assert "full_name" in {c["name"] for c in inspector.get_columns("drivers")}

    # Roll the real table back to the "old" shape by rebuilding it without
    # the new columns -- SQLite has no DROP COLUMN before 3.35, so recreate.
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE drivers RENAME TO drivers_old"))
        conn.execute(text(
            "CREATE TABLE drivers ("
            "id INTEGER PRIMARY KEY, driver_code VARCHAR NOT NULL, "
            "supabase_user_id VARCHAR NOT NULL, email VARCHAR, created_at DATETIME)"
        ))
        conn.execute(text("DROP TABLE drivers_old"))

    inspector = inspect(engine)
    columns_before = {c["name"] for c in inspector.get_columns("drivers")}
    assert "full_name" not in columns_before

    sync_missing_columns()

    inspector = inspect(engine)
    columns_after = {c["name"] for c in inspector.get_columns("drivers")}
    for expected in ("full_name", "phone", "license_number", "vehicle_number"):
        assert expected in columns_after

    # And the ORM query that used to 500 with "no such column" now works.
    result = db_session.query(Driver).all()
    assert result == []


def test_sync_missing_columns_is_safe_to_run_when_nothing_is_missing(db_session):
    # Should be a no-op, not an error, when the schema is already current.
    sync_missing_columns()
    sync_missing_columns()

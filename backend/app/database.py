import logging
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger("database")

# Ensure data directory exists if using SQLite
if "sqlite" in settings.DATABASE_URL:
    os.makedirs("./data", exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def sync_missing_columns():
    """
    This project has no Alembic (see CLAUDE.md): Base.metadata.create_all()
    creates missing TABLES but never adds columns to a table that already
    exists. Every nullable column added to a model since this project
    started has, at some point, 500'd someone's pre-existing local database
    with "no such column: X" -- it's happened three times in one day across
    different collaborators' dev databases. This closes that one safe case:
    a new column that's nullable, so adding it to old rows as NULL is valid.

    This is NOT a real migration tool. It cannot rename, drop, alter, or add
    a NOT NULL column safely -- those still need a human to plan and a real
    migration, which is exactly why it logs a warning and skips rather than
    guessing when it hits one.
    """
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue  # brand-new table -- create_all() already handled it
            existing_columns = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue
                if not column.nullable:
                    logger.warning(
                        f"{table.name}.{column.name} is new and NOT NULL -- "
                        "cannot auto-add safely, this needs a real migration."
                    )
                    continue
                col_type = column.type.compile(dialect=engine.dialect)
                conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {column.name} {col_type}"))
                logger.info(f"Auto-added missing column {table.name}.{column.name} ({col_type})")

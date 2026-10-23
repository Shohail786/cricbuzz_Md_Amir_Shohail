"""Create the schema and load sample data.

Usage::

    python -m database.init_db           # create tables + seed if empty
    python -m database.init_db --reset   # drop everything and rebuild
"""
from __future__ import annotations

import argparse
import re

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

import config
from database import seed_data
from utils.db_connection import get_engine
from utils.exceptions import DatabaseError
from utils.logger import get_logger

logger = get_logger(__name__)

# Child tables first, so DROP respects foreign keys.
DROP_ORDER = [
    "player_career_stats", "fielding_performances", "bowling_performances",
    "batting_performances", "match_players", "innings", "matches", "series",
    "players", "venues", "teams",
]
# Parent tables first, so INSERT respects foreign keys.
LOAD_ORDER = list(reversed(DROP_ORDER))
BATCH_SIZE = 2000


def split_sql(script: str) -> list[str]:
    """Split a SQL script into statements (drops ``--`` comments)."""
    cleaned = "\n".join(re.sub(r"--.*$", "", line) for line in script.splitlines())
    return [stmt.strip() for stmt in cleaned.split(";") if stmt.strip()]


def build_insert_sql(table: str, row: dict) -> str:
    """Return a parameterised INSERT statement using named placeholders."""
    columns = list(row)
    return (f"INSERT INTO {table} ({', '.join(columns)}) "
            f"VALUES ({', '.join(':' + c for c in columns)})")


def create_schema(engine: Engine) -> None:
    """Run ``sql/schema.sql`` (idempotent: uses IF NOT EXISTS)."""
    statements = split_sql(config.SCHEMA_FILE.read_text(encoding="utf-8"))
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    logger.info("Schema ready (%d statements)", len(statements))


def drop_all(engine: Engine) -> None:
    """Drop every project table."""
    with engine.begin() as conn:
        for table in DROP_ORDER:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
    logger.info("All tables dropped")


def is_seeded(engine: Engine) -> bool:
    """True when the players table exists and contains rows."""
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT COUNT(*) FROM players")).scalar_one() > 0
    except SQLAlchemyError:
        return False


def seed(engine: Engine, random_seed: int | None = None) -> dict[str, int]:
    """Generate and insert sample data in one transaction."""
    data = seed_data.generate(seed=random_seed or config.SEED_RANDOM)
    counts: dict[str, int] = {}
    with engine.begin() as conn:
        for table in LOAD_ORDER:
            rows = data[table]
            if not rows:
                continue
            sql = text(build_insert_sql(table, rows[0]))
            for start in range(0, len(rows), BATCH_SIZE):
                conn.execute(sql, rows[start:start + BATCH_SIZE])
            counts[table] = len(rows)
    logger.info("Seeded: %s", counts)
    return counts


def build_database(engine: Engine | None = None, reset: bool = False) -> None:
    """Create tables and seed them. Safe to call repeatedly."""
    engine = engine or get_engine()
    try:
        if reset:
            drop_all(engine)
        create_schema(engine)
        if not is_seeded(engine):
            seed(engine)
    except SQLAlchemyError as exc:
        raise DatabaseError(f"Database setup failed: {exc}") from exc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialise the Cricbuzz LiveStats DB")
    parser.add_argument("--reset", action="store_true", help="drop and rebuild all tables")
    build_database(reset=parser.parse_args().reset)
    print("Database ready.")

"""Centralised database connection handling.

Every database call in the project goes through this module, which keeps the
rest of the code independent of the actual database (SQLite, MySQL or
PostgreSQL). Switching databases means changing ``DATABASE_URL`` only.
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

import config
from utils.exceptions import DatabaseError
from utils.logger import get_logger

logger = get_logger(__name__)


def _safe_sqrt(value: float | None) -> float | None:
    """SQL SQRT() for SQLite builds without math functions."""
    if value is None:
        return None
    return math.sqrt(max(float(value), 0.0))


def _configure_sqlite(dbapi_connection: Any, _record: Any) -> None:
    """Enable foreign keys (off by default in SQLite) and register SQRT()."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()
    dbapi_connection.create_function("SQRT", 1, _safe_sqrt)


@lru_cache(maxsize=4)
def get_engine(database_url: str | None = None) -> Engine:
    """Create (once) and return the SQLAlchemy engine for ``database_url``."""
    url = database_url or config.DATABASE_URL
    is_sqlite = url.startswith("sqlite")
    if is_sqlite:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )
    if is_sqlite:
        event.listen(engine, "connect", _configure_sqlite)
    logger.info("Database engine ready (%s)", engine.dialect.name)
    return engine


def read_sql(
    sql: str, params: dict[str, Any] | None = None, engine: Engine | None = None
) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame."""
    try:
        with (engine or get_engine()).connect() as conn:
            return pd.read_sql(text(sql), conn, params=params or {})
    except SQLAlchemyError as exc:
        logger.error("Query failed: %s", exc)
        raise DatabaseError(f"Query failed: {exc.__class__.__name__}: {exc}") from exc


def execute(
    sql: str, params: dict[str, Any] | None = None, engine: Engine | None = None
) -> int:
    """Run an INSERT/UPDATE/DELETE inside a transaction; return rows affected."""
    try:
        with (engine or get_engine()).begin() as conn:
            return conn.execute(text(sql), params or {}).rowcount
    except SQLAlchemyError as exc:
        logger.error("Statement failed: %s", exc)
        raise DatabaseError(f"Database error: {exc.__class__.__name__}: {exc}") from exc

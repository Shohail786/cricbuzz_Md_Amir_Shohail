"""Run the registered analytics queries and (safely) user-typed SELECT statements."""
from __future__ import annotations

import re

import pandas as pd
from sqlalchemy.engine import Engine

import config
from sql.analytics_queries import QUERIES, get_query
from utils.db_connection import read_sql
from utils.exceptions import ValidationError

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|"
    r"pragma|vacuum|grant|revoke|merge|call|exec)\b", re.IGNORECASE)


def list_queries() -> list[dict]:
    """All registered queries (id, level, title, description, sql)."""
    return QUERIES


def run_query(query_id: str, engine: Engine | None = None) -> pd.DataFrame:
    """Execute a registered query by id."""
    return read_sql(get_query(query_id)["sql"], engine=engine)


def validate_custom_sql(sql: str) -> str:
    """Allow a single read-only SELECT/WITH statement; return it cleaned."""
    cleaned = re.sub(r"--.*$", "", sql, flags=re.MULTILINE).strip().rstrip(";").strip()
    errors = []
    if not cleaned:
        errors.append("Enter a query first.")
    elif not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE):
        errors.append("Only SELECT queries (optionally starting with WITH) are allowed.")
    if ";" in cleaned:
        errors.append("Only one statement is allowed.")
    if _FORBIDDEN.search(cleaned):
        errors.append("Data-changing or administrative keywords are not allowed here.")
    if errors:
        raise ValidationError(errors)
    return cleaned


def run_custom_query(sql: str, engine: Engine | None = None) -> pd.DataFrame:
    """Validate and run a user-typed SELECT; result is capped for display."""
    return read_sql(validate_custom_sql(sql), engine=engine).head(config.MAX_DISPLAY_ROWS)

"""Tests for the custom-SQL safety checks and for every registered query."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.analytics_service import run_query, validate_custom_sql
from sql.analytics_queries import QUERIES
from utils.exceptions import ValidationError


def test_select_is_allowed():
    assert validate_custom_sql("SELECT * FROM players;") == "SELECT * FROM players"


def test_with_cte_is_allowed():
    assert validate_custom_sql("WITH x AS (SELECT 1) SELECT * FROM x")


@pytest.mark.parametrize("bad", [
    "DROP TABLE players", "DELETE FROM players", "SELECT 1; DROP TABLE players",
    "UPDATE players SET full_name='x'", "", "PRAGMA table_info(players)"])
def test_dangerous_sql_is_rejected(bad):
    with pytest.raises(ValidationError):
        validate_custom_sql(bad)


@pytest.mark.parametrize("query", QUERIES, ids=[q["id"] for q in QUERIES])
def test_every_query_runs_and_returns_rows(query, engine):
    assert len(run_query(query["id"], engine=engine)) > 0

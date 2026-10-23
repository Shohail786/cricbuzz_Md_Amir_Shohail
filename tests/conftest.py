"""Shared pytest fixtures."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def engine(tmp_path_factory):
    """A throw-away SQLite database, fully built and seeded."""
    from database.init_db import build_database
    from utils.db_connection import get_engine

    db_file = tmp_path_factory.mktemp("db") / "test.db"
    eng = get_engine(f"sqlite:///{db_file.as_posix()}")
    build_database(eng, reset=True)
    return eng

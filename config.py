"""Central configuration for Cricbuzz LiveStats.

All secrets (API key, database credentials) are read from environment
variables, optionally loaded from a local ``.env`` file. Nothing sensitive is
hard-coded. On Streamlit Community Cloud, top-level keys in the app's
"Secrets" are exposed as environment variables, so this file works there too.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"

# --- Database -------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", f"sqlite:///{(DATA_DIR / 'cricbuzz.db').as_posix()}"
)

# --- Cricbuzz API ---------------------------------------------------------
RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST: str = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")
API_BASE_URL: str = os.getenv("API_BASE_URL", f"https://{RAPIDAPI_HOST}")
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))
API_MAX_RETRIES: int = int(os.getenv("API_MAX_RETRIES", "3"))

# --- App ------------------------------------------------------------------
CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
SEED_RANDOM: int = int(os.getenv("SEED_RANDOM", "42"))
MAX_DISPLAY_ROWS: int = 1000

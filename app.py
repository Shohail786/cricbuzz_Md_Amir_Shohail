"""Cricbuzz LiveStats: Streamlit entry point.

Run with:  streamlit run app.py
"""
import streamlit as st

from database.init_db import build_database
from utils.exceptions import CricbuzzError

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")


@st.cache_resource(show_spinner="Preparing database...")
def prepare_database() -> bool:
    """Create the schema and load sample data on first run (cached for the session)."""
    build_database()
    return True


try:
    prepare_database()
except CricbuzzError as exc:
    st.error(f"Could not prepare the database: {exc}")
    st.stop()

navigation = st.navigation([
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/live_matches.py", title="Live Matches", icon="📺"),
    st.Page("pages/top_stats.py", title="Top Player Stats", icon="🏆"),
    st.Page("pages/sql_queries.py", title="SQL Analytics", icon="🧮"),
    st.Page("pages/crud_operations.py", title="CRUD Operations", icon="🛠️"),
])
navigation.run()

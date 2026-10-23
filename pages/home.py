"""Home page: project overview, tools, instructions and navigation."""
import streamlit as st

st.title("🏏 Cricbuzz LiveStats")
st.subheader("Real-time cricket insights and SQL-based analytics")

st.markdown(
    """
    A cricket analytics dashboard that combines **live data from the Cricbuzz API**
    with a **SQL database** to deliver real-time updates, player statistics,
    25+ analytical queries and full CRUD management.
    """
)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Pages")
    st.page_link("pages/live_matches.py", label="Live Matches: scorecards from the API", icon="📺")
    st.page_link("pages/top_stats.py", label="Top Player Stats: batting and bowling leaders", icon="🏆")
    st.page_link("pages/sql_queries.py", label="SQL Analytics: 25 queries plus a custom SQL box", icon="🧮")
    st.page_link("pages/crud_operations.py", label="CRUD Operations: manage players and stats", icon="🛠️")
with col2:
    st.markdown("### Tech stack")
    st.markdown("- **Python**, **Streamlit** (multi-page UI)\n"
                "- **SQL** via SQLAlchemy (SQLite, MySQL or PostgreSQL)\n"
                "- **REST API** with `requests` and JSON parsing\n"
                "- **pandas** and **Plotly** for analysis and charts")

st.markdown("### Getting started")
st.markdown(
    "1. Copy `.env.example` to `.env` and add your `RAPIDAPI_KEY`.\n"
    "2. Run `python -m database.init_db` (or just start the app: it creates the database).\n"
    "3. Start the app with `streamlit run app.py`.\n"
    "4. Use the sidebar to move between pages."
)

st.info(
    "**About the data:** live matches, scorecards and the API top-stats come from the "
    "Cricbuzz API. The historical tables behind the SQL questions (per-innings batting, "
    "bowling and fielding) contain generated *sample data* with fictional players, "
    "because the API does not provide a bulk history. See `README.md` for details."
)

with st.expander("Project folder structure"):
    st.code(
        "cricbuzz_livestats/\n"
        "|-- app.py                  # entry point + navigation\n"
        "|-- config.py               # settings from environment\n"
        "|-- pages/                  # one file per Streamlit page\n"
        "|-- api/cricbuzz_client.py  # the only code that calls the API\n"
        "|-- services/               # business logic and JSON parsing\n"
        "|-- database/               # repositories, seeding\n"
        "|-- sql/                    # schema.sql + the 25 queries\n"
        "|-- utils/                  # db connection, validators, logging\n"
        "|-- tests/                  # pytest test-suite\n",
        language="text",
    )

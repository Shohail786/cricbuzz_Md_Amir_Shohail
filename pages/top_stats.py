"""Top Player Stats page: leaderboards from the database plus API top-stats."""
import plotly.express as px
import streamlit as st

import config
from services.match_service import MatchService
from utils.db_connection import read_sql
from utils.exceptions import CricbuzzError

st.title("🏆 Top Player Stats")

CATEGORIES = {
    "Most runs": ("total_runs", "Runs", True),
    "Highest score": ("highest_score", "Highest score", True),
    "Best batting average": ("batting_avg", "Average", True),
    "Most centuries": ("centuries", "Centuries", True),
    "Most wickets": ("total_wickets", "Wickets", True),
    "Best economy (min. 20 wickets)": ("economy_rate", "Economy", False),
}

tab_db, tab_api = st.tabs(["From the database", "From the Cricbuzz API"])

with tab_db:
    col1, col2, col3 = st.columns(3)
    fmt = col1.selectbox("Format", ["ODI", "Test", "T20I"])
    category = col2.selectbox("Category", list(CATEGORIES))
    top_n = col3.slider("How many players", 5, 20, 10)
    column, label, descending = CATEGORIES[category]
    order = "DESC" if descending else "ASC"
    extra = " AND c.total_wickets >= 20" if column == "economy_rate" else ""
    # column/order come from a fixed dictionary above, never from user text
    df = read_sql(
        f"SELECT p.full_name AS player, t.team_name AS team, c.{column} AS value "
        f"FROM player_career_stats c JOIN players p ON p.player_id = c.player_id "
        f"LEFT JOIN teams t ON t.team_id = p.team_id "
        f"WHERE c.match_format = :fmt AND c.{column} IS NOT NULL{extra} "
        f"ORDER BY c.{column} {order} LIMIT :n", {"fmt": fmt, "n": top_n})
    if df.empty:
        st.info("No data for this selection.")
    else:
        fig = px.bar(df.iloc[::-1], x="value", y="player", color="team", orientation="h",
                     labels={"value": label, "player": ""}, title=f"{category} ({fmt})")
        st.plotly_chart(fig)
        st.dataframe(df.rename(columns={"value": label}), hide_index=True)

with tab_api:
    st.write("Fetch leaderboards directly from the Cricbuzz API (uses API quota).")
    stat_type = st.selectbox("Stat", ["mostRuns", "highestScore", "highestAvg", "mostHundreds",
                                      "mostWickets", "lowestAvg", "lowestEcon"])

    @st.cache_data(ttl=config.CACHE_TTL_SECONDS * 5, show_spinner="Calling the API...")
    def fetch_api_stats(kind: str):
        return MatchService().top_stats(kind)

    if st.button("Fetch from API"):
        try:
            table = fetch_api_stats(stat_type)
        except CricbuzzError as exc:
            st.error(str(exc))
        else:
            if table.empty:
                st.info("The API returned no rows for this stat.")
            else:
                st.dataframe(table, hide_index=True)

"""SQL Analytics page: the 25 practice queries plus a read-only custom SQL box."""
import streamlit as st

from services import analytics_service
from utils.exceptions import CricbuzzError, ValidationError

st.title("🧮 SQL Queries and Analytics")

queries = analytics_service.list_queries()
tab_pre, tab_custom = st.tabs(["Practice queries (Q1-Q25)", "Custom SQL"])

with tab_pre:
    level = st.radio("Level", ["All", "Beginner", "Intermediate", "Advanced"], horizontal=True)
    visible = [q for q in queries if level == "All" or q["level"] == level]
    labels = {f"{q['id']}: {q['title']}": q for q in visible}
    query = labels[st.selectbox("Choose a query", list(labels))]

    st.caption(f"{query['level']} | {query['description']}")
    with st.expander("Show SQL", expanded=False):
        st.code(query["sql"], language="sql")
    if st.button("▶ Run query", type="primary"):
        try:
            result = analytics_service.run_query(query["id"])
        except CricbuzzError as exc:
            st.error(str(exc))
        else:
            st.success(f"{len(result)} row(s)")
            st.dataframe(result, hide_index=True)
            st.download_button("Download CSV", result.to_csv(index=False).encode("utf-8"),
                               file_name=f"{query['id']}.csv", mime="text/csv")

with tab_custom:
    st.write("Write a read-only `SELECT` query against the cricket database.")
    sql_text = st.text_area("SQL", "SELECT * FROM players LIMIT 10;", height=150)
    if st.button("Run custom query"):
        try:
            result = analytics_service.run_custom_query(sql_text)
        except ValidationError as exc:
            for message in exc.errors:
                st.warning(message)
        except CricbuzzError as exc:
            st.error(str(exc))
        else:
            st.success(f"{len(result)} row(s)")
            st.dataframe(result, hide_index=True)
    with st.expander("Table reference"):
        st.write("teams, venues, players, series, matches, innings, match_players, "
                 "batting_performances, bowling_performances, fielding_performances, "
                 "player_career_stats")

"""Live Matches page: ongoing matches and detailed scorecards from the Cricbuzz API."""
import streamlit as st

import config
from services.match_service import MatchService
from utils.exceptions import ApiError

st.title("📺 Live Matches")


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner="Fetching live matches...")
def load_live() -> list[dict]:
    return MatchService().live_matches()


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner="Fetching scorecard...")
def load_scorecard(match_id: int) -> list[dict]:
    return MatchService().scorecard(match_id)


if st.button("🔄 Refresh"):
    st.cache_data.clear()

try:
    matches = load_live()
except ApiError as exc:
    st.error(str(exc))
    st.info("Add `RAPIDAPI_KEY` (and check `RAPIDAPI_HOST`) in your `.env` file, then reload.")
    st.stop()

if not matches:
    st.info("No live matches right now. Try again later.")
    st.stop()

st.caption(f"{len(matches)} match(es). Data is cached for {config.CACHE_TTL_SECONDS}s to save API quota.")

for match in matches:
    with st.container(border=True):
        st.markdown(f"**{match['series'] or 'Series'}**: {match['description'] or ''} "
                    f"({match['format'] or '-'})")
        left, right = st.columns(2)
        left.metric(match["team1"] or "Team 1", match["team1_score"])
        right.metric(match["team2"] or "Team 2", match["team2_score"])
        st.write(f"**Status:** {match['status'] or match['state'] or '-'}")
        if match["venue"]:
            st.write(f"**Venue:** {match['venue']}")

labels = {f"{m['team1']} vs {m['team2']} ({m['description']})": m["match_id"]
          for m in matches if m["match_id"]}
if labels:
    st.subheader("Detailed scorecard")
    choice = st.selectbox("Choose a match", list(labels))
    try:
        innings = load_scorecard(labels[choice])
    except ApiError as exc:
        st.error(str(exc))
    else:
        if not innings:
            st.info("Scorecard not available yet.")
        for inn in innings:
            st.markdown(f"#### {inn['title']}: {inn['summary']}")
            if not inn["batting"].empty:
                st.dataframe(inn["batting"], hide_index=True)
            if not inn["bowling"].empty:
                st.dataframe(inn["bowling"], hide_index=True)

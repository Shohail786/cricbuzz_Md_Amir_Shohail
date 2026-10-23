"""CRUD page: create, read, update and delete players and their career stats."""
from datetime import date

import streamlit as st

from services.player_service import PlayerService
from utils.exceptions import CricbuzzError, ValidationError
from utils.validators import VALID_FORMATS, VALID_ROLES

st.title("🛠️ CRUD Operations")
service = PlayerService()


def show_error(exc: CricbuzzError) -> None:
    """Display validation messages individually, other errors as a single message."""
    if isinstance(exc, ValidationError):
        for message in exc.errors:
            st.error(message)
    else:
        st.error(str(exc))


def optional_text(value) -> str:
    return "" if value is None or (isinstance(value, float) and value != value) else str(value)


try:
    teams = service.teams()
except CricbuzzError as exc:
    show_error(exc)
    st.stop()

team_names = dict(zip(teams["team_id"].astype(int), teams["team_name"]))
tab_read, tab_create, tab_update, tab_delete, tab_stats = st.tabs(
    ["📖 Read", "➕ Create", "✏️ Update", "🗑️ Delete", "📊 Career stats"])

# ------------------------------------------------------------------ READ
with tab_read:
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search by name")
    team_choice = c2.selectbox("Team", [0] + list(team_names),
                               format_func=lambda i: "All teams" if i == 0 else team_names[i])
    try:
        players = service.search(search, team_choice or None)
        st.caption(f"{len(players)} player(s)")
        st.dataframe(players, hide_index=True)
    except CricbuzzError as exc:
        show_error(exc)

# ---------------------------------------------------------------- CREATE
with tab_create:
    with st.form("create_player", clear_on_submit=True):
        name = st.text_input("Full name")
        team_id = st.selectbox("Team", list(team_names), format_func=team_names.get)
        role = st.selectbox("Playing role", VALID_ROLES)
        bat_style = st.text_input("Batting style", placeholder="Right-hand bat")
        bowl_style = st.text_input("Bowling style", placeholder="Right-arm fast")
        dob = st.date_input("Date of birth (optional)", value=None,
                            min_value=date(1950, 1, 1), max_value=date.today())
        submitted = st.form_submit_button("Add player")
    if submitted:
        try:
            new_id = service.create({
                "full_name": name, "team_id": team_id, "playing_role": role,
                "batting_style": bat_style, "bowling_style": bowl_style,
                "date_of_birth": dob.isoformat() if dob else None})
            st.success(f"Player added with id {new_id}.")
        except CricbuzzError as exc:
            show_error(exc)

# ---------------------------------------------------------------- UPDATE
with tab_update:
    all_players = service.search()
    if all_players.empty:
        st.info("No players available.")
    else:
        options = dict(zip(all_players["player_id"].astype(int), all_players["full_name"]))
        pid = st.selectbox("Player to edit", list(options), format_func=options.get, key="upd_pid")
        current = service.get(pid)
        with st.form(f"update_player_{pid}"):
            name = st.text_input("Full name", current["full_name"])
            raw_team = current.get("team_id")
            current_team = int(raw_team) if raw_team is not None and raw_team == raw_team \
                else list(team_names)[0]
            team_id = st.selectbox("Team", list(team_names), format_func=team_names.get,
                                   index=list(team_names).index(current_team))
            role = st.selectbox("Playing role", VALID_ROLES,
                                index=VALID_ROLES.index(current["playing_role"]))
            bat_style = st.text_input("Batting style", optional_text(current["batting_style"]))
            bowl_style = st.text_input("Bowling style", optional_text(current["bowling_style"]))
            dob_text = st.text_input("Date of birth (YYYY-MM-DD)",
                                     optional_text(current["date_of_birth"]))
            submitted = st.form_submit_button("Save changes")
        if submitted:
            try:
                service.update(pid, {"full_name": name, "team_id": team_id, "playing_role": role,
                                     "batting_style": bat_style, "bowling_style": bowl_style,
                                     "date_of_birth": dob_text})
                st.success("Player updated.")
            except CricbuzzError as exc:
                show_error(exc)

# ---------------------------------------------------------------- DELETE
with tab_delete:
    all_players = service.search()
    if all_players.empty:
        st.info("No players available.")
    else:
        options = dict(zip(all_players["player_id"].astype(int), all_players["full_name"]))
        pid = st.selectbox("Player to delete", list(options), format_func=options.get, key="del_pid")
        st.warning("Deleting a player also deletes their career stats and match records.")
        confirm = st.checkbox("I understand this cannot be undone")
        if st.button("Delete player", type="primary", disabled=not confirm):
            try:
                service.delete(pid)
                st.success("Player deleted. Reload the tab to refresh lists.")
            except CricbuzzError as exc:
                show_error(exc)

# ----------------------------------------------------------- CAREER STATS
with tab_stats:
    all_players = service.search()
    if all_players.empty:
        st.info("No players available.")
    else:
        options = dict(zip(all_players["player_id"].astype(int), all_players["full_name"]))
        pid = st.selectbox("Player", list(options), format_func=options.get, key="stat_pid")
        st.dataframe(service.stats(pid), hide_index=True)
        st.markdown("**Add or update a format's stats**")
        with st.form("stats_form"):
            fmt = st.selectbox("Format", VALID_FORMATS)
            a, b, c = st.columns(3)
            matches = a.number_input("Matches", min_value=0, step=1)
            innings = b.number_input("Innings batted", min_value=0, step=1)
            runs = c.number_input("Total runs", min_value=0, step=1)
            d, e, f = st.columns(3)
            high = d.number_input("Highest score", min_value=0, step=1)
            hundreds = e.number_input("Centuries", min_value=0, step=1)
            fifties = f.number_input("Fifties", min_value=0, step=1)
            g, h, i = st.columns(3)
            avg = g.number_input("Batting average", min_value=0.0, step=0.01)
            sr = h.number_input("Strike rate", min_value=0.0, step=0.01)
            wickets = i.number_input("Wickets", min_value=0, step=1)
            j, k = st.columns(2)
            bowl_avg = j.number_input("Bowling average (0 = none)", min_value=0.0, step=0.01)
            econ = k.number_input("Economy (0 = none)", min_value=0.0, step=0.01)
            saved = st.form_submit_button("Save stats")
        if saved:
            try:
                outcome = service.save_stats(pid, {
                    "match_format": fmt, "matches_played": int(matches),
                    "innings_batted": int(innings), "total_runs": int(runs),
                    "highest_score": int(high), "centuries": int(hundreds),
                    "fifties": int(fifties), "total_wickets": int(wickets),
                    "batting_avg": float(avg), "strike_rate": float(sr),
                    "bowling_avg": float(bowl_avg) or None, "economy_rate": float(econ) or None})
                st.success(f"Stats {outcome}.")
            except CricbuzzError as exc:
                show_error(exc)
        del_fmt = st.selectbox("Delete stats for format", VALID_FORMATS, key="del_fmt")
        if st.button("Delete this format's stats"):
            try:
                service.delete_stats(pid, del_fmt)
                st.success("Stats deleted.")
            except CricbuzzError as exc:
                show_error(exc)

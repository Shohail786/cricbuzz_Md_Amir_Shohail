"""Data-access layer for players and their career statistics (CRUD).

All SQL uses bound parameters (never string formatting of user input), which
prevents SQL injection. Writes run inside transactions via ``execute``.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy.engine import Engine

from utils.db_connection import execute, read_sql
from utils.exceptions import DatabaseError

PLAYER_COLUMNS = ("full_name", "team_id", "playing_role", "batting_style",
                  "bowling_style", "date_of_birth")
STATS_COLUMNS = ("matches_played", "innings_batted", "total_runs", "highest_score",
                 "batting_avg", "strike_rate", "centuries", "fifties",
                 "total_wickets", "bowling_avg", "economy_rate")


class PlayerRepository:
    """CRUD operations on ``players`` and ``player_career_stats``."""

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine

    # ------------------------------------------------------------- teams
    def list_teams(self) -> pd.DataFrame:
        """All teams (for dropdowns)."""
        return read_sql("SELECT team_id, team_name FROM teams ORDER BY team_name",
                        engine=self._engine)

    # ------------------------------------------------------------ players
    def list_players(self, search: str = "", team_id: int | None = None) -> pd.DataFrame:
        """Players joined with team name, optionally filtered by name/team."""
        sql = ("SELECT p.player_id, p.full_name, t.team_name, p.playing_role, "
               "p.batting_style, p.bowling_style, p.date_of_birth "
               "FROM players p LEFT JOIN teams t ON t.team_id = p.team_id WHERE 1 = 1")
        params: dict[str, Any] = {}
        if search.strip():
            sql += " AND LOWER(p.full_name) LIKE :pattern"
            params["pattern"] = f"%{search.strip().lower()}%"
        if team_id is not None:
            sql += " AND p.team_id = :team_id"
            params["team_id"] = team_id
        return read_sql(sql + " ORDER BY p.full_name", params, self._engine)

    def get_player(self, player_id: int) -> dict[str, Any] | None:
        """One player as a dict, or None."""
        df = read_sql("SELECT * FROM players WHERE player_id = :pid",
                      {"pid": player_id}, self._engine)
        return None if df.empty else df.iloc[0].to_dict()

    def insert_player(self, data: dict[str, Any]) -> int:
        """Insert a player and return the new id."""
        next_id = int(read_sql("SELECT COALESCE(MAX(player_id), 0) + 1 AS n FROM players",
                               engine=self._engine)["n"].iloc[0])
        params = {col: data.get(col) for col in PLAYER_COLUMNS}
        params["player_id"] = next_id
        execute("INSERT INTO players (player_id, full_name, team_id, playing_role, "
                "batting_style, bowling_style, date_of_birth) VALUES "
                "(:player_id, :full_name, :team_id, :playing_role, :batting_style, "
                ":bowling_style, :date_of_birth)", params, self._engine)
        return next_id

    def update_player(self, player_id: int, data: dict[str, Any]) -> int:
        """Update a player; returns the number of rows changed."""
        params = {col: data.get(col) for col in PLAYER_COLUMNS}
        params["pid"] = player_id
        return execute("UPDATE players SET full_name = :full_name, team_id = :team_id, "
                       "playing_role = :playing_role, batting_style = :batting_style, "
                       "bowling_style = :bowling_style, date_of_birth = :date_of_birth "
                       "WHERE player_id = :pid", params, self._engine)

    def delete_player(self, player_id: int) -> int:
        """Delete a player (child rows cascade); returns rows deleted."""
        return execute("DELETE FROM players WHERE player_id = :pid",
                       {"pid": player_id}, self._engine)

    # -------------------------------------------------------- career stats
    def get_stats(self, player_id: int) -> pd.DataFrame:
        """Career stats rows (one per format) for a player."""
        return read_sql("SELECT * FROM player_career_stats WHERE player_id = :pid "
                        "ORDER BY match_format", {"pid": player_id}, self._engine)

    def upsert_stats(self, player_id: int, data: dict[str, Any]) -> str:
        """Insert or update one (player, format) stats row. Returns 'inserted'/'updated'."""
        params = {col: data.get(col) for col in STATS_COLUMNS}
        params.update(pid=player_id, fmt=data["match_format"])
        exists = not read_sql(
            "SELECT 1 FROM player_career_stats WHERE player_id = :pid AND match_format = :fmt",
            {"pid": player_id, "fmt": data["match_format"]}, self._engine).empty
        if exists:
            execute("UPDATE player_career_stats SET "
                    + ", ".join(f"{c} = :{c}" for c in STATS_COLUMNS)
                    + " WHERE player_id = :pid AND match_format = :fmt", params, self._engine)
            return "updated"
        execute("INSERT INTO player_career_stats (player_id, match_format, "
                + ", ".join(STATS_COLUMNS) + ") VALUES (:pid, :fmt, "
                + ", ".join(f":{c}" for c in STATS_COLUMNS) + ")", params, self._engine)
        return "inserted"

    def delete_stats(self, player_id: int, match_format: str) -> int:
        """Delete one (player, format) stats row."""
        return execute("DELETE FROM player_career_stats WHERE player_id = :pid "
                       "AND match_format = :fmt",
                       {"pid": player_id, "fmt": match_format}, self._engine)


__all__ = ["PlayerRepository", "DatabaseError"]

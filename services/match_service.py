"""Turn raw Cricbuzz JSON into tidy Python/pandas objects for the pages.

Parsers are DEFENSIVE: every level uses ``.get`` with defaults because nested
API responses regularly omit keys. The field names follow the usual RapidAPI
Cricbuzz response shape; if your provider differs, adjust only this file.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from api.cricbuzz_client import CricbuzzClient


def _innings_text(team_score: dict[str, Any] | None) -> str:
    """Format a team's score dict as e.g. '210/3 (35.2 ov) & 250'."""
    parts = []
    for key in sorted((team_score or {}), key=str):
        inn = (team_score or {}).get(key) or {}
        if not isinstance(inn, dict) or "runs" not in inn:
            continue
        text = str(inn.get("runs"))
        if inn.get("wickets") not in (None, 10):
            text += f"/{inn.get('wickets')}"
        if inn.get("overs") is not None:
            text += f" ({inn.get('overs')} ov)"
        parts.append(text)
    return " & ".join(parts) if parts else "Yet to bat"


def parse_matches(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the typeMatches -> seriesMatches -> matches nesting."""
    matches: list[dict[str, Any]] = []
    for type_block in payload.get("typeMatches", []) or []:
        for series_block in type_block.get("seriesMatches", []) or []:
            wrapper = series_block.get("seriesAdWrapper") or {}
            for item in wrapper.get("matches", []) or []:
                info = item.get("matchInfo") or {}
                score = item.get("matchScore") or {}
                venue = info.get("venueInfo") or {}
                team1, team2 = info.get("team1") or {}, info.get("team2") or {}
                matches.append({
                    "match_id": info.get("matchId"),
                    "series": info.get("seriesName") or wrapper.get("seriesName"),
                    "description": info.get("matchDesc"),
                    "format": info.get("matchFormat"),
                    "state": info.get("state"),
                    "status": info.get("status"),
                    "team1": team1.get("teamName") or team1.get("teamSName"),
                    "team2": team2.get("teamName") or team2.get("teamSName"),
                    "team1_score": _innings_text(score.get("team1Score")),
                    "team2_score": _innings_text(score.get("team2Score")),
                    "venue": ", ".join(x for x in (venue.get("ground"), venue.get("city")) if x),
                })
    return matches


def parse_scorecard(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return one dict per innings with batting and bowling DataFrames."""
    innings_list = []
    for inn in payload.get("scoreCard", []) or []:
        bat_team = inn.get("batTeamDetails") or {}
        bowl_team = inn.get("bowlTeamDetails") or {}
        score = inn.get("scoreDetails") or {}
        batting = [{"Batter": b.get("batName"), "Runs": b.get("runs"), "Balls": b.get("balls"),
                    "4s": b.get("fours"), "6s": b.get("sixes"), "SR": b.get("strikeRate"),
                    "Dismissal": b.get("outDesc")}
                   for b in (bat_team.get("batsmenData") or {}).values()]
        bowling = [{"Bowler": b.get("bowlName"), "Overs": b.get("overs"), "Maidens": b.get("maidens"),
                    "Runs": b.get("runs"), "Wickets": b.get("wickets"), "Economy": b.get("economy")}
                   for b in (bowl_team.get("bowlersData") or {}).values()]
        innings_list.append({
            "title": f"{bat_team.get('batTeamName', 'Team')} innings",
            "summary": f"{score.get('runs', '-')}/{score.get('wickets', '-')} "
                       f"({score.get('overs', '-')} ov)",
            "batting": pd.DataFrame(batting), "bowling": pd.DataFrame(bowling)})
    return innings_list


def parse_stats_table(payload: dict[str, Any]) -> pd.DataFrame:
    """Convert a {'headers': [...], 'values': [{'values': [...]}]} stats payload to a DataFrame."""
    headers = payload.get("headers") or []
    rows = [r.get("values", []) for r in payload.get("values", []) or []]
    if not rows:
        return pd.DataFrame()
    width = max(len(r) for r in rows)
    columns = (headers + [f"col_{i}" for i in range(len(headers), width)])[:width]
    return pd.DataFrame([r + [None] * (width - len(r)) for r in rows], columns=columns)


class MatchService:
    """Facade used by the Live Matches and Top Stats pages."""

    def __init__(self, client: CricbuzzClient | None = None) -> None:
        self.client = client or CricbuzzClient()

    def live_matches(self) -> list[dict[str, Any]]:
        return parse_matches(self.client.get_live_matches())

    def recent_matches(self) -> list[dict[str, Any]]:
        return parse_matches(self.client.get_recent_matches())

    def scorecard(self, match_id: int) -> list[dict[str, Any]]:
        return parse_scorecard(self.client.get_scorecard(match_id))

    def top_stats(self, stats_type: str) -> pd.DataFrame:
        return parse_stats_table(self.client.get_top_stats(stats_type))

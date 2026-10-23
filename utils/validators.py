"""Input validation for the CRUD forms. Each validator returns a list of error messages."""
from __future__ import annotations

from datetime import date
from typing import Any

from utils.exceptions import ValidationError

VALID_ROLES = ("Batsman", "Bowler", "All-rounder", "Wicket-keeper")
VALID_FORMATS = ("Test", "ODI", "T20I")


def validate_player(data: dict[str, Any]) -> list[str]:
    """Validate a player record; empty list means valid."""
    errors: list[str] = []
    name = (data.get("full_name") or "").strip()
    if len(name) < 2:
        errors.append("Full name must be at least 2 characters.")
    if len(name) > 120:
        errors.append("Full name must be 120 characters or fewer.")
    if data.get("playing_role") not in VALID_ROLES:
        errors.append(f"Playing role must be one of: {', '.join(VALID_ROLES)}.")
    dob = data.get("date_of_birth")
    if dob:
        try:
            parsed = dob if isinstance(dob, date) else date.fromisoformat(str(dob))
            if parsed >= date.today():
                errors.append("Date of birth must be in the past.")
        except ValueError:
            errors.append("Date of birth must be a valid date (YYYY-MM-DD).")
    return errors


def validate_career_stats(data: dict[str, Any]) -> list[str]:
    """Validate a player_career_stats record; empty list means valid."""
    errors: list[str] = []
    if data.get("match_format") not in VALID_FORMATS:
        errors.append(f"Format must be one of: {', '.join(VALID_FORMATS)}.")
    for field in ("matches_played", "innings_batted", "total_runs", "highest_score",
                  "centuries", "fifties", "total_wickets"):
        value = data.get(field)
        if not isinstance(value, int) or value < 0:
            errors.append(f"{field.replace('_', ' ').capitalize()} must be a whole number >= 0.")
    if not errors:
        if data["highest_score"] > data["total_runs"]:
            errors.append("Highest score cannot exceed total runs.")
        if data["innings_batted"] > data["matches_played"] * 2:
            errors.append("Innings batted cannot exceed twice the matches played.")
        if data["centuries"] + data["fifties"] > data["innings_batted"]:
            errors.append("Centuries + fifties cannot exceed innings batted.")
    for field, limit in (("batting_avg", 200), ("strike_rate", 400),
                         ("bowling_avg", 500), ("economy_rate", 36)):
        value = data.get(field)
        if value is not None and not (0 <= value <= limit):
            errors.append(f"{field.replace('_', ' ').capitalize()} must be between 0 and {limit}.")
    return errors


def ensure_valid(errors: list[str]) -> None:
    """Raise ValidationError if ``errors`` is not empty."""
    if errors:
        raise ValidationError(errors)

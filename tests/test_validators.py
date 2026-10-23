"""Unit tests for input validation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.validators import validate_career_stats, validate_player


def good_player():
    return {"full_name": "Test Player", "playing_role": "Batsman", "date_of_birth": "1995-05-05"}


def good_stats():
    return {"match_format": "ODI", "matches_played": 10, "innings_batted": 9, "total_runs": 300,
            "highest_score": 90, "centuries": 0, "fifties": 2, "total_wickets": 0,
            "batting_avg": 33.3, "strike_rate": 85.0, "bowling_avg": None, "economy_rate": None}


def test_valid_player_passes():
    assert validate_player(good_player()) == []


def test_short_name_and_bad_role_rejected():
    errors = validate_player({"full_name": "A", "playing_role": "Goalkeeper"})
    assert len(errors) == 2


def test_future_dob_rejected():
    data = good_player() | {"date_of_birth": "2999-01-01"}
    assert any("past" in e for e in validate_player(data))


def test_valid_stats_pass():
    assert validate_career_stats(good_stats()) == []


def test_highest_score_cannot_exceed_runs():
    data = good_stats() | {"highest_score": 500}
    assert any("Highest score" in e for e in validate_career_stats(data))


def test_negative_and_out_of_range_values_rejected():
    data = good_stats() | {"total_runs": -1, "economy_rate": 99}
    assert len(validate_career_stats(data)) >= 2

"""Tests for JSON parsing, using small hand-written API payloads (no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.match_service import parse_matches, parse_scorecard, parse_stats_table

LIVE = {"typeMatches": [{"seriesMatches": [{"seriesAdWrapper": {"seriesName": "Demo Series", "matches": [{
    "matchInfo": {"matchId": 1, "matchDesc": "1st ODI", "matchFormat": "ODI", "state": "In Progress",
                  "status": "IND need 40 runs", "team1": {"teamName": "India"},
                  "team2": {"teamName": "Australia"}, "venueInfo": {"ground": "MCG", "city": "Melbourne"}},
    "matchScore": {"team1Score": {"inngs1": {"runs": 210, "wickets": 3, "overs": 35.2}}}}]}}]}]}


def test_parse_matches_flattens_nesting():
    matches = parse_matches(LIVE)
    assert len(matches) == 1
    assert matches[0]["team1_score"] == "210/3 (35.2 ov)"
    assert matches[0]["team2_score"] == "Yet to bat"
    assert matches[0]["venue"] == "MCG, Melbourne"


def test_parse_matches_survives_empty_payload():
    assert parse_matches({}) == []
    assert parse_matches({"typeMatches": [{"seriesMatches": [{}]}]}) == []


def test_parse_scorecard():
    payload = {"scoreCard": [{"batTeamDetails": {"batTeamName": "India", "batsmenData": {
        "bat_1": {"batName": "A", "runs": 56, "balls": 45, "fours": 4, "sixes": 1, "strikeRate": 124.4}}},
        "bowlTeamDetails": {"bowlersData": {"bowl_1": {"bowlName": "B", "overs": 10, "runs": 50,
                                                       "wickets": 2, "economy": 5.0}}},
        "scoreDetails": {"runs": 250, "wickets": 8, "overs": 50}}]}
    innings = parse_scorecard(payload)
    assert innings[0]["title"] == "India innings"
    assert innings[0]["batting"].loc[0, "Runs"] == 56
    assert innings[0]["bowling"].loc[0, "Wickets"] == 2


def test_parse_stats_table_pads_short_rows():
    df = parse_stats_table({"headers": ["Player", "Runs"], "values": [{"values": ["X", 10]}, {"values": ["Y"]}]})
    assert list(df.columns) == ["Player", "Runs"]
    assert df.shape == (2, 2)

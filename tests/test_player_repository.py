"""Integration test of CRUD against a real (temporary) SQLite database."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.player_repository import PlayerRepository
from services.player_service import PlayerService
from utils.exceptions import ValidationError


def test_full_crud_cycle(engine):
    service = PlayerService(PlayerRepository(engine))
    new_id = service.create({"full_name": "Crud Tester", "team_id": 1, "playing_role": "Bowler"})
    assert service.get(new_id)["full_name"] == "Crud Tester"

    service.update(new_id, {"full_name": "Crud Tester Jr", "team_id": 1, "playing_role": "All-rounder"})
    assert service.get(new_id)["playing_role"] == "All-rounder"

    outcome = service.save_stats(new_id, {
        "match_format": "ODI", "matches_played": 5, "innings_batted": 5, "total_runs": 100,
        "highest_score": 50, "centuries": 0, "fifties": 1, "total_wickets": 3,
        "batting_avg": 20.0, "strike_rate": 80.0, "bowling_avg": 30.0, "economy_rate": 5.0})
    assert outcome == "inserted"

    service.delete(new_id)
    assert service.stats(new_id).empty  # cascade delete removed the stats row
    with pytest.raises(ValidationError):
        service.get(new_id)


def test_invalid_player_is_rejected(engine):
    with pytest.raises(ValidationError):
        PlayerService(PlayerRepository(engine)).create({"full_name": "", "playing_role": "Nope"})

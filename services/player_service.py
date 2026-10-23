"""Business logic for the CRUD page: validate first, then call the repository."""
from __future__ import annotations

from typing import Any

import pandas as pd

from database.player_repository import PlayerRepository
from utils.exceptions import ValidationError
from utils.validators import ensure_valid, validate_career_stats, validate_player


def _clean(data: dict[str, Any]) -> dict[str, Any]:
    """Strip strings and turn empty strings into None."""
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, str):
            value = value.strip() or None
        cleaned[key] = value
    return cleaned


class PlayerService:
    """Create / read / update / delete players and their career stats."""

    def __init__(self, repository: PlayerRepository | None = None) -> None:
        self.repo = repository or PlayerRepository()

    def teams(self) -> pd.DataFrame:
        return self.repo.list_teams()

    def search(self, text: str = "", team_id: int | None = None) -> pd.DataFrame:
        return self.repo.list_players(text, team_id)

    def get(self, player_id: int) -> dict[str, Any]:
        player = self.repo.get_player(player_id)
        if player is None:
            raise ValidationError([f"Player {player_id} does not exist."])
        return player

    def create(self, data: dict[str, Any]) -> int:
        data = _clean(data)
        ensure_valid(validate_player(data))
        return self.repo.insert_player(data)

    def update(self, player_id: int, data: dict[str, Any]) -> None:
        data = _clean(data)
        ensure_valid(validate_player(data))
        if self.repo.update_player(player_id, data) == 0:
            raise ValidationError([f"Player {player_id} does not exist."])

    def delete(self, player_id: int) -> None:
        if self.repo.delete_player(player_id) == 0:
            raise ValidationError([f"Player {player_id} does not exist."])

    def stats(self, player_id: int) -> pd.DataFrame:
        return self.repo.get_stats(player_id)

    def save_stats(self, player_id: int, data: dict[str, Any]) -> str:
        ensure_valid(validate_career_stats(data))
        return self.repo.upsert_stats(player_id, data)

    def delete_stats(self, player_id: int, match_format: str) -> None:
        if self.repo.delete_stats(player_id, match_format) == 0:
            raise ValidationError([f"No {match_format} stats found for this player."])

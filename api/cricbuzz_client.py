"""HTTP client for the Cricbuzz REST API (RapidAPI style).

This is the ONLY module that talks to the API. It adds the auth headers, a
timeout, automatic retries with back-off for 429/5xx, and converts every
failure into ``ApiError`` so pages can show a friendly message.

IMPORTANT: endpoint paths below are the commonly used layout of the RapidAPI
"Cricbuzz Cricket" API. Confirm them in YOUR API dashboard and edit ``ENDPOINTS``
if your provider differs; nothing else in the project needs to change.
"""
from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config
from utils.exceptions import ApiError
from utils.logger import get_logger

logger = get_logger(__name__)

ENDPOINTS = {
    "live": "/matches/v1/live",
    "recent": "/matches/v1/recent",
    "upcoming": "/matches/v1/upcoming",
    "match_info": "/mcenter/v1/{match_id}",
    "scorecard": "/mcenter/v1/{match_id}/scard",
    "series_list": "/series/v1/international",
    "teams": "/teams/v1/international",
    "team_players": "/teams/v1/{team_id}/players",
    "player": "/stats/v1/player/{player_id}",
    "player_batting": "/stats/v1/player/{player_id}/batting",
    "player_bowling": "/stats/v1/player/{player_id}/bowling",
    "top_stats": "/stats/v1/topstats/{stats_id}",
    "rankings": "/stats/v1/rankings/{category}",
    "venue": "/venues/v1/{venue_id}",
}


class CricbuzzClient:
    """Thin, testable wrapper around the Cricbuzz API."""

    def __init__(self, api_key: str | None = None, host: str | None = None,
                 base_url: str | None = None, timeout: int | None = None,
                 max_retries: int | None = None) -> None:
        self.api_key = api_key if api_key is not None else config.RAPIDAPI_KEY
        self.host = host or config.RAPIDAPI_HOST
        self.base_url = (base_url or config.API_BASE_URL).rstrip("/")
        self.timeout = timeout or config.API_TIMEOUT
        retry = Retry(total=max_retries if max_retries is not None else config.API_MAX_RETRIES,
                      backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504),
                      allowed_methods=("GET",), respect_retry_after_header=True)
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    @property
    def is_configured(self) -> bool:
        """True when an API key is present."""
        return bool(self.api_key)

    def _get(self, endpoint_key: str, params: dict[str, Any] | None = None,
             **path_args: Any) -> dict[str, Any]:
        """GET an endpoint and return parsed JSON, raising ApiError on any problem."""
        if not self.is_configured:
            raise ApiError("API key missing. Add RAPIDAPI_KEY to your .env file.")
        url = self.base_url + ENDPOINTS[endpoint_key].format(**path_args)
        headers = {"X-RapidAPI-Key": self.api_key, "X-RapidAPI-Host": self.host}
        try:
            response = self.session.get(url, headers=headers, params=params,
                                        timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.Timeout as exc:
            raise ApiError("The API timed out. Please try again.") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ApiError("Could not reach the API. Check your internet connection.") from exc
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            hints = {401: "invalid API key", 403: "not subscribed to this API/endpoint",
                     404: "endpoint or id not found", 429: "rate limit exceeded"}
            raise ApiError(f"API returned HTTP {status} ({hints.get(status, 'error')}).") from exc
        except ValueError as exc:  # JSON decoding error
            raise ApiError("The API returned data that is not valid JSON.") from exc
        except requests.exceptions.RequestException as exc:
            raise ApiError(f"Request failed: {exc}") from exc
        if not isinstance(payload, dict):
            raise ApiError("Unexpected API response format.")
        logger.info("GET %s OK", url)
        return payload

    # ------------------------------------------------------------ matches
    def get_live_matches(self) -> dict[str, Any]:
        return self._get("live")

    def get_recent_matches(self) -> dict[str, Any]:
        return self._get("recent")

    def get_upcoming_matches(self) -> dict[str, Any]:
        return self._get("upcoming")

    def get_match_info(self, match_id: int) -> dict[str, Any]:
        return self._get("match_info", match_id=match_id)

    def get_scorecard(self, match_id: int) -> dict[str, Any]:
        return self._get("scorecard", match_id=match_id)

    # ------------------------------------------------- series / teams / players
    def get_series_list(self) -> dict[str, Any]:
        return self._get("series_list")

    def get_teams(self) -> dict[str, Any]:
        return self._get("teams")

    def get_team_players(self, team_id: int) -> dict[str, Any]:
        return self._get("team_players", team_id=team_id)

    def get_player(self, player_id: int) -> dict[str, Any]:
        return self._get("player", player_id=player_id)

    def get_player_batting(self, player_id: int) -> dict[str, Any]:
        return self._get("player_batting", player_id=player_id)

    def get_player_bowling(self, player_id: int) -> dict[str, Any]:
        return self._get("player_bowling", player_id=player_id)

    def get_top_stats(self, stats_type: str, stats_id: int = 0,
                      match_type: int | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"statsType": stats_type}
        if match_type is not None:
            params["matchType"] = match_type
        return self._get("top_stats", params=params, stats_id=stats_id)

    def get_rankings(self, category: str = "batsmen", format_type: str = "test") -> dict[str, Any]:
        return self._get("rankings", params={"formatType": format_type}, category=category)

    def get_venue(self, venue_id: int) -> dict[str, Any]:
        return self._get("venue", venue_id=venue_id)

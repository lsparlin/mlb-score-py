"""MLB Stats API client with typed model returns."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from mlb_score.models import Game, GameState, TeamInfo, TeamScore

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"

# Maps MLB API status.statusCode values to GameState.
# Reference: https://statsapi.mlb.com/api/doc
MLB_STATUS_CODE_MAP: dict[str, GameState] = {
    "F": GameState.FINAL,
    "I": GameState.LIVE,
    "P": GameState.SCHEDULED,
    "W": GameState.SCHEDULED,  # walkup / warmup
    "S": GameState.SCHEDULED,  # scheduled (delayed)
}


class ApiError(Exception):
    """Raised when the MLB API request fails."""

    pass


class UserError(Exception):
    """Raised when user-provided input is invalid."""

    pass


class MlbClient:
    """Encapsulates MLB API fetching and parsing into typed models.

    If the MLB API changes its JSON structure, only this class needs to be updated.
    """

    def __init__(self, user_agent: str = "mlb-score-cli/1.0") -> None:
        self._user_agent = user_agent

    def fetch_schedule(self, date_str: str) -> list[Game]:
        """Fetch and parse all games for a single date (YYYY-MM-DD).

        Returns a list of fully instantiated Game models.
        Raises ApiError on network or HTTP failures.
        """
        raw = self._fetch_raw(date_str)
        return self._parse_games(raw)

    def fetch_date_range(
        self,
        target_date: date,
        days: int = 1,
    ) -> dict[date, list[Game]]:
        """Fetch and parse games for a range of dates ending at target_date.

        Returns a dict mapping every queried date to its list of Game models.
        Dates with no games map to an empty list.
        """
        result: dict[date, list[Game]] = {}
        for i in range(days):
            lookup_date = target_date - timedelta(days=i)
            result[lookup_date] = self.fetch_schedule(lookup_date.isoformat())
        return result

    # --- internal ---

    def _fetch_raw(self, date_str: str) -> dict[str, Any]:
        """Perform the HTTP request and return raw JSON."""
        url = MLB_API.format(date=date_str)
        req = Request(url, headers={"User-Agent": self._user_agent})
        try:
            with urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except URLError as e:
            raise ApiError(f"Error fetching data for {date_str}: {e}") from e
        except json.JSONDecodeError as e:
            raise ApiError(f"Invalid response from MLB API for {date_str}: {e}") from e

    def _parse_games(self, raw: dict[str, Any]) -> list[Game]:
        """Parse all games from a raw API response."""
        dates = raw.get("dates")
        if not dates:
            return []
        games: list[Game] = []
        first = dates[0] if dates else None
        if not isinstance(first, dict):
            return []
        for raw_game in first.get("games", []):
            games.append(self._parse_game(raw_game))
        return games

    def _parse_game(self, raw: dict[str, Any]) -> Game:
        """Convert a raw API game object into a structured Game model."""
        teams = raw.get("teams", {})
        status = raw.get("status", {})
        code = status.get("statusCode", "F")
        state = MLB_STATUS_CODE_MAP.get(code, GameState.SCHEDULED)
        return Game(
            away_team=self._parse_team(teams, "away"),
            home_team=self._parse_team(teams, "home"),
            venue=raw.get("venue", {}).get("name", ""),
            day_night=raw.get("dayNight", ""),
            state=state,
        )

    def _parse_team(self, teams: dict[str, Any], side: str) -> TeamScore:
        """Parse a team entry from raw API response into a TeamScore."""
        team_raw = teams.get(side, {}).get("team", {})
        info = TeamInfo(
            name=team_raw.get("name", ""),
            abbreviation=team_raw.get("abbreviation", ""),
        )
        return TeamScore(
            team=info,
            score=teams.get(side, {}).get("score", 0),
            is_winner=teams.get(side, {}).get("isWinner"),
            is_home=(side == "home"),
        )

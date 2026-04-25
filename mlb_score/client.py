"""MLB Stats API client."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from mlb_score.models import Game
from mlb_score.parser import parse_games

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"


class ApiError(Exception):
    """Raised when the MLB API request fails."""

    pass


class UserError(Exception):
    """Raised when user-provided input is invalid."""

    pass


class MlbClient:
    """Fetches raw JSON from the MLB Stats API and delegates parsing to the parser module."""

    def __init__(self, user_agent: str = "mlb-score-cli/1.0") -> None:
        self._user_agent = user_agent

    def fetch_schedule(self, date_str: str) -> list[Game]:
        """Fetch and parse all games for a single date (YYYY-MM-DD).

        Raises ApiError on network or HTTP failures.
        """
        return parse_games(self._fetch_raw(date_str))

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

    def _fetch_raw(self, date_str: str) -> dict[str, Any]:
        url = MLB_API.format(date=date_str)
        req = Request(url, headers={"User-Agent": self._user_agent})
        try:
            with urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except URLError as e:
            raise ApiError(f"Error fetching data for {date_str}: {e}") from e
        except json.JSONDecodeError as e:
            raise ApiError(f"Invalid response from MLB API for {date_str}: {e}") from e

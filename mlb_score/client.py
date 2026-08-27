"""HTTP transport for the MLB Stats API. Owns network errors and date-range iteration.

JSON-to-model parsing is delegated entirely to parser.py; this module has no knowledge
of the API response schema.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any
from urllib.request import Request, urlopen

from mlb_score.models import Game
from mlb_score.parser import parse_games, parse_games_by_date

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
MLB_API_RANGE = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start}&endDate={end}"


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

        Uses a single API request covering the whole range.
        Returns a dict mapping every queried date to its list of Game models.
        Dates with no games map to an empty list.
        """
        start_date = target_date - timedelta(days=days - 1)
        parsed = self._fetch_range_raw(start_date, target_date)
        # Include every queried date, even ones the API omitted (no games that day)
        queried_dates = (target_date - timedelta(days=i) for i in range(days))
        return {lookup_date: parsed.get(lookup_date, []) for lookup_date in queried_dates}

    def _fetch_range_raw(self, start_date: date, end_date: date) -> dict[date, list[Game]]:
        url = MLB_API_RANGE.format(start=start_date.isoformat(), end=end_date.isoformat())
        context = f"{start_date.isoformat()} to {end_date.isoformat()}"
        return parse_games_by_date(self._request_json(url, context))

    def _fetch_raw(self, date_str: str) -> dict[str, Any]:
        url = MLB_API.format(date=date_str)
        return self._request_json(url, date_str)

    def _request_json(self, url: str, context: str) -> dict[str, Any]:
        """Fetch and decode JSON, wrapping transport/parse failures in ApiError.

        `context` (e.g. a date or range) is included in error messages.
        """
        req = Request(url, headers={"User-Agent": self._user_agent})
        try:
            with urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except OSError as e:
            # URLError, socket timeouts, connection resets, TLS failures, etc.
            raise ApiError(f"Error fetching data for {context}: {e}") from e
        except json.JSONDecodeError as e:
            raise ApiError(f"Invalid response from MLB API for {context}: {e}") from e

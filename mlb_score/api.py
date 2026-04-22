"""MLB Stats API client."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

MLB_API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"


class ApiError(Exception):
    """Raised when the MLB API request fails."""

    pass


def fetch_schedule(date_str: str) -> dict[str, Any]:
    """Fetch the MLB schedule for a single date (YYYY-MM-DD).

    Returns the raw JSON response from the API.
    Raises ApiError on network or HTTP failures.
    """
    url = MLB_API.format(date=date_str)
    req = Request(url, headers={"User-Agent": "mlb-score-cli/1.0"})
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except URLError as e:
        raise ApiError(f"Error fetching data for {date_str}: {e}") from e


def fetch_date_range(
    target_date: date,
    days: int = 1,
) -> list[tuple[date, dict[str, Any]]]:
    """Fetch schedules for a range of dates ending at target_date.

    Returns list of (date, raw_api_response) tuples.
    """
    results: list[tuple[date, dict[str, Any]]] = []
    for i in range(days):
        lookup_date = target_date - timedelta(days=i)
        data = fetch_schedule(lookup_date.isoformat())
        results.append((lookup_date, data))
    return results

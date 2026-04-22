"""Tests for API client error handling."""

from datetime import date, timedelta
from unittest.mock import patch
from urllib.error import URLError

import pytest

from mlb_score.api import ApiError, fetch_schedule, fetch_date_range


def test_fetch_schedule_raises_api_error_on_network_failure():
    """URLError from urlopen is wrapped as ApiError."""
    with patch("mlb_score.api.urlopen", side_effect=URLError("connection refused")):
        with pytest.raises(ApiError) as exc_info:
            fetch_schedule("2026-04-21")
        assert "2026-04-21" in str(exc_info.value)


def test_fetch_date_range_returns_correct_dates():
    """fetch_date_range yields dates counting backward from target."""
    call_log = []

    def fake_fetch(date_str: str):
        call_log.append(date_str)
        return {"dates": [{"games": []}]}

    with patch("mlb_score.api.fetch_schedule", side_effect=fake_fetch):
        results = fetch_date_range(date(2026, 4, 21), days=3)

    fetched_dates = [d for d, _ in results]
    assert fetched_dates == [
        date(2026, 4, 21),
        date(2026, 4, 20),
        date(2026, 4, 19),
    ]
    # Verify the API was called with ISO-formatted strings
    assert call_log == ["2026-04-21", "2026-04-20", "2026-04-19"]


def test_fetch_date_range_single_day():
    """Default days=1 returns only the target date."""
    with patch("mlb_score.api.fetch_schedule", return_value={"dates": [{"games": []}]}):
        results = fetch_date_range(date(2026, 4, 21))

    assert len(results) == 1
    assert results[0][0] == date(2026, 4, 21)


def test_fetch_schedule_api_error_preserves_cause():
    """ApiError chains the original exception."""
    with patch("mlb_score.api.urlopen", side_effect=URLError("timeout")):
        with pytest.raises(ApiError) as exc_info:
            fetch_schedule("2026-04-21")
        assert exc_info.value.__cause__ is not None

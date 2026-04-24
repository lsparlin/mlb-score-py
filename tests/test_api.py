"""Tests for MlbClient error handling and fetching."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from mlb_score.client import ApiError, MlbClient
from mlb_score.models import Game
from tests.conftest import load_fixture


def test_fetch_schedule_raises_api_error_on_network_failure():
    """URLError from urlopen is wrapped as ApiError."""
    from urllib.error import URLError

    client = MlbClient()
    with patch("mlb_score.client.urlopen", side_effect=URLError("connection refused")):
        with pytest.raises(ApiError) as exc_info:
            client.fetch_schedule("2026-04-21")
        assert "2026-04-21" in str(exc_info.value)


def test_fetch_schedule_empty_date_returns_empty_list():
    """fetch_schedule returns an empty list when the API has no games for the date."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: b'{"dates": [{"games": []}]}')
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        games = client.fetch_schedule("2026-04-21")
    assert games == []


def test_fetch_schedule_empty_dates_array_returns_empty_list():
    """fetch_schedule handles an empty dates array gracefully."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: b'{"dates": []}')
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        games = client.fetch_schedule("2026-04-21")
    assert games == []


def test_fetch_date_range_calls_correct_dates():
    """fetch_date_range calls fetch_schedule for each date counting backward."""
    call_log = []

    def fake_fetch(date_str: str):
        call_log.append(date_str)
        return []  # no games

    client = MlbClient()
    with patch.object(client, "fetch_schedule", side_effect=fake_fetch):
        results = client.fetch_date_range(date(2026, 4, 21), days=3)

    # Verify the API was called with ISO-formatted strings
    assert call_log == ["2026-04-21", "2026-04-20", "2026-04-19"]
    # All queried dates present, even with no games
    assert sorted(results.keys()) == [
        date(2026, 4, 19),
        date(2026, 4, 20),
        date(2026, 4, 21),
    ]
    for games in results.values():
        assert games == []


def test_fetch_date_range_single_day():
    """Default days=1 returns only the target date."""
    client = MlbClient()
    with patch.object(client, "fetch_schedule", return_value=[]):
        results = client.fetch_date_range(date(2026, 4, 21))

    assert len(results) == 1
    assert date(2026, 4, 21) in results
    assert results[date(2026, 4, 21)] == []


def test_fetch_schedule_api_error_preserves_cause():
    """ApiError chains the original exception."""
    from urllib.error import URLError

    client = MlbClient()
    with patch("mlb_score.client.urlopen", side_effect=URLError("timeout")):
        with pytest.raises(ApiError) as exc_info:
            client.fetch_schedule("2026-04-21")
        assert exc_info.value.__cause__ is not None


def test_fetch_schedule_parses_games_into_models(schedule_raw):
    """fetch_schedule returns fully instantiated Game models."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        raw_json = load_fixture("schedule_2026-04-21.json")
        import json

        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: json.dumps(raw_json).encode())
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        games = client.fetch_schedule("2026-04-21")

    assert isinstance(games, list)
    assert len(games) > 0
    assert isinstance(games[0], Game)
    assert games[0].away_team.team.name != ""
    assert games[0].home_team.team.name != ""


def test_fetch_schedule_raises_api_error_on_invalid_json():
    """Non-JSON responses (e.g. 502) raise ApiError with context."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: b"Not Found")
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        with pytest.raises(ApiError) as exc_info:
            client.fetch_schedule("2026-04-21")
        assert "2026-04-21" in str(exc_info.value)


def test_fetch_schedule_handles_null_dates_entry():
    """If dates[0] is None, return empty list instead of crashing."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: b'{"dates": [null]}')
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        games = client.fetch_schedule("2026-04-21")
    assert games == []


@pytest.fixture
def schedule_raw():
    return load_fixture("schedule_2026-04-21.json")

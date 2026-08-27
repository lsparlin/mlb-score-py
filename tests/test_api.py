"""Tests for MlbClient error handling and fetching, and parser logic."""

import http.client
import json
import socket
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from mlb_score.client import ApiError, MlbClient
from mlb_score.models import Game, GameState
from mlb_score.parser import parse_game, parse_games, parse_games_by_date, parse_team
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
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(
            read=lambda: b'{"dates": [{"games": []}]}'
        )
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


def test_fetch_date_range_includes_all_queried_dates_even_when_api_returns_none():
    """Every queried date appears in the result, even if the API omits it."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: b'{"dates": []}')
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        results = client.fetch_date_range(date(2026, 4, 21), days=3)

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
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: b'{"dates": []}')
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
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

        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(
            read=lambda: json.dumps(raw_json).encode()
        )
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


# --- parser ---

_TEAMS = {
    "away": {"team": {"name": "Cardinals", "abbreviation": "STL"}, "score": 5, "isWinner": True},
    "home": {"team": {"name": "Dodgers", "abbreviation": "LAD"}, "score": 3, "isWinner": False},
}


def test_parse_games_empty_response():
    assert parse_games({}) == []
    assert parse_games({"dates": []}) == []


def test_parse_games_null_date_entry():
    assert parse_games({"dates": [None]}) == []


def test_parse_games_from_fixture():
    raw = load_fixture("schedule_2026-04-21.json")
    games = parse_games(raw)
    assert len(games) > 0
    assert all(isinstance(g, Game) for g in games)
    assert all(g.away_team.team.name != "" for g in games)


def test_parse_game_final():
    raw = {
        "teams": _TEAMS,
        "status": {"statusCode": "F"},
        "venue": {"name": "Busch Stadium"},
        "dayNight": "Night",
    }
    game = parse_game(raw)
    assert game.state == GameState.FINAL
    assert game.away_team.team.name == "Cardinals"
    assert game.away_team.is_winner is True
    assert game.home_team.score == 3
    assert game.venue == "Busch Stadium"


def test_parse_game_live():
    raw = {
        "teams": _TEAMS,
        "status": {"statusCode": "I"},
        "venue": {"name": "Busch Stadium"},
        "dayNight": "Day",
    }
    assert parse_game(raw).state == GameState.LIVE


def test_parse_game_live_extracts_detailed_state():
    raw = {
        "teams": _TEAMS,
        "status": {"statusCode": "I", "detailedState": "Top 7th"},
        "venue": {"name": "Busch Stadium"},
        "dayNight": "Day",
    }
    assert parse_game(raw).detailed_state == "Top 7th"


def test_parse_game_without_detailed_state_defaults_to_empty():
    raw = {
        "teams": _TEAMS,
        "status": {"statusCode": "F"},
        "venue": {"name": "Busch Stadium"},
        "dayNight": "Night",
    }
    assert parse_game(raw).detailed_state == ""


def test_parse_game_unknown_status_defaults_to_scheduled():
    raw = {
        "teams": _TEAMS,
        "status": {"statusCode": "X"},
        "venue": {"name": "Busch Stadium"},
        "dayNight": "Night",
    }
    assert parse_game(raw).state == GameState.SCHEDULED


def test_parse_team_is_home_flag():
    away = parse_team(_TEAMS, "away")
    home = parse_team(_TEAMS, "home")
    assert away.is_home is False
    assert home.is_home is True


def test_fetch_schedule_raises_api_error_on_socket_timeout():
    """A raw socket timeout (OSError, not URLError) is wrapped as ApiError."""
    client = MlbClient()
    with patch("mlb_score.client.urlopen", side_effect=socket.timeout("timed out")):
        with pytest.raises(ApiError) as exc_info:
            client.fetch_schedule("2026-04-21")
        assert "2026-04-21" in str(exc_info.value)


def test_fetch_schedule_raises_api_error_on_connection_reset():
    """A dropped connection mid-response is wrapped as ApiError, not a traceback."""
    client = MlbClient()
    error = http.client.RemoteDisconnected("Remote end closed connection")
    with patch("mlb_score.client.urlopen", side_effect=error):
        with pytest.raises(ApiError) as exc_info:
            client.fetch_schedule("2026-04-21")
        assert "2026-04-21" in str(exc_info.value)


def test_parse_games_by_date_groups_multiple_dates():
    """parse_games_by_date groups games from each dates[] entry under its date."""
    raw = {
        "dates": [
            {
                "date": "2026-04-19",
                "games": [
                    {
                        "teams": _TEAMS,
                        "status": {"statusCode": "F"},
                        "venue": {"name": "Busch Stadium"},
                        "dayNight": "Night",
                    }
                ],
            },
            {
                "date": "2026-04-21",
                "games": [
                    {
                        "teams": _TEAMS,
                        "status": {"statusCode": "F"},
                        "venue": {"name": "Busch Stadium"},
                        "dayNight": "Night",
                    },
                    {
                        "teams": _TEAMS,
                        "status": {"statusCode": "F"},
                        "venue": {"name": "Busch Stadium"},
                        "dayNight": "Night",
                    },
                ],
            },
        ]
    }
    result = parse_games_by_date(raw)
    assert set(result) == {date(2026, 4, 19), date(2026, 4, 21)}
    assert len(result[date(2026, 4, 19)]) == 1
    assert len(result[date(2026, 4, 21)]) == 2
    assert all(isinstance(g, Game) for games in result.values() for g in games)


def test_fetch_date_range_uses_single_api_call():
    """fetch_date_range makes exactly one API request covering the full range."""
    raw = load_fixture("schedule_2026-04-21.json")
    client = MlbClient()
    with patch("mlb_score.client.urlopen") as mock_urlopen:
        body = json.dumps(raw).encode()
        mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: body)
        mock_urlopen.return_value.__exit__ = lambda s, *a: None
        results = client.fetch_date_range(date(2026, 4, 21), days=3)

    assert mock_urlopen.call_count == 1
    url = mock_urlopen.call_args.args[0].full_url
    assert "startDate=2026-04-19" in url
    assert "endDate=2026-04-21" in url
    # All three queried dates present in the result
    assert sorted(results.keys()) == [date(2026, 4, 19), date(2026, 4, 20), date(2026, 4, 21)]
    # Games for 04-21 come from the fixture
    assert len(results[date(2026, 4, 21)]) > 0


def test_fetch_date_range_raises_api_error_on_network_failure():
    """Network failures during a range fetch raise ApiError mentioning both dates."""
    from urllib.error import URLError

    client = MlbClient()
    with patch("mlb_score.client.urlopen", side_effect=URLError("connection refused")):
        with pytest.raises(ApiError) as exc_info:
            client.fetch_date_range(date(2026, 4, 21), days=3)
        assert "2026-04-19" in str(exc_info.value)
        assert "2026-04-21" in str(exc_info.value)

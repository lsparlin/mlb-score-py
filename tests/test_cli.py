"""Integration tests for CLI entry point."""

from datetime import date, timedelta
from unittest.mock import patch

from mlb_score.client import ApiError
from mlb_score.cli import main, parse_args
from mlb_score.models import Game, Schedule
from tests.conftest import load_fixture

# --- Argument parsing ---


def test_parse_args_defaults():
    args = parse_args(["Cardinals"])
    assert args.team == "Cardinals"
    assert args.date is None
    assert args.days == 1


def test_parse_args_with_date():
    args = parse_args(["Yankees", "-d", "2026-04-15"])
    assert args.team == "Yankees"
    assert args.date == "2026-04-15"


def test_parse_args_with_days():
    args = parse_args(["Dodgers", "-n", "5"])
    assert args.days == 5


# --- main() happy path ---


def test_main_returns_zero_on_success(capsys):
    raw = load_fixture("schedule_2026-04-21.json")
    import json
    from unittest.mock import MagicMock

    def fake_fetch_schedule(date_str: str):
        from mlb_score.client import MlbClient

        client = MlbClient()
        with patch("mlb_score.client.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: json.dumps(raw).encode())
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            return client.fetch_schedule(date_str)

    with patch("mlb_score.cli.MlbClient") as MockClient:
        mock_client = MockClient.return_value
        mock_client.fetch_date_range.return_value = {date(2026, 4, 21): fake_fetch_schedule("2026-04-21")}
        code = main(["Cardinals", "-d", "2026-04-21"])

    assert code == 0
    captured = capsys.readouterr()
    assert "Cardinals" in captured.out


def test_main_returns_zero_with_multiple_days(capsys):
    raw = load_fixture("schedule_2026-04-21.json")
    import json
    from unittest.mock import MagicMock

    def fake_fetch(date_str: str):
        from mlb_score.client import MlbClient

        client = MlbClient()
        with patch("mlb_score.client.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: json.dumps(raw).encode())
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            return client.fetch_schedule(date_str)

    games_21 = fake_fetch("2026-04-21")
    games_20: list[Game] = []

    with patch("mlb_score.cli.MlbClient") as MockClient:
        mock_client = MockClient.return_value
        mock_client.fetch_date_range.return_value = {
            date(2026, 4, 21): games_21,
            date(2026, 4, 20): games_20,
        }
        code = main(["Cardinals", "-d", "2026-04-21", "-n", "2"])

    assert code == 0


# --- main() no games found ---


def test_main_returns_one_when_no_games(capsys):
    with patch("mlb_score.cli.MlbClient") as MockClient:
        mock_client = MockClient.return_value
        mock_client.fetch_date_range.return_value = {}
        code = main(["Cardinals"])

    assert code == 1
    captured = capsys.readouterr()
    assert "No games found" in captured.out


# --- main() API error ---


def test_main_returns_one_on_api_error(capsys):
    with patch("mlb_score.cli.MlbClient") as MockClient:
        mock_client = MockClient.return_value
        mock_client.fetch_date_range.side_effect = ApiError("network failure")
        code = main(["Cardinals"])

    assert code == 1
    captured = capsys.readouterr()
    # Error goes to stderr
    assert "network failure" in captured.err


# --- main() uses yesterday by default ---


def test_main_defaults_to_yesterday():
    """Without -d flag, target date is yesterday."""
    raw = load_fixture("schedule_2026-04-21.json")
    import json
    from unittest.mock import MagicMock

    call_log = []

    def fake_fetch(target_date, days=1):
        call_log.append((target_date, days))
        from mlb_score.client import MlbClient

        client = MlbClient()
        with patch("mlb_score.client.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: MagicMock(read=lambda: json.dumps(raw).encode())
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            result = {}
            for i in range(days):
                lookup_date = target_date - timedelta(days=i)
                games = client.fetch_schedule(lookup_date.isoformat())
                if games:
                    result[lookup_date] = games
            return result

    with patch("mlb_score.cli.MlbClient") as MockClient:
        mock_client = MockClient.return_value
        mock_client.fetch_date_range.side_effect = fake_fetch
        main(["Cardinals"])

    assert len(call_log) == 1
    target_date, _ = call_log[0]
    # Should be yesterday (not today)
    assert target_date < date.today()

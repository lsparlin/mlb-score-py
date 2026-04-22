"""Integration tests for CLI entry point."""

from datetime import date
from unittest.mock import patch

import pytest

from mlb_score.api import ApiError
from mlb_score.cli import main, parse_args
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

    with patch("mlb_score.cli.fetch_date_range", return_value=[(date(2026, 4, 21), raw)]):
        code = main(["Cardinals", "-d", "2026-04-21"])

    assert code == 0
    captured = capsys.readouterr()
    assert "Cardinals" in captured.out


def test_main_returns_zero_with_multiple_days(capsys):
    raw = load_fixture("schedule_2026-04-21.json")

    with patch(
        "mlb_score.cli.fetch_date_range",
        return_value=[
            (date(2026, 4, 21), raw),
            (date(2026, 4, 20), {"dates": [{"games": []}]}),
        ],
    ):
        code = main(["Cardinals", "-d", "2026-04-21", "-n", "2"])

    assert code == 0


# --- main() no games found ---


def test_main_returns_one_when_no_games(capsys):
    empty_raw = {"dates": [{"games": []}]}

    with patch("mlb_score.cli.fetch_date_range", return_value=[(date(2026, 4, 21), empty_raw)]):
        code = main(["Cardinals"])

    assert code == 1
    captured = capsys.readouterr()
    assert "No games found" in captured.out


# --- main() API error ---


def test_main_returns_one_on_api_error(capsys):
    with patch("mlb_score.cli.fetch_date_range", side_effect=ApiError("network failure")):
        code = main(["Cardinals"])

    assert code == 1
    captured = capsys.readouterr()
    # Error goes to stderr
    assert "network failure" in captured.err


# --- main() uses yesterday by default ---


def test_main_defaults_to_yesterday():
    """Without -d flag, target date is yesterday."""
    raw = load_fixture("schedule_2026-04-21.json")
    call_log = []

    def fake_fetch(target_date, days=1):
        call_log.append((target_date, days))
        return [(target_date, raw)]

    with patch("mlb_score.cli.fetch_date_range", side_effect=fake_fetch):
        main(["Cardinals"])

    assert len(call_log) == 1
    target_date, _ = call_log[0]
    # Should be yesterday (not today)
    from datetime import timedelta
    assert target_date < date.today()

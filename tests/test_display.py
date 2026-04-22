"""Tests for display formatting."""

from mlb_score.display import format_game, print_no_results, print_results
from mlb_score.models import Game, Schedule, TeamInfo, TeamScore


def _team(name: str) -> TeamInfo:
    return TeamInfo(name=name)


def test_format_game_contains_team_names():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        venue="Busch Stadium",
        day_night="Night",
    )
    result = format_game(game)
    assert "Cardinals" in result
    assert "Dodgers" in result


def test_format_game_contains_score():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        venue="Busch Stadium",
        day_night="Night",
    )
    result = format_game(game)
    assert "5\u20133" in result


def test_format_game_contains_venue():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        venue="Busch Stadium",
        day_night="Night",
    )
    result = format_game(game)
    assert "Busch Stadium" in result


def test_format_game_contains_label():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        venue="Busch Stadium",
        day_night="Night",
    )
    result = format_game(game)
    assert "WIN" in result


def test_print_results_outputs(capsys):
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        venue="Busch Stadium",
        day_night="Night",
    )
    schedule = Schedule()
    from datetime import date

    schedule.games_by_date[date(2026, 4, 21)] = [game]

    print_results(schedule, date(2026, 4, 21), "Cardinals")
    captured = capsys.readouterr()
    assert "Cardinals" in captured.out


def test_print_no_results_outputs(capsys):
    from datetime import date

    print_no_results("Pirates", date(2026, 4, 21))
    captured = capsys.readouterr()
    assert "No games found" in captured.out

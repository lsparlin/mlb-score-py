"""Tests for display formatting."""

from datetime import date

from mlb_score.display import format_game, print_no_results, print_results
from mlb_score.models import Game, GameState, Schedule, TeamInfo, TeamScore


def test_format_game_contains_team_names(cardinals_beat_dodgers):
    result = format_game(cardinals_beat_dodgers)
    assert "Cardinals" in result
    assert "Dodgers" in result


def test_format_game_contains_score(cardinals_beat_dodgers):
    result = format_game(cardinals_beat_dodgers)
    assert "5–3" in result


def test_format_game_contains_venue(cardinals_beat_dodgers):
    result = format_game(cardinals_beat_dodgers)
    assert "Busch Stadium" in result


def test_format_game_contains_label(cardinals_beat_dodgers):
    result = format_game(cardinals_beat_dodgers)
    assert "WIN" in result


def test_print_results_outputs(cardinals_beat_dodgers, capsys):
    schedule = Schedule()
    schedule.games_by_date[date(2026, 4, 21)] = [cardinals_beat_dodgers]
    print_results(schedule, date(2026, 4, 21), "Cardinals")
    captured = capsys.readouterr()
    assert "Cardinals" in captured.out


def test_print_no_results_outputs(capsys):
    print_no_results("Pirates", date(2026, 4, 21))
    captured = capsys.readouterr()
    assert "No games found" in captured.out


def test_format_game_scheduled():
    game = Game(
        away_team=TeamScore(team=TeamInfo(name="Cardinals"), score=0, is_winner=None),
        home_team=TeamScore(team=TeamInfo(name="Dodgers"), score=0, is_winner=None),
        venue="Busch Stadium",
        day_night="Night",
        state=GameState.SCHEDULED,
    )
    result = format_game(game)
    assert "vs" in result
    assert "SCHEDULED" in result
    assert "✅" not in result
    assert "❌" not in result


def test_format_game_live():
    game = Game(
        away_team=TeamScore(team=TeamInfo(name="Cardinals"), score=3, is_winner=None),
        home_team=TeamScore(team=TeamInfo(name="Dodgers"), score=2, is_winner=None),
        venue="Busch Stadium",
        day_night="Night",
        state=GameState.LIVE,
    )
    result = format_game(game)
    assert "3–2" in result
    assert "LIVE" in result

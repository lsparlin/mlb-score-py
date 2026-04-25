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


def test_format_game_final_score_follows_away_home_order(cardinals_beat_dodgers):
    # Cardinals (away, winner) 5 – Dodgers (home) 3
    result = format_game(cardinals_beat_dodgers)
    assert "5–3" in result
    assert "3–5" not in result


def test_format_game_final_home_wins_score_follows_away_home_order(astros_vs_guardians):
    # Astros (away) 5 – Guardians (home, winner) 8
    result = format_game(astros_vs_guardians)
    assert "5–8" in result
    assert "8–5" not in result


def test_format_game_live_score_uses_away_home_order():
    game = Game(
        away_team=TeamScore(team=TeamInfo(name="Cardinals"), score=3, is_winner=None),
        home_team=TeamScore(team=TeamInfo(name="Dodgers"), score=7, is_winner=None),
        venue="Dodger Stadium",
        day_night="Night",
        state=GameState.LIVE,
    )
    result = format_game(game)
    assert "3–7" in result
    assert "7–3" not in result


def test_format_game_scheduled_shows_vs_no_winner_marks():
    game = Game(
        away_team=TeamScore(team=TeamInfo(name="Cardinals"), score=0, is_winner=None),
        home_team=TeamScore(team=TeamInfo(name="Dodgers"), score=0, is_winner=None),
        venue="Busch Stadium",
        day_night="Night",
        state=GameState.SCHEDULED,
    )
    result = format_game(game)
    assert "vs" in result
    assert "✅" not in result
    assert "❌" not in result


def test_format_game_win_loss_reflects_searched_team_home_loss():
    """Cardinals (home) lost to Mariners (away) 11-9 — searching 'cardinals' should show LOSS."""
    game = Game(
        away_team=TeamScore(team=TeamInfo(name="Seattle Mariners"), score=11, is_winner=True),
        home_team=TeamScore(team=TeamInfo(name="St. Louis Cardinals"), score=9, is_winner=False),
        venue="Busch Stadium",
        day_night="Day",
        state=GameState.FINAL,
    )
    result = format_game(game, team="cardinals")
    assert "LOSS" in result
    assert "WIN" not in result


def test_format_game_win_loss_reflects_searched_team_home_win(astros_vs_guardians):
    """Guardians (home) beat Astros (away) — searching 'guardians' should show WIN."""
    result = format_game(astros_vs_guardians, team="guardians")
    assert "WIN" in result
    assert "LOSS" not in result


def test_format_game_win_loss_reflects_searched_team_away_win(cardinals_beat_dodgers):
    """Cardinals (away) beat Dodgers — searching 'cardinals' should show WIN."""
    result = format_game(cardinals_beat_dodgers, team="cardinals")
    assert "WIN" in result
    assert "LOSS" not in result


def test_format_game_win_loss_reflects_searched_team_away_loss(astros_vs_guardians):
    """Astros (away) lost to Guardians — searching 'astros' should show LOSS."""
    result = format_game(astros_vs_guardians, team="astros")
    assert "LOSS" in result
    assert "WIN" not in result

"""Tests for data model properties."""

from mlb_score.models import Game, GameState, TeamInfo, TeamScore


def _team(name: str) -> TeamInfo:
    return TeamInfo(name=name)


# --- TeamInfo ---


def test_team_display_name():
    assert TeamInfo(name="Cardinals").display_name == "Cardinals"


# --- TeamScore ---


def test_teamscore_status_win():
    score = TeamScore(team=_team("Cardinals"), is_winner=True)
    assert score.status == "WIN"


def test_teamscore_status_loss():
    score = TeamScore(team=_team("Cardinals"), is_winner=False)
    assert score.status == "LOSS"


def test_teamscore_status_unknown():
    score = TeamScore(team=_team("Cardinals"), is_winner=None)
    assert score.status == ""


# --- Game: winner ---


def test_game_winner_away():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        state=GameState.FINAL,
    )
    assert game.winner == _team("Cardinals")


def test_game_winner_home():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=2, is_winner=False),
        home_team=TeamScore(team=_team("Dodgers"), score=4, is_winner=True),
        state=GameState.FINAL,
    )
    assert game.winner == _team("Dodgers")


def test_game_winner_none_when_no_winner_declared():
    """When no winner is declared, winner returns None even for FINAL games."""
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=1, is_winner=None),
        home_team=TeamScore(team=_team("Dodgers"), score=1, is_winner=None),
        state=GameState.FINAL,
    )
    assert game.winner is None


# --- Game: score_string (winner-first) ---


def test_score_string_away_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        state=GameState.FINAL,
    )
    assert game.score_string == "5\u20133"


def test_score_string_home_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=2, is_winner=False),
        home_team=TeamScore(team=_team("Dodgers"), score=4, is_winner=True),
        state=GameState.FINAL,
    )
    assert game.score_string == "4\u20132"


# --- Game: matchup_string and label ---


def test_matchup_away_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        state=GameState.FINAL,
    )
    assert "Cardinals" in game.matchup_string
    assert game.label == "FINAL"
    assert game.winner == _team("Cardinals")


def test_matchup_home_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=2, is_winner=False),
        home_team=TeamScore(team=_team("Dodgers"), score=4, is_winner=True),
        state=GameState.FINAL,
    )
    assert "Dodgers" in game.matchup_string
    assert game.label == "FINAL"
    assert game.winner == _team("Dodgers")


# --- GameState ---


def test_game_state_scheduled():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=0, is_winner=None),
        home_team=TeamScore(team=_team("Dodgers"), score=0, is_winner=None),
        state=GameState.SCHEDULED,
    )
    assert game.state == GameState.SCHEDULED
    assert game.label == "SCHEDULED"
    assert game.winner is None
    assert game.score_string == "vs"
    assert "@" in game.matchup_string
    assert "✅" not in game.matchup_string
    assert "❌" not in game.matchup_string


def test_game_state_live():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=3, is_winner=None),
        home_team=TeamScore(team=_team("Dodgers"), score=2, is_winner=None),
        state=GameState.LIVE,
    )
    assert game.state == GameState.LIVE
    assert game.label == "LIVE"
    assert game.winner is None
    assert game.score_string == "3–2"


def test_game_state_final():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        state=GameState.FINAL,
    )
    assert game.state == GameState.FINAL
    assert game.label == "FINAL"
    assert game.winner == _team("Cardinals")
    assert "5–3" in game.score_string

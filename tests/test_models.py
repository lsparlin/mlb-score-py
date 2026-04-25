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


# --- GameState ---


def test_game_state_scheduled():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=0, is_winner=None),
        home_team=TeamScore(team=_team("Dodgers"), score=0, is_winner=None),
        state=GameState.SCHEDULED,
    )
    assert game.state == GameState.SCHEDULED
    assert game.winner is None


def test_game_state_live():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=3, is_winner=None),
        home_team=TeamScore(team=_team("Dodgers"), score=2, is_winner=None),
        state=GameState.LIVE,
    )
    assert game.state == GameState.LIVE
    assert game.winner is None


def test_game_state_final():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
        state=GameState.FINAL,
    )
    assert game.state == GameState.FINAL
    assert game.winner == _team("Cardinals")

"""Tests for data model properties."""

from mlb_score.models import Game, TeamInfo, TeamScore


def _team(name: str) -> TeamInfo:
    return TeamInfo(name=name)


# --- TeamInfo ---


def test_team_display_name_with_location():
    team = TeamInfo(name="Cardinals", location="St. Louis")
    assert team.display_name == "St. Louis Cardinals"


def test_team_display_name_no_location():
    team = TeamInfo(name="Cardinals")
    assert team.display_name == "Cardinals"


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
    )
    assert game.winner == _team("Cardinals")


def test_game_winner_home():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=2, is_winner=False),
        home_team=TeamScore(team=_team("Dodgers"), score=4, is_winner=True),
    )
    assert game.winner == _team("Dodgers")


def test_game_winner_fallback_unfinished():
    """When both teams have is_winner=None, fallback to home team."""
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=1, is_winner=None),
        home_team=TeamScore(team=_team("Dodgers"), score=1, is_winner=None),
    )
    assert game.winner == _team("Dodgers")


# --- Game: score_string (winner-first) ---


def test_score_string_away_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
    )
    assert game.score_string == "5\u20133"


def test_score_string_home_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=2, is_winner=False),
        home_team=TeamScore(team=_team("Dodgers"), score=4, is_winner=True),
    )
    assert game.score_string == "4\u20132"


# --- Game: matchup_string and label ---


def test_matchup_away_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=_team("Dodgers"), score=3, is_winner=False),
    )
    assert "Cardinals" in game.matchup_string
    assert game.label == "WIN"


def test_matchup_home_wins():
    game = Game(
        away_team=TeamScore(team=_team("Cardinals"), score=2, is_winner=False),
        home_team=TeamScore(team=_team("Dodgers"), score=4, is_winner=True),
    )
    assert "Dodgers" in game.matchup_string
    assert game.label == "LOSS"

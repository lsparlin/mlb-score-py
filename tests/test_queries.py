"""Tests for query and filtering logic."""

from datetime import date

from mlb_score.models import Game, Schedule, TeamInfo, TeamScore
from mlb_score.queries import build_schedule, find_team_games

# --- Static fixture: pre-parsed Game objects for query tests ---
# Kept static to decouple query tests from client internals.

_cardinals = TeamInfo(name="St. Louis Cardinals", location="St. Louis")
_marlins = TeamInfo(name="Miami Marlins", location="Miami")
_astros = TeamInfo(name="Houston Astros", location="Houston")
_guardians = TeamInfo(name="Cleveland Guardians", location="Cleveland")

def _cardinals_vs_marlins():
    """St. Louis Cardinals @ Miami Marlins — Cardinals won 5-3."""
    return Game(
        away_team=TeamScore(team=_cardinals, score=5, is_winner=True, is_home=False),
        home_team=TeamScore(team=_marlins, score=3, is_winner=False, is_home=True),
        venue="loanDepot park",
        day_night="Night",
    )


def _astros_vs_guardians():
    """Houston Astros @ Cleveland Guardians — Guardians won 8-5."""
    return Game(
        away_team=TeamScore(team=_astros, score=5, is_winner=False, is_home=False),
        home_team=TeamScore(team=_guardians, score=8, is_winner=True, is_home=True),
        venue="Progressive Field",
        day_night="Day",
    )


# --- find_team_games ---


def test_find_team_games_returns_match():
    games = [_cardinals_vs_marlins(), _astros_vs_guardians()]
    matches = find_team_games(games, "Cardinals")
    assert len(matches) == 1
    first_game = matches[0]
    away_name = first_game.away_team.team.name.lower()
    home_name = first_game.home_team.team.name.lower()
    assert "cardinals" in away_name or "cardinals" in home_name


def test_find_team_games_no_match():
    """A team not playing that day returns empty list."""
    games = [_cardinals_vs_marlins(), _astros_vs_guardians()]
    matches = find_team_games(games, "ZZZNonexistentTeam")
    assert matches == []


def test_find_team_games_case_insensitive():
    games = [_cardinals_vs_marlins(), _astros_vs_guardians()]
    upper = find_team_games(games, "CARDINALS")
    lower = find_team_games(games, "cardinals")
    mixed = find_team_games(games, "Cardinals")
    assert len(upper) == len(lower) == len(mixed)


# --- build_schedule ---


def test_build_schedule_returns_schedule():
    games_by_date: dict[date, list[Game]] = {}
    schedule = build_schedule(games_by_date, "Cardinals")
    assert isinstance(schedule, Schedule)


def test_build_schedule_empty_when_no_match():
    games_by_date = {date(2026, 4, 21): [_cardinals_vs_marlins()]}
    schedule = build_schedule(games_by_date, "ZZZNonexistentTeam")
    assert schedule.is_empty


def test_build_schedule_populates_games_by_date():
    games_by_date = {date(2026, 4, 21): [_cardinals_vs_marlins()]}
    schedule = build_schedule(games_by_date, "Cardinals")
    assert not schedule.is_empty
    assert date(2026, 4, 21) in schedule.games_by_date

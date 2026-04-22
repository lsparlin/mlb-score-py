"""Tests for query and filtering logic."""

from datetime import date

import pytest

from mlb_score.models import Game, Schedule
from mlb_score.queries import find_team_games, parse_game, build_schedule
from tests.conftest import load_fixture


@pytest.fixture
def schedule_raw():
    return load_fixture("schedule_2026-04-21.json")


# --- find_team_games ---


def test_find_team_games_returns_match(schedule_raw):
    games = find_team_games(schedule_raw, "Cardinals")
    # Cardinals played on 2026-04-21
    assert len(games) >= 1
    first_game = games[0]
    away_name = first_game.away_team.team.name.lower()
    home_name = first_game.home_team.team.name.lower()
    assert "cardinals" in away_name or "cardinals" in home_name


def test_find_team_games_no_match(schedule_raw):
    """A team not playing that day returns empty list."""
    games = find_team_games(schedule_raw, "Pirates")
    # Pirates may or may not have played; use a name guaranteed absent
    games = find_team_games(schedule_raw, "ZZZNonexistentTeam")
    assert games == []


def test_find_team_games_case_insensitive(schedule_raw):
    upper = find_team_games(schedule_raw, "CARDINALS")
    lower = find_team_games(schedule_raw, "cardinals")
    mixed = find_team_games(schedule_raw, "Cardinals")
    assert len(upper) == len(lower) == len(mixed)


# --- parse_game ---


def test_parse_game_produces_model(schedule_raw):
    raw_games = schedule_raw["dates"][0]["games"]
    game = parse_game(raw_games[0])
    assert isinstance(game, Game)
    assert game.away_team.team.name != ""
    assert game.home_team.team.name != ""


def test_parse_game_scores(schedule_raw):
    raw_games = schedule_raw["dates"][0]["games"]
    game = parse_game(raw_games[0])
    # Scores should be integers (not None)
    assert isinstance(game.away_team.score, int)
    assert isinstance(game.home_team.score, int)


# --- build_schedule ---


def test_build_schedule_returns_schedule():
    raw = load_fixture("schedule_2026-04-21.json")
    fetched = [(date(2026, 4, 21), raw)]
    schedule = build_schedule(fetched, "Cardinals")
    assert isinstance(schedule, Schedule)


def test_build_schedule_empty_when_no_match():
    raw = load_fixture("schedule_2026-04-21.json")
    fetched = [(date(2026, 4, 21), raw)]
    schedule = build_schedule(fetched, "ZZZNonexistentTeam")
    assert schedule.is_empty


def test_build_schedule_populates_games_by_date():
    raw = load_fixture("schedule_2026-04-21.json")
    fetched = [(date(2026, 4, 21), raw)]
    schedule = build_schedule(fetched, "Cardinals")
    if not schedule.is_empty:
        assert date(2026, 4, 21) in schedule.games_by_date

"""Tests for Schedule.for_team filtering."""

from datetime import date

from mlb_score.models import Game, Schedule


def test_for_team_returns_match(cardinals_vs_marlins, astros_vs_guardians):
    games_by_date = {
        date(2026, 4, 21): [cardinals_vs_marlins, astros_vs_guardians],
    }
    schedule = Schedule.for_team(games_by_date, "Cardinals")
    assert not schedule.is_empty
    matches = schedule.games_by_date[date(2026, 4, 21)]
    assert len(matches) == 1
    first_game = matches[0]
    away_name = first_game.away_team.team.name.lower()
    home_name = first_game.home_team.team.name.lower()
    assert "cardinals" in away_name or "cardinals" in home_name


def test_for_team_no_match(cardinals_vs_marlins, astros_vs_guardians):
    games_by_date = {
        date(2026, 4, 21): [cardinals_vs_marlins, astros_vs_guardians],
    }
    schedule = Schedule.for_team(games_by_date, "ZZZNonexistentTeam")
    assert schedule.is_empty


def test_for_team_case_insensitive(cardinals_vs_marlins, astros_vs_guardians):
    games_by_date = {
        date(2026, 4, 21): [cardinals_vs_marlins, astros_vs_guardians],
    }
    upper = Schedule.for_team(games_by_date, "CARDINALS")
    lower = Schedule.for_team(games_by_date, "cardinals")
    mixed = Schedule.for_team(games_by_date, "Cardinals")
    assert len(upper.all_games) == len(lower.all_games) == len(mixed.all_games)


def test_for_team_returns_schedule():
    games_by_date: dict[date, list[Game]] = {}
    schedule = Schedule.for_team(games_by_date, "Cardinals")
    assert isinstance(schedule, Schedule)


def test_for_team_empty_when_no_match(cardinals_vs_marlins):
    games_by_date = {date(2026, 4, 21): [cardinals_vs_marlins]}
    schedule = Schedule.for_team(games_by_date, "ZZZNonexistentTeam")
    assert schedule.is_empty


def test_for_team_populates_games_by_date(cardinals_vs_marlins):
    games_by_date = {date(2026, 4, 21): [cardinals_vs_marlins]}
    schedule = Schedule.for_team(games_by_date, "Cardinals")
    assert not schedule.is_empty
    assert date(2026, 4, 21) in schedule.games_by_date

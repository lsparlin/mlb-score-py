"""Shared test fixtures."""

import json
from pathlib import Path

import pytest

from mlb_score.models import Game, GameState, TeamInfo, TeamScore

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture file by name."""
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


@pytest.fixture
def cardinals_vs_marlins():
    """St. Louis Cardinals @ Miami Marlins — Cardinals won 5-3."""
    return Game(
        away_team=TeamScore(team=TeamInfo(name="St. Louis Cardinals"), score=5, is_winner=True, is_home=False),
        home_team=TeamScore(team=TeamInfo(name="Miami Marlins"), score=3, is_winner=False, is_home=True),
        venue="loanDepot park",
        day_night="Night",
        state=GameState.FINAL,
    )


@pytest.fixture
def astros_vs_guardians():
    """Houston Astros @ Cleveland Guardians — Guardians won 8-5."""
    return Game(
        away_team=TeamScore(team=TeamInfo(name="Houston Astros"), score=5, is_winner=False, is_home=False),
        home_team=TeamScore(team=TeamInfo(name="Cleveland Guardians"), score=8, is_winner=True, is_home=True),
        venue="Progressive Field",
        day_night="Day",
        state=GameState.FINAL,
    )


@pytest.fixture
def cardinals_beat_dodgers():
    """Cardinals beat Dodgers 5-3, FINAL at Busch Stadium."""
    return Game(
        away_team=TeamScore(team=TeamInfo(name="Cardinals"), score=5, is_winner=True),
        home_team=TeamScore(team=TeamInfo(name="Dodgers"), score=3, is_winner=False),
        venue="Busch Stadium",
        day_night="Night",
        state=GameState.FINAL,
    )

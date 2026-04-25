"""Data models for MLB games, teams, and schedules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class GameState(str, Enum):
    """The current state of a game."""

    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINAL = "FINAL"


@dataclass(frozen=True)
class TeamInfo:
    """Represents an MLB team from the API response."""

    name: str
    abbreviation: str = ""

    @property
    def display_name(self) -> str:
        return self.name


@dataclass(frozen=True)
class TeamScore:
    """A team's result in a single game."""

    team: TeamInfo
    score: int = 0
    is_winner: Optional[bool] = None
    is_home: bool = False

    @property
    def status(self) -> str:
        if self.is_winner is True:
            return "WIN"
        if self.is_winner is False:
            return "LOSS"
        return ""


@dataclass(frozen=True)
class Game:
    """A single MLB game with both teams and metadata."""

    away_team: TeamScore
    home_team: TeamScore
    state: GameState
    venue: str = ""
    day_night: str = ""

    @property
    def winner(self) -> Optional[TeamInfo]:
        if self.state != GameState.FINAL:
            return None
        if self.away_team.is_winner:
            return self.away_team.team
        if self.home_team.is_winner:
            return self.home_team.team
        return None


@dataclass
class Schedule:
    """Collection of games for a date range."""

    games_by_date: dict[date, list[Game]] = field(default_factory=dict)

    @property
    def all_games(self) -> list[Game]:
        flat: list[Game] = []
        for games in self.games_by_date.values():
            flat.extend(games)
        return flat

    @property
    def is_empty(self) -> bool:
        return len(self.all_games) == 0

    @classmethod
    def for_team(
        cls, games_by_date: dict[date, list[Game]], team_name: str
    ) -> "Schedule":
        """Build a Schedule containing only games matching the given team name."""
        team_name_lower = team_name.lower()
        schedule = cls()
        for lookup_date, games in games_by_date.items():
            team_games = [
                game
                for game in games
                if team_name_lower in game.away_team.team.name.lower()
                or team_name_lower in game.home_team.team.name.lower()
            ]
            if team_games:
                schedule.games_by_date[lookup_date] = team_games
        return schedule

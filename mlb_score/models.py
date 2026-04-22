"""Data models for MLB games, teams, and schedules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class TeamInfo:
    """Represents an MLB team from the API response."""

    name: str
    location: str = ""
    abbreviation: str = ""

    @property
    def display_name(self) -> str:
        if self.location:
            return f"{self.location} {self.name}"
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
    venue: str = ""
    day_night: str = ""
    game_date: Optional[date] = None

    @property
    def winner(self) -> TeamInfo:
        if self.away_team.is_winner:
            return self.away_team.team
        if self.home_team.is_winner:
            return self.home_team.team
        return self.home_team.team  # fallback for unfinished games

    @property
    def score_string(self) -> str:
        """Score always shown winner-first."""
        if self.winner == self.away_team.team:
            return f"{self.away_team.score}–{self.home_team.score}"
        return f"{self.home_team.score}–{self.away_team.score}"

    @property
    def matchup_string(self) -> str:
        """Matchup line with winner indicator."""
        if self.winner == self.away_team.team:
            return f"✅ {self.away_team.team.name} @ {self.home_team.team.name}"
        return f"❌ {self.home_team.team.name} @ {self.away_team.team.name}"

    @property
    def label(self) -> str:
        if self.winner == self.away_team.team:
            return "WIN"
        return "LOSS"


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

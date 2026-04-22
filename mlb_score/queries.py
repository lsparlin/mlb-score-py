"""Query and filtering logic for MLB game data."""

from __future__ import annotations

from datetime import date
from typing import Any

from mlb_score.models import Game, Schedule, TeamInfo, TeamScore


def _parse_team(raw_teams: dict[str, Any], side: str) -> TeamScore:
    """Parse a team entry from raw API response into a TeamScore."""
    team_raw = (
        raw_teams.get(side, {})
        .get("team", {})
    )
    info = TeamInfo(
        name=team_raw.get("name", ""),
        abbreviation=team_raw.get("abbreviation", ""),
    )
    return TeamScore(
        team=info,
        score=raw_teams.get(side, {}).get("score", 0),
        is_winner=raw_teams.get(side, {}).get("isWinner"),
        is_home=(side == "home"),
    )


def parse_game(raw: dict[str, Any]) -> Game:
    """Convert a raw API game object into a structured Game model."""
    teams = raw.get("teams", {})
    return Game(
        away_team=_parse_team(teams, "away"),
        home_team=_parse_team(teams, "home"),
        venue=raw.get("venue", {}).get("name", ""),
        day_night=raw.get("dayNight", ""),
    )


def find_team_games(raw_data: dict[str, Any], team_name: str) -> list[Game]:
    """Find all games involving a team by name substring match.

    Args:
        raw_data: Raw API response for a single date.
        team_name: Team name (case-insensitive substring match).

    Returns:
        List of parsed Game objects matching the team.
    """
    team_name_lower = team_name.lower()
    matches: list[Game] = []

    raw_games = raw_data.get("dates", [])[0].get("games", [])
    for raw_game in raw_games:
        teams = raw_game.get("teams", {})
        away_name = (
            teams.get("away", {}).get("team", {}).get("name", "").lower()
        )
        home_name = (
            teams.get("home", {}).get("team", {}).get("name", "").lower()
        )

        if team_name_lower in away_name or team_name_lower in home_name:
            matches.append(parse_game(raw_game))

    return matches


def build_schedule(
    fetched_data: list[tuple[date, dict[str, Any]]],
    team_name: str,
) -> Schedule:
    """Build a filtered Schedule from raw API responses.

    Args:
        fetched_data: List of (date, raw_api_response) tuples.
        team_name: Team name to filter by.

    Returns:
        Schedule containing only games involving the requested team.
    """
    schedule = Schedule()
    for lookup_date, raw_data in fetched_data:
        games = find_team_games(raw_data, team_name)
        if games:
            schedule.games_by_date[lookup_date] = games
    return schedule

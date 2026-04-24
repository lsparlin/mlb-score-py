"""Query and filtering logic for MLB game data.

Operates exclusively on typed models; all parsing is delegated to MlbClient.
"""

from __future__ import annotations

from datetime import date

from mlb_score.models import Game, Schedule


def find_team_games(games: list[Game], team_name: str) -> list[Game]:
    """Filter a list of games to only those involving the given team.

    Args:
        games: List of already-parsed Game objects.
        team_name: Team name (case-insensitive substring match).

    Returns:
        Filtered list of Game objects matching the team.
    """
    team_name_lower = team_name.lower()
    return [
        game
        for game in games
        if team_name_lower in game.away_team.team.name.lower()
        or team_name_lower in game.home_team.team.name.lower()
    ]


def build_schedule(
    games_by_date: dict[date, list[Game]],
    team_name: str,
) -> Schedule:
    """Build a filtered Schedule from per-date game lists.

    Args:
        games_by_date: Dict mapping each date to its list of Game objects.
        team_name: Team name to filter by.

    Returns:
        Schedule containing only games involving the requested team.
    """
    schedule = Schedule()
    for lookup_date, games in games_by_date.items():
        team_games = find_team_games(games, team_name)
        if team_games:
            schedule.games_by_date[lookup_date] = team_games
    return schedule

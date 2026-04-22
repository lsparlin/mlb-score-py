"""Display formatting for MLB game results."""

from __future__ import annotations

from datetime import date

from mlb_score.models import Game, Schedule


def format_game(game: Game) -> str:
    """Format a single game as a display string.

    Example output:
      ✅ Cardinals @ Dodgers
      5–3  · Busch Stadium  · Day  · WIN
    """
    return (
        f"  {game.matchup_string}\n"
        f"  {game.score_string}  · {game.venue}  · "
        f"{game.day_night.title()}  · {game.label}"
    )


def print_results(schedule: Schedule, target_date: date, team: str) -> None:
    """Print a full schedule of results to stdout."""
    print(f"\n🏟️  {target_date.strftime('%A, %B %d, %Y')}\n")
    print(f"🔎 {team}\n")

    dates = sorted(schedule.games_by_date.keys(), reverse=True)
    total_dates = len(dates)

    for i, lookup_date in enumerate(dates):
        games = schedule.games_by_date[lookup_date]
        if total_dates > 1 or i > 0:
            print(f"  {lookup_date.strftime('%Y-%m-%d (%a)')}\n")
        for game in games:
            print(format_game(game))
        print()


def print_no_results(team: str, target_date: date) -> None:
    """Print a message when no games are found."""
    print(f"  No games found for '{team}' on {target_date}.")
    print(f"  Try a different team name or check the date.")

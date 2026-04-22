"""Display formatting for MLB game results."""

from __future__ import annotations

from datetime import date

from mlb_score.models import Game, Schedule

# ANSI color codes (safe for all modern terminals)
BOLD = "\033[1m"
DIM = "\033[2m"
CYN = "\033[36m"  # cyan
GRN = "\033[32m"  # green
RED = "\033[31m"  # red
WHT = "\033[97m"  # bright white
RST = "\033[0m"   # reset


def _colorize(text: str, *codes: str) -> str:
    """Wrap text with ANSI color codes."""
    return f"{''.join(codes)}{text}{RST}"


def format_game(game: Game) -> str:
    """Format a single game as a display string.

    Example output (with colors):
      ✅ St. Louis Cardinals @ Miami Marlins
         5–3  · loanDepot park  · Night  · WIN
    """
    # Score in bright white, venue/night in dim
    score = _colorize(game.score_string, BOLD, WHT)
    venue = _colorize(f"{game.venue}  ·  {game.day_night.title()}", DIM)

    # WIN in green, LOSS in red
    if game.label == "WIN":
        label = _colorize(game.label, BOLD, GRN)
    else:
        label = _colorize(game.label, BOLD, RED)

    return (
        f"  {game.matchup_string}\n"
        f"     {score}  · {venue}  · {label}"
    )


def print_results(schedule: Schedule, target_date: date, team: str) -> None:
    """Print a full schedule of results to stdout."""
    # Header block
    header = _colorize(f"🏟️  {target_date.strftime('%A, %B %d, %Y')}", BOLD, CYN)
    subtitle = _colorize(f"⚾  {team}", DIM)
    sep = "─" * 48

    print()
    print(header)
    print(subtitle)
    print(_colorize(sep, DIM))
    print()

    dates = sorted(schedule.games_by_date.keys(), reverse=True)

    for lookup_date in dates:
        games = schedule.games_by_date[lookup_date]

        # Date header (shown when multiple dates or between groups)
        if len(dates) > 1:
            date_label = _colorize(
                f"📅  {lookup_date.strftime('%Y-%m-%d (%a)')}", BOLD, CYN
            )
            print(f"  {date_label}")
            print(_colorize("  " + sep, DIM))
            print()

        for game in games:
            print(format_game(game))
            print()


def print_no_results(team: str, target_date: date) -> None:
    """Print a message when no games are found."""
    msg = _colorize(f"No games found for '{team}' on {target_date}.", RED)
    hint = _colorize("Try a different team name or check the date.", DIM)
    print(f"  {msg}")
    print(f"  {hint}")

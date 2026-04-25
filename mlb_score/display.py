"""All rendering decisions for MLB game results — ANSI formatting, layout, and date labels.

date_label() lives here (not in cli.py) because labelling the date range is a rendering
decision about what appears in the header, not an orchestration decision about what was queried.
"""

from __future__ import annotations

from datetime import date

from mlb_score.models import Game, GameState, Schedule

# ANSI color codes (safe for all modern terminals)
BOLD = "\033[1m"
DIM = "\033[2m"
CYN = "\033[36m"  # cyan
GRN = "\033[32m"  # green
RED = "\033[31m"  # red
WHT = "\033[97m"  # bright white
YEL = "\033[93m"  # yellow
RST = "\033[0m"   # reset


def date_label(today: bool, days: int, has_explicit_date: bool) -> str:
    """Derive a human-readable label for the date range shown in the header."""
    if has_explicit_date:
        return ""
    if today and days == 1:
        return "Today"
    if today:
        return f"Today and prior {days - 1} days"
    if days == 1:
        return "Yesterday"
    return f"Last {days} days"


def _colorize(text: str, *codes: str) -> str:
    """Wrap text with ANSI color codes."""
    return f"{''.join(codes)}{text}{RST}"


def _score_string(game: Game) -> str:
    if game.state == GameState.SCHEDULED:
        return "vs"
    return f"{game.away_team.score}–{game.home_team.score}"


def _searched_team_won(game: Game, team: str) -> bool:
    team_lower = team.lower()
    searched_is_away = team_lower in game.away_team.team.name.lower()
    return (
        searched_is_away and game.winner == game.away_team.team
    ) or (
        not searched_is_away and game.winner == game.home_team.team
    )


def _matchup_string(game: Game) -> str:
    return f"{game.away_team.team.name} @ {game.home_team.team.name}"


def format_game(game: Game, team: str = "") -> str:
    """Format a single game as a display string.

    Example output (with colors):
      St. Louis Cardinals @ Miami Marlins
         5–3  · loanDepot park  · Night  · WIN
    """
    # Score in bright white, venue/night in dim
    score = _colorize(_score_string(game), BOLD, WHT)
    venue = _colorize(f"{game.venue}  ·  {game.day_night.title()}", DIM)

    # Color the label based on game state
    if game.state == GameState.FINAL:
        if _searched_team_won(game, team):
            label = _colorize("WIN", BOLD, GRN)
        else:
            label = _colorize("LOSS", BOLD, RED)
    elif game.state == GameState.LIVE:
        label = _colorize("LIVE", BOLD, YEL)
    else:  # GameState.SCHEDULED
        label = _colorize("SCHEDULED", DIM)

    return (
        f"  {_matchup_string(game)}\n"
        f"     {score}  · {venue}  · {label}"
    )


def print_results(schedule: Schedule, target_date: date, team: str, *, label: str = "") -> None:
    """Print a full schedule of results to stdout."""
    # Header block
    header = _colorize(f"📅  {target_date.strftime('%A, %B %d, %Y')}", BOLD, CYN)
    subtitle_parts = [f"⚾  {team}"]
    if label:
        subtitle_parts.append(_colorize(label, DIM))
    subtitle = _colorize(" · ".join(subtitle_parts), DIM)
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
            print(format_game(game, team))
            print()


def print_no_results(team: str, target_date: date) -> None:
    """Print a message when no games are found."""
    msg = _colorize(f"No games found for '{team}' on {target_date}.", RED)
    hint = _colorize("Try a different team name or check the date.", DIM)
    print(f"  {msg}")
    print(f"  {hint}")

"""Parses raw MLB Stats API JSON into typed models.

All .get() calls use empty-string or zero defaults intentionally: the API returns partial
data for scheduled and live games (no scores, no winner). Raising on missing fields would
break valid real-world responses.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from mlb_score.models import Game, GameState, TeamInfo, TeamScore

# Maps MLB API status.statusCode values to GameState.
# Reference: https://statsapi.mlb.com/api/doc
MLB_STATUS_CODE_MAP: dict[str, GameState] = {
    "F": GameState.FINAL,
    "I": GameState.LIVE,
    "P": GameState.SCHEDULED,
    "W": GameState.SCHEDULED,  # walkup / warmup
    "S": GameState.SCHEDULED,  # scheduled (delayed)
}


def parse_games(raw: dict[str, Any]) -> list[Game]:
    dates = raw.get("dates")
    if not dates:
        return []
    first = dates[0]
    if not isinstance(first, dict):
        return []
    return [parse_game(raw_game) for raw_game in first.get("games", [])]


def parse_games_by_date(raw: dict[str, Any]) -> dict[date, list[Game]]:
    """Parse a (possibly multi-date) schedule response, grouped by date.

    The MLB API returns one entry per date under `dates[]`; this maps each
    entry's date to its list of Game models.
    """
    result: dict[date, list[Game]] = {}
    for entry in raw.get("dates") or []:
        if not isinstance(entry, dict):
            continue
        try:
            lookup_date = date.fromisoformat(entry.get("date", ""))
        except ValueError:
            continue
        result[lookup_date] = [parse_game(g) for g in entry.get("games", [])]
    return result


def parse_game(raw: dict[str, Any]) -> Game:
    teams = raw.get("teams", {})
    status = raw.get("status", {})
    code = status.get("statusCode", "F")
    state = MLB_STATUS_CODE_MAP.get(code, GameState.SCHEDULED)
    return Game(
        away_team=parse_team(teams, "away"),
        home_team=parse_team(teams, "home"),
        venue=raw.get("venue", {}).get("name", ""),
        day_night=raw.get("dayNight", ""),
        state=state,
    )


def parse_team(teams: dict[str, Any], side: str) -> TeamScore:
    team_raw = teams.get(side, {}).get("team", {})
    info = TeamInfo(
        name=team_raw.get("name", ""),
        abbreviation=team_raw.get("abbreviation", ""),
    )
    return TeamScore(
        team=info,
        score=teams.get(side, {}).get("score", 0),
        is_winner=teams.get(side, {}).get("isWinner"),
        is_home=(side == "home"),
    )

# PRD: Game State Domain Model

## Status: ✅ Implemented

## Goal
Accurately represent the current state of a game (Scheduled, In Progress, Final) to avoid misleading results for future or ongoing games.

## Current State
The `Game` model assumes games are completed. It calculates a `winner` by falling back to the home team if no winner is declared. This leads to a "LOSS" label being applied to games that haven't even started yet.

## Proposed Changes
1. **Introduce `GameState` Enum**: Define an enum with states: `SCHEDULED`, `LIVE`, `FINAL`.
2. **Detect State from API**: Use the API response (e.g., presence of scores, `isWinner` flags, or status strings) to determine the actual state of the game.
3. **Conditional Logic in Models**:
    - Update `Game.winner` to return `Optional[TeamInfo]`.
    - Update `Game.label` to return "TBD" or "Scheduled" if the game is not `FINAL`.
4. **UI Update**: Update `display.py` to show different indicators (e.g., a clock icon or "Upcoming" text) for games that are not yet completed.

## Expected Outcome
The tool will provide accurate information for games occurring today or in the future, eliminating the "False Loss" bug for upcoming matchups.

## Implementation

- `GameState(str, Enum)` with `SCHEDULED`, `LIVE`, `FINAL` — `str` base class for JSON compatibility
- `Game.state` is a **required** field (no default) to force callers to be explicit about game state
- `MlbClient._STATUS_CODE_MAP` maps MLB API `status.statusCode` values (`F`, `I`, `P`, `W`, `S`) → `GameState`
- `Game.winner` returns `Optional[TeamInfo]` — `None` for non-FINAL games
- `Game.label` returns `state.value` (`"SCHEDULED"`, `"LIVE"`, `"FINAL"`)
- `Game.score_string` returns actual score for LIVE/FINAL, `"vs"` for SCHEDULED
- `Game.matchup_string` drops ✅/❌ indicators for non-FINAL games
- `format_game` renders: green WIN / red LOSS for FINAL, yellow LIVE, dim SCHEDULED
- `GameState` exported in `__all__`
- 5 new tests covering all three game states; all existing tests updated with explicit `state`

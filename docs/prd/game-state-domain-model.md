# PRD: Game State Domain Model

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

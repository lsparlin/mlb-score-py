# PRD: MLB Client Abstraction

## Goal
Encapsulate the raw API interaction and data parsing into a unified client, removing "leaky abstractions" from the query and CLI layers.

## Current State
The project uses a functional approach where `api.py` returns raw dictionaries (`dict[str, Any]`) and `queries.py` is responsible for parsing those dictionaries into models. This means the query layer is tightly coupled to the structure of the MLB API JSON response.

## Proposed Changes
1. **Create `MlbClient` Class**: Implement a client class that manages the API connection and configuration (like User-Agent).
2. **Move Parsing Logic**: Shift the `parse_game` and `_parse_team` logic from `queries.py` into the `MlbClient`.
3. **Typed Returns**: The client's methods should return fully instantiated `Game`, `TeamScore`, and `Schedule` models rather than raw JSON.
4. **Simplified Query Layer**: `queries.py` should only handle filtering (e.g., "find games for team X") and aggregation, operating entirely on typed models.

## Expected Outcome
Improved maintainability. If the MLB API changes its JSON structure, only the `MlbClient` needs to be updated. The rest of the application remains agnostic to the transport and raw format.

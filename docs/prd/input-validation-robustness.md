# PRD: Input Validation & Robustness

## Goal
Prevent the application from crashing with tracebacks when presented with invalid user input or unexpected API responses.

## Current State
Several parts of the application assume a "happy path":
- `date.fromisoformat()` in `cli.py` crashes on malformed date strings.
- `json.loads()` in `api.py` crashes if the API returns non-JSON (e.g., 502 Bad Gateway).
- `raw_data.get("dates", [])[0]` in `queries.py` will throw an `IndexError` if the API returns an empty dates list.

## Proposed Changes
1. **Safe Date Parsing**: Wrap `date.fromisoformat` in a try/except block and provide a clear error message to the user.
2. **Defensive JSON Loading**: Wrap the API response reading in a try/except block to handle `json.JSONDecodeError`.
3. **Null-Safe API Traversal**: Replace index-based access (e.g., `[0]`) with safe checks or helper methods that handle empty responses gracefully.
4. **Consistent Error Branding**: Ensure all errors are routed through `ApiError` or a new `UserError` exception to maintain a consistent CLI output format.

## Expected Outcome
The tool will no longer crash with Python tracebacks. Instead, it will provide helpful, human-readable error messages, improving the perceived quality and reliability of the tool.

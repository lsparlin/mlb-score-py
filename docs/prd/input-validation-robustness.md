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

## Status: ✅ Implemented

## Implementation
- **`cli.py`**: `resolve_target_date()` wraps `date.fromisoformat` in try/except, raises `UserError` on `ValueError` with a formatted message.
- **`cli.py`**: `main()` validates `args.days < 1` and raises `UserError` for non-positive integers.
- **`cli.py`**: Both error paths are caught in `main()` and printed as `"Error: {message}"` to stderr with exit code 1.
- **`client.py`**: `UserError` class added for user-facing input errors, distinct from `ApiError` for external failures.
- **`client.py`**: `_fetch_raw()` catches `json.JSONDecodeError` and wraps it in `ApiError` with context.
- **`client.py`**: `_parse_games()` uses null-safe guard (`isinstance(first, dict)`) on `dates[0]` to prevent IndexError on malformed API responses.
- **`__init__.py`**: `UserError` exported in `__all__` for public API access.
- **Tests**: Added 3 CLI validation tests (`test_main_rejects_zero_days`, `test_main_rejects_negative_days`, `test_main_handles_bad_date_format`) and 2 API robustness tests (`test_fetch_schedule_raises_api_error_on_invalid_json`, `test_fetch_schedule_handles_null_dates_entry`).
- **Test cleanup**: Removed `test_main_handles_user_error_from_client` (tested a theoretical path with no production caller).

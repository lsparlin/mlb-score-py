# PRD: Parallelize API Requests

## Status: ❌ Superseded — do not implement

> **Superseded by the batched date-range fetch** (PR #1, commit `cc56ff1`).
> The problem this PRD targeted no longer exists: `MlbClient.fetch_date_range`
> covers the entire requested range with a **single** API request
> (`startDate`/`endDate`), so there are no N sequential per-date calls left to
> parallelize. Archived as a historical record of the design path that was
> never needed.

## Goal
Reduce the latency of requests spanning multiple days by performing API calls in parallel.

## Current State
The `fetch_date_range` function in `mlb_score/api.py` iterates through the requested number of days and performs a synchronous, sequential HTTP request for each date. This results in $O(N)$ time complexity where $N$ is the number of days requested.

## Proposed Changes
1. **Introduce Concurrency**: Use `concurrent.futures.ThreadPoolExecutor` to fetch multiple dates simultaneously.
2. **Preserve Order**: Ensure that the results are aggregated and returned in the correct chronological order despite the asynchronous nature of the requests.
3. **Maintain Stdlib Constraints**: Continue using only Python standard library modules (`concurrent.futures`, `urllib`).

## Implementation Detail
- Update `fetch_date_range` to map `fetch_schedule` across the generated date range using a `ThreadPoolExecutor`.
- Use `executor.map` or `as_completed` to gather results.

## Expected Outcome
Significant reduction in execution time for `-n` values greater than 3. The user experience will transition from "waiting for several requests" to "nearly instant" results for typical lookback periods (e.g., 7-30 days).

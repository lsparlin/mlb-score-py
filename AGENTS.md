# mlb-score

## Purpose

CLI tool to look up MLB game outcomes for a given team, using MLB's public stats API.

## Quick reference

```bash
uv run mlb-score <team> [-d YYYY-MM-DD] [--today] [-n <days>]
```

- `<team>` — team name (e.g. `Cardinals`, `Dodgers`, `Yankees`)
- `-d` — specific date (defaults to yesterday)
- `--today` — use today's date (mutually exclusive with `-d`)
- `-n` — number of days to look back (default: 1)

## Module structure

```
mlb_score/
├── __init__.py      # public API surface (MlbClient, Game, GameState, TeamInfo, etc.)
├── client.py        # MLB Stats API client (MlbClient class, fetch_schedule, fetch_date_range)
├── models.py        # Game, TeamInfo, TeamScore, GameState dataclasses/enums; Schedule.for_team filtering
├── parser.py        # JSON-to-model parsing (raw API JSON → typed models)
├── display.py       # ANSI color formatting and printing
├── cli.py           # argument parsing + entry point (returns exit code)
└── __main__.py      # enables `python -m mlb_score`
```

## Key details

- Uses `https://statsapi.mlb.com/api/v1/schedule` — no API key needed
- Python 3.9+, stdlib only (no runtime dependencies)
- API exposed via `MlbClient` class (`fetch_schedule`, `fetch_date_range`)
- ANSI color output: cyan headers, green WIN/red LOSS, dimmed metadata
- CLI entry point installed as `mlb-score` via `[project.scripts]`

## Development

```bash
uv sync              # install deps (pytest, ruff) in .venv
uv run pytest -v     # run tests with real API fixtures
uv run ruff check .  # linting
uv run ruff format . # formatting
```

### Tooling

| Tool | Purpose |
|------|---------|
| hatchling | Build backend (auto-discovers packages) |
| pytest | Testing (fixtures from real MLB API responses in `tests/fixtures/`) |
| ruff | Linting + formatting (E, F, I, N, W rules) |
| uv | Dependency management (`uv.lock` lockfile) |

## Code style

- **Docstrings state expected behavior, not rationale.** One or two lines on
  what the function does. The *why* (design decisions, bug history) belongs
  in the commit message, a PRD, or — when the behavior must keep holding — a
  regression test, not in the docstring.

## Documentation workflow

PRDs are **change proposals**, not living specs — a completed PRD is stale by
definition on a maintained project, so it gets archived rather than kept
current.

- `docs/product.md` — the product's target state (what it does / should do,
  at the behavior level). Update when the product's *intent* changes, not on
  every feature.
- `docs/prd/` — active PRDs: one per in-flight change, kept short and focused
  on the delta.
- `docs/prd/archive/` — when a PRD **lands or is superseded**, move it here
  in the same PR that completes it, with a final status header: `✅ Implemented`
  or `❌ Superseded` (plus a line on what replaced it).
- Archived PRDs are **immutable** — a snapshot of the proposal as made. Never
  re-edit them to track later code changes.
- If a PRD involves a non-obvious *why* (an architectural trade-off), record
  the decision as a numbered ADR under `docs/decisions/` (create the folder
  with the first one); routine changes don't warrant one.

Rationale: PRDs describe a *delta*; the product doc describes *state*. The
moment a delta lands, its description goes stale — the state (code +
product doc) stays the source of truth.

## When asked about MLB scores

Run `uv run mlb-score <team>` — no need to read the source code.

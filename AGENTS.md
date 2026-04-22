# mlb-score

## Purpose

CLI tool to look up MLB game outcomes for a given team, using MLB's public stats API.

## Quick reference

```bash
mlb-score <team> [-d YYYY-MM-DD] [-n <days>]
```

- `<team>` — team name (e.g. `Cardinals`, `Dodgers`, `Yankees`)
- `-d` — specific date (defaults to yesterday, shows "Yesterday" label)
- `-n` — number of days to look back (default: 1, shows "Last N days")

## Module structure

```
mlb_score/
├── __init__.py      # public API surface (fetch_schedule, Game, TeamInfo, etc.)
├── api.py           # MLB Stats API client (function-based, no class wrapper)
├── models.py        # Game, TeamInfo, TeamScore, Schedule dataclasses
├── queries.py       # filtering and parsing logic
├── display.py       # ANSI color formatting and printing
└── cli.py           # argument parsing + entry point (returns exit code)
```

## Key details

- Uses `https://statsapi.mlb.com/api/v1/schedule` — no API key needed
- Python 3.9+, stdlib only (no runtime dependencies)
- Function-based API (`fetch_schedule`, `fetch_date_range`) — no class wrapper
- ANSI color output: cyan headers, green WIN/red LOSS, dimmed metadata
- CLI entry point installed as `mlb-score` via `[project.scripts]`

## Development

```bash
uv sync              # install deps (pytest, ruff) in .venv
uv run pytest -v     # 38 tests with real API fixtures
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

## When asked about MLB scores

Run `mlb-score <team>` directly — no need to read the source code.

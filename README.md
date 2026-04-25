# mlb-score

CLI tool and Python library to look up MLB game outcomes for a given team.

## Installing the CLI locally

```bash
uv tool install --editable .
```

After this, `mlb-score` is available on your PATH from anywhere — no `uv run` needed.

## Usage

```bash
uv run mlb-score Cardinals                    # yesterday's game
uv run mlb-score Cardinals --today            # today's games
uv run mlb-score Yankees -d 2026-04-15       # specific date
uv run mlb-score Dodgers -n 3                 # last 3 days
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `team` | Team name (positional) | required |
| `-d, --date` | Specific date (YYYY-MM-DD) | yesterday |
| `--today` | Use today's date (mutually exclusive with `-d`) | — |
| `-n, --days` | Number of days to look back | 1 |

### Output

Colored terminal output with:
- Date header in bold cyan
- Team name with context label ("Yesterday", "Today", "Last N days")
- Scores in bright white, venue/time dimmed
- WIN in green, LOSS in red

## As a Library

```python
from datetime import date, timedelta
from mlb_score import MlbClient, find_team_games
from mlb_score.queries import build_schedule
from mlb_score.display import print_results

client = MlbClient()
fetched = client.fetch_date_range(date.today() - timedelta(days=1), days=3)
schedule = build_schedule(fetched, "Cardinals")
print_results(schedule, date.today() - timedelta(days=1), "Cardinals")
```

### Modules

| Module | Responsibility |
|--------|---------------|
| `mlb_score.client` | MLB Stats API client (`MlbClient`, `fetch_schedule`, `fetch_date_range`) |
| `mlb_score.models` | Data models (`Game`, `GameState`, `TeamInfo`, `TeamScore`) |
| `mlb_score.queries` | Filtering and parsing (`find_team_games`, `build_schedule`) |
| `mlb_score.display` | Formatting output with ANSI colors (`format_game`, `print_results`) |
| `mlb_score.cli` | CLI argument parsing and entry point |

## Development

```bash
# Set up environment (requires uv)
uv sync

# Run tests
uv run pytest -v

# Lint and format
uv run ruff check .
uv run ruff format .
```

### Tooling

| Tool | Purpose |
|------|---------|
| [hatchling](https://github.com/pypa/hatch) | Build backend |
| [pytest](https://pytest.org/) | Testing (fixtures from real MLB API responses) |
| [ruff](https://docs.astral.sh/ruff/) | Linting and formatting |
| [uv](https://docs.astral.sh/uv/) | Dependency management |

## Team name hints

Use the team nickname as it appears in MLB's API: `Cardinals`, `Dodgers`, `Yankees`, `Marlins`, etc.

## Requirements

- Python 3.9+ (stdlib only, no runtime dependencies)
- [uv](https://docs.astral.sh/uv/) for development

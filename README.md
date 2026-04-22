# mlb-score

CLI tool and Python library to look up MLB game outcomes for a given team.

## Usage

```bash
python3 mlb_score.py Cardinals          # yesterday's game
python3 mlb_score.py Yankees -d 2026-04-15  # specific date
python3 mlb_score.py Dodgers -n 3        # last 3 days
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `team` | Team name (positional) | required |
| `-d, --date` | Specific date (YYYY-MM-DD) | yesterday |
| `-n, --days` | Number of days to look back | 1 |

## As a Library

```python
from mlb_score.api import fetch_date_range
from mlb_score.queries import build_schedule
from mlb_score.display import print_results

# Fetch last 3 days for the Cardinals
fetched = fetch_date_range(date.today() - timedelta(days=1), days=3)
schedule = build_schedule(fetched, "Cardinals")
print_results(schedule, date.today() - timedelta(days=1), "Cardinals")
```

### Modules

| Module | Responsibility |
|--------|---------------|
| `mlb_score.api` | MLB Stats API client (`fetch_schedule`, `MLBApiClient`) |
| `mlb_score.models` | Data models (`Game`, `TeamInfo`, `TeamScore`, `Schedule`) |
| `mlb_score.queries` | Filtering and parsing (`find_team_games`, `build_schedule`) |
| `mlb_score.display` | Formatting output (`format_game`, `print_results`) |
| `mlb_score.cli` | CLI argument parsing and entry point |

## Team name hints

Use the team nickname as it appears in MLB's API: `Cardinals`, `Dodgers`, `Yankees`, `Marlins`, etc.

## Requirements

- Python 3.7+ (stdlib only, no dependencies)

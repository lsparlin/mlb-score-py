# mlb-score

## Purpose

CLI tool to look up MLB game outcomes for a given team, using MLB's public stats API.

## Quick reference

```bash
python3 mlb_score.py <team> [-d YYYY-MM-DD] [-n <days>]
```

- `<team>` — team name (e.g. `Cardinals`, `Dodgers`, `Yankees`)
- `-d` — specific date (defaults to yesterday)
- `-n` — number of days to look back (default: 1)

## Module structure

```
mlb_score/
├── __init__.py      # public API surface
├── api.py           # MLB Stats API client
├── models.py        # Game, TeamInfo, TeamScore, Schedule dataclasses
├── queries.py       # filtering and parsing logic
├── display.py       # formatting and printing
└── cli.py           # argument parsing + entry point
```

## Key details

- Uses `https://statsapi.mlb.com/api/v1/schedule` — no API key needed
- Python 3.7+, stdlib only (no pip install required)
- Outputs formatted score with winner/loser indicator, venue, and day/night

## When asked about MLB scores

Run `python3 mlb_score.py <team>` directly — no need to read the source code.

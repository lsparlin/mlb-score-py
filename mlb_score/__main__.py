"""MLB Score — CLI tool to look up MLB game outcomes for a given team.

Enables `python -m mlb_score` as an alternative to the `mlb-score` entry point.

Usage:
    python3 -m mlb_score Cardinals          # yesterday's game
    python3 -m mlb_score Yankees -d 2026-04-15  # specific date
    python3 -m mlb_score Dodgers -n 3        # last 3 days
"""

import sys

from mlb_score.cli import main

if __name__ == "__main__":
    sys.exit(main())

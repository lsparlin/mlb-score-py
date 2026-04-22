#!/usr/bin/env python3
"""MLB Score — CLI tool to look up MLB game outcomes for a given team.

Usage:
    python3 mlb_score.py Cardinals          # yesterday's game
    python3 mlb_score.py Yankees -d 2026-04-15  # specific date
    python3 mlb_score.py Dodgers -n 3        # last 3 days
"""

import sys

from mlb_score.cli import main

if __name__ == "__main__":
    sys.exit(main())

"""CLI entry point for mlb-score."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from mlb_score.api import ApiError, fetch_date_range
from mlb_score.queries import build_schedule
from mlb_score.display import print_results, print_no_results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Look up MLB game outcomes for a team."
    )
    parser.add_argument(
        "team",
        help="Team name (e.g. 'Cardinals', 'Dodgers', 'Yankees')",
    )
    parser.add_argument(
        "-d",
        "--date",
        help="Date to look up (YYYY-MM-DD), defaults to yesterday",
        default=None,
    )
    parser.add_argument(
        "-n",
        "--days",
        type=int,
        default=1,
        help="Number of days to look back (default: 1)",
    )
    return parser.parse_args(argv)


def resolve_target_date(args: argparse.Namespace) -> date:
    """Determine the target date from arguments."""
    if args.date:
        return date.fromisoformat(args.date)
    return date.today() - timedelta(days=1)


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Returns exit code."""
    args = parse_args(argv)
    target_date = resolve_target_date(args)

    try:
        fetched_data = fetch_date_range(target_date, args.days)
    except ApiError as e:
        print(f"{e}", file=sys.stderr)
        return 1

    schedule = build_schedule(fetched_data, args.team)

    if schedule.is_empty:
        print_no_results(args.team, target_date)
        return 1

    print_results(schedule, target_date, args.team)
    return 0


if __name__ == "__main__":
    sys.exit(main())

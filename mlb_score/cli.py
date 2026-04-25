"""CLI entry point for mlb-score."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from mlb_score.client import ApiError, MlbClient, UserError
from mlb_score.display import print_no_results, print_results
from mlb_score.queries import build_schedule


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Look up MLB game outcomes for a team.")
    parser.add_argument(
        "team",
        help="Team name (e.g. 'Cardinals', 'Dodgers', 'Yankees')",
    )
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "-d",
        "--date",
        help="Date to look up (YYYY-MM-DD), defaults to yesterday",
        default=None,
    )
    date_group.add_argument(
        "--today",
        action="store_true",
        default=False,
        help="Look up today's games instead of yesterday's",
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
        try:
            return date.fromisoformat(args.date)
        except ValueError:
            raise UserError(
                f"Invalid date format '{args.date}'. Use YYYY-MM-DD."
            )
    if args.today:
        return date.today()
    return date.today() - timedelta(days=1)


def main(argv: list[str] | None = None) -> int:
    """Main entry point. Returns exit code."""
    args = parse_args(argv)

    # Build a human-readable label for the date range
    if args.today and args.days == 1:
        label = "Today"
    elif args.today:
        label = f"Today and prior {args.days - 1} days"
    elif args.date is None and args.days == 1:
        label = "Yesterday"
    elif args.date is None:
        label = f"Last {args.days} days"
    else:
        label = ""

    try:
        target_date = resolve_target_date(args)
    except UserError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.days < 1:
            raise UserError("Days must be a positive integer.")
        client = MlbClient()
        games_by_date = client.fetch_date_range(target_date, args.days)
    except ApiError as e:
        print(f"{e}", file=sys.stderr)
        return 1
    except UserError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    schedule = build_schedule(games_by_date, args.team)

    if schedule.is_empty:
        print_no_results(args.team, target_date)
        return 1

    print_results(schedule, target_date, args.team, label=label)
    return 0


if __name__ == "__main__":
    sys.exit(main())

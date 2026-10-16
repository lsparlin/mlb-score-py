# Product Description: mlb-score

A higher-level statement of what mlb-score is and what it is *for*. This is
the target state of the product — the thing individual PRDs and commits move
toward. It is deliberately less specific than a PRD: it describes behavior
and intent, not implementation. For how to build on the code, see `AGENTS.md`;
for the history of specific changes, see `docs/prd/archive/`.

## What it is

A command-line tool that answers one question: **"How did my team do?"**

Given a team and a date (or a span of days), it reports that team's MLB games
and outcomes — who they played, the score, and the result from that team's
perspective — as a clean, colorized listing.

## The problem

Checking how a favorite team did requires opening a web app, navigating to a
team or scoreboard, and scanning for the game. There is no lightweight,
scriptable, terminal-native answer. `mlb-score` is that answer: one command,
one screen of results, no account and no API key.

## What it should do

- **One command, instant answer.** `mlb-score <team>` resolves the team and
  prints its game for yesterday by default.
- **Flexible time.** `-d` for a specific date, `--today` for today, `-n` for a
  lookback window — without the caller having to loop.
- **Fuzzy team matching.** Partial and case-insensitive names should find the
  team; the user shouldn't need the official full name.
- **Correct outcomes.** Results reflect the searched team's perspective
  (WIN/LOSS), and a game that is scheduled or live is labeled as such — never
  a fake loss.
- **Readable output.** A human-friendly, colorized listing that also degrades
  gracefully to plain text when piped or when `NO_COLOR` is set.
- **Honest failures.** Bad input or an API problem yields a short, clear error
  and a non-zero exit — never a stack trace.

## What it is *not*

- Not a general sports/MLB client. It is a narrow, opinionated answer to one
  question, not a swiss-army stats API wrapper.
- Not a data store or dashboard. Each run is a fresh, stateless query.
- Not a dependency-free-for-its-own-sake project. "Stdlib only" is a
  *maintainability* choice (no runtime deps to rot), not a constraint to
  optimize at the expense of clarity.

## Design principles

These hold across features and should be weighed in any PRD:

1. **One question, done well.** Optimize for the single "how did they do"
   lookup. Resist broadening scope without a clear product reason.
2. **Resilient to partial data.** The MLB API returns incomplete records for
   scheduled and live games; the product degrades to "what we know" rather
   than failing or misleading.
3. **Layered and replaceable.** Transport, parsing, models, and display are
   independent; each should be changeable without touching the others.
4. **Predictable I/O.** Consistent output shape and exit codes, so the tool is
   safe to script against.

## Open questions

Capture product-level decisions that are genuinely unsettled here (each is a
candidate for a PRD once we act on it):

- Should `-n` combined with `--today` look *forward* as well as back for a
  team's upcoming games?
- Do we want multi-team input in a single invocation?
- Is a `--json` output mode worth adding for scripting?

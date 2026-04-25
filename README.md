# mlb-score

CLI tool to look up MLB game outcomes for a given team.

## Installing the CLI locally

Requires [uv](https://docs.astral.sh/uv/). Clone the repo, then:

```bash
uv tool install --editable .
```

After this, `mlb-score` is available on your PATH from anywhere — no `uv run` needed.

## Usage

```bash
mlb-score Cardinals                    # yesterday's game
mlb-score Cardinals --today            # today's games
mlb-score Yankees -d 2026-04-15        # specific date
mlb-score Dodgers -n 3                 # last 3 days
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `team` | Team name (positional) | required |
| `-d, --date` | Specific date (YYYY-MM-DD) | yesterday |
| `--today` | Use today's date (mutually exclusive with `-d`) | — |
| `-n, --days` | Number of days to look back | 1 |

### Output

```
📅  Friday, April 24, 2026
⚾  Cardinals · Yesterday
────────────────────────────────────────────────

  Seattle Mariners @ St. Louis Cardinals
     3–11  · Busch Stadium  ·  Night  · WIN
```

## Development

### Requirements

- Python 3.9+ (stdlib only, no runtime dependencies)
- [uv](https://docs.astral.sh/uv/) for development

### Setup

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

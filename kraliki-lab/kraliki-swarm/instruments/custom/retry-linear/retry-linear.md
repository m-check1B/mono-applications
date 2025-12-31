# retry-linear

Retry creating Linear issues that failed due to rate limiting.

## Usage

Run to attempt creating any pending issues stored in `data/pending_linear_issues.json`.

Options (passed as args):
- `--dry-run`: Preview what would be created without actually creating
- `--clear`: Clear the pending file after successful creation

## What it does

1. Reads pending issues from `data/pending_linear_issues.json`
2. Attempts to create each issue via Linear API
3. If rate limited again, saves remaining issues for next retry
4. If successful, clears the pending file

## When to use

- After waiting for Linear rate limit to reset (usually 1 hour)
- Manually when you see pending issues on the dashboard
- Can be scheduled via cron for automatic retry

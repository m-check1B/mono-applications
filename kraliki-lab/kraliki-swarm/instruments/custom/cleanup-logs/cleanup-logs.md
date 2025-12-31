# cleanup-logs

Clean up old agent logs to save disk space.

## Usage

Run to archive or remove agent logs older than N days (default: 3 days).

Options (passed as args):
- `--days N`: Keep logs newer than N days (default: 3)
- `--dry-run`: Preview what would be deleted without removing
- `--archive`: Move to archive instead of delete
- `--no-confirm`: Skip confirmation prompt

## Examples

```bash
# Preview what would be cleaned (dry run)
python3 /github/applications/kraliki-lab/kraliki-swarm/instruments/loader.py run cleanup-logs --dry-run

# Clean logs older than 7 days
python3 /github/applications/kraliki-lab/kraliki-swarm/instruments/loader.py run cleanup-logs --days 7

# Archive instead of delete
python3 /github/applications/kraliki-lab/kraliki-swarm/instruments/loader.py run cleanup-logs --archive
```

## Output

JSON with cleanup results: files processed, size freed, archived vs deleted.

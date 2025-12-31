#!/usr/bin/env python3
"""Clean up old agent logs to save disk space.

Kraliki Self-Improvement: Agent log cleanup instrument.
Addresses the ~500MB log accumulation issue.
"""

import argparse
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

LOGS_DIR = Path("/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/logs/agents")
ARCHIVE_DIR = Path("/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/logs/agents/_archive")


def get_file_age_days(filepath: Path) -> float:
    """Get file age in days."""
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    return (datetime.now() - mtime).total_seconds() / 86400


def get_file_size_kb(filepath: Path) -> float:
    """Get file size in KB."""
    return filepath.stat().st_size / 1024


def cleanup_logs(
    days: int = 3,
    dry_run: bool = False,
    archive: bool = False,
    no_confirm: bool = False
) -> dict:
    """Clean up agent logs older than specified days.

    Args:
        days: Keep logs newer than this many days
        dry_run: Preview only, don't actually remove
        archive: Move to archive instead of delete
        no_confirm: Skip confirmation prompt

    Returns:
        Dict with cleanup results
    """
    results = {
        "dry_run": dry_run,
        "days_threshold": days,
        "action": "archive" if archive else "delete",
        "files_found": 0,
        "files_processed": 0,
        "files_skipped": 0,
        "size_freed_kb": 0,
        "errors": []
    }

    if not LOGS_DIR.exists():
        results["errors"].append(f"Logs directory not found: {LOGS_DIR}")
        return results

    # Find old log files
    old_files = []
    for log_file in LOGS_DIR.glob("*.log"):
        age = get_file_age_days(log_file)
        if age > days:
            old_files.append({
                "path": log_file,
                "age_days": round(age, 1),
                "size_kb": round(get_file_size_kb(log_file), 1)
            })

    results["files_found"] = len(old_files)
    total_size = sum(f["size_kb"] for f in old_files)
    results["size_freed_kb"] = round(total_size, 1)

    if not old_files:
        print(f"No log files older than {days} days found.")
        return results

    # Show summary
    print(f"\n=== Agent Log Cleanup ===")
    print(f"Logs directory: {LOGS_DIR}")
    print(f"Files older than {days} days: {len(old_files)}")
    print(f"Total size: {total_size / 1024:.1f} MB")
    print(f"Action: {'ARCHIVE' if archive else 'DELETE'} {'(DRY RUN)' if dry_run else ''}")

    # Show oldest files
    old_files.sort(key=lambda x: -x["age_days"])
    print(f"\nOldest files:")
    for f in old_files[:5]:
        print(f"  {f['path'].name}: {f['age_days']}d old, {f['size_kb']:.1f} KB")
    if len(old_files) > 5:
        print(f"  ... and {len(old_files) - 5} more files")

    if dry_run:
        print(f"\n[DRY RUN] Would {'archive' if archive else 'delete'} {len(old_files)} files ({total_size / 1024:.1f} MB)")
        return results

    # Confirm if not --no-confirm
    if not no_confirm:
        print(f"\nThis will {'archive' if archive else 'DELETE'} {len(old_files)} log files.")
        response = input("Proceed? [y/N] ")
        if response.lower() != 'y':
            print("Aborted.")
            return results

    # Perform cleanup
    if archive:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for f in old_files:
        try:
            if archive:
                dest = ARCHIVE_DIR / f["path"].name
                shutil.move(str(f["path"]), str(dest))
            else:
                f["path"].unlink()
            results["files_processed"] += 1
        except Exception as e:
            results["files_skipped"] += 1
            results["errors"].append(f"{f['path'].name}: {str(e)}")

    print(f"\n=== Cleanup Complete ===")
    print(f"{'Archived' if archive else 'Deleted'}: {results['files_processed']} files")
    print(f"Space freed: {results['size_freed_kb'] / 1024:.1f} MB")
    if results["errors"]:
        print(f"Errors: {len(results['errors'])}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Clean up old agent logs")
    parser.add_argument("--days", type=int, default=3,
                        help="Keep logs newer than N days (default: 3)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be deleted")
    parser.add_argument("--archive", action="store_true",
                        help="Move to archive instead of delete")
    parser.add_argument("--no-confirm", action="store_true",
                        help="Skip confirmation prompt")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    results = cleanup_logs(
        days=args.days,
        dry_run=args.dry_run,
        archive=args.archive,
        no_confirm=args.no_confirm
    )

    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

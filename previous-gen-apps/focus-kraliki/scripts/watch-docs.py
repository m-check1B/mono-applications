#!/usr/bin/env python3
"""
Watch Focus by Kraliki docs directory and automatically index changes to mgrep.

This script monitors the docs/ directory for file changes and
automatically updates the mgrep index when files are modified.
"""

import sys
import time
import json
import signal
import io
from pathlib import Path
from datetime import datetime
from urllib import request, error

# Configuration
MGREP_URL = "http://localhost:8001"
STORE_ID = "focus_kraliki_docs"
DOCS_DIR = Path(__file__).parent.parent / "docs"
POLL_INTERVAL = 5  # Seconds between checks


def index_file(file_path: Path) -> bool:
    """Index a single file to mgrep using multipart upload."""
    try:
        content = file_path.read_text(encoding="utf-8")

        boundary = f"----WebKitFormBoundary{hash(file_path)}"
        body = io.BytesIO()

        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode(
                "utf-8"
            )
        )
        body.write(f"Content-Type: text/markdown\r\n\r\n".encode("utf-8"))
        body.write(content.encode("utf-8"))
        body.write("\r\n".encode("utf-8"))

        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            'Content-Disposition: form-data; name="external_id"\r\n\r\n'.encode("utf-8")
        )
        body.write(str(file_path).encode("utf-8"))
        body.write("\r\n".encode("utf-8"))

        metadata = json.dumps({"file_path": str(file_path)})
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            'Content-Disposition: form-data; name="metadata"\r\n\r\n'.encode("utf-8")
        )
        body.write(metadata.encode("utf-8"))
        body.write("\r\n".encode("utf-8"))

        body.write(f"--{boundary}--\r\n".encode("utf-8"))

        body.seek(0)

        req = request.Request(
            f"{MGREP_URL}/v1/stores/{STORE_ID}/files",
            data=body.read(),
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=30) as resp:
            print(f"  ✓ Indexed: {file_path.name}")
            return True
    except Exception as e:
        print(f"  ✗ Failed to index {file_path.name}: {e}")
        return False


def get_file_mtime(path: Path) -> float:
    """Get file modification time."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0


def scan_and_index():
    """Scan docs directory and index any changed files."""
    if not DOCS_DIR.exists():
        print(f"✗ Docs directory not found: {DOCS_DIR}")
        return

    # Get all markdown files
    files = list(DOCS_DIR.glob("**/*.md"))
    files.sort()

    # Check each file for changes
    changed_files = []
    for file_path in files:
        mtime = get_file_mtime(file_path)
        if mtime == 0:
            continue

        # Check if file has been modified since last check
        last_mtime = file_mtimes.get(str(file_path), 0)
        if mtime > last_mtime:
            changed_files.append(file_path)
            file_mtimes[str(file_path)] = mtime

    if changed_files:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Found {len(changed_files)} changed file(s):")

        # Index changed files
        for file_path in changed_files:
            index_file(file_path)
            time.sleep(0.1)  # Rate limiting


def check_mgrep_health():
    """Check if mgrep service is available."""
    try:
        with request.urlopen(f"{MGREP_URL}/v1/stores", timeout=5):
            return True
    except (error.URLError, TimeoutError, OSError):
        return False


def signal_handler(signum, frame):
    """Handle interrupt signals."""
    print("\nShutting down...")
    sys.exit(0)


# Track file modification times
file_mtimes = {}


def main():
    global file_mtimes

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Focus by Kraliki Documentation Watcher")
    print("=" * 50)
    print(f"Watching: {DOCS_DIR}")
    print(f"Store ID: {STORE_ID}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print("\nPress Ctrl+C to stop\n")

    # Check mgrep is running
    if not check_mgrep_health():
        print("✗ mgrep service is not running!")
        print(f"  Start it with: docker compose -f docker-compose.mgrep.yml up -d")
        sys.exit(1)

    print("✓ mgrep service is running\n")

    # Initial scan
    print("Performing initial scan...")
    scan_and_index()
    print("\nWatching for changes...\n")

    # Main loop
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            scan_and_index()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()

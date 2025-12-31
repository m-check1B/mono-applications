#!/usr/bin/env python3
"""
Index Focus by Kraliki documentation files to mgrep for semantic search.

This script scans the docs/ directory and indexes all markdown files
to the mgrep semantic search service.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict
from urllib import request
from urllib.error import HTTPError, URLError

# Configuration
MGREP_URL = "http://localhost:8001"
STORE_ID = "focus_kraliki_docs"
DOCS_DIR = Path(__file__).parent.parent / "docs"


def create_store(store_id: str, name: str, description: str) -> bool:
    """Create a mgrep store for indexing documents."""
    payload = {"name": name, "description": description}

    try:
        req = request.Request(
            f"{MGREP_URL}/v1/stores",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"✓ Created store '{store_id}'")
            return True
    except HTTPError as e:
        if e.code == 409:
            print(f"✓ Store '{store_id}' already exists")
            return True
        print(f"✗ Failed to create store: {e}")
        return False
    except URLError as e:
        print(f"✗ Failed to connect to mgrep: {e}")
        print(
            f"  Make sure mgrep is running: docker compose -f docker-compose.mgrep.yml up -d"
        )
        return False


def index_file(store_id: str, file_path: Path) -> bool:
    """Index a single file to mgrep using multipart upload."""
    try:
        import io
        import mimetypes

        content = file_path.read_text(encoding="utf-8")

        # Prepare multipart/form-data
        boundary = f"----WebKitFormBoundary{hash(file_path)}"
        body = io.BytesIO()

        # Add file part
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode(
                "utf-8"
            )
        )
        body.write(f"Content-Type: text/markdown\r\n\r\n".encode("utf-8"))
        body.write(content.encode("utf-8"))
        body.write("\r\n".encode("utf-8"))

        # Add external_id part (using file path as external ID)
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            'Content-Disposition: form-data; name="external_id"\r\n\r\n'.encode("utf-8")
        )
        body.write(str(file_path).encode("utf-8"))
        body.write("\r\n".encode("utf-8"))

        # Add metadata part
        metadata = json.dumps({"file_path": str(file_path)})
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            'Content-Disposition: form-data; name="metadata"\r\n\r\n'.encode("utf-8")
        )
        body.write(metadata.encode("utf-8"))
        body.write("\r\n".encode("utf-8"))

        # Close boundary
        body.write(f"--{boundary}--\r\n".encode("utf-8"))

        body.seek(0)

        req = request.Request(
            f"{MGREP_URL}/v1/stores/{store_id}/files",
            data=body.read(),
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"  ✓ Indexed: {file_path.name}")
            return True
    except HTTPError as e:
        print(f"  ✗ Failed to index {file_path.name}: HTTP {e.code}")
        return False
    except URLError as e:
        print(f"  ✗ Failed to index {file_path.name}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Failed to index {file_path.name}: {e}")
        return False


def get_markdown_files(docs_dir: Path) -> List[Path]:
    """Get all markdown files in the docs directory."""
    if not docs_dir.exists():
        print(f"✗ Docs directory not found: {docs_dir}")
        return []

    files = list(docs_dir.glob("**/*.md"))
    files.sort()
    return files


def main():
    print("Focus by Kraliki Documentation Indexer")
    print("=" * 50)

    # Check if docs directory exists
    if not DOCS_DIR.exists():
        print(f"✗ Docs directory not found: {DOCS_DIR}")
        sys.exit(1)

    # Create store (skip if already exists)
    print(f"\nChecking mgrep store: {STORE_ID}")
    if not create_store(
        STORE_ID,
        STORE_ID,
        "Semantic search for Focus by Kraliki project documentation",
    ):
        print("Continuing with existing store...")

    # Get files to index
    print(f"\nScanning documentation directory: {DOCS_DIR}")
    files = get_markdown_files(DOCS_DIR)

    if not files:
        print("✗ No markdown files found")
        sys.exit(1)

    print(f"Found {len(files)} documentation files")

    # Index files
    print(f"\nIndexing files...")
    success_count = 0
    failed_count = 0

    for file_path in files:
        if index_file(STORE_ID, file_path):
            success_count += 1
        else:
            failed_count += 1
        time.sleep(0.1)  # Rate limiting

    print(f"\nIndexing complete!")
    print(f"  Success: {success_count}")
    print(f"  Failed: {failed_count}")

    print(f"\nYou can now search using:")
    print(f"  curl -X POST {MGREP_URL}/v1/stores/search \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(
        f'    -d \'{{"query": "your query here", "store_identifiers": ["{STORE_ID}"]}}\''
    )


if __name__ == "__main__":
    main()

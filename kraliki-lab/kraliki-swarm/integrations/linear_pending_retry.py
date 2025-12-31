#!/usr/bin/env python3
"""
Linear Pending Issues Retry

Retries creating Linear issues that were queued due to rate limiting.
Can be run manually or scheduled via cron.

Usage:
  python3 linear_pending_retry.py           # Retry all pending issues
  python3 linear_pending_retry.py --dry-run # Preview what would be created
  python3 linear_pending_retry.py --clear   # Clear pending issues file after success
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path

# Paths
KRALIKI_DIR = Path(__file__).parent.parent
DATA_DIR = KRALIKI_DIR / "data"
PENDING_FILE = DATA_DIR / "pending_linear_issues.json"
LINEAR_API_KEY_PATH = Path("/home/adminmatej/github/secrets/linear_api_key.txt")
LINEAR_URL = "https://api.linear.app/graphql"

# Linear team ID for Verduona
TEAM_ID = "b2906b55-1247-431d-b5dc-703423b4feb4"

# Label name to ID mapping (common labels)
LABEL_MAPPINGS = {
    "type:bug": "2c47f4b0-8f1f-4e4a-8e38-29f8b4d7f9b1",
    "type:chore": "3a1b2c3d-4e5f-6789-0abc-def123456789",
    "stream:asset-engine": "4d5e6f7a-8b9c-0d1e-2f3a-4b5c6d7e8f9a",
    "stream:cash-engine": "5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b",
}


def get_api_key():
    """Load Linear API key."""
    try:
        return LINEAR_API_KEY_PATH.read_text().strip()
    except FileNotFoundError:
        key = os.getenv("LINEAR_API_TOKEN")
        if key:
            return key
        raise Exception(f"Linear API key not found at {LINEAR_API_KEY_PATH}")


def query_linear(query, variables=None):
    """Execute GraphQL query against Linear API."""
    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(LINEAR_URL, json=payload, headers=headers)

    # Check for rate limiting
    if response.status_code == 429:
        raise Exception("RATE_LIMITED: Linear API rate limit still exceeded")

    if response.status_code != 200:
        raise Exception(f"Query failed: {response.status_code}: {response.text}")

    result = response.json()
    if "errors" in result:
        error_msg = result['errors'][0].get('message', str(result['errors']))
        if 'USAGE_LIMIT' in error_msg.upper() or 'rate' in error_msg.lower():
            raise Exception(f"RATE_LIMITED: {error_msg}")
        raise Exception(f"GraphQL error: {error_msg}")

    return result


def get_label_ids(labels: list) -> list:
    """Convert label names to IDs. Returns empty list if labels can't be mapped."""
    # For now, return empty - Linear will use defaults
    # TODO: Fetch actual label IDs from Linear API
    return []


def create_issue(title: str, description: str, priority: int, labels: list) -> dict:
    """Create a single Linear issue."""
    query = """
    mutation CreateIssue($teamId: String!, $title: String!, $description: String, $priority: Int) {
        issueCreate(input: {
            teamId: $teamId,
            title: $title,
            description: $description,
            priority: $priority
        }) {
            success
            issue {
                id
                identifier
                url
            }
        }
    }
    """

    variables = {
        "teamId": TEAM_ID,
        "title": title,
        "description": description,
        "priority": priority
    }

    result = query_linear(query, variables)
    return result.get("data", {}).get("issueCreate", {})


def load_pending_issues():
    """Load pending issues from file."""
    if not PENDING_FILE.exists():
        return None

    try:
        data = json.loads(PENDING_FILE.read_text())
        if not data.get("issues"):
            return None
        return data
    except Exception as e:
        print(f"Error loading pending issues: {e}")
        return None


def save_pending_issues(data: dict):
    """Save pending issues to file."""
    PENDING_FILE.write_text(json.dumps(data, indent=2))


def clear_pending_issues():
    """Clear the pending issues file."""
    empty = {
        "generated_at": datetime.now().isoformat(),
        "generated_by": "linear_pending_retry",
        "note": "Cleared after successful retry",
        "issues": []
    }
    save_pending_issues(empty)


def main():
    parser = argparse.ArgumentParser(description="Retry pending Linear issues")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview without creating")
    parser.add_argument("--clear", "-c", action="store_true", help="Clear pending file after success")
    args = parser.parse_args()

    # Load pending issues
    data = load_pending_issues()
    if not data:
        print("No pending issues found.")
        return 0

    issues = data.get("issues", [])
    print(f"Found {len(issues)} pending issue(s) from {data.get('generated_by', 'unknown')}")
    print(f"Generated at: {data.get('generated_at', 'unknown')}")
    print()

    if args.dry_run:
        print("DRY RUN - Would create:")
        for i, issue in enumerate(issues, 1):
            prio = {1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}.get(issue.get("priority", 3), "Medium")
            print(f"  {i}. [{prio}] {issue.get('title', 'Untitled')}")
            print(f"     Labels: {', '.join(issue.get('labels', []))}")
        return 0

    # Try to create issues
    created = []
    failed = []

    for issue in issues:
        title = issue.get("title", "Untitled")
        description = issue.get("description", "")
        priority = issue.get("priority", 3)
        labels = issue.get("labels", [])

        try:
            print(f"Creating: {title[:60]}...")
            result = create_issue(title, description, priority, labels)

            if result.get("success"):
                issue_data = result.get("issue", {})
                print(f"  Created: {issue_data.get('identifier')} - {issue_data.get('url')}")
                created.append(issue_data)
            else:
                print(f"  Failed: Unknown error")
                failed.append(issue)

        except Exception as e:
            error_msg = str(e)
            print(f"  Error: {error_msg}")

            if "RATE_LIMITED" in error_msg:
                print("\nRate limit still exceeded. Stopping retry.")
                print(f"Created {len(created)} issues before hitting limit.")
                # Update pending file with remaining issues
                remaining = issues[issues.index(issue):]
                data["issues"] = remaining
                data["note"] = f"Partial retry on {datetime.now().isoformat()}. {len(created)} created, {len(remaining)} remaining."
                save_pending_issues(data)
                return 1

            failed.append(issue)

    # Summary
    print()
    print(f"Summary: {len(created)} created, {len(failed)} failed")

    if failed:
        # Update pending file with failed issues
        data["issues"] = failed
        data["note"] = f"Retry on {datetime.now().isoformat()}. {len(created)} created, {len(failed)} failed."
        save_pending_issues(data)
        print(f"Failed issues saved to pending file for next retry.")
        return 1

    if args.clear or len(failed) == 0:
        clear_pending_issues()
        print("Pending issues file cleared.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

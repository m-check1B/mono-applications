#!/usr/bin/env python3
"""
Linear → features.json Sync
============================
Fetches issues with stream labels from Linear and adds them to features.json.

Usage:
    python linear-to-features.py              # Sync stream-labeled issues
    python linear-to-features.py --dry-run    # Preview without writing
    python linear-to-features.py --label DEV  # Use different label prefix
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request
from urllib.error import HTTPError, URLError

# Paths
SCRIPT_DIR = Path(__file__).parent
AI_AUTOMATION_DIR = SCRIPT_DIR.parent
PLANNING_DIR = AI_AUTOMATION_DIR / "software-dev" / "planning"
FEATURES_FILE = PLANNING_DIR / "features.json"
ROOT = AI_AUTOMATION_DIR.parent

GRAPHQL_URL = "https://api.linear.app/graphql"
ISSUES_QUERY = """
query Issues($after: String, $filter: IssueFilter) {
  issues(first: 250, after: $after, filter: $filter) {
    nodes {
      id
      identifier
      title
      url
      priority
      estimate
      description
      createdAt
      updatedAt
      dueDate
      state { name type }
      team { id key name }
      labels { nodes { name } }
      assignee { name }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

def load_api_key() -> Optional[str]:
    """Load Linear API key from environment or secrets file"""
    key = os.getenv("LINEAR_API_KEY") or os.getenv("LINEAR_TOKEN")
    if key:
        return key

    token_file = ROOT / "secrets" / "linear_api_key.txt"
    if token_file.exists():
        return token_file.read_text().strip()

    return None


def graphql_request(token: str, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make a GraphQL request to Linear API"""
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": token},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8") if exc.fp else ""
        raise RuntimeError(f"Linear API HTTP error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Linear API connection error: {exc}") from exc

    data = json.loads(raw)
    if "errors" in data:
        raise RuntimeError(f"Linear API error: {data['errors']}")
    return data


def fetch_labeled_issues(token: str, label: str) -> List[Dict[str, Any]]:
    """Fetch all issues with labels starting with the specified prefix (e.g., stream matches stream:cash-engine)"""
    issues: List[Dict[str, Any]] = []
    after = None

    # Filter for issues with labels starting with prefix, not completed/canceled
    # We fetch all issues and filter client-side for label prefix matching
    issue_filter = {
        "state": {"type": {"nin": ["completed", "canceled"]}}
    }

    while True:
        variables = {"after": after, "filter": issue_filter}
        data = graphql_request(token, ISSUES_QUERY, variables)
        payload = data.get("data", {}).get("issues", {})
        nodes = payload.get("nodes", [])

        # Filter for issues with label matching prefix (stream, stream:cash-engine, etc.)
        for node in nodes:
            labels = [l.get("name", "") for l in node.get("labels", {}).get("nodes", [])]
            if any(lbl.upper().startswith(label.upper()) for lbl in labels):
                issues.append(node)

        page = payload.get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        after = page.get("endCursor")

    return issues


def linear_priority_to_string(priority: Optional[int]) -> str:
    """Convert Linear priority (0-4) to string"""
    if priority is None:
        return "MEDIUM"
    mapping = {
        0: "LOW",      # No priority
        1: "HIGH",     # Urgent
        2: "HIGH",     # High
        3: "MEDIUM",   # Medium
        4: "LOW",      # Low
    }
    return mapping.get(priority, "MEDIUM")


def issue_to_feature(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a Linear issue to features.json format"""
    identifier = issue.get("identifier", "UNKNOWN")
    title = issue.get("title", "Untitled")
    description = issue.get("description", "")
    priority = linear_priority_to_string(issue.get("priority"))
    due_date = issue.get("dueDate")
    labels = [l.get("name", "") for l in issue.get("labels", {}).get("nodes", [])]
    state = issue.get("state", {}).get("name", "Unknown")
    url = issue.get("url", "")

    # Determine category from labels
    category = "dev"  # default
    if any("marketing" in l.lower() for l in labels):
        category = "marketing"
    elif any("ops" in l.lower() for l in labels):
        category = "ops"
    elif any("deploy" in l.lower() for l in labels):
        category = "deploy"

    # Build notes
    notes_parts = []
    if description:
        notes_parts.append(description[:500])
    if url:
        notes_parts.append(f"Linear: {url}")

    feature = {
        "id": f"LIN-{identifier}",
        "description": title,
        "category": category,
        "priority": priority,
        "verification": f"Linear issue {identifier} marked as Done",
        "passes": False,
        "notes": " | ".join(notes_parts) if notes_parts else None,
        "tags": [l for l in labels if l.upper() != "GIN" and not l.lower().startswith("stream")],
        "linear_id": issue.get("id"),
        "linear_identifier": identifier,
        "linear_state": state,
    }

    if due_date:
        feature["due"] = due_date

    return feature


def load_features() -> Dict[str, Any]:
    """Load features.json"""
    if not FEATURES_FILE.exists():
        return {"features": []}
    with open(FEATURES_FILE) as f:
        return json.load(f)


def save_features(data: Dict[str, Any]):
    """Save features.json"""
    with open(FEATURES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def sync_issues(label: str = "stream", dry_run: bool = False) -> int:
    """Sync Linear issues to features.json. Returns count of new features added."""
    token = load_api_key()
    if not token:
        raise RuntimeError("LINEAR_API_KEY not found. Set env var or secrets/linear_api_key.txt")

    print(f"Fetching issues with label '{label}'...")
    issues = fetch_labeled_issues(token, label)
    print(f"Found {len(issues)} issues")

    if not issues:
        print("No issues to sync")
        return 0

    # Load current features
    features_data = load_features()
    existing_features = features_data.get("features", [])

    # Get existing Linear IDs to avoid duplicates
    existing_linear_ids = set()
    for f in existing_features:
        if f.get("linear_id"):
            existing_linear_ids.add(f["linear_id"])
        # Also check by ID pattern
        if f.get("id", "").startswith("LIN-"):
            existing_linear_ids.add(f["id"])

    # Convert and add new issues
    added = 0
    for issue in issues:
        linear_id = issue.get("id")
        identifier = issue.get("identifier")
        feature_id = f"LIN-{identifier}"

        if linear_id in existing_linear_ids or feature_id in existing_linear_ids:
            print(f"  Skipping {identifier} (already exists)")
            continue

        feature = issue_to_feature(issue)
        print(f"  Adding {identifier}: {issue.get('title', '')[:50]}...")

        if not dry_run:
            existing_features.append(feature)
            existing_linear_ids.add(linear_id)
            existing_linear_ids.add(feature_id)

        added += 1

    # Save if not dry run
    if not dry_run and added > 0:
        features_data["features"] = existing_features
        save_features(features_data)
        print(f"Saved {added} new features to features.json")
    elif dry_run:
        print(f"[DRY RUN] Would add {added} new features")

    return added


def main():
    parser = argparse.ArgumentParser(description="Sync Linear issues to features.json")
    parser.add_argument("--label", default="stream", help="Label prefix to filter issues (default: stream)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    try:
        added = sync_issues(label=args.label, dry_run=args.dry_run)
        print(f"\nSync complete. {added} new features.")
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

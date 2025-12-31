#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import request
from urllib.error import HTTPError, URLError

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
TEAMS_QUERY = """
query Teams {
  teams {
    nodes { id key name }
  }
}
"""


class LinearSyncError(RuntimeError):
    pass


def load_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    data: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def load_api_key(root: Path, env_file: Optional[Path], token_file: Optional[Path]) -> Optional[str]:
    key = os.getenv("LINEAR_API_KEY") or os.getenv("LINEAR_TOKEN")
    if key:
        return key

    env_candidates = [env_file] if env_file else [root / "secrets/linear.env", root / "secrets/linear_api_key.env"]
    for candidate in env_candidates:
        if not candidate:
            continue
        data = load_env_file(candidate)
        key = data.get("LINEAR_API_KEY") or data.get("LINEAR_TOKEN")
        if key:
            return key

    token_candidates = [token_file] if token_file else [root / "secrets/linear_api_key.txt"]
    for candidate in token_candidates:
        if candidate and candidate.exists():
            token = candidate.read_text().strip()
            if token:
                return token

    return None


def graphql_request(token: str, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        raise LinearSyncError(f"Linear API HTTP error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise LinearSyncError(f"Linear API connection error: {exc}") from exc

    data = json.loads(raw)
    if "errors" in data:
        raise LinearSyncError(f"Linear API error: {data['errors']}")
    return data


def fetch_teams(token: str) -> List[Dict[str, Any]]:
    data = graphql_request(token, TEAMS_QUERY)
    return data.get("data", {}).get("teams", {}).get("nodes", [])


def build_filter(include_closed: bool, team_ids: List[str], team_keys: List[str]) -> Optional[Dict[str, Any]]:
    if include_closed and not team_ids and not team_keys:
        return None

    issue_filter: Dict[str, Any] = {}
    if not include_closed:
        issue_filter["state"] = {"type": {"nin": ["completed", "canceled"]}}

    if team_ids:
        issue_filter["team"] = {"id": {"in": team_ids}}
    elif team_keys:
        issue_filter["team"] = {"key": {"in": team_keys}}

    return issue_filter or None


def fetch_issues(token: str, include_closed: bool, team_ids: List[str], team_keys: List[str]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    after = None
    issue_filter = build_filter(include_closed, team_ids, team_keys)

    while True:
        variables = {"after": after, "filter": issue_filter}
        data = graphql_request(token, ISSUES_QUERY, variables)
        payload = data.get("data", {}).get("issues", {})
        nodes = payload.get("nodes", [])
        issues.extend(nodes)
        page = payload.get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        after = page.get("endCursor")

    return issues


def load_issues_from_file(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text())
    if isinstance(raw, dict) and "issues" in raw:
        return raw["issues"]
    if isinstance(raw, list):
        return raw
    raise LinearSyncError("Unsupported input format for --from-file")


def issue_labels(issue: Dict[str, Any]) -> List[str]:
    labels = issue.get("labels", {}).get("nodes", [])
    return [label.get("name", "") for label in labels if label.get("name")]


def summarize_issues(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_state: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    by_team: Dict[str, int] = {}
    legacy_candidates: List[Dict[str, Any]] = []

    for issue in issues:
        state = issue.get("state", {}).get("type", "unknown")
        by_state[state] = by_state.get(state, 0) + 1

        priority = issue.get("priority", 0)
        by_priority[str(priority)] = by_priority.get(str(priority), 0) + 1

        team = issue.get("team", {}).get("key") or issue.get("team", {}).get("name") or "unknown"
        by_team[team] = by_team.get(team, 0) + 1

        labels = issue_labels(issue)
        if any(label.startswith("GIN") for label in labels):
            legacy_candidates.append(issue)

    return {
        "by_state": by_state,
        "by_priority": by_priority,
        "by_team": by_team,
        "legacy_candidates": legacy_candidates,
    }


def render_digest(issues: List[Dict[str, Any]], summary: Dict[str, Any], synced_at: str) -> str:
    lines: List[str] = []
    lines.append("# Linear Digest")
    lines.append("")
    lines.append(f"Synced at: {synced_at}")
    lines.append(f"Open issues: {len(issues)}")
    lines.append("")

    lines.append("## By state")
    for state, count in sorted(summary["by_state"].items(), key=lambda x: x[0]):
        lines.append(f"- {state}: {count}")
    lines.append("")

    lines.append("## By priority")
    for priority, count in sorted(summary["by_priority"].items(), key=lambda x: int(x[0])):
        lines.append(f"- P{priority}: {count}")
    lines.append("")

    lines.append("## By team")
    for team, count in sorted(summary["by_team"].items(), key=lambda x: x[0].lower()):
        lines.append(f"- {team}: {count}")
    lines.append("")

    legacy = summary["legacy_candidates"]
    lines.append("## Legacy labels (GIN) (top 10)")
    if not legacy:
        lines.append("- none")
    else:
        for issue in legacy[:10]:
            lines.append(format_issue_line(issue))
    lines.append("")

    lines.append("## Top issues (priority + recency)")
    def parse_updated(issue: Dict[str, Any]) -> float:
        raw = issue.get("updatedAt") or ""
        try:
            return dt.datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0

    sorted_issues = sorted(
        issues,
        key=lambda i: ((i.get("priority") or 5), -parse_updated(i)),
    )
    for issue in sorted_issues[:15]:
        lines.append(format_issue_line(issue))

    lines.append("")
    return "\n".join(lines)


def format_issue_line(issue: Dict[str, Any]) -> str:
    ident = issue.get("identifier", "?")
    title = issue.get("title", "")
    state = issue.get("state", {}).get("name", "?")
    priority = issue.get("priority", 0)
    assignee = (issue.get("assignee") or {}).get("name", "unassigned")
    url = issue.get("url", "")
    return f"- [{ident}] {title} (state: {state}, P{priority}, {assignee}) - {url}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Linear issues into Kraliki repo mirror.")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: ai-automation/gin/linear-sync)")
    parser.add_argument("--include-closed", action="store_true", help="Include completed/canceled issues")
    parser.add_argument("--team-ids", default="", help="Comma-separated team IDs to include")
    parser.add_argument("--team-keys", default="", help="Comma-separated team keys to include")
    parser.add_argument("--from-file", default=None, help="Load issues from a local JSON file")
    parser.add_argument("--list-teams", action="store_true", help="List teams and exit")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of issues in digest")
    parser.add_argument("--env-file", default=None, help="Path to env file with LINEAR_API_KEY")
    parser.add_argument("--token-file", default=None, help="Path to token file")

    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    output_dir = Path(args.output_dir) if args.output_dir else root / "ai-automation/gin/linear-sync"
    output_dir.mkdir(parents=True, exist_ok=True)

    issues: List[Dict[str, Any]]

    if args.from_file:
        issues = load_issues_from_file(Path(args.from_file))
    else:
        token = load_api_key(root, Path(args.env_file) if args.env_file else None, Path(args.token_file) if args.token_file else None)
        if not token:
            raise LinearSyncError("LINEAR_API_KEY not found. Set env var or secrets/linear.env")

        if args.list_teams:
            teams = fetch_teams(token)
            print(json.dumps(teams, indent=2))
            return 0

        team_ids = [item.strip() for item in args.team_ids.split(",") if item.strip()]
        team_keys = [item.strip() for item in args.team_keys.split(",") if item.strip()]
        issues = fetch_issues(token, args.include_closed, team_ids, team_keys)

    if args.limit > 0:
        issues = issues[: args.limit]

    synced_at = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    summary = summarize_issues(issues)

    payload = {
        "synced_at": synced_at,
        "issue_count": len(issues),
        "issues": issues,
    }

    (output_dir / "linear-issues.json").write_text(json.dumps(payload, indent=2))
    (output_dir / "linear-digest.md").write_text(render_digest(issues, summary, synced_at))
    (output_dir / "last_sync.txt").write_text(synced_at)

    print(f"Synced {len(issues)} issues -> {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LinearSyncError as exc:
        print(f"Linear sync failed: {exc}")
        raise SystemExit(1)

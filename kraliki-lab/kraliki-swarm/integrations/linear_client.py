#!/usr/bin/env python3
"""
Linear API Client for GIN
=========================
Create and manage Linear issues from discovery highways.

Features:
- Retry with exponential backoff
- Circuit breaker for sustained failures
- Centralized error logging
"""

import json
import re
import socket
import ssl
from pathlib import Path
from typing import Optional, Dict, Any
from urllib import request
from urllib.error import HTTPError, URLError

# Import robust utilities
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "control"))
from robust_utils import (
    retry_with_backoff,
    CircuitBreaker,
    log_error,
    update_health_metric,
)

GRAPHQL_URL = "https://api.linear.app/graphql"
SECRETS_DIR = Path("/home/adminmatej/github/secrets")

# Cache for team/label IDs
_cache: Dict[str, Any] = {}

# Query result cache (for idempotent queries only)
_query_cache: Dict[str, Any] = {}
_cache_ttl: float = 60.0  # 60 seconds cache TTL
_last_cache_cleanup: float = 0

# Circuit breaker for Linear API
_linear_breaker = CircuitBreaker(
    "linear_api", failure_threshold=5, recovery_timeout=120
)

# Rate limiting - track last API call time
import time

_last_api_call: float = 0
_MIN_API_INTERVAL: float = 0.5  # 500ms between API calls to avoid rate limiting


def _cleanup_cache():
    """Remove expired entries from query cache"""
    global _last_cache_cleanup
    now = time.time()
    if now - _last_cache_cleanup < 300:  # Cleanup every 5 minutes
        return

    cutoff = now - _cache_ttl
    to_remove = [k for k, (_, ts) in _query_cache.items() if ts < cutoff]
    for k in to_remove:
        del _query_cache[k]
    _last_cache_cleanup = now


_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_FILTER_FIELD_RE = re.compile(r"\b(notEq|notIn)\s*:")


def _safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Safely get value from dict or object, handling None values.

    Unlike dict.get(), this handles the case where obj[key] returns None,
    not just when key is missing.
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _looks_like_uuid(value: str) -> bool:
    return bool(value and _UUID_RE.match(value))


def _is_transient_error(error: Exception) -> bool:
    """Check if error is transient (network timeout, temporary outage) vs persistent.

    Returns True for errors that should NOT open circuit breaker.
    Returns False for errors that SHOULD open circuit breaker.
    """
    if isinstance(
        error, (socket.timeout, ConnectionResetError, ConnectionRefusedError)
    ):
        return True

    if isinstance(error, URLError):
        if isinstance(error.reason, (socket.timeout, ConnectionRefusedError)):
            return True

    if isinstance(error, HTTPError):
        # 5xx errors are server-side, may be transient
        if 500 <= error.code < 600:
            return True
        # 429 rate limiting - transient
        if error.code == 429:
            return True

    # SSL errors might be transient
    if isinstance(error, ssl.SSLError):
        return True

    # Everything else (4xx client errors, validation) is persistent
    return False


def _is_query_validation_error(error_body: str) -> bool:
    """Check if error body indicates a GraphQL query/validation issue."""
    if not error_body:
        return False
    try:
        payload = json.loads(error_body)
    except json.JSONDecodeError:
        return False

    for err in payload.get("errors", []) or []:
        extensions = err.get("extensions", {}) if isinstance(err, dict) else {}
        code = extensions.get("code")
        if code in ("GRAPHQL_VALIDATION_FAILED", "BAD_USER_INPUT"):
            return True
        if extensions.get("userError") is True:
            return True
    return False


def _normalize_query_filters(query: str) -> str:
    def repl(match: re.Match) -> str:
        field = match.group(1)
        return ("neq" if field == "notEq" else "nin") + ":"

    return _FILTER_FIELD_RE.sub(repl, query)


def _normalize_filter_keys(value: Any) -> Any:
    """Normalize Linear filter keys from legacy formats."""
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if key == "notEq":
                key = "neq"
            elif key == "notIn":
                key = "nin"
            normalized[key] = _normalize_filter_keys(item)
        return normalized
    if isinstance(value, list):
        return [_normalize_filter_keys(item) for item in value]
    return value


def resolve_issue_id(issue_id_or_identifier: str) -> Optional[str]:
    """Resolve a Linear issue UUID from a UUID or identifier (e.g., VD-306)."""
    if not issue_id_or_identifier:
        return None
    if _looks_like_uuid(issue_id_or_identifier):
        return issue_id_or_identifier

    result = graphql(
        """
        query SearchIssue($term: String!) {
            searchIssues(term: $term, first: 1) {
                nodes { id identifier }
            }
        }
    """,
        {"term": issue_id_or_identifier},
    )

    issues = result.get("data", {}).get("searchIssues", {}).get("nodes", [])
    if not issues:
        return None
    return issues[0].get("id")


def load_api_key() -> Optional[str]:
    """Load Linear API key from secrets"""
    token_file = SECRETS_DIR / "linear_api_key.txt"
    if token_file.exists():
        return token_file.read_text().strip()
    return None


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=30.0)
def graphql(query: str, variables: Optional[Dict] = None) -> Dict:
    """Execute GraphQL query with retry and circuit breaker"""
    global _last_api_call

    # Check cache for idempotent queries (not mutations)
    is_mutation = "mutation" in query.lower()
    if not is_mutation:
        _cleanup_cache()
        cache_key = (
            f"{query[:200]}{str(sorted(variables.items()) if variables else '')}"
        )
        if cache_key in _query_cache:
            cached_data, cache_time = _query_cache[cache_key]
            if time.time() - cache_time < _cache_ttl:
                return cached_data

    # Rate limiting - wait if needed
    elapsed = time.time() - _last_api_call
    if elapsed < _MIN_API_INTERVAL:
        time.sleep(_MIN_API_INTERVAL - elapsed)

    # Check circuit breaker
    if not _linear_breaker.can_execute():
        log_error("linear_client", "circuit_open", "Linear API circuit breaker is open")
        raise RuntimeError(
            "Linear API circuit breaker is open - too many recent failures"
        )

    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("Linear API key not found")

    payload = {"query": _normalize_query_filters(query)}
    if variables:
        payload["variables"] = _normalize_filter_keys(variables)

    req = request.Request(
        GRAPHQL_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": api_key},
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            _linear_breaker.record_success()
            _last_api_call = time.time()
            update_health_metric(
                "linear",
                "last_success",
                __import__("datetime").datetime.now().isoformat(),
            )
            # Cache successful queries (not mutations)
            if not is_mutation:
                cache_key = f"{query[:200]}{str(sorted(variables.items()) if variables else '')}"
                _query_cache[cache_key] = (result, time.time())
            return result
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        is_query_error = _is_query_validation_error(error_body)
        if not _is_transient_error(e) and not is_query_error:
            _linear_breaker.record_failure()
        query_preview = query.strip().split("\n")[0] if query else "unknown"
        log_error(
            "linear_client",
            "query_error" if is_query_error else "api_error",
            f"HTTP {e.code}: {error_body[:500]} | Query: {query_preview[:100]}",
        )
        raise RuntimeError(f"Linear API error: {e.code} - {error_body}")
    except Exception as e:
        if not _is_transient_error(e):
            _linear_breaker.record_failure()
        query_preview = query.strip().split("\n")[0] if query else "unknown"
        log_error(
            "linear_client",
            "connection_error",
            f"{str(e)} | Query: {query_preview[:100]}",
        )
        raise


def get_team_id(team_key: str = "VD") -> Optional[str]:
    """Get team ID by key"""
    if f"team_{team_key}" in _cache:
        return _cache[f"team_{team_key}"]

    result = graphql("""
        query Teams {
            teams { nodes { id key name } }
        }
    """)

    for team in result.get("data", {}).get("teams", {}).get("nodes", []):
        if team.get("key") == team_key:
            _cache[f"team_{team_key}"] = team["id"]
            return team["id"]

    return None


def get_or_create_label(team_id: str, label_name: str) -> Optional[str]:
    """Get label ID, create if doesn't exist"""
    cache_key = f"label_{team_id}_{label_name}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Fetch all labels and filter in Python (avoids GraphQL type issues)
    result = graphql("""
        query Labels {
            issueLabels(first: 250) {
                nodes { id name team { id } }
            }
        }
    """)

    for label in result.get("data", {}).get("issueLabels", {}).get("nodes", []):
        if (
            label.get("name") == label_name
            and label.get("team", {}).get("id") == team_id
        ):
            _cache[cache_key] = label["id"]
            return label["id"]

    # Create label if not found (teamId is String in input)
    result = graphql(
        """
        mutation CreateLabel($teamId: String!, $name: String!) {
            issueLabelCreate(input: { teamId: $teamId, name: $name, color: "#6366f1" }) {
                success
                issueLabel { id }
            }
        }
    """,
        {"teamId": team_id, "name": label_name},
    )

    label_id = (
        result.get("data", {})
        .get("issueLabelCreate", {})
        .get("issueLabel", {})
        .get("id")
    )
    if label_id:
        _cache[cache_key] = label_id
    return label_id


def create_issue(
    title: str,
    description: str,
    team_key: str = "VD",
    labels: list = None,
    priority: int = 2,  # 1=urgent, 2=high, 3=medium, 4=low
) -> Optional[Dict]:
    """
    Create a Linear issue.

    Returns:
        Dict with id, identifier, url or None on failure
    """
    team_id = get_team_id(team_key)
    if not team_id:
        return None

    # Get label IDs
    label_ids = []
    for label_name in labels or []:
        label_id = get_or_create_label(team_id, label_name)
        if label_id:
            label_ids.append(label_id)

    # Map priority string to number
    priority_map = {"HIGH": 2, "MEDIUM": 3, "LOW": 4, "URGENT": 1}
    if isinstance(priority, str):
        priority = priority_map.get(priority.upper(), 3)

    mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    url
                    title
                }
            }
        }
    """

    variables = {
        "input": {
            "teamId": team_id,
            "title": title,
            "description": description,
            "priority": priority,
            "labelIds": label_ids,
        }
    }

    result = graphql(mutation, variables)

    issue_data = result.get("data", {}).get("issueCreate", {})
    if issue_data.get("success"):
        return issue_data.get("issue")

    return None


def issue_exists(title: str, team_key: str = "VD") -> bool:
    """Check if issue with similar title exists (not completed/canceled)"""
    # Use title search to reduce data fetched - search for key words from title
    search_term = title[:50]  # Use first 50 chars for search

    try:
        result = graphql(
            """
            query SearchIssues($filter: IssueFilter!) {
                issues(filter: $filter, first: 20) {
                    nodes { title state { type } }
                }
            }
        """,
            {
                "filter": {
                    "title": {
                        "containsIgnoreCase": search_term[:30]
                    },  # Use shorter search term
                    "state": {"type": {"nin": ["completed", "canceled"]}},
                }
            },
        )

        title_lower = title.lower()
        for issue in result.get("data", {}).get("issues", {}).get("nodes", []):
            if issue.get("title", "").lower() == title_lower:
                return True
        return False
    except Exception:
        # If search fails, assume issue doesn't exist to allow creation attempt
        # The circuit breaker will handle actual API failures
        return False


def get_done_state_id(team_id: str) -> Optional[str]:
    """Get the 'Done' state ID for a team"""
    cache_key = f"done_state_{team_id}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Fetch all states and filter in Python (avoids GraphQL type issues)
    result = graphql("""
        query States {
            workflowStates(first: 250) {
                nodes { id name type team { id } }
            }
        }
    """)

    for state in result.get("data", {}).get("workflowStates", {}).get("nodes", []):
        if (
            state.get("type") == "completed"
            and state.get("team", {}).get("id") == team_id
        ):
            _cache[cache_key] = state["id"]
            return state["id"]

    return None


def get_in_progress_state_id(team_id: str) -> Optional[str]:
    """Get the 'In Progress' state ID for a team"""
    cache_key = f"in_progress_state_{team_id}"
    if cache_key in _cache:
        return _cache[cache_key]

    result = graphql("""
        query States {
            workflowStates(first: 250) {
                nodes { id name type team { id } }
            }
        }
    """)

    for state in result.get("data", {}).get("workflowStates", {}).get("nodes", []):
        if (
            state.get("type") == "started"
            and state.get("team", {}).get("id") == team_id
        ):
            _cache[cache_key] = state["id"]
            return state["id"]

    return None


def start_issue(issue_id: str, team_key: str = "VD") -> bool:
    """Mark a Linear issue as In Progress"""
    try:
        resolved_id = resolve_issue_id(issue_id)
        if not resolved_id:
            return False

        team_id = get_team_id(team_key)
        if not team_id:
            return False

        in_progress_state_id = get_in_progress_state_id(team_id)
        if not in_progress_state_id:
            return False

        result = graphql(
            """
            mutation UpdateIssue($id: String!, $stateId: String!) {
                issueUpdate(id: $id, input: { stateId: $stateId }) {
                    success
                    issue { id identifier state { name } }
                }
            }
        """,
            {"id": resolved_id, "stateId": in_progress_state_id},
        )

        return result.get("data", {}).get("issueUpdate", {}).get("success", False)
    except Exception:
        return False


def get_pending_tasks(
    team_key: str = "VD", label: str = "GIN", limit: int = 20
) -> list:
    """
    Fetch pending tasks from Linear with GIN label.

    Returns list of tasks sorted by priority:
    [
        {
            "id": "linear-uuid",
            "identifier": "VD-123",
            "title": "Task title",
            "description": "Task description",
            "priority": 2,
            "labels": ["GIN", "GIN-DEV"],
            "state": "Todo"
        },
        ...
    ]
    """
    try:
        # Fetch issues with GIN label that are not completed/canceled
        # Include backlog, unstarted states (exclude only completed/canceled)
        result = graphql(
            """
            query PendingTasks($filter: IssueFilter!, $first: Int!) {
                issues(filter: $filter, first: $first) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        state { name type }
                        labels { nodes { name } }
                    }
                }
            }
        """,
            {
                "filter": {
                    "labels": {"name": {"eq": label}},
                    "state": {"type": {"nin": ["completed", "canceled"]}},
                },
                "first": limit,
            },
        )

        tasks = []
        for issue in result.get("data", {}).get("issues", {}).get("nodes", []):
            state = _safe_get(issue, "state", {})
            state_type = _safe_get(state, "type", "")

            # Skip issues already in progress (being worked on by another agent)
            if state_type == "started":
                continue

            labels_data = _safe_get(issue, "labels", {})
            labels_nodes = _safe_get(labels_data, "nodes", [])
            labels = [_safe_get(l, "name", "") for l in labels_nodes]

            tasks.append(
                {
                    "id": issue.get("id"),
                    "identifier": issue.get("identifier"),
                    "title": issue.get("title", ""),
                    "description": issue.get("description", ""),
                    "priority": issue.get("priority", 4),
                    "labels": labels,
                    "state": _safe_get(state, "name", "Unknown"),
                    "state_type": state_type,
                    # Map to features.json-like category
                    "category": "dev"
                    if "GIN-DEV" in labels
                    else "business"
                    if "GIN-BIZ" in labels
                    else "dev",
                }
            )

        # Sort by priority (1=urgent, 2=high, 3=medium, 4=low)
        tasks.sort(key=lambda x: x.get("priority", 4))

        return tasks
    except Exception as e:
        log_error("linear_client", "get_pending_tasks_error", str(e))
        return []


def get_task_by_id(issue_id: str) -> Optional[Dict]:
    """Fetch a single task by Linear ID"""
    try:
        resolved_id = resolve_issue_id(issue_id)
        if not resolved_id:
            return None

        result = graphql(
            """
            query GetIssue($id: String!) {
                issue(id: $id) {
                    id
                    identifier
                    title
                    description
                    priority
                    state { name type }
                    labels { nodes { name } }
                }
            }
        """,
            {"id": resolved_id},
        )

        issue = result.get("data", {}).get("issue")
        if not issue:
            return None

        state = _safe_get(issue, "state", {})
        labels_data = _safe_get(issue, "labels", {})
        labels_nodes = _safe_get(labels_data, "nodes", [])
        labels = [_safe_get(l, "name", "") for l in labels_nodes]

        return {
            "id": issue.get("id"),
            "identifier": issue.get("identifier"),
            "title": issue.get("title", ""),
            "description": issue.get("description", ""),
            "priority": issue.get("priority", 4),
            "labels": labels,
            "state": _safe_get(state, "name", "Unknown"),
            "category": "dev"
            if "GIN-DEV" in labels
            else "business"
            if "GIN-BIZ" in labels
            else "dev",
        }
    except Exception as e:
        log_error("linear_client", "get_task_by_id_error", str(e))
        return None


def complete_issue(issue_id: str, team_key: str = "VD") -> bool:
    """Mark a Linear issue as Done"""
    try:
        resolved_id = resolve_issue_id(issue_id)
        if not resolved_id:
            return False

        team_id = get_team_id(team_key)
        if not team_id:
            return False

        done_state_id = get_done_state_id(team_id)
        if not done_state_id:
            return False

        result = graphql(
            """
            mutation UpdateIssue($id: String!, $stateId: String!) {
                issueUpdate(id: $id, input: { stateId: $stateId }) {
                    success
                    issue { id identifier state { name } }
                }
            }
        """,
            {"id": resolved_id, "stateId": done_state_id},
        )

        return result.get("data", {}).get("issueUpdate", {}).get("success", False)
    except Exception:
        return False


def update_issue_title(issue_id: str, new_title: str) -> bool:
    """Update the title of a Linear issue"""
    try:
        resolved_id = resolve_issue_id(issue_id)
        if not resolved_id:
            return False

        result = graphql(
            """
            mutation UpdateIssue($id: String!, $title: String!) {
                issueUpdate(id: $id, input: { title: $title }) {
                    success
                    issue { id identifier title }
                }
            }
        """,
            {"id": resolved_id, "title": new_title},
        )

        return result.get("data", {}).get("issueUpdate", {}).get("success", False)
    except Exception as e:
        log_error("linear_client", "update_title_error", str(e))
        return False


def add_label_to_issue(issue_id: str, label_name: str, team_key: str = "VD") -> bool:
    """Add a label to an existing issue without overwriting existing ones"""
    try:
        resolved_id = resolve_issue_id(issue_id)
        if not resolved_id:
            return False

        team_id = get_team_id(team_key)
        if not team_id:
            return False

        label_id = get_or_create_label(team_id, label_name)
        if not label_id:
            return False

        # Get current labels to avoid overwriting
        task = get_task_by_id(resolved_id)
        if not task:
            return False

        # Get current label IDs
        # We need to fetch labels with IDs for the update
        result = graphql(
            """
            query GetIssueLabels($id: String!) {
                issue(id: $id) {
                    labels { nodes { id name } }
                }
            }
        """,
            {"id": resolved_id},
        )

        current_label_ids = [
            l["id"]
            for l in result.get("data", {})
            .get("issue", {})
            .get("labels", {})
            .get("nodes", [])
        ]

        if label_id in current_label_ids:
            return True  # Already has label

        current_label_ids.append(label_id)

        result = graphql(
            """
            mutation UpdateIssue($id: String!, $labelIds: [String!]) {
                issueUpdate(id: $id, input: { labelIds: $labelIds }) {
                    success
                }
            }
        """,
            {"id": resolved_id, "labelIds": current_label_ids},
        )

        return result.get("data", {}).get("issueUpdate", {}).get("success", False)
    except Exception:
        return False


# Quick test
if __name__ == "__main__":
    print("Testing Linear client...")
    team_id = get_team_id("VD")
    print(f"Team ID: {team_id}")

    if team_id:
        label_id = get_or_create_label(team_id, "GIN")
        print(f"GIN label ID: {label_id}")
        done_id = get_done_state_id(team_id)
        print(f"Done state ID: {done_id}")
        in_progress_id = get_in_progress_state_id(team_id)
        print(f"In Progress state ID: {in_progress_id}")

    print("\nFetching pending GIN tasks...")
    tasks = get_pending_tasks()
    print(f"Found {len(tasks)} pending tasks:")
    for t in tasks[:5]:
        print(f"  [{t['identifier']}] {t['title'][:50]}... (priority: {t['priority']})")

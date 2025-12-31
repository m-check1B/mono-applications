#!/usr/bin/env python3
import sys
import json
import os

# Ensure we can import from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from integrations.linear_client import graphql
from control import pipeline_policy

query = """
query OrchestratorIssues($filter: IssueFilter!) {
    issues(filter: $filter, first: 50) {
        nodes {
            id
            identifier
            title
            priority
            state { name type }
            labels { nodes { name } }
            assignee { name }
        }
    }
}
"""

policy = pipeline_policy.load_pipeline_policy()
taxonomy = pipeline_policy.load_pipeline_taxonomy()
label_groups = pipeline_policy.get_enabled_label_groups(
    policy=policy, taxonomy=taxonomy
)
if os.getenv("LINEAR_INCLUDE_LEGACY_LABELS", "0") == "1":
    for group in label_groups:
        if "stream:cash-engine" in group:
            group.append("GIN-BIZ")
        if "stream:asset-engine" in group:
            group.extend(["GIN-DEV", "GIN-FIX"])

def fetch_issues(label_group):
    variables = {
        "filter": {
            "and": [
                {"labels": {"name": {"in": label_group}}},
                {"state": {"type": {"nin": ["completed", "canceled"]}}},
                {"labels": {"name": {"neq": "mac-browser"}}},
                {"labels": {"name": {"neq": "human-blocked"}}},
                {"labels": {"name": {"neq": "human-action"}}},
            ]
        }
    }
    result = graphql(query, variables)
    return result.get("data", {}).get("issues", {}).get("nodes", [])

try:
    issues = []
    for group in label_groups:
        issues = fetch_issues(group)
        if issues:
            break
    print(json.dumps(issues, indent=2))
except Exception as e:
    print(f"Error querying Linear: {e}", file=sys.stderr)
    sys.exit(1)

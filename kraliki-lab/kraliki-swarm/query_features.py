#!/usr/bin/env python3
import sys

sys.path.insert(0, ".")
from integrations.linear_client import graphql

result = graphql(
    """
    query FeatureIssues($filter: IssueFilter!) {
        issues(filter: $filter, first: 30) {
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
            "and": [
                {"labels": {"name": {"in": ["type:feature", "Feature"]}}},
                {"state": {"type": {"nin": ["completed", "canceled"]}}},
                {"labels": {"name": {"neq": "mac-browser"}}},
            ]
        }
    },
)

issues = result.get("data", {}).get("issues", {}).get("nodes", [])
print(f"Found {len(issues)} Feature issues:")
for i in issues[:20]:
    labels = [l.get("name") for l in i.get("labels", {}).get("nodes", [])]
    state = i.get("state", {})
    print(
        f"[{i.get('identifier')}] {i.get('title')[:60]}... (P{i.get('priority')}, {state.get('name')})"
    )
    print(f"  Labels: {', '.join(labels)}")
    print()

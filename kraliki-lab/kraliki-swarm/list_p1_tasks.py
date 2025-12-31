#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, ".")
from integrations.linear_client import graphql
from control import pipeline_policy

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

def fetch_p1_issues(label_group):
    result = graphql(
        """
        query PriorityIssues($filter: IssueFilter!) {
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
    """,
        {
            "filter": {
                "and": [
                    {"state": {"type": {"nin": ["completed", "canceled"]}}},
                    {"priority": {"eq": 1}},
                    {"labels": {"name": {"in": label_group}}},
                ]
            }
        },
    )
    return result.get("data", {}).get("issues", {}).get("nodes", [])

issues = []
selected_group = None
label_summary = "; ".join([", ".join(group) for group in label_groups]) or "none"
for group in label_groups:
    issues = fetch_p1_issues(group)
    if issues:
        selected_group = group
        break

if selected_group:
    print(f"Found {len(issues)} P1 issues (labels: {', '.join(selected_group)}):")
else:
    print(f"Found 0 P1 issues (labels: {label_summary}).")
for i in issues:
    labels = [l.get("name") for l in i.get("labels", {}).get("nodes", [])]
    state = i.get("state", {})
    assignee = i.get("assignee", {}).get("name") if i.get("assignee") else "Unassigned"
    print(
        f"[{i.get('identifier')}] {i.get('title')[:60]}... (P{i.get('priority')}, {state.get('name')}, {assignee})"
    )
    print(f"  Labels: {', '.join(labels)}")
    print()

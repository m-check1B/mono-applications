#!/usr/bin/env python3
import sys

sys.path.insert(0, ".")
from integrations.linear_client import graphql

result = graphql("""
    query AllLabels {
        issueLabels(first: 100) {
            nodes { id name color }
        }
    }
""")

labels = result.get("data", {}).get("issueLabels", {}).get("nodes", [])
print(f"Available labels ({len(labels)} total):")
for l in sorted(labels, key=lambda x: x.get("name", "")):
    print(f"  - {l.get('name')}")

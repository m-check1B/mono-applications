# Build-Audit-Fix Pattern

**Purpose:** Ensure code quality through systematic building, auditing, and fixing cycles.

## Overview

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  BUILD  │────▶│  AUDIT  │────▶│   FIX   │
│ (Codex) │     │ (Codex) │     │ (Codex) │
└─────────┘     └─────────┘     └────┬────┘
     ▲                               │
     │                               │
     └───────────────────────────────┘
         (Cycle until audit passes)
```

## When to Use

- Building production-quality code
- Security-sensitive features
- Complex algorithms
- Critical business logic

## Phase 1: Build

**Worker:** Codex (backend-builder or appropriate builder)

**Input:**
```yaml
phase: "build"
task: "Description of what to build"
requirements:
  - "Functional requirements"
constraints:
  - "Technical constraints"
context:
  - "Relevant context/dependencies"
```

**Output Expected:**
- Working implementation
- Basic tests
- Documentation

**Quality Bar:** Code runs, tests pass, meets requirements.

## Phase 2: Audit

**Worker:** Codex (code-auditor)

**Input:**
```yaml
phase: "audit"
build_output:
  files:
    - "List of files from build phase"
  tests: "Test results from build phase"
audit_focus:
  - "security"
  - "correctness"
  - "performance"
  - "maintainability"
```

**Output Expected:**
```yaml
verdict: "PASS|NEEDS_FIXES"

findings:
  critical: []
  high: []
  medium: []
  low: []

pass_conditions:
  - "No critical issues"
  - "No high issues"
```

**Quality Bar:** No critical or high severity issues.

## Phase 3: Fix

**Worker:** Codex (same as builder, or patcher)

**Input:**
```yaml
phase: "fix"
original_code:
  files:
    - "Files that need fixing"
audit_findings:
  - id: "ISSUE-001"
    severity: "high"
    location: "file:line"
    problem: "Description"
    fix: "Suggested fix"
```

**Output Expected:**
- Fixed code addressing each finding
- Updated tests if needed
- Brief explanation of changes

**Quality Bar:** All high+ issues resolved.

## Orchestration Script

```python
#!/usr/bin/env python3
"""
Build-Audit-Fix orchestration script for Magic Box.
"""

import subprocess
import json
import sys

MAX_CYCLES = 3

def run_builder(task: str) -> dict:
    """Run the builder worker."""
    result = subprocess.run([
        "claude", "--prompt",
        "prompts/workers/codex/backend-builder.md",
        task
    ], capture_output=True, text=True)
    return {"output": result.stdout, "files": extract_files(result.stdout)}


def run_auditor(files: list) -> dict:
    """Run the auditor worker."""
    files_str = "\n".join(files)
    result = subprocess.run([
        "codex", "--prompt",
        "prompts/workers/codex/code-auditor.md",
        f"Audit these files:\n{files_str}"
    ], capture_output=True, text=True)
    return parse_audit_result(result.stdout)


def run_fixer(findings: list) -> dict:
    """Run the fixer worker."""
    findings_str = json.dumps(findings, indent=2)
    result = subprocess.run([
        "codex", "--prompt",
        "prompts/workers/codex/backend-builder.md",
        f"Fix these issues:\n{findings_str}"
    ], capture_output=True, text=True)
    return {"output": result.stdout, "files": extract_files(result.stdout)}


def main(task: str):
    print(f"Starting Build-Audit-Fix for: {task}")

    for cycle in range(MAX_CYCLES):
        print(f"\n=== Cycle {cycle + 1}/{MAX_CYCLES} ===")

        # Build
        print("Phase 1: Building...")
        build_result = run_builder(task)
        print(f"Built {len(build_result['files'])} files")

        # Audit
        print("Phase 2: Auditing...")
        audit_result = run_auditor(build_result['files'])

        critical_count = len(audit_result.get('critical', []))
        high_count = len(audit_result.get('high', []))

        if critical_count == 0 and high_count == 0:
            print("PASS: No critical or high issues found")
            print("\n=== Build-Audit-Fix Complete ===")
            return 0

        print(f"Found {critical_count} critical, {high_count} high issues")

        # Fix
        print("Phase 3: Fixing...")
        findings = audit_result.get('critical', []) + audit_result.get('high', [])
        fix_result = run_fixer(findings)

        # Update task for next cycle (include fixed files)
        task = f"Continue improving:\n{fix_result['output']}"

    print("\nWARNING: Max cycles reached, manual review needed")
    return 1


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Build sample API"
    sys.exit(main(task))
```

## Example Execution

```bash
# Task: Build user registration
$ ./build-audit-fix.py "Build user registration API with email validation"

=== Cycle 1/3 ===
Phase 1: Building...
Built 3 files: src/api/users.py, src/models/user.py, tests/test_users.py

Phase 2: Auditing...
Found 1 critical, 2 high issues:
- CRIT: SQL injection in user lookup
- HIGH: Password logged in plaintext
- HIGH: No input validation

Phase 3: Fixing...
Fixed 3 issues in src/api/users.py

=== Cycle 2/3 ===
Phase 1: Building...
(Using fixed code from previous cycle)

Phase 2: Auditing...
Found 0 critical, 0 high issues
2 medium issues noted for future improvement

PASS: No critical or high issues found

=== Build-Audit-Fix Complete ===
```

## Best Practices

1. **Set clear quality bars** - Define what "pass" means before starting
2. **Limit cycles** - 3 cycles max, then escalate to human
3. **Focus high-severity first** - Fix critical/high before medium/low
4. **Track iterations** - Log what was fixed in each cycle
5. **Learn from patterns** - Common issues indicate training gaps

## When to Escalate

- Max cycles reached without passing
- Architectural issues requiring redesign
- Contradictory requirements
- Security issues requiring expert review

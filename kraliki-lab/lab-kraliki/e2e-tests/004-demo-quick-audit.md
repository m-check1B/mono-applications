# E2E Test: 004 - Quick Audit Demo Flow

## Test Information

| Field | Value |
|-------|-------|
| Priority | HIGH |
| Estimated Duration | 10 minutes |
| Prerequisites | Lab by Kraliki environment, Claude CLI access |
| Location | Demo environment or customer VM |

## Objective

Verify that the Quick Audit demo (5-minute demo for technical buyers) executes correctly and produces expected output.

## Pre-conditions

1. Lab by Kraliki environment running
2. Claude CLI accessible
3. Sample code file available
4. API keys configured

## Reference

Demo script location: `/demo/scenarios/quick-audit.md`

## Test Steps

### Step 1: Environment Check

| Action | Verify demo environment is ready |
|--------|----------------------------------|
| Command | `./scripts/demo-start.sh` or equivalent |
| Expected | - Claude Code responding |
| | - mgrep semantic search running |
| | - Sample projects loaded |
| Verification | All health checks pass |

### Step 2: Load Sample Code

| Action | Display sample code file |
|--------|--------------------------|
| Command | `cat demo/sample-projects/sample-code.py` |
| Expected | Sample Python code with deliberate issues displayed |
| Verification | File contents visible |

### Step 3: Execute Audit Command

| Action | Run the Build-Audit-Fix pattern |
|--------|--------------------------------|
| Command | ```bash
claude "Audit this code using the Build-Audit-Fix pattern:

[paste code or file path]

1. Have Codex identify security, performance, and maintainability issues
2. Rank issues by severity
3. Suggest specific fixes for the top 3"
``` |
| Expected | Claude processes the request |
| Verification | Command executes without error |

### Step 4: Verify Security Issues Found

| Action | Check audit output for security issues |
|--------|---------------------------------------|
| Expected | Audit should identify: |
| | - SQL injection vulnerability |
| | - Hardcoded API key |
| | - Insecure deserialization (pickle) |
| | - Command injection via os.system |
| Verification | Review audit output |

### Step 5: Verify Performance Issues Found

| Action | Check audit output for performance issues |
|--------|------------------------------------------|
| Expected | - Nested loop inefficiency identified |
| | - Severity ranking provided |
| Verification | Review audit output |

### Step 6: Verify Fix Suggestions

| Action | Check suggested fixes |
|--------|----------------------|
| Expected | - Specific code fixes provided |
| | - Explanations for each fix |
| | - Top 3 issues addressed |
| Verification | Review fix suggestions |

### Step 7: Timing Check

| Action | Measure total execution time |
|--------|------------------------------|
| Expected | Complete audit in under 3 minutes |
| Verification | Record timestamp |

### Step 8: Output Quality

| Action | Assess output presentation |
|--------|---------------------------|
| Expected | - Issues categorized (Security, Performance, Maintainability) |
| | - Clear severity ranking |
| | - Actionable fix suggestions |
| Verification | Review output format |

## Pass Criteria

- Environment health check passes
- Audit completes without errors
- At least 3 security issues identified
- Performance issue identified
- Fix suggestions provided
- Total time under 3 minutes

## Sample Code Reference

```python
# sample-code.py - Demo file with common issues
import os
import pickle

def get_user_data(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)

    # Hardcoded secret
    api_key = "sk-1234567890abcdef"

    # Insecure deserialization
    user_prefs = pickle.loads(open('prefs.pkl', 'rb').read())

    # No input validation
    os.system(f"log_access.sh {user_id}")

    return result

def calculate_total(items):
    # Performance issue - nested loops
    total = 0
    for item in items:
        for i in range(1000):
            total += item.price * 1
    return total
```

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Claude not responding | Check API key, restart CLI |
| Incomplete output | Increase token limit |
| Wrong file path | Verify sample-code.py location |
| Timeout | Check network, API rate limits |

## Related Tests

- 005-demo-agency-website.md
- 008-vm-provisioning.md

# Demo Scenario: Quick Audit

**Duration:** 5 minutes
**Pattern:** Build-Audit-Fix (simplified)
**Target audience:** Any technical buyer (quick intro demo)

---

## Purpose

This is a fast demo for initial calls when you have limited time. Shows the core value proposition in under 5 minutes.

---

## The Demo (5 min total)

### Step 1: Setup (30 sec)

> "Let me show you Lab by Kraliki in action. I'll pick a random code file and run a quick audit."

```bash
# Use any code file - ideally something with obvious issues
cat sample-code.py
```

### Step 2: Execute (2 min)

```bash
claude "Audit this code using the Build-Audit-Fix pattern:

[paste code snippet or file path]

1. Have Codex identify security, performance, and maintainability issues
2. Rank issues by severity
3. Suggest specific fixes for the top 3"
```

### Step 3: Show Results (1 min)

Display the audit output:
- Issues found (categorized)
- Severity rankings
- Specific fix suggestions

### Step 4: Value Statement (1 min)

> "What you just saw:
> - Input: raw code
> - Output: prioritized issues with fixes
> - Time: 2 minutes
>
> Now imagine this running on every PR, every deployment, every legacy codebase you inherit.
>
> That's Lab by Kraliki."

### Step 5: Bridge to Full Demo (30 sec)

> "This is the simplest pattern. We have:
> - Parallel execution for research-heavy work
> - Multi-AI voting for complex decisions
> - Full project workflows for agencies
>
> Want to see how it would handle your specific workflows?"

---

## Sample Code for Demo

If you need a sample file with deliberate issues:

```python
# sample-code.py - Demo file with common issues

import os
import pickle

def get_user_data(user_id):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"

    # No error handling
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

Save this to `/demo/sample-projects/sample-code.py` for quick access.

---

## Tips

- Keep it fast - resist the urge to explain too much
- Let the output speak for itself
- End with a question, not a lecture
- If they want more, that's success - book the full demo

---

*Quick Audit Demo Script v1.0*

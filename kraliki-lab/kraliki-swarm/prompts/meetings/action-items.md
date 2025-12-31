---
name: action-items
description: Extract and organize action items from meeting notes
category: meetings
source: OpenAI Academy
---

# Create Action Items List

Turn meeting notes into a clear, owner-assigned task list.

## Prompt Template

```
Turn the following meeting notes into a clean task list. The tasks should be grouped by owner and include deadlines if mentioned. Notes: [paste text].
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[paste text]` | Meeting notes with tasks | Notes containing commitments and assignments |

## Example Usage

**Input:**
```
Turn the following meeting notes into a clean task list. The tasks should be grouped by owner and include deadlines if mentioned. Notes:

Sprint retro notes:
- need to improve test coverage, Sarah said she'd look into it
- deployment pipeline is slow, Mike to investigate by Friday
- docs are outdated, team agreed Lisa will update them next week
- Sarah also volunteered to set up the new linting rules
- Mike should also check the staging environment config
- unassigned: need to schedule the architecture review
```

**Output:**
```
ACTION ITEMS

SARAH:
- [ ] Investigate and improve test coverage
- [ ] Set up new linting rules

MIKE:
- [ ] Investigate deployment pipeline slowness (Due: Friday)
- [ ] Review staging environment configuration

LISA:
- [ ] Update outdated documentation (Due: Next week)

UNASSIGNED:
- [ ] Schedule architecture review meeting

---
Total: 6 action items
Assigned: 5 | Unassigned: 1
```

## When to Use

- After any meeting to capture commitments
- Converting discussion outcomes into trackable tasks
- Preparing follow-up emails with clear assignments
- Building sprint or project backlogs from meetings

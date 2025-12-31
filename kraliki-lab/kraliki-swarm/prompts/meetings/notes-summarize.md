---
name: notes-summarize
description: Summarize rough meeting notes into a structured recap
category: meetings
source: OpenAI Academy
---

# Summarize Meeting Notes

Transform informal notes into an organized, shareable summary.

## Prompt Template

```
Summarize these meeting notes into a structured recap. The notes are rough and informal. Organize them into categories: key decisions, next steps, and responsibilities. Notes: [paste text].
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[paste text]` | Raw meeting notes | Bullet points, fragments, informal notes |

## Example Usage

**Input:**
```
Summarize these meeting notes into a structured recap. The notes are rough and informal. Organize them into categories: key decisions, next steps, and responsibilities. Notes:

- talked about API versioning
- decided to go with URL path versioning (/v1/, /v2/)
- Bob mentioned we need docs
- migration plan needed
- Alice will handle the breaking changes doc
- ship v2 by end of Q1
- need to notify partners
- Carol to send partner email
- discussed deprecation timeline - 6 months for v1
```

**Output:**
```
MEETING RECAP: API Versioning Strategy

KEY DECISIONS:
- URL path versioning adopted (e.g., /v1/, /v2/)
- V2 target ship date: End of Q1
- V1 deprecation timeline: 6 months after V2 launch

NEXT STEPS:
1. Create breaking changes documentation
2. Develop migration plan for partners
3. Send notification to partners about upcoming changes
4. Update internal documentation

RESPONSIBILITIES:
- Alice: Write breaking changes documentation
- Carol: Draft and send partner notification email
- TBD: Migration plan ownership

OPEN ITEMS:
- Migration plan owner needs to be assigned
```

## When to Use

- After any meeting with informal note-taking
- Creating official records from brainstorm sessions
- Sharing meeting outcomes with absent stakeholders
- Building documentation from discussions

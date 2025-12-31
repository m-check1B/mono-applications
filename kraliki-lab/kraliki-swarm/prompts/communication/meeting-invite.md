---
name: meeting-invite
description: Draft professional calendar meeting invitations
category: communication
source: OpenAI Academy
---

# Draft Meeting Invite

Create well-structured meeting invitations with agenda, goals, and preparation notes.

## Prompt Template

```
Draft a meeting invitation for a session about [topic]. The meeting will include [attendees/roles] and should outline agenda items, goals, and preparation required. Provide the text in calendar-invite format.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[topic]` | Subject of the meeting | "Q1 planning", "product roadmap review" |
| `[attendees/roles]` | Who will attend | "engineering leads and product managers", "the sales team" |

## Example Usage

**Input:**
```
Draft a meeting invitation for a session about the new authentication system design. The meeting will include backend engineers and the security team and should outline agenda items, goals, and preparation required. Provide the text in calendar-invite format.
```

**Output:**
```
Title: Authentication System Design Review

Duration: 60 minutes

Attendees: Backend Engineering, Security Team

Agenda:
1. Current authentication flow overview (10 min)
2. Proposed OAuth2/OIDC implementation (20 min)
3. Security considerations and threat model (15 min)
4. Questions and next steps (15 min)

Goals:
- Align on authentication architecture approach
- Identify security requirements and constraints
- Define action items for implementation

Preparation:
- Review current auth documentation
- Bring questions about integration with existing services
- Security team: prepare threat model template
```

## When to Use

- Scheduling project kickoffs
- Planning design reviews
- Organizing cross-team collaboration sessions
- Setting up recurring status meetings

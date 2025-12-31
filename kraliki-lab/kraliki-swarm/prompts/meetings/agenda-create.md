---
name: agenda-create
description: Create structured meeting agendas with time estimates
category: meetings
source: OpenAI Academy
---

# Create Meeting Agenda

Build a well-organized agenda with time allocations and clear goals.

## Prompt Template

```
Create a structured agenda for a meeting about [topic]. The meeting will last [time] and include [attendees]. Break the agenda into sections with time estimates and goals for each section.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[topic]` | Subject of the meeting | "sprint planning", "quarterly review" |
| `[time]` | Meeting duration | "60 minutes", "2 hours" |
| `[attendees]` | Who will participate | "engineering and product teams", "leadership" |

## Example Usage

**Input:**
```
Create a structured agenda for a meeting about the product launch readiness review. The meeting will last 45 minutes and include engineering, marketing, and support teams. Break the agenda into sections with time estimates and goals for each section.
```

**Output:**
```
Product Launch Readiness Review
Duration: 45 minutes
Attendees: Engineering, Marketing, Support

AGENDA

1. Welcome and Context (5 min)
   Goal: Align on launch scope and timeline

2. Engineering Status (10 min)
   Goal: Confirm feature completion and known issues

3. Marketing Readiness (10 min)
   Goal: Review launch materials and campaign status

4. Support Preparation (10 min)
   Goal: Validate documentation and escalation paths

5. Risk Review (5 min)
   Goal: Identify blockers and contingency plans

6. Next Steps and Close (5 min)
   Goal: Assign action items and confirm launch/no-launch decision
```

## When to Use

- Planning recurring team meetings
- Organizing project kickoffs
- Structuring review sessions
- Preparing for important stakeholder meetings

---
name: project-update
description: Write concise project status updates for stakeholders
category: productivity
source: OpenAI Academy
---

# Write Project Update

Create clear, professional project status updates.

## Prompt Template

```
Draft a short project update for stakeholders. The project is [describe project]. Include progress made, current blockers, and next steps. Write in a professional, concise style.
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `[describe project]` | Project context and name | "the mobile app redesign", "the Q1 infrastructure migration" |

## Example Usage

**Input:**
```
Draft a short project update for stakeholders. The project is the customer portal v2 launch. Include progress made, current blockers, and next steps. Write in a professional, concise style.

Context:
- Started 6 weeks ago, target launch is in 2 weeks
- Frontend 90% complete, backend 80%
- Waiting on legal review for new terms of service
- Found performance issue in dashboard loading
- Next: complete testing, fix perf issue, get legal sign-off
```

**Output:**
```
PROJECT UPDATE: Customer Portal v2

Date: December 27, 2025
Target Launch: January 10, 2026
Status: On Track (with risks)

PROGRESS THIS WEEK:
- Frontend development 90% complete
- Backend API integration 80% complete
- User acceptance testing started with pilot group
- Authentication flow tested and verified

CURRENT BLOCKERS:

1. Legal Review Pending
   New Terms of Service awaiting legal approval
   Impact: Cannot launch without approved ToS
   Mitigation: Escalated to legal leadership; expect response by Jan 2

2. Dashboard Performance Issue
   Dashboard load time exceeds 3 seconds on large datasets
   Impact: May affect user experience at launch
   Mitigation: Identified root cause; fix in progress, ETA 3 days

NEXT STEPS (Next 2 Weeks):
- Complete backend API development (by Dec 30)
- Resolve performance issue (by Jan 2)
- Obtain legal sign-off on ToS (by Jan 3)
- Complete QA testing cycle (by Jan 7)
- Soft launch to 10% of users (Jan 8)
- Full launch (Jan 10)

RISKS:
- Medium: Legal review may take longer than expected
- Low: Additional performance issues may surface in testing

HELP NEEDED:
- Please encourage legal team prioritization of ToS review

---
Next update: January 3, 2025
Contact: [Project Manager Name]
```

## When to Use

- Weekly stakeholder updates
- Steering committee reports
- Sprint review summaries
- Status emails to leadership

# HW-020: Configure Cal.com Events

**Status:** BLOCKED (Needs Human)
**Context:** Launch Checklist Day 1
**Goal:** Enable booking for Sales and Workshops.

## Instructions
1.  Log in to `cal.com/verduona`.
2.  Create/Update the following event types:

### Event Type 1: Discovery Call (Sales)
*   **Title:** AI Strategy Diagnostic
*   **Description:** A 20-minute chat to see if your team is ready for an AI orchestration workflow. No pitch, just diagnostics.
*   **URL Slug:** `diagnostic`
*   **Duration:** 20 minutes
*   **Location:** Google Meet
*   **Questions:**
    1.  Current team size?
    2.  Top 3 AI tools you currently use?
    3.  What is your biggest operational bottleneck?

### Event Type 2: Workshop Signup (Public)
*   **Title:** Workshop: Become AI Competent
*   **Description:** 4-hour intensive training. Learn the "Lab by Kraliki" orchestration method.
*   **URL Slug:** `workshop-competence`
*   **Duration:** 240 minutes (4 hours)
*   **Price:** €149.00
*   **Location:** Zoom / In-Person (Prague)
*   **Requires Confirmation:** Yes

### Event Type 3: Consulting Kickoff (Client Only)
*   **Title:** Project Kickoff / Audit
*   **Description:** Deep dive into your technical infrastructure.
*   **URL Slug:** `kickoff`
*   **Duration:** 60 minutes
*   **Hidden:** Yes (Private Link)

## Workflow Settings
*   **Reminders:** Email 24h before, 1h before.
*   **Buffer:** 15 mins before/after calls.
*   **Availability:** Mon-Thu, 13:00 - 17:00 CET.

## Definition of Done
- [ ] Links `cal.com/verduona/diagnostic` and `cal.com/verduona/workshop-competence` are working.

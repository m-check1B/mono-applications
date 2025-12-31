# Mac Cursor Automation

**Status:** Active
**Updated:** 2025-12-30
**Method:** Cursor on Mac (no bridge)

---

## Overview

Mac-based browser execution for tasks that require real browser interaction. Linux agents do **not** run interactive browser automation. The Mac operator uses Cursor with direct `/github` repo access and executes tasks from Linear.

**Key principle:** No bridges or polling. Cursor on Mac is the single path for interactive browser work.

---

## Architecture

```
Linux Dev Server                         Mac (Cursor)
┌─────────────────────┐                 ┌─────────────────────┐
│ Linux Agent         │                 │ Cursor on Mac       │
│ Needs browser task  │                 │ (manual execution)  │
│                     │                 │                     │
│ 1. Update Linear    │ ──────────────► │ 2. Open Linear task │
│    task with        │                 │    in Cursor        │
│    clear steps      │                 │                     │
│                     │                 │ 3. Execute steps    │
│                     │                 │    in browser       │
│                     │ ◄────────────── │ 4. Report results   │
│                     │    Linear       │    in Linear        │
└─────────────────────┘                 └─────────────────────┘
```

---

## How to Request Browser Automation

### Step 1: Update Linear Task

Use Linear UI or MCP. Add a clear note and optional label:

- Label: `mac-cursor` (preferred)
- Comment: "Mac Cursor required"

### Step 2: Write Clear Instructions

Include in the description:

```markdown
## Task: [Clear objective]

### Steps
1. Navigate to [specific URL]
2. Click [specific element]
3. Verify [expected result]
4. Screenshot [what to capture]

### Context
Repo path: /home/adminmatej/github/...
Relevant files: [specific paths]

### Expected Result
[What success looks like]

### Report Back
- Screenshot of [result]
- Any errors encountered
- Time taken
```

---

## What Mac Handles vs Playwright

| Task | Use |
|------|-----|
| Page loads, HTTP errors | Playwright (Linux, headless) |
| Form validation | Playwright (Linux, headless) |
| API responses | Playwright (Linux, headless) |
| Console errors | Playwright (Linux, headless) |
| **OAuth/Social login** | Mac Cursor |
| **Payment flows** | Mac Cursor |
| **Account creation** | Mac Cursor |
| **DNS/registrar changes** | Mac Cursor |
| **Visual regression** | Mac Cursor |
| **CAPTCHA handling** | Mac Cursor |

---

## Beta Apps

| App | URL |
|-----|-----|
| Focus by Kraliki | focus.verduona.dev |
| Voice by Kraliki | voice.verduona.dev |
| Speak by Kraliki | speak.verduona.dev |
| Learn by Kraliki | learn.verduona.dev |
| Lab by Kraliki | lab.verduona.dev |
| Kraliki Swarm | kraliki.verduona.dev |

---

## DO NOT

- **DO NOT** run interactive browser automation on Linux
- **DO NOT** rely on any Mac bridge or polling
- **DO NOT** assume Mac has credentials - put instructions in the task

---

## Escalation

If Mac execution is blocked:
1. Update Linear issue status to "Blocked"
2. Add comment explaining the blocker
3. Add `human-blocked` label

---

*Part of Kraliki Swarm Infrastructure*
*Last updated: 2025-12-30*

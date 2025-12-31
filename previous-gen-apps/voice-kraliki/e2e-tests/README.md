# CC-Lite 2026 - E2E Test Plans

Manual E2E test plans for the AI Call Center platform.

**Public URL:** https://voice.verduona.dev
**Local URL:** http://127.0.0.1:3000

## Test Execution

These tests are designed for manual execution via Claude Code Chrome extension.
The user watches via RDP from Mac and pastes test instructions into the Chrome extension.

## Test List

| ID | Test Name | Priority | Status |
|----|-----------|----------|--------|
| 001 | Homepage Load | Critical | Pending |
| 002 | Auth Login Flow | Critical | Pending |
| 003 | Auth Registration Flow | High | Pending |
| 004 | Dashboard Overview | Critical | Pending |
| 005 | Supervisor Dashboard | High | Pending |
| 006 | Agent Workspace | High | Pending |
| 007 | Campaigns Page | Medium | Pending |
| 008 | Teams Management | Medium | Pending |
| 009 | IVR Operations | Medium | Pending |
| 010 | Analytics Page | Medium | Pending |

## Directory Structure

```
e2e-tests/
  README.md           # This file
  001-homepage-load.md
  002-auth-login.md
  003-auth-register.md
  004-dashboard-overview.md
  005-supervisor-dashboard.md
  006-agent-workspace.md
  007-campaigns.md
  008-teams-management.md
  009-ivr-operations.md
  010-analytics.md
  results/            # Test execution results
```

## Test Credentials

- **Email:** testuser@example.com
- **Password:** test123

## How to Run Tests

1. CLI Agent creates test plans (this folder)
2. Human pastes test into Chrome extension
3. Browser Agent executes tests
4. Results saved to `results/` folder
5. CLI Agent picks up results via `/e2e-results-pickup`

## Key Routes Tested

- `/` - Homepage/Landing
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/supervisor/dashboard` - Supervisor view
- `/calls/agent` - Agent workspace
- `/campaigns` - Campaign management
- `/teams` - Team management
- `/operations/ivr` - IVR flow management
- `/analytics` - Analytics dashboard

---

Last updated: 2025-12-25

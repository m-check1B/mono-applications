# Speak by Kraliki - E2E Test Plans

Manual E2E test plans for browser-based visual testing.

**Public URL:** https://speak.verduona.dev

## Test Execution

These tests are designed for the Chrome browser extension to execute:

1. CLI Agent creates test plans (this folder)
2. Human pastes tests into Chrome extension
3. Browser Agent executes and writes results to `results/`
4. CLI Agent picks up results and creates Linear issues for failures

## Test Files

| File | Feature | Priority |
|------|---------|----------|
| 001-homepage.md | Landing page, navigation, responsive design | HIGH |
| 002-authentication.md | Login, register, logout flows | HIGH |
| 003-employee-feedback.md | Voice/text feedback submission flow | CRITICAL |
| 004-dashboard-overview.md | Dashboard metrics, alerts, actions | HIGH |
| 005-survey-management.md | Create, launch, pause surveys | HIGH |
| 006-transcript-review.md | Transcript viewing and trust layer | MEDIUM |

## Results Folder

Test results are written to `results/` with format:
- `YYYY-MM-DD_NNN-testname_PASSED.md` - Test passed
- `YYYY-MM-DD_NNN-testname_FAILED.md` - Test failed with details

## Test Status Legend

- CRITICAL: Must pass for app to be usable
- HIGH: Core functionality, should pass
- MEDIUM: Important but not blocking
- LOW: Nice to have

---

Last updated: 2025-12-25

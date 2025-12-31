# Kraliki E2E Tests

**Base URL:** https://beta.kraliki.com

## How to Run

1. Open Chrome extension (Claude Code) on server
2. Paste the test file contents into the extension
3. Watch execution via RDP
4. Report results back

## Test Files

| # | Test | Page | Purpose |
|---|------|------|---------|
| 001 | CLI Toggle | /agents | Verify CODEX toggle only affects CODEX |
| 002 | Send to Linear | /comms | Verify Linear issue creation |
| 003 | Memory Inactive | /memory | Verify inactive agents detection |
| 004 | Brain Page | /brain | Verify CEO dashboard loads |
| 005 | Human Blockers | /jobs | Verify jobs and blockers display |
| 006 | Agents Page | /agents | Verify management sections visibility |

## Quick Test Command

For Chrome extension, paste:
```
Run all E2E tests from /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/e2e-tests/
Start with 001, then 002, etc.
Report PASS/FAIL for each.
```

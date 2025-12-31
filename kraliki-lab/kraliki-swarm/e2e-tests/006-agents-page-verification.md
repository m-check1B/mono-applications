# E2E Test: Agents Page Verification (Beta)

**URL:** https://beta.kraliki.com/agents
**Purpose:** Verify the Agents page loads correctly and all management sections are visible.

## Steps

1. Navigate to https://beta.kraliki.com/agents

2. Verify the page header:
   - Check for text: "Agent Management // Swarm Control"
   - Verify control buttons are present: REFRESH, PAUSE_ALL, KILL_STALE, HARD_RESET

3. Verify the CLI_POLICY_CONTROL section:
   - Check for "CLI_POLICY_CONTROL // SPAWN_AUTHORIZATION" heading
   - Verify CLI items like OPENCODE, GEMINI, CODEX, CLAUDE are visible and show "ONLINE" status

4. Verify CLI_HEALTH section:
   - Check for "CLI_HEALTH // ALL_OK" heading
   - Verify circuit breakers for LINEAR, CLAUDE, CODEX, GEMINI, OPENCODE are shown as "CLOSED"

5. Verify AGENT_LAUNCHER section:
   - Check for "AGENT_LAUNCHER // GENOME_WATCHDOG" heading
   - Verify genome units like OPENCODE_UNIT, GEMINI_UNIT, CODEX_UNIT, CLAUDE_UNIT are visible
   - Verify genomes like ORCHESTRATOR, BIZ_DISCOVERY, etc. are listed with checkboxes and SPAWN buttons

6. Verify ACTIVE_AGENT_FEED section:
   - Check for "ACTIVE_AGENT_FEED // SECTOR_01" heading
   - Verify the table headers: Agent ID, Genome, CLI, Status, PID, Start, Duration, Points
   - Note if any agents (like OC-orchestrator) are currently "running" or "completed"

7. Take a screenshot of the full page.

## Expected Result
- PASS: All sections (Header, CLI Policy, CLI Health, Launcher, Agent Feed) are visible and populated with data.
- FAIL: Any section is missing, or the page fails to load (e.g., stuck on "INQUIRY_INTO_SWARM_STATE" or showing "Internal Error").

## Report Back
Tell me: PASS or FAIL with details of what was observed.

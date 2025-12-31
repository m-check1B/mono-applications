# E2E Test: CLI Toggle - CODEX

**URL:** https://beta.kraliki.com/agents
**Purpose:** Verify CLI toggle only affects the selected CLI

## Steps

1. Navigate to https://beta.kraliki.com/agents

2. In the CLI_POLICY_CONTROL section, note the current state of all 4 CLIs:
   - OPENCODE: [ONLINE/OFFLINE]
   - GEMINI: [ONLINE/OFFLINE]
   - CODEX: [ONLINE/OFFLINE]
   - CLAUDE: [ONLINE/OFFLINE]

3. Click the DISABLE button for CODEX

4. Verify the result:
   - CODEX should now show OFFLINE
   - OPENCODE should remain unchanged
   - GEMINI should remain unchanged
   - CLAUDE should remain unchanged

5. Take a screenshot

## Expected Result
- PASS: Only CODEX changed to OFFLINE
- FAIL: Other CLIs were affected

## Report Back
Tell me: PASS or FAIL with details

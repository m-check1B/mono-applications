# E2E Test: Memory Page - Inactive Agents Detection

**URL:** https://beta.kraliki.com/memory
**Purpose:** Verify inactive agents warning displays

## Steps

1. Navigate to https://beta.kraliki.com/memory

2. Check the stats grid at top:
   - STORES count
   - RETRIEVES count
   - ACTIVE_AGENTS count
   - INACTIVE_AGENTS count (should show if any)

3. If INACTIVE_AGENTS > 0, check for red warning section:
   - Should show "MEMORY_WARNING // X AGENTS NOT USING MEMORY"
   - Should list agent names

4. Check "MEMORY_USAGE // BY_AGENT" section shows per-agent stats

5. Take a screenshot

## Expected Result
- PASS: Page loads, stats display, inactive agents shown if any
- FAIL: Page errors or missing sections

## Report Back
Tell me: PASS or FAIL, and what stats you see

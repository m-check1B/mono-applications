# E2E Test: Jobs Page - Human Blockers

**URL:** https://beta.kraliki.com/jobs
**Purpose:** Verify Jobs page shows Linear issues and Human Blockers

## Steps

1. Navigate to https://beta.kraliki.com/jobs

2. Check for Linear issues section:
   - Should show VD-XXX issues
   - Priority indicators
   - Status badges

3. Check for Human Blockers section:
   - Should show items from humans-work-needed queue
   - Or "No blockers" message

4. Take a screenshot

## Expected Result
- PASS: Both sections visible, data loads
- FAIL: Error or missing sections

## Report Back
Tell me: PASS or FAIL, how many issues/blockers shown

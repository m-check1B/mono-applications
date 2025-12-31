# E2E Test: Send to Linear (Comms Page)

**URL:** https://beta.kraliki.com/comms
**Purpose:** Verify "Create Linear Issue" form works

## Steps

1. Navigate to https://beta.kraliki.com/comms

2. Find the "CREATE LINEAR ISSUE" section

3. Fill in the form:
   - Title: "E2E Test Issue - Delete Me"
   - Description: "This is an automated E2E test"
   - Priority: 3 (Medium)
   - Label: feature

4. Click CREATE_ISSUE button

5. Check for success message

6. Take a screenshot

## Expected Result
- PASS: Success message appears, issue created
- FAIL: Error message or no response

## Report Back
Tell me: PASS or FAIL with the response message

# Test 005: Survey Management

**Priority:** HIGH
**URL:** https://speak.verduona.dev/dashboard/surveys

## Preconditions

- Browser is open
- User is authenticated as company admin
- Access to dashboard

## Test Steps

### Step 1: Access Survey List

1. Navigate to https://speak.verduona.dev/dashboard/surveys
2. Wait for page to load

**Expected:**
- Page title "SURVEYS" is visible
- "< Dashboard" back link is present
- "CREATE SURVEY" button is visible
- Survey list or empty state message

### Step 2: Empty State

1. If no surveys exist, observe the empty state

**Expected:**
- Message: "You don't have any surveys yet" (or Czech equivalent)
- "CREATE SURVEY" button in the empty state area

### Step 3: Open Create Survey Modal

1. Click "CREATE SURVEY" button

**Expected:**
- Modal dialog opens
- Modal has X close button
- Form fields are visible

### Step 4: Verify Survey Form Fields

1. Check the create survey form

**Expected:**
- Survey name input (required)
- Description textarea
- Frequency dropdown (once, weekly, monthly, quarterly)
- Questions section with at least one question input
- "ADD QUESTION" button
- Cancel and Create buttons at bottom

### Step 5: Form Validation

1. Leave name field empty
2. Click Create button

**Expected:**
- Form validation error on name field
- Survey is not created

### Step 6: Add Questions

1. Fill in survey name: "Test Survey"
2. Fill in first question: "How are you feeling today?"
3. Click "ADD QUESTION" button

**Expected:**
- New question input field appears
- Delete (X) button appears on each question (when more than one)

### Step 7: Remove Question

1. Click X button on the second question

**Expected:**
- Question is removed from list
- Only first question remains

### Step 8: Create Survey

1. Ensure name and at least one question are filled
2. Select frequency: "Monthly"
3. Click Create button

**Expected:**
- Modal closes
- New survey appears in the list
- Survey shows status "DRAFT"

### Step 9: View Survey in List

1. Find the newly created survey

**Expected:**
- Survey name is displayed
- Status badge shows "DRAFT"
- Frequency label shows "Monthly"
- Question count is visible
- "LAUNCH" and "STATS" buttons are present

### Step 10: Launch Survey

1. Click "LAUNCH" button on the draft survey

**Expected:**
- Survey status changes to "ACTIVE"
- Launch button changes to "PAUSE" button

### Step 11: Pause Survey

1. Click "PAUSE" button on the active survey

**Expected:**
- Survey status changes to "PAUSED"
- Pause button changes back to "LAUNCH" button

### Step 12: View Survey Stats

1. Click "STATS" button on any survey

**Expected:**
- Navigation to survey detail page (/dashboard/surveys/[id])
- Survey statistics are displayed

### Step 13: Close Modal

1. Navigate back to /dashboard/surveys
2. Open create modal
3. Click X button or Cancel button

**Expected:**
- Modal closes
- Survey list is visible again

## Success Criteria

- Survey CRUD operations work
- Form validation prevents invalid submissions
- Status changes work correctly (draft -> active -> paused)
- Navigation between survey list and details works

## Notes

- Survey creation requires at least name and one question
- Frequency options: once, weekly, monthly, quarterly
- Status flow: draft -> active/paused -> completed

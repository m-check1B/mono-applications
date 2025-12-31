# Test 004: Dashboard Overview

**Priority:** HIGH
**URL:** https://speak.verduona.dev/dashboard

## Preconditions

- Browser is open
- User must be authenticated (logged in as company admin)
- At least one survey with responses exists (for full testing)

## Test Steps

### Step 1: Access Dashboard (Unauthenticated)

1. Open a new incognito/private browser window
2. Navigate to https://speak.verduona.dev/dashboard

**Expected:**
- User is redirected to /login
- Login form is displayed

### Step 2: Dashboard Layout (Authenticated)

1. Log in with valid credentials
2. Navigate to /dashboard
3. Wait for data to load

**Expected:**
- "Speak INTELLIGENCE" header is visible
- "Status: Live_Stream" indicator is present
- Loading indicator appears, then content loads
- "NEW_CAMPAIGN" button is visible

### Step 3: Verify Key Metrics Cards

1. Observe the four metric cards at the top

**Expected:**
- Sentiment card: Shows current sentiment (POSITIVE/NEUTRAL/NEGATIVE)
- Participation card: Shows percentage and count
- Active Alerts card: Shows alert count
- Pending Actions card: Shows action count
- All cards have hover effects (translate on hover)

### Step 4: Verify Topics Section

1. Find the "SIGNAL_CLUSTERS" section (left column)

**Expected:**
- Topic list or "NO_SIGNALS_MAPPED" message
- If topics exist: bar chart visualization
- Sentiment indicator per topic

### Step 5: Verify Alerts Section

1. Find the "LIVE_ALERT_STREAM" section

**Expected:**
- Recent alerts list or "ALL_SYSTEMS_OPTIMAL" message
- Alert type and timestamp visible
- "FULL_LOGS" link to /dashboard/alerts

### Step 6: Verify Actions Section

1. Find the "EXECUTION_TIMELINE" section at bottom

**Expected:**
- Action cards grid or "LOOP_STABLE: NO_PENDING_EXECUTIONS" message
- Status labels on each action
- "SYNC_NOW" button to manage actions

### Step 7: Navigate to Surveys

1. Click "NEW_CAMPAIGN" button

**Expected:**
- Browser navigates to /dashboard/surveys
- Surveys list or create survey interface loads

### Step 8: Navigate to Alerts

1. Navigate back to /dashboard
2. Click on "[VIEW_INCIDENTS]" link

**Expected:**
- Browser navigates to /dashboard/alerts
- Alerts management interface loads

### Step 9: Navigate to Actions

1. Navigate back to /dashboard
2. Click on "[MANAGE_LOOP]" link

**Expected:**
- Browser navigates to /dashboard/actions
- Actions management interface loads

## Success Criteria

- Dashboard loads without errors when authenticated
- Unauthenticated access redirects to login
- All four metric cards display correctly
- Navigation to sub-pages works
- Data loads and displays (or shows empty state messages)

## Notes

- If no data exists, dashboard shows appropriate empty states
- Dashboard design follows Modern Brutalism (terminal green, sharp edges)
- All text is uppercase per design system

# E2E Test 004: Dashboard Overview

**Priority:** Critical
**Route:** `/dashboard`
**URL:** https://voice.verduona.dev/dashboard

## Objective

Verify the main dashboard loads correctly after authentication and displays key metrics.

## Prerequisites

- Logged in as testuser@example.com
- Valid session token

## Test Steps

### Test A: Dashboard Load After Login

```
1. Navigate to https://voice.verduona.dev/auth/login
2. Login with testuser@example.com / test123
3. Wait for redirect to /dashboard
4. Verify dashboard page loads with:
   - Page title "Operator Console Overview"
   - System status indicator
   - Main metrics cards
5. Take a screenshot
```

### Test B: Dashboard Metrics Display

```
1. After login, on /dashboard page
2. Verify the following metric tiles are visible:
   - Total Companies count
   - Active Campaigns count
   - Calls Today count
   - Success Rate percentage
3. Check system status shows "healthy" or equivalent
4. Take a screenshot of the metrics section
```

### Test C: Dashboard Action Buttons

```
1. On the dashboard page
2. Locate "Start Outbound Session" button
3. Locate "Manage Incoming" button
4. Verify both buttons are clickable
5. Click "Start Outbound Session"
6. Verify navigation to /calls/outbound
7. Take a screenshot
```

### Test D: System Information Section

```
1. On the dashboard page
2. Scroll to system information section
3. Verify display of:
   - System Status (healthy/error)
   - Backend URL
   - WebSocket URL
   - Last Updated timestamp
4. Take a screenshot
```

## Expected Results

### Test A
- [ ] Dashboard loads after successful login
- [ ] Page title is correct
- [ ] No authentication errors

### Test B
- [ ] All 4 metric tiles visible
- [ ] Metrics show actual values (not loading)
- [ ] System status is "healthy"

### Test C
- [ ] Both action buttons visible
- [ ] Buttons are clickable and styled correctly
- [ ] Navigation works correctly

### Test D
- [ ] System information section visible
- [ ] All info fields populated
- [ ] Timestamp is recent

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Enter email: testuser@example.com
Enter password: test123
Click Sign in button
Wait for dashboard to load
Take a screenshot
Report what metrics and buttons you see on the dashboard
Check if "System Status" shows "healthy"
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

# E2E Test 005: Supervisor Dashboard

**Priority:** High
**Route:** `/supervisor/dashboard`
**URL:** https://voice.verduona.dev/supervisor/dashboard

## Objective

Verify the supervisor dashboard provides real-time team monitoring capabilities.

## Prerequisites

- Logged in as testuser@example.com
- Valid session token

## Test Steps

### Test A: Supervisor Dashboard Access

```
1. Login at https://voice.verduona.dev/auth/login
2. Navigate to https://voice.verduona.dev/supervisor/dashboard
3. Verify page loads without access errors
4. Check for supervisor-specific UI elements
5. Take a screenshot
```

### Test B: Team Monitoring Display

```
1. On supervisor dashboard
2. Look for:
   - Agent status overview (available, busy, offline)
   - Queue status information
   - Active calls list
   - Performance metrics
3. Take a screenshot showing team monitoring widgets
```

### Test C: Navigation to Sub-pages

```
1. On supervisor dashboard
2. Find navigation to:
   - Active Calls (/supervisor/active-calls)
   - Queue Management (/supervisor/queue)
3. Click on Active Calls link
4. Verify page loads
5. Take a screenshot
```

## Expected Results

### Test A
- [ ] Page loads successfully
- [ ] No 401/403 authentication errors
- [ ] Supervisor-specific layout visible

### Test B
- [ ] Team status widgets displayed
- [ ] Data loads (or shows "no data" gracefully)
- [ ] Real-time updates working (if applicable)

### Test C
- [ ] Sub-navigation works
- [ ] Related supervisor pages accessible
- [ ] Consistent UI across supervisor section

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Login with testuser@example.com / test123
Navigate to https://voice.verduona.dev/supervisor/dashboard
Take a screenshot
Report what supervisor monitoring features you see
List any navigation links to other supervisor pages
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

# E2E Test 007: Campaigns Page

**Priority:** Medium
**Route:** `/campaigns`
**URL:** https://voice.verduona.dev/campaigns

## Objective

Verify the campaigns management page loads and displays campaign data correctly.

## Prerequisites

- Logged in as testuser@example.com
- Valid session token

## Test Steps

### Test A: Campaigns Page Load

```
1. Login at https://voice.verduona.dev/auth/login
2. Navigate to https://voice.verduona.dev/campaigns
3. Verify page loads with:
   - Page title/header for campaigns
   - Campaign list or table
   - Action buttons (Create, Filter, etc.)
4. Take a screenshot
```

### Test B: Campaign List Display

```
1. On campaigns page
2. Check if campaigns are listed with:
   - Campaign name
   - Status (active, paused, etc.)
   - Date/time information
   - Contact count
3. If no campaigns, verify "empty state" message
4. Take a screenshot
```

### Test C: Campaign Actions

```
1. On campaigns page
2. Look for action buttons:
   - Create New Campaign
   - Edit campaign (on existing items)
   - Start/Pause campaign
   - Delete campaign
3. Note which actions are available
4. Take a screenshot showing available actions
```

## Expected Results

### Test A
- [ ] Page loads successfully
- [ ] Proper header/navigation visible
- [ ] Campaign management UI displayed

### Test B
- [ ] Campaign list or empty state shown
- [ ] Campaign data formatted correctly
- [ ] Status indicators clear

### Test C
- [ ] CRUD actions available
- [ ] Buttons properly styled
- [ ] Actions are accessible

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Login with testuser@example.com / test123
Navigate to https://voice.verduona.dev/campaigns
Take a screenshot
Report:
- How many campaigns are listed?
- What actions/buttons are available?
- What information is shown for each campaign?
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

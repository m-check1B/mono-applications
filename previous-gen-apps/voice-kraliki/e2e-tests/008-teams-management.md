# E2E Test 008: Teams Management

**Priority:** Medium
**Route:** `/teams`
**URL:** https://voice.verduona.dev/teams

## Objective

Verify the teams management page allows viewing and managing agent teams.

## Prerequisites

- Logged in as testuser@example.com
- Valid session token

## Test Steps

### Test A: Teams Page Load

```
1. Login at https://voice.verduona.dev/auth/login
2. Navigate to https://voice.verduona.dev/teams
3. Verify page loads with:
   - Teams list or grid view
   - Team cards with member counts
   - Create Team button
4. Take a screenshot
```

### Test B: Team Details

```
1. On teams page
2. Click on a team card (if teams exist)
3. Verify team details page shows:
   - Team name and description
   - Team members list
   - Team performance metrics (if available)
4. Take a screenshot of team details
```

### Test C: Create New Team

```
1. On teams page
2. Click "Create Team" or "New Team" button
3. Verify form appears with:
   - Team name field
   - Description field
   - Save/Cancel buttons
4. Take a screenshot of the form
5. Click Cancel to return without creating
```

### Test D: Agents Sub-page

```
1. Navigate to https://voice.verduona.dev/agents
2. Verify agents listing page loads
3. Check for agent profile cards
4. Take a screenshot
```

## Expected Results

### Test A
- [ ] Teams page loads successfully
- [ ] Teams displayed (or empty state)
- [ ] Create button available

### Test B
- [ ] Team details accessible
- [ ] Member information visible
- [ ] Navigation works correctly

### Test C
- [ ] Create form displays
- [ ] Form fields present
- [ ] Cancel works without saving

### Test D
- [ ] Agents page accessible
- [ ] Agent profiles displayed
- [ ] Navigation consistent

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Login with testuser@example.com / test123
Navigate to https://voice.verduona.dev/teams
Take a screenshot
Report:
- How many teams are listed?
- Is there a Create Team button?
- What information is shown for each team?
Then navigate to https://voice.verduona.dev/agents
Take a screenshot
Report what agent information is displayed
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

# Test 007: Quick Action Buttons (FABs)

**Priority:** P1 (High)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify all floating action buttons open their respective context panels.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Tasks Button

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Locate the Tasks button (CheckSquare icon) in bottom-right FABs
3. Click the Tasks button

**Expected Results:**
- [ ] Tasks button is visible with CheckSquare icon
- [ ] Tooltip shows "Tasks (Ctrl+T)" on hover
- [ ] Clicking opens the Tasks context panel
- [ ] Panel slides in from the side
- [ ] Tasks list or empty state is displayed

### Scenario B: Knowledge Button

1. Click the Knowledge button (Book icon)

**Expected Results:**
- [ ] Knowledge button is visible with Book icon
- [ ] Clicking opens the Knowledge context panel
- [ ] Knowledge items or empty state is displayed

### Scenario C: Calendar Button

1. Click the Calendar button (Calendar icon)

**Expected Results:**
- [ ] Calendar button is visible with Calendar icon
- [ ] Tooltip shows "Calendar (Ctrl+C)" on hover
- [ ] Clicking opens the Calendar context panel
- [ ] Calendar view or events are displayed

### Scenario D: Timer/Pomodoro Button

1. Click the Timer button (Timer icon, accent colored)

**Expected Results:**
- [ ] Timer button is visible with Timer icon
- [ ] Button has accent background color (stands out)
- [ ] Tooltip shows "Focus Protocol"
- [ ] Clicking opens the Pomodoro/Timer panel
- [ ] Timer controls are visible

### Scenario E: Settings Button

1. Click the Settings button (Settings icon, slightly muted)

**Expected Results:**
- [ ] Settings button is visible with Settings/gear icon
- [ ] Tooltip shows "Settings (Ctrl+,)"
- [ ] Button has opacity-60 styling (less prominent)
- [ ] Clicking opens the Settings context panel
- [ ] Settings options are displayed

## Panel Behavior

### Scenario F: Close Panel

1. Open any panel (e.g., Tasks)
2. Click outside the panel OR click close button

**Expected Results:**
- [ ] Panel slides out / closes
- [ ] Dashboard returns to normal state
- [ ] Can reopen same or different panel

### Scenario G: Switch Panels

1. Open Tasks panel
2. Click Knowledge button

**Expected Results:**
- [ ] Tasks panel closes
- [ ] Knowledge panel opens
- [ ] Smooth transition between panels

## Keyboard Shortcuts

### Scenario H: Keyboard Navigation

1. Press `Ctrl+T` (or Cmd+T on Mac)
2. Press `Ctrl+C` (or Cmd+C)
3. Press `Ctrl+,` (or Cmd+,)

**Expected Results:**
- [ ] Ctrl+T opens Tasks panel
- [ ] Ctrl+C opens Calendar panel
- [ ] Ctrl+, opens Settings panel

## FAB Button Reference

| Button | Icon | Tooltip | Shortcut | Panel |
|--------|------|---------|----------|-------|
| Tasks | CheckSquare | Tasks (Ctrl+T) | Ctrl+T | tasks |
| Knowledge | Book | Knowledge | - | knowledge |
| Calendar | Calendar | Calendar (Ctrl+C) | Ctrl+C | calendar |
| Timer | Timer | Focus Protocol | - | pomodoro |
| Settings | Settings | Settings (Ctrl+,) | Ctrl+, | settings |

## Pass Criteria

- All 5 FABs are visible and clickable
- Each FAB opens correct context panel
- Panels can be closed
- Keyboard shortcuts work

## Screenshots Required

1. FABs visible on dashboard
2. Tasks panel open
3. Timer panel open
4. Settings panel open

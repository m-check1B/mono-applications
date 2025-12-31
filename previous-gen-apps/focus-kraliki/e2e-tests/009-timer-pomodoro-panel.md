# Test 009: Timer / Pomodoro Panel

**Priority:** P1 (High)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify the Timer/Pomodoro context panel displays and functions correctly.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Open Timer Panel

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Click Timer FAB button (accent colored, Timer icon)

**Expected Results:**
- [ ] Timer panel slides in from the side
- [ ] Panel header shows "Timer", "Pomodoro", or "Focus Protocol"
- [ ] Close button is available
- [ ] Timer display is visible

### Scenario B: Timer Initial State

1. Open Timer panel

**Expected Results:**
- [ ] Timer shows initial time (e.g., 25:00 for Pomodoro)
- [ ] Start/Play button is visible
- [ ] Timer is not running
- [ ] Session type indicator (Focus, Break) may be visible

### Scenario C: Start Timer

1. Open Timer panel
2. Click Start/Play button

**Expected Results:**
- [ ] Timer begins counting down
- [ ] Display updates every second
- [ ] Start button changes to Pause
- [ ] Visual indication that timer is active

### Scenario D: Pause Timer

1. With timer running, click Pause button

**Expected Results:**
- [ ] Timer pauses at current time
- [ ] Display stops updating
- [ ] Pause button changes to Resume/Play
- [ ] Can resume from paused time

### Scenario E: Reset Timer

1. With timer running or paused
2. Click Reset button

**Expected Results:**
- [ ] Timer resets to initial time
- [ ] Timer is stopped
- [ ] Can start fresh session

### Scenario F: Timer Controls

1. Look for timer configuration options

**Expected Results:**
- [ ] Work duration setting (e.g., 25 min default)
- [ ] Break duration setting (e.g., 5 min default)
- [ ] Long break setting (e.g., 15 min)
- [ ] Settings are adjustable

### Scenario G: Timer Completion

1. Set a very short timer (if possible) or wait
2. Let timer complete

**Expected Results:**
- [ ] Notification/sound when timer ends
- [ ] Visual indication of completion
- [ ] Prompt for next session (break or work)
- [ ] Session history may update

## Timer Types (if Pomodoro)

| Type | Duration | After |
|------|----------|-------|
| Focus/Work | 25 min | Short Break |
| Short Break | 5 min | Focus |
| Long Break | 15 min | Focus (after 4 sessions) |

## Deep Link

### Scenario H: Direct URL

1. Navigate directly to: `https://focus.verduona.dev/dashboard/time`

**Expected Results:**
- [ ] Redirects to dashboard
- [ ] Timer panel opens automatically
- [ ] Uses PanelRedirect component

## AI Integration

### Scenario I: Start Timer via Voice/AI

1. Close Timer panel
2. Type in AI: `start timer` or `start focus session`

**Expected Results:**
- [ ] AI recognizes intent
- [ ] Timer panel opens
- [ ] Timer may start automatically

## Pass Criteria

- Timer panel opens correctly
- Can start, pause, and reset timer
- Timer counts down correctly
- Deep link works

## Screenshots Required

1. Timer panel initial state
2. Timer running
3. Timer paused
4. Timer controls/settings

# Test 013: Dark Mode Toggle

**Priority:** P2 (Medium)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 3 minutes

## Objective

Verify dark mode toggle works correctly and styling adapts properly.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Access Theme Settings

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Open Settings panel (click Settings FAB or Ctrl+,)
3. Find theme/appearance section

**Expected Results:**
- [ ] Theme toggle is visible
- [ ] Current mode is indicated
- [ ] Options: Light, Dark, System

### Scenario B: Light Mode

1. Select Light mode

**Expected Results:**
- [ ] Background is light/white
- [ ] Text is dark/black
- [ ] Borders are black (2px)
- [ ] Shadows are black (4px offset)
- [ ] Cards have white background
- [ ] Brutalist styling with black accents

### Scenario C: Dark Mode

1. Select Dark mode

**Expected Results:**
- [ ] Background is dark (5% gray)
- [ ] Text is light/white
- [ ] Borders are white (2px)
- [ ] Shadows are white (4px offset)
- [ ] Cards have dark background
- [ ] Brutalist styling with white accents

### Scenario D: System Mode

1. Select System mode
2. Note system preference

**Expected Results:**
- [ ] Mode follows OS/browser preference
- [ ] Matches system dark/light setting
- [ ] Changes if system preference changes

### Scenario E: Mode Persistence

1. Set to Dark mode
2. Refresh the page

**Expected Results:**
- [ ] Dark mode persists after refresh
- [ ] No flash of light mode on load
- [ ] Setting is remembered

3. Close browser and reopen

**Expected Results:**
- [ ] Dark mode still active
- [ ] Setting stored in localStorage

### Scenario F: All Pages Dark Mode

1. Set Dark mode
2. Navigate to various pages:
   - Dashboard
   - Login page
   - Registration page
   - Onboarding page

**Expected Results:**
- [ ] Dark mode applies consistently
- [ ] All pages use dark theme
- [ ] No styling inconsistencies

## CSS Variables Check

In Dark mode, verify these CSS custom properties:
- `--background`: Dark color
- `--foreground`: Light color
- `--border`: 2px white
- Shadows: White offset shadows

## Brutalist Dark Mode Specifics

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Background | White | 5% Gray |
| Text | Black | White |
| Borders | 2px Black | 2px White |
| Card Shadow | 4px Black | 4px White |
| Button Shadow | 2px Black | 2px White |
| Accent | Neon colors | Neon colors (same) |

## Pass Criteria

- Can switch between light/dark/system
- Styling adapts correctly
- Mode persists across sessions
- All pages support dark mode

## Screenshots Required

1. Light mode dashboard
2. Dark mode dashboard
3. Theme toggle in settings
4. Login page in dark mode

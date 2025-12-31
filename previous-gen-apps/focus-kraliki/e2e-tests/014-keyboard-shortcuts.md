# Test 014: Keyboard Shortcuts

**Priority:** P2 (Medium)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify all keyboard shortcuts work correctly.

## Preconditions

- User is logged in
- On the dashboard page
- No input field focused

## Test Steps

### Scenario A: Tasks Panel (Ctrl+T)

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Ensure no input is focused
3. Press Ctrl+T (or Cmd+T on Mac)

**Expected Results:**
- [ ] Tasks panel opens
- [ ] Same as clicking Tasks FAB
- [ ] Panel slides in from side

### Scenario B: Projects Panel (Ctrl+P)

1. Ensure no input is focused
2. Press Ctrl+P (or Cmd+P on Mac)

**Expected Results:**
- [ ] Projects panel opens
- [ ] Panel displays project content

### Scenario C: Calendar Panel (Ctrl+C)

1. Ensure no input is focused
2. Press Ctrl+C (or Cmd+C on Mac)

**Expected Results:**
- [ ] Calendar panel opens
- [ ] Calendar view is displayed

### Scenario D: Settings Panel (Ctrl+,)

1. Ensure no input is focused
2. Press Ctrl+, (or Cmd+, on Mac)

**Expected Results:**
- [ ] Settings panel opens
- [ ] Settings options are displayed

### Scenario E: Time Panel (Ctrl+E)

1. Ensure no input is focused
2. Press Ctrl+E (or Cmd+E on Mac)

**Expected Results:**
- [ ] Time/Timer panel opens
- [ ] Timer controls are displayed

### Scenario F: Infra Panel (Ctrl+I)

1. Ensure no input is focused
2. Press Ctrl+I (or Cmd+I on Mac)

**Expected Results:**
- [ ] Infrastructure panel opens
- [ ] Infra information is displayed

### Scenario G: Command Palette (Ctrl+K)

1. Ensure no input is focused
2. Press Ctrl+K (or Cmd+K on Mac)

**Expected Results:**
- [ ] Command palette opens
- [ ] Search/command input visible
- [ ] Can type commands or search

### Scenario H: Shortcut While Input Focused

1. Focus the AI input field
2. Press Ctrl+T

**Expected Results:**
- [ ] Shortcut may be suppressed
- [ ] Normal browser behavior OR
- [ ] Shortcut still works (implementation dependent)

### Scenario I: Close Panel with Escape

1. Open any panel (e.g., Tasks)
2. Press Escape key

**Expected Results:**
- [ ] Panel closes (if implemented)
- [ ] Returns to main dashboard view

## Keyboard Shortcuts Reference

| Shortcut | Panel/Action |
|----------|--------------|
| Ctrl+T | Tasks |
| Ctrl+P | Projects |
| Ctrl+C | Calendar |
| Ctrl+, | Settings |
| Ctrl+E | Time/Timer |
| Ctrl+I | Infrastructure |
| Ctrl+K | Command Palette |

## Notes

- On Mac, use Cmd instead of Ctrl
- Shortcuts use `event.metaKey || event.ctrlKey` for cross-platform
- Some shortcuts may conflict with browser defaults

## Browser Shortcut Conflicts

| Shortcut | Browser Default | Conflict? |
|----------|-----------------|-----------|
| Ctrl+T | New Tab | Yes (may need prevent) |
| Ctrl+P | Print | Yes (may need prevent) |
| Ctrl+K | Focus URL bar | Mild |

## Pass Criteria

- All 7 shortcuts trigger correct actions
- Works on both Windows/Linux and Mac
- Command palette opens correctly
- No conflicts that break functionality

## Screenshots Required

1. Tasks panel opened via shortcut
2. Command palette open
3. Settings panel opened via shortcut

# Test 005: Dashboard Main View

**Priority:** P0 (Critical)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify the main dashboard view loads correctly with all core elements.

## Preconditions

- User is logged in

## Test Steps

### Scenario A: Dashboard Layout

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Verify all main UI elements are present

**Expected Results:**
- [ ] Page loads without errors
- [ ] "AI-POWERED" indicator is visible at top
- [ ] "Focus by Kraliki" title is prominently displayed (large font)
- [ ] "AI-First Command Center" subtitle is visible
- [ ] "Speak your intent. AI creates. Forms are optional" tagline is visible

### Scenario B: AI Canvas / Input Area

1. Locate the main AI input area (UnifiedCanvas component)

**Expected Results:**
- [ ] AI input field/textarea is visible
- [ ] Input is interactive and accepts text
- [ ] Send button or input submission mechanism is available
- [ ] Placeholder or prompt text is visible

### Scenario C: Quick Prompts

1. Locate the quick prompt buttons below the AI canvas

**Expected Results:**
- [ ] Quick prompt buttons are visible
- [ ] At least 4 prompts are shown:
  - "Show urgent tasks"
  - "Plan my week"
  - "What's blocking me?"
  - "Find notes about..."
- [ ] Buttons have brutalist styling
- [ ] Clicking a prompt populates the input field

### Scenario D: Floating Action Buttons

1. Locate floating action buttons on the right side of the screen

**Expected Results:**
- [ ] Tasks button is visible (CheckSquare icon)
- [ ] Knowledge button is visible (Book icon)
- [ ] Calendar button is visible (Calendar icon)
- [ ] Timer/Pomodoro button is visible (Timer icon, accent color)
- [ ] Settings button is visible (Settings icon, slightly muted)
- [ ] Buttons have tooltip text on hover
- [ ] Buttons have brutalist shadow styling

### Scenario E: AI-First Messaging

1. Verify the AI-first hierarchy messaging at bottom

**Expected Results:**
- [ ] "Conversation-First Design" badge is visible
- [ ] "AI creates everything. Forms are escape hatches. No traditional CRUD" text is visible

## UI Elements Summary

| Element | Location | Visible |
|---------|----------|---------|
| AI-POWERED badge | Top center | Required |
| Focus by Kraliki title | Center | Required |
| AI Input Canvas | Center | Required |
| Quick Prompts | Below canvas | Required |
| Tasks FAB | Bottom right | Required |
| Knowledge FAB | Bottom right | Required |
| Calendar FAB | Bottom right | Required |
| Timer FAB | Bottom right | Required |
| Settings FAB | Bottom right | Required |

## Pass Criteria

- All core UI elements are visible
- Layout is responsive and properly styled
- No JavaScript console errors
- Page loads within 3 seconds

## Screenshots Required

1. Full dashboard view
2. AI input canvas close-up
3. Quick prompts section
4. Floating action buttons

## Notes

- Dashboard uses "Fighter Jet HUD" layout concept
- Processing indicator appears at top center when AI is working
- Context panels are hidden by default (slide in on demand)

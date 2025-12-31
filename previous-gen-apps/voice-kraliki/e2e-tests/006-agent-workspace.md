# E2E Test 006: Agent Workspace

**Priority:** High
**Route:** `/calls/agent`
**URL:** https://voice.verduona.dev/calls/agent

## Objective

Verify the AI Agent Workspace loads correctly with call controls and AI assistance features.

## Prerequisites

- Logged in as testuser@example.com
- Microphone permissions may be required for full functionality

## Test Steps

### Test A: Agent Workspace Load

```
1. Login at https://voice.verduona.dev/auth/login
2. Navigate to https://voice.verduona.dev/calls/agent
3. Verify page title "AI Agent Workspace" is displayed
4. Check for main components:
   - Header with page description
   - Start Demo Call button
   - Status indicators (Session, Audio, Call)
5. Take a screenshot
```

### Test B: UI Components Check

```
1. On Agent Workspace page
2. Verify status bar shows:
   - Session status
   - Audio status
   - Call status (Active/Inactive)
3. Look for "Getting Started" instructions section
4. Verify instructions explain the 3 steps
5. Take a screenshot of the instructions
```

### Test C: Start Demo Call Button

```
1. On Agent Workspace page
2. Locate "Start Demo Call" button
3. Verify button is styled correctly (green/primary)
4. Note: Clicking will request microphone access
5. Take a screenshot showing the button
```

### Test D: Call Controls Panel

```
1. On Agent Workspace page
2. After clicking Start Demo Call (if testing fully)
3. Verify appearance of:
   - End Call button (red)
   - Mute/Unmute control
   - Session status changes to "connected"
4. Take a screenshot of active call state
```

## Expected Results

### Test A
- [ ] Page loads with proper layout
- [ ] Title and description visible
- [ ] Main action button present

### Test B
- [ ] All status indicators visible
- [ ] Instructions section explains workflow
- [ ] 3 numbered steps displayed

### Test C
- [ ] Start Demo Call button visible
- [ ] Button is properly styled
- [ ] Button is clickable

### Test D
- [ ] Call controls appear when call starts
- [ ] Status updates correctly
- [ ] AI workspace components visible

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Login with testuser@example.com / test123
Navigate to https://voice.verduona.dev/calls/agent
Take a screenshot
Report:
- Is the page title "AI Agent Workspace"?
- Is there a "Start Demo Call" button?
- What status indicators are shown?
- What instructions are displayed?
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

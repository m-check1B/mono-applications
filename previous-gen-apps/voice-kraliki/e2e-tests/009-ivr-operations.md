# E2E Test 009: IVR Operations

**Priority:** Medium
**Route:** `/operations/ivr`
**URL:** https://voice.verduona.dev/operations/ivr

## Objective

Verify the IVR (Interactive Voice Response) management page loads and displays IVR flows.

## Prerequisites

- Logged in as testuser@example.com
- Valid session token

## Test Steps

### Test A: IVR Page Load

```
1. Login at https://voice.verduona.dev/auth/login
2. Navigate to https://voice.verduona.dev/operations/ivr
3. Verify page loads with:
   - IVR flows list
   - Create Flow button
   - Flow status indicators
4. Take a screenshot
```

### Test B: IVR Builder Access

```
1. On IVR operations page
2. Navigate to https://voice.verduona.dev/operations/ivr/builder
3. Verify IVR builder page loads with:
   - Visual flow designer (if implemented)
   - Node toolbox
   - Canvas area
4. Take a screenshot
```

### Test C: Routing Page

```
1. Navigate to https://voice.verduona.dev/operations/routing
2. Verify routing rules page loads
3. Check for:
   - Routing rules list
   - Create Rule button
   - Rule priorities
4. Take a screenshot
```

### Test D: Recordings Page

```
1. Navigate to https://voice.verduona.dev/operations/recordings
2. Verify recordings page loads
3. Check for:
   - Recordings list
   - Playback controls
   - Transcription status
4. Take a screenshot
```

### Test E: Voicemail Page

```
1. Navigate to https://voice.verduona.dev/operations/voicemail
2. Verify voicemail page loads
3. Check for:
   - Voicemail inbox list
   - New/Read status
   - Playback functionality
4. Take a screenshot
```

## Expected Results

### Test A
- [ ] IVR page loads successfully
- [ ] Flows list or empty state shown
- [ ] Create button available

### Test B
- [ ] Builder page accessible
- [ ] Visual components present
- [ ] No JavaScript errors

### Test C
- [ ] Routing page loads
- [ ] Rules displayed correctly
- [ ] Create functionality present

### Test D
- [ ] Recordings page loads
- [ ] Recording list or empty state
- [ ] Playback controls visible

### Test E
- [ ] Voicemail page loads
- [ ] Inbox displayed correctly
- [ ] Status indicators visible

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Login with testuser@example.com / test123
Navigate to https://voice.verduona.dev/operations/ivr
Take a screenshot
Report what IVR features are available

Navigate to https://voice.verduona.dev/operations/routing
Take a screenshot
Report what routing options are displayed

Navigate to https://voice.verduona.dev/operations/recordings
Take a screenshot
Report the recordings page content
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

# Test 012: Onboarding Flow

**Priority:** P1 (High)
**URL:** https://focus.verduona.dev/onboarding
**Estimated Time:** 8 minutes

## Objective

Verify the 4-step onboarding flow works correctly for new users.

## Preconditions

- User is newly registered OR onboarding not yet completed
- Browser is logged in

## Test Steps

### Scenario A: Access Onboarding

1. Create new account or access with new user
2. Should be redirected to onboarding OR
3. Navigate directly to: `https://focus.verduona.dev/onboarding`

**Expected Results:**
- [ ] Onboarding page loads
- [ ] "Welcome to Focus by Kraliki!" title visible
- [ ] Progress bar shows "Step 1 of 4"
- [ ] "Skip onboarding" option available

### Scenario B: Step 1 - Persona Selection

1. View the persona selection step

**Expected Results:**
- [ ] 3 personas are displayed:
  - Solo Developer (Code icon)
  - Freelancer (Briefcase icon)
  - Explorer (Compass icon)
- [ ] Each persona shows name and description
- [ ] Can click to select a persona

2. Select "Solo Developer" persona

**Expected Results:**
- [ ] Selected persona is highlighted
- [ ] Checkmark appears on selected card
- [ ] Progress bar advances to Step 2
- [ ] User moves to privacy preferences

### Scenario C: Step 2 - Privacy Preferences

1. View privacy preferences step

**Expected Results:**
- [ ] Shield icon visible
- [ ] "Privacy & Data Controls" title
- [ ] BYOK information box displayed
- [ ] Feature toggles visible:
  - Gemini File Search
  - II-Agent Assistance
- [ ] Privacy acknowledgment checkbox
- [ ] Continue button (disabled until acknowledgment)

2. Configure preferences

**Expected Results:**
- [ ] Can toggle Gemini on/off
- [ ] Can toggle II-Agent on/off
- [ ] Must check privacy acknowledgment to continue

3. Check acknowledgment and click Continue

**Expected Results:**
- [ ] Preferences are saved
- [ ] Progress to Step 3

### Scenario D: Step 3 - Feature Configuration

1. View feature configuration step

**Expected Results:**
- [ ] Settings icon visible
- [ ] "Feature Configuration" title
- [ ] Feature toggles:
  - Gemini File Search
  - II-Agent
  - Voice Transcription
- [ ] Back button available
- [ ] Continue button available

2. Toggle some features and continue

**Expected Results:**
- [ ] Can enable/disable each feature
- [ ] Features are saved
- [ ] Progress to Step 4

### Scenario E: Step 4 - Completion

1. View completion step

**Expected Results:**
- [ ] Checkmark icon visible
- [ ] "You're all set!" title
- [ ] Selected persona mentioned
- [ ] Recommended next steps listed (if persona has them)
- [ ] "Go to Dashboard" button visible

2. Click "Go to Dashboard"

**Expected Results:**
- [ ] Onboarding is marked complete
- [ ] Redirected to `/dashboard`
- [ ] Full dashboard access available

### Scenario F: Skip Onboarding

1. On any onboarding step
2. Click "Skip onboarding" link

**Expected Results:**
- [ ] Confirmation dialog appears
- [ ] "Are you sure you want to skip?" message
- [ ] Can cancel or confirm

3. Confirm skip

**Expected Results:**
- [ ] Onboarding is skipped
- [ ] Explorer persona is assigned (default)
- [ ] Redirected to dashboard

### Scenario G: Back Navigation

1. On Step 3 (Feature Configuration)
2. Click "Back" button

**Expected Results:**
- [ ] Returns to Step 2
- [ ] Previous selections preserved
- [ ] Can modify and continue again

## Persona Details

| Persona | Icon | Description |
|---------|------|-------------|
| Solo Developer | Code | Technical focus, dev tools |
| Freelancer | Briefcase | Client work, billing |
| Explorer | Compass | Minimal, discover features |
| Operations Lead | CalendarCheck | Team coordination |

## Progress Bar

- Step 1: Persona Selection (25%)
- Step 2: Privacy Preferences (50%)
- Step 3: Feature Configuration (75%)
- Step 4: Completion (100%)

## Pass Criteria

- All 4 steps complete successfully
- Persona selection works
- Privacy acknowledgment required
- Feature toggles save
- Skip onboarding works
- Dashboard access after completion

## Screenshots Required

1. Step 1 - Persona selection
2. Step 2 - Privacy preferences
3. Step 3 - Feature configuration
4. Step 4 - Completion screen
5. Dashboard after onboarding

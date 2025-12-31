# Test 004: Google OAuth Flow

**Priority:** P1 (High)
**URL:** https://focus.verduona.dev/login
**Estimated Time:** 3 minutes

## Objective

Verify Google OAuth login functionality initiates correctly.

## Preconditions

- Browser is not logged in
- Google account is available for testing (optional for full flow)

## Test Steps

### Scenario A: Initiate Google OAuth

1. Navigate to: `https://focus.verduona.dev/login`
2. Locate "Continue with Google" button
3. Click the Google OAuth button

**Expected Results:**
- [ ] Google OAuth button is visible with Google icon
- [ ] Button text reads "Continue with Google"
- [ ] Clicking opens a popup window (not redirect)
- [ ] Popup window navigates to Google OAuth URL
- [ ] If popups are blocked, error message appears

### Scenario B: Popup Blocked

1. Configure browser to block popups
2. Navigate to: `https://focus.verduona.dev/login`
3. Click "Continue with Google" button

**Expected Results:**
- [ ] Error message appears: "Please allow popups for Google Sign In"
- [ ] User stays on login page
- [ ] Loading state ends

### Scenario C: OAuth Cancelled

1. Navigate to: `https://focus.verduona.dev/login`
2. Click "Continue with Google" button
3. When popup opens, close it without completing OAuth

**Expected Results:**
- [ ] Error message appears: "Google login cancelled"
- [ ] User stays on login page
- [ ] Can retry the OAuth flow

## Technical Notes

- OAuth uses popup window (500x600px)
- State parameter used for CSRF protection
- Callback handled via `postMessage` API
- Redirect URI should be same origin

## UI Elements to Verify

- [ ] Google button has SVG icon
- [ ] Button styling matches brutalist theme
- [ ] Hover state is visible
- [ ] Loading state shows when OAuth initiates

## Pass Criteria

- Google OAuth popup opens correctly
- Popup blocked scenario shows error
- Cancelled OAuth shows appropriate message

## Screenshots Required

1. Login page with Google button visible
2. Google OAuth popup (if testable)
3. Error state (popup blocked or cancelled)

## Notes

Full OAuth completion requires a real Google account and may not be testable in automated E2E.
This test focuses on the initiation and error handling of the OAuth flow.

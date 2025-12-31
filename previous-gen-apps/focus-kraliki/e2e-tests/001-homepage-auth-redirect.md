# Test 001: Homepage & Auth Redirect

**Priority:** P0 (Critical)
**URL:** https://focus.verduona.dev
**Estimated Time:** 2 minutes

## Objective

Verify that the homepage correctly redirects based on authentication state.

## Preconditions

- None (test both logged-out and logged-in states)

## Test Steps

### Scenario A: Unauthenticated User

1. Open a new incognito/private browser window
2. Navigate to: `https://focus.verduona.dev`
3. Wait for page to load (may show "Loading..." briefly)

**Expected Results:**
- [ ] Page redirects to `/login`
- [ ] Login form is displayed
- [ ] "Focus by Kraliki" title is visible
- [ ] Email and password input fields are present
- [ ] "Sign In" button is visible
- [ ] "Continue with Google" button is visible
- [ ] "Sign up" link is visible at bottom

### Scenario B: Authenticated User

1. Log in to Focus by Kraliki first (use Scenario A to access login)
2. After login, note you are on `/dashboard`
3. Navigate directly to: `https://focus.verduona.dev`

**Expected Results:**
- [ ] Page redirects to `/dashboard`
- [ ] Main dashboard view is displayed
- [ ] "Focus by Kraliki" branding is visible
- [ ] "AI-POWERED" indicator is visible
- [ ] AI input canvas is visible
- [ ] Floating action buttons (Tasks, Knowledge, etc.) are visible

## Pass Criteria

- Both Scenario A and Scenario B pass
- Redirects happen within 2 seconds
- No JavaScript console errors

## Notes

- The homepage component shows "Loading..." while determining auth state
- Uses `authStore` Svelte store for authentication state

## Screenshots Required

1. Login page (after unauthenticated redirect)
2. Dashboard (after authenticated redirect)

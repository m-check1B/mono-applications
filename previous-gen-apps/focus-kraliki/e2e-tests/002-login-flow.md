# Test 002: Login Flow

**Priority:** P0 (Critical)
**URL:** https://focus.verduona.dev/login
**Estimated Time:** 5 minutes

## Objective

Verify the email/password login functionality works correctly.

## Preconditions

- Valid test account exists (or create one via registration first)
- Browser is not logged in (incognito/private mode recommended)

## Test Steps

### Scenario A: Successful Login

1. Navigate to: `https://focus.verduona.dev/login`
2. Verify login page elements are present
3. Enter valid email in the email field
4. Enter valid password in the password field
5. Click "SIGN IN" button

**Expected Results:**
- [ ] Login page loads correctly
- [ ] "Focus by Kraliki" title is displayed
- [ ] "Sign in to your account" subtitle is visible
- [ ] Email field accepts input
- [ ] Password field accepts input (masked)
- [ ] After clicking SIGN IN, button shows "SIGNING IN..."
- [ ] User is redirected to `/dashboard`
- [ ] Dashboard shows user is authenticated

### Scenario B: Empty Fields Validation

1. Navigate to: `https://focus.verduona.dev/login`
2. Leave email field empty
3. Leave password field empty
4. Click "SIGN IN" button

**Expected Results:**
- [ ] Error message appears: "Please enter email and password"
- [ ] Error is displayed in red/destructive styled box
- [ ] User stays on login page
- [ ] No redirect occurs

### Scenario C: Invalid Credentials

1. Navigate to: `https://focus.verduona.dev/login`
2. Enter email: `invalid@example.com`
3. Enter password: `wrongpassword`
4. Click "SIGN IN" button

**Expected Results:**
- [ ] Error message appears (e.g., "Login failed" or similar)
- [ ] Error is displayed in brutalist-styled error box
- [ ] User stays on login page
- [ ] Password field may be cleared

### Scenario D: Navigation to Register

1. Navigate to: `https://focus.verduona.dev/login`
2. Click "Sign up" link at bottom

**Expected Results:**
- [ ] User is redirected to `/register`
- [ ] Registration form is displayed

## UI Elements to Verify

- [ ] Modern Brutalism styling (sharp corners, bold borders)
- [ ] Input fields have brutal-border class styling
- [ ] Button has uppercase text
- [ ] Focus states show shadow effect on inputs
- [ ] Google OAuth button is present with icon

## Pass Criteria

- Scenario A: Successful login redirects to dashboard
- Scenario B: Empty fields show validation error
- Scenario C: Invalid credentials show error
- Scenario D: Navigation works correctly

## Screenshots Required

1. Login page initial state
2. Login page with filled fields
3. Error state (validation or invalid credentials)
4. Successful redirect to dashboard

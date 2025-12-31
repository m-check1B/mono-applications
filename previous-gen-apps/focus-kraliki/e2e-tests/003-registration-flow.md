# Test 003: Registration Flow

**Priority:** P0 (Critical)
**URL:** https://focus.verduona.dev/register
**Estimated Time:** 5 minutes

## Objective

Verify the user registration process works correctly with all validations.

## Preconditions

- Browser is not logged in
- Use a unique email address for testing

## Test Steps

### Scenario A: Successful Registration

1. Navigate to: `https://focus.verduona.dev/register`
2. Verify registration page elements are present
3. Enter full name: `Test User`
4. Enter unique email: `testuser_[timestamp]@example.com`
5. Enter password: `SecurePassword123`
6. Enter confirm password: `SecurePassword123`
7. Click "CREATE ACCOUNT" button

**Expected Results:**
- [ ] Registration page loads correctly
- [ ] "Create Account" title is displayed
- [ ] "Get started with Focus by Kraliki" subtitle is visible
- [ ] All four input fields are present (Name, Email, Password, Confirm)
- [ ] After clicking CREATE ACCOUNT, button shows "CREATING ACCOUNT..."
- [ ] User is redirected to `/dashboard` on success
- [ ] New user is logged in automatically

### Scenario B: Empty Fields Validation

1. Navigate to: `https://focus.verduona.dev/register`
2. Leave all fields empty
3. Click "CREATE ACCOUNT" button

**Expected Results:**
- [ ] Error message appears: "Please fill in all fields"
- [ ] User stays on registration page

### Scenario C: Password Too Short

1. Navigate to: `https://focus.verduona.dev/register`
2. Enter full name: `Test User`
3. Enter email: `test@example.com`
4. Enter password: `short` (less than 8 characters)
5. Enter confirm password: `short`
6. Click "CREATE ACCOUNT" button

**Expected Results:**
- [ ] Error message appears: "Password must be at least 8 characters"
- [ ] User stays on registration page
- [ ] Password hint text shows "At least 8 characters"

### Scenario D: Password Mismatch

1. Navigate to: `https://focus.verduona.dev/register`
2. Enter full name: `Test User`
3. Enter email: `test@example.com`
4. Enter password: `SecurePassword123`
5. Enter confirm password: `DifferentPassword456`
6. Click "CREATE ACCOUNT" button

**Expected Results:**
- [ ] Error message appears: "Passwords do not match"
- [ ] User stays on registration page

### Scenario E: Duplicate Email

1. Navigate to: `https://focus.verduona.dev/register`
2. Enter full name: `Test User`
3. Enter email that already exists
4. Enter valid matching passwords
5. Click "CREATE ACCOUNT" button

**Expected Results:**
- [ ] Error message appears indicating email already exists
- [ ] User stays on registration page

### Scenario F: Navigation to Login

1. Navigate to: `https://focus.verduona.dev/register`
2. Click "Sign in" link at bottom

**Expected Results:**
- [ ] User is redirected to `/login`
- [ ] Login form is displayed

## UI Elements to Verify

- [ ] Modern Brutalism styling consistent with login page
- [ ] All input fields have proper labels (uppercase, bold)
- [ ] Password requirements hint is displayed
- [ ] Error messages use destructive/red styling
- [ ] Button has uppercase text and brutal styling

## Form Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Full Name | text | Yes | Non-empty |
| Email | email | Yes | Valid email format |
| Password | password | Yes | Min 8 characters |
| Confirm Password | password | Yes | Must match password |

## Pass Criteria

- All validation scenarios work correctly
- Successful registration creates account and logs in
- Error messages are clear and helpful

## Screenshots Required

1. Registration page initial state
2. Filled form before submission
3. Validation error state
4. Successful registration (dashboard view)

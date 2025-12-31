# E2E Test 003: Auth Registration Flow

**Priority:** High
**Route:** `/auth/register`
**URL:** https://voice.verduona.dev/auth/register

## Objective

Verify the registration flow displays correctly and handles input validation.

## Prerequisites

- None (public page)

## Test Steps

### Test A: Registration Form Display

```
1. Navigate to https://voice.verduona.dev/auth/register
2. Verify registration form is displayed with:
   - Email input field
   - Password input field
   - Confirm password field (if present)
   - Create account / Register button
3. Verify link to login page exists
4. Take a screenshot
```

### Test B: Form Validation

```
1. Navigate to https://voice.verduona.dev/auth/register
2. Enter invalid email format (e.g., "notanemail")
3. Click register button
4. Verify email validation error appears
5. Enter valid email but weak password
6. Verify password requirements are shown
7. Take a screenshot
```

### Test C: Navigation to Login

```
1. Navigate to https://voice.verduona.dev/auth/register
2. Find and click "Already have an account?" or "Sign in" link
3. Verify navigation to /auth/login
4. Take a screenshot
```

## Expected Results

### Test A
- [ ] Registration form loads correctly
- [ ] All required fields are visible
- [ ] Form has proper labels and placeholders
- [ ] Sign in link is visible

### Test B
- [ ] Email validation works
- [ ] Password requirements enforced
- [ ] Clear error messages displayed

### Test C
- [ ] Login link navigates correctly
- [ ] Smooth page transition

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/register
Take a screenshot
Report what form fields are visible
Click on any "Sign in" or login link
Report if navigation to login page works
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

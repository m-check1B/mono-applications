# E2E Test 002: Auth Login Flow

**Priority:** Critical
**Route:** `/auth/login`
**URL:** https://voice.verduona.dev/auth/login

## Objective

Verify the login flow works correctly with valid and invalid credentials.

## Prerequisites

- Test account: testuser@example.com / test123
- Page accessible without authentication

## Test Steps

### Test A: Valid Login

```
1. Navigate to https://voice.verduona.dev/auth/login
2. Verify login form is displayed with:
   - Email input field
   - Password input field
   - Sign in button
3. Enter email: testuser@example.com
4. Enter password: test123
5. Click "Sign in" button
6. Wait for redirect
7. Verify redirect to /dashboard
8. Take a screenshot of the dashboard
```

### Test B: Invalid Login

```
1. Navigate to https://voice.verduona.dev/auth/login
2. Enter email: wrong@example.com
3. Enter password: wrongpassword
4. Click "Sign in" button
5. Verify error message appears
6. Take a screenshot showing error message
```

### Test C: Empty Fields Validation

```
1. Navigate to https://voice.verduona.dev/auth/login
2. Click "Sign in" button without entering any data
3. Verify validation message appears
4. Take a screenshot
```

## Expected Results

### Test A
- [ ] Login form displays correctly
- [ ] Successful login redirects to /dashboard
- [ ] User session is established
- [ ] Dashboard shows user-specific content

### Test B
- [ ] Error message displayed for invalid credentials
- [ ] User stays on login page
- [ ] No sensitive information leaked in error

### Test C
- [ ] Form validation prevents empty submission
- [ ] Clear error message shown

## Verification Command (Quick Test)

```
Navigate to https://voice.verduona.dev/auth/login
Enter email: testuser@example.com
Enter password: test123
Click the Sign in button
Wait for navigation
Take a screenshot
Report if login was successful and what page you see
```

---

## Results

**Date:**
**Status:** Pending
**Tester:**
**Notes:**

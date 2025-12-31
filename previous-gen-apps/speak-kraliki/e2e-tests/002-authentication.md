# Test 002: Authentication Flows

**Priority:** HIGH
**URL:** https://speak.verduona.dev

## Preconditions

- Browser is open
- User is not logged in

## Test Steps

### Step 1: Login Page Display

1. Navigate to https://speak.verduona.dev/login
2. Wait for page to load

**Expected:**
- Email input field is visible
- Password input field is visible
- Submit button is visible
- Link to registration page exists

### Step 2: Login Form Validation

1. Click submit button without entering any data

**Expected:**
- Form shows validation errors (required fields)
- No network request is made
- Email field is marked invalid

### Step 3: Invalid Credentials Error

1. Enter email: test@invalid.com
2. Enter password: wrongpassword
3. Click submit button
4. Wait for response

**Expected:**
- Error message is displayed
- User remains on login page
- Password field is cleared or remains

### Step 4: Registration Page Display

1. Navigate to https://speak.verduona.dev/register
2. Wait for page to load

**Expected:**
- Company name field (if present)
- Email input field is visible
- Password input field is visible
- Password confirmation field (if present)
- Submit button is visible
- Link to login page exists

### Step 5: Registration Form Validation

1. Enter invalid email format (e.g., "notanemail")
2. Click submit button

**Expected:**
- Email validation error is shown
- Form is not submitted

### Step 6: Password Validation

1. Enter valid email
2. Enter short password (e.g., "123")
3. Click submit

**Expected:**
- Password validation error shown (if password requirements exist)

## Success Criteria

- Login form displays correctly
- Validation messages appear appropriately
- Invalid credentials show error
- Registration form displays correctly
- Form validation works on registration

## Notes

- This test does not create actual accounts (no test credentials available)
- For authenticated flow tests, see 004-dashboard-overview.md

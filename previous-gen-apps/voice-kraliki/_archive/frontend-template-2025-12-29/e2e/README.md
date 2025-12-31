# E2E Test Infrastructure for Voice by Kraliki

Comprehensive end-to-end testing infrastructure built with Playwright, featuring reusable fixtures, Page Object Models, and custom utilities.

## Directory Structure

```
e2e/
├── fixtures/
│   ├── auth.fixture.ts      # Authentication fixture with auto-login
│   └── test-data.ts          # Test data and mock API responses
├── pages/
│   ├── LoginPage.ts          # Login page object model
│   ├── DashboardPage.ts      # Dashboard page object model
│   └── CallPage.ts           # Call page object model
├── utils/
│   ├── helpers.ts            # Helper utilities
│   └── assertions.ts         # Custom assertions
├── tests/
│   ├── auth.spec.ts          # Authentication tests
│   ├── dashboard.spec.ts     # Dashboard tests
│   └── calls.spec.ts         # Call functionality tests
├── global-setup.ts           # Global test setup
├── global-teardown.ts        # Global test cleanup
└── README.md                 # This file
```

## Quick Start

### Install Dependencies

```bash
npm install
```

### Run All Tests

```bash
npm run test:e2e
```

### Run Tests in UI Mode

```bash
npm run test:e2e:ui
```

### Run Tests in Debug Mode

```bash
npm run test:e2e:debug
```

### Run Tests with Headed Browser

```bash
npm run test:e2e:headed
```

### View Test Report

```bash
npm run test:e2e:report
```

## Environment Variables

Create a `.env.test` file or set environment variables:

```bash
# Backend URL
BACKEND_URL=http://localhost:8000

# Frontend URL
PLAYWRIGHT_BASE_URL=http://localhost:3000

# Test User Credentials
TEST_USER_EMAIL=test.user@example.com
TEST_USER_PASSWORD=TestPassword123!

# Test Admin Credentials
TEST_ADMIN_EMAIL=admin@example.com
TEST_ADMIN_PASSWORD=AdminPassword123!

# Optional Settings
SEED_TEST_DATA=true          # Seed database before tests
CLEANUP_TEST_DATA=true       # Clean up after tests
CLEANUP_SCREENSHOTS=true     # Remove old screenshots
SKIP_SERVER=false            # Skip starting dev server
SLOW_MO=0                    # Slow down test execution (ms)
HEADLESS=true                # Run in headless mode
```

## Using Authentication Fixture

The authentication fixture automatically handles login and reuses auth state across tests for better performance.

### Basic Usage

```typescript
import { test, expect } from '../fixtures/auth.fixture';

test('should access protected page', async ({ authenticatedPage }) => {
  // Page is already authenticated
  await authenticatedPage.goto('/dashboard');
  
  // User is logged in
  expect(await authenticatedPage.url()).toContain('/dashboard');
});
```

### Access Auth State

```typescript
test('should display user info', async ({ authenticatedPage, authState }) => {
  await authenticatedPage.goto('/profile');
  
  // Access user information from auth state
  console.log('User email:', authState.user.email);
  console.log('User role:', authState.user.role);
});
```

### Login as Different User

```typescript
test('should login as admin', async ({ page, loginAs }) => {
  const authState = await loginAs('admin@example.com', 'AdminPassword123!');
  
  // Now logged in as admin
  await page.goto('/admin');
});
```

### Logout

```typescript
test('should logout', async ({ authenticatedPage, logout }) => {
  await authenticatedPage.goto('/dashboard');
  
  // Perform logout
  await logout();
  
  // User is logged out
  expect(await authenticatedPage.url()).toContain('/login');
});
```

## Using Page Object Models

Page Object Models provide a clean interface to interact with pages.

### LoginPage

```typescript
import { LoginPage } from '../pages/LoginPage';

test('should login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password');
  
  expect(await loginPage.isLoggedIn()).toBe(true);
});
```

### DashboardPage

```typescript
import { DashboardPage } from '../pages/DashboardPage';

test('should view calls', async ({ authenticatedPage }) => {
  const dashboardPage = new DashboardPage(authenticatedPage);
  
  await dashboardPage.goto();
  await dashboardPage.viewCalls();
  
  expect(await authenticatedPage.url()).toContain('/calls');
});
```

### CallPage

```typescript
import { CallPage } from '../pages/CallPage';

test('should make a call', async ({ authenticatedPage }) => {
  const callPage = new CallPage(authenticatedPage);
  
  await callPage.goto();
  await callPage.startOutboundCall('+15551234567');
  
  expect(await callPage.isCallActive()).toBe(true);
  
  await callPage.endCall();
});
```

## Using Helper Utilities

### Wait for Loading

```typescript
import { waitForLoadingComplete } from '../utils/helpers';

test('should wait for page load', async ({ page }) => {
  await page.goto('/dashboard');
  await waitForLoadingComplete(page);
  
  // Page is fully loaded
});
```

### Wait for API Response

```typescript
import { waitForApiResponse } from '../utils/helpers';

test('should wait for API call', async ({ page }) => {
  const responsePromise = waitForApiResponse(page, '/api/v1/calls');
  
  await page.click('button:has-text("Load Calls")');
  await responsePromise;
  
  // API call completed
});
```

### Generate Test Data

```typescript
import { generateTestData } from '../utils/helpers';

test('should register new user', async ({ page }) => {
  const email = generateTestData.email();
  const password = generateTestData.password();
  const name = generateTestData.name();
  
  // Use generated data for registration
});
```

### Take Screenshot

```typescript
import { takeScreenshot } from '../utils/helpers';

test('should capture error state', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Take screenshot for debugging
  await takeScreenshot(page, 'dashboard-error');
});
```

## Using Custom Assertions

### Assert Authentication

```typescript
import { assertAuthenticated } from '../utils/assertions';

test('should be authenticated', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
  await assertAuthenticated(authenticatedPage);
});
```

### Assert Call in Progress

```typescript
import { assertCallInProgress } from '../utils/assertions';

test('should have active call', async ({ authenticatedPage }) => {
  // ... start call ...
  await assertCallInProgress(authenticatedPage);
});
```

### Assert Provider Active

```typescript
import { assertProviderActive } from '../utils/assertions';

test('should use Twilio provider', async ({ authenticatedPage }) => {
  // ... start call with Twilio ...
  await assertProviderActive(authenticatedPage, 'Twilio');
});
```

### Assert Error Displayed

```typescript
import { assertErrorDisplayed } from '../utils/assertions';

test('should show error', async ({ page }) => {
  // ... trigger error ...
  await assertErrorDisplayed(page, 'Invalid phone number');
});
```

## Test Data

Access predefined test data from fixtures:

```typescript
import {
  TEST_USER,
  TEST_ADMIN,
  TEST_PHONE_NUMBERS,
  TEST_COMPANIES,
  MOCK_API_RESPONSES
} from '../fixtures/test-data';

test('should use test data', async ({ page }) => {
  // Use test user
  console.log('Email:', TEST_USER.email);
  console.log('Password:', TEST_USER.password);
  
  // Use test phone numbers
  const validPhone = TEST_PHONE_NUMBERS.valid.us;
  const invalidPhone = TEST_PHONE_NUMBERS.invalid.tooShort;
  
  // Use mock API responses
  const mockLogin = MOCK_API_RESPONSES.loginSuccess;
});
```

## Running Specific Tests

### Run Single Test File

```bash
npx playwright test e2e/tests/auth.spec.ts
```

### Run Tests by Name

```bash
npx playwright test -g "should login"
```

### Run Tests in Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Run Mobile Tests

```bash
npx playwright test --project=mobile-chrome
npx playwright test --project=mobile-safari
```

## Debugging Tests

### Debug Mode

```bash
npm run test:e2e:debug
```

### Headed Mode

```bash
npm run test:e2e:headed
```

### Slow Motion

```bash
SLOW_MO=1000 npm run test:e2e
```

### Browser DevTools

```bash
PWDEBUG=1 npm run test:e2e
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      
      - name: Run E2E tests
        run: npm run test:e2e
        env:
          CI: true
          BACKEND_URL: http://localhost:8000
          PLAYWRIGHT_BASE_URL: http://localhost:3000
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: e2e/test-results/
```

## Best Practices

1. **Use Page Object Models** - Keep tests clean by using POMs
2. **Reuse Authentication** - Use the auth fixture to avoid repeated logins
3. **Use Custom Assertions** - Make tests more readable
4. **Wait for Elements** - Always wait for elements before interacting
5. **Handle Async Properly** - Use await for all async operations
6. **Keep Tests Isolated** - Each test should be independent
7. **Use Test Data** - Use predefined test data from fixtures
8. **Clean Up** - Clean up after tests (auth state, database)

## Troubleshooting

### Tests Failing Due to Timeout

Increase timeout in `playwright.config.ts`:

```typescript
timeout: 60 * 1000, // 60 seconds
```

### Authentication Not Working

Check that test user exists in database and credentials are correct in `.env.test`.

### Backend/Frontend Not Available

Make sure both servers are running before tests:

```bash
# Terminal 1 - Backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev

# Terminal 3 - Tests
npm run test:e2e
```

### Screenshots Not Saved

Check that `screenshots` directory exists:

```bash
mkdir -p e2e/screenshots
```

## Additional Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Playwright Fixtures](https://playwright.dev/docs/test-fixtures)

## Contributing

When adding new tests:

1. Create Page Object Models for new pages
2. Add test data to `fixtures/test-data.ts`
3. Add custom assertions if needed
4. Follow existing test patterns
5. Document any new utilities

## License

MIT

# E2E Test Infrastructure - Quick Reference Card

## Common Commands

```bash
# Run all tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui

# Run in debug mode
npm run test:e2e:debug

# Run headed (see browser)
npm run test:e2e:headed

# View report
npm run test:e2e:report

# Run specific test
npx playwright test e2e/tests/auth.spec.ts

# Run specific browser
npx playwright test --project=chromium

# Run with grep pattern
npx playwright test -g "should login"
```

## Import Statements

```typescript
// Fixtures
import { test, expect } from '../fixtures/auth.fixture';

// Page Objects
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { CallPage } from '../pages/CallPage';

// Test Data
import { TEST_USER, TEST_PHONE_NUMBERS } from '../fixtures/test-data';

// Utilities
import { waitForLoadingComplete, generateTestData } from '../utils/helpers';
import { assertAuthenticated, assertCallInProgress } from '../utils/assertions';
```

## Basic Test Template

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';

test('Test description', async ({ authenticatedPage }) => {
  const page = new DashboardPage(authenticatedPage);
  
  // Your test code here
  await page.goto();
  
  expect(await page.isVisible()).toBe(true);
});
```

## Fixtures

```typescript
// Authenticated page (already logged in)
test('...', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
});

// Auth state
test('...', async ({ authState }) => {
  console.log(authState.user.email);
});

// Login as different user
test('...', async ({ page, loginAs }) => {
  await loginAs('user@example.com', 'password');
});

// Logout
test('...', async ({ authenticatedPage, logout }) => {
  await logout();
});
```

## Page Objects

```typescript
// Login
const loginPage = new LoginPage(page);
await loginPage.goto();
await loginPage.login(email, password);

// Dashboard
const dashboard = new DashboardPage(page);
await dashboard.goto();
await dashboard.viewCalls();

// Call
const callPage = new CallPage(page);
await callPage.startOutboundCall('+15551234567');
await callPage.endCall();
```

## Common Assertions

```typescript
// Authentication
await assertAuthenticated(page);
await assertNotAuthenticated(page);

// Call state
await assertCallInProgress(page);
await assertProviderActive(page, 'Twilio');

// UI state
await assertErrorDisplayed(page, 'Invalid phone');
await assertSuccessMessage(page);
await assertLoadingComplete(page);

// Navigation
await assertUrlContains(page, '/dashboard');

// Elements
await assertElementHasText(page, 'h1', 'Dashboard');
await assertButtonEnabled(page, 'button');
```

## Common Helpers

```typescript
// Wait
await waitForLoadingComplete(page);
await waitForApiResponse(page, '/api/v1/calls');

// Generate data
const email = generateTestData.email();
const phone = generateTestData.phoneNumber();
const name = generateTestData.name();

// Screenshots
await takeScreenshot(page, 'error-state');

// LocalStorage
await setLocalStorageItem(page, 'key', 'value');
const value = await getLocalStorageItem(page, 'key');
```

## Test Data

```typescript
// Users
TEST_USER.email        // test.user@example.com
TEST_USER.password     // TestPassword123!
TEST_ADMIN.email       // admin@example.com

// Phone numbers
TEST_PHONE_NUMBERS.valid.us           // +15551234567
TEST_PHONE_NUMBERS.invalid.tooShort   // +1555
TEST_PHONE_NUMBERS.special.busy       // +15559998888

// Mock responses
MOCK_API_RESPONSES.loginSuccess
MOCK_API_RESPONSES.callList
```

## Common Page Object Methods

### LoginPage
```typescript
await loginPage.goto()
await loginPage.login(email, password)
await loginPage.loginAndWaitForDashboard(email, password)
await loginPage.isLoggedIn()
await loginPage.hasError()
```

### DashboardPage
```typescript
await dashboard.goto()
await dashboard.isVisible()
await dashboard.startCall()
await dashboard.viewCalls()
await dashboard.logout()
await dashboard.getUserInfo()
```

### CallPage
```typescript
await callPage.goto()
await callPage.startOutboundCall(phone)
await callPage.endCall()
await callPage.switchProvider('Twilio')
await callPage.mute()
await callPage.unmute()
await callPage.isCallActive()
```

## Environment Variables

```bash
BACKEND_URL=http://localhost:8000
PLAYWRIGHT_BASE_URL=http://localhost:3000
TEST_USER_EMAIL=test.user@example.com
TEST_USER_PASSWORD=TestPassword123!
SEED_TEST_DATA=true
CLEANUP_TEST_DATA=true
SLOW_MO=1000
HEADLESS=false
```

## Debugging

```bash
# Debug mode
npm run test:e2e:debug

# Headed mode
npm run test:e2e:headed

# Slow motion
SLOW_MO=1000 npm run test:e2e

# Playwright inspector
PWDEBUG=1 npm run test:e2e

# Specific test with debug
npx playwright test e2e/tests/auth.spec.ts --debug
```

## File Structure

```
e2e/
├── fixtures/
│   ├── auth.fixture.ts      # Auth fixture
│   └── test-data.ts          # Test data
├── pages/
│   ├── LoginPage.ts          # Login POM
│   ├── DashboardPage.ts      # Dashboard POM
│   └── CallPage.ts           # Call POM
├── utils/
│   ├── helpers.ts            # Utilities
│   └── assertions.ts         # Assertions
├── tests/
│   ├── auth.spec.ts          # Auth tests
│   ├── dashboard.spec.ts     # Dashboard tests
│   └── calls.spec.ts         # Call tests
└── global-setup.ts           # Setup
```

## Common Patterns

### Wait for element
```typescript
await expect(page.locator('button')).toBeVisible();
```

### Click and wait
```typescript
await page.click('button');
await page.waitForURL('**/dashboard');
```

### Fill form
```typescript
await page.fill('input[name="email"]', email);
await page.fill('input[name="password"]', password);
await page.click('button[type="submit"]');
```

### Check element
```typescript
expect(await element.isVisible()).toBe(true);
expect(await element.textContent()).toContain('text');
```

### Mock API
```typescript
await mockApiResponse(page, '/api/calls', mockData);
```

## Tips

1. Always use `await` with async operations
2. Use Page Object Models instead of direct selectors
3. Use custom assertions for readability
4. Use authenticated fixtures to save time
5. Wait for elements before interacting
6. Use test data from fixtures
7. Take screenshots for debugging
8. Clean up after tests (logout, end calls)

## Documentation

- Main docs: `e2e/README.md`
- Examples: `e2e/USAGE_EXAMPLES.md`
- Summary: `E2E_INFRASTRUCTURE_SUMMARY.md`
- This card: `e2e/QUICK_REFERENCE.md`

## Support

- Playwright docs: https://playwright.dev/
- Check existing tests for patterns
- Use UI mode for debugging: `npm run test:e2e:ui`

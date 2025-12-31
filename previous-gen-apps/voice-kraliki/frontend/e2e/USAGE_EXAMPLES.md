# E2E Test Infrastructure - Usage Examples

This document provides practical examples of using the E2E test infrastructure.

## Example 1: Basic Authentication Test

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { LoginPage } from '../pages/LoginPage';
import { TEST_USER } from '../fixtures/test-data';
import { assertAuthenticated } from '../utils/assertions';

test('User can login and access dashboard', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  // Navigate to login page
  await loginPage.goto();
  
  // Perform login
  await loginPage.loginAndWaitForDashboard(TEST_USER.email, TEST_USER.password);
  
  // Verify authentication
  await assertAuthenticated(page);
  expect(page.url()).toContain('/dashboard');
});
```

## Example 2: Using Authenticated Context

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';

test('Authenticated user can view dashboard', async ({ authenticatedPage }) => {
  // Page is already authenticated - no need to login!
  const dashboardPage = new DashboardPage(authenticatedPage);
  
  await dashboardPage.goto();
  expect(await dashboardPage.isVisible()).toBe(true);
});
```

## Example 3: Making a Phone Call

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { CallPage } from '../pages/CallPage';
import { TEST_PHONE_NUMBERS } from '../fixtures/test-data';
import { assertCallInProgress } from '../utils/assertions';

test('User can make an outbound call', async ({ authenticatedPage }) => {
  const callPage = new CallPage(authenticatedPage);
  
  // Navigate to call page
  await callPage.goto();
  
  // Start an outbound call
  await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);
  
  // Verify call is in progress
  await assertCallInProgress(authenticatedPage);
  expect(await callPage.isCallActive()).toBe(true);
  
  // End the call
  await callPage.endCall();
  await callPage.waitForCallEnded();
});
```

## Example 4: Testing Provider Switching

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { CallPage } from '../pages/CallPage';
import { TEST_PHONE_NUMBERS } from '../fixtures/test-data';
import { assertProviderActive } from '../utils/assertions';

test('User can switch telephony provider during call', async ({ authenticatedPage }) => {
  const callPage = new CallPage(authenticatedPage);
  
  await callPage.goto();
  
  // Start call with default provider
  await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);
  
  // Switch to Vonage provider
  await callPage.switchProvider('Vonage');
  
  // Verify provider switched
  await assertProviderActive(authenticatedPage, 'Vonage');
  
  // End call
  await callPage.endCall();
});
```

## Example 5: Testing Error Handling

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { CallPage } from '../pages/CallPage';
import { TEST_PHONE_NUMBERS } from '../fixtures/test-data';
import { assertErrorDisplayed } from '../utils/assertions';

test('System shows error for invalid phone number', async ({ authenticatedPage }) => {
  const callPage = new CallPage(authenticatedPage);
  
  await callPage.goto();
  
  // Try to call invalid number
  await callPage.phoneNumberInput.fill(TEST_PHONE_NUMBERS.invalid.tooShort);
  await callPage.dialButton.click();
  
  // Verify error is displayed
  await assertErrorDisplayed(authenticatedPage, 'Invalid phone number');
});
```

## Example 6: Using Test Data Generator

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { generateTestData } from '../utils/helpers';

test('Can register new user with generated data', async ({ page }) => {
  // Generate test data
  const userData = {
    email: generateTestData.email(),
    password: generateTestData.password(),
    name: generateTestData.name(),
    company: generateTestData.companyName()
  };
  
  // Navigate to registration
  await page.goto('/auth/register');
  
  // Fill form with generated data
  await page.fill('input[name="email"]', userData.email);
  await page.fill('input[name="password"]', userData.password);
  await page.fill('input[name="name"]', userData.name);
  
  // Submit form
  await page.click('button[type="submit"]');
  
  // Verify success
  await page.waitForURL('**/dashboard');
});
```

## Example 7: Waiting for API Responses

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';
import { waitForApiResponse, waitForLoadingComplete } from '../utils/helpers';

test('Dashboard loads call history from API', async ({ authenticatedPage }) => {
  const dashboardPage = new DashboardPage(authenticatedPage);
  
  // Set up API response waiter
  const apiPromise = waitForApiResponse(authenticatedPage, '/api/v1/calls');
  
  // Navigate to dashboard
  await dashboardPage.goto();
  
  // Wait for API call to complete
  await apiPromise;
  await waitForLoadingComplete(authenticatedPage);
  
  // Verify data loaded
  const callCount = await dashboardPage.getRecentCallsCount();
  expect(callCount).toBeGreaterThanOrEqual(0);
});
```

## Example 8: Testing Navigation

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';
import { assertUrlContains } from '../utils/assertions';

test('User can navigate between pages', async ({ authenticatedPage }) => {
  const dashboardPage = new DashboardPage(authenticatedPage);
  
  // Start on dashboard
  await dashboardPage.goto();
  await assertUrlContains(authenticatedPage, '/dashboard');
  
  // Navigate to calls
  await dashboardPage.viewCalls();
  await assertUrlContains(authenticatedPage, '/calls');
  
  // Navigate to analytics
  await dashboardPage.viewAnalytics();
  await assertUrlContains(authenticatedPage, '/analytics');
  
  // Navigate to settings
  await dashboardPage.goToSettings();
  await assertUrlContains(authenticatedPage, '/settings');
});
```

## Example 9: Testing with Multiple Users

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { LoginPage } from '../pages/LoginPage';
import { TEST_ADMIN, TEST_AGENT } from '../fixtures/test-data';

test('Admin user has access to admin panel', async ({ page, loginAs }) => {
  // Login as admin
  await loginAs(TEST_ADMIN.email, TEST_ADMIN.password);
  
  // Navigate to admin panel
  await page.goto('/admin');
  
  // Verify admin access
  expect(page.url()).toContain('/admin');
});

test('Agent user has limited access', async ({ page, loginAs }) => {
  // Login as agent
  await loginAs(TEST_AGENT.email, TEST_AGENT.password);
  
  // Try to access admin panel
  await page.goto('/admin');
  
  // Should be redirected
  await page.waitForTimeout(1000);
  expect(page.url()).not.toContain('/admin');
});
```

## Example 10: Testing Call Audio Controls

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { CallPage } from '../pages/CallPage';
import { TEST_PHONE_NUMBERS } from '../fixtures/test-data';

test('User can control call audio', async ({ authenticatedPage }) => {
  const callPage = new CallPage(authenticatedPage);
  
  await callPage.goto();
  await callPage.startOutboundCall(TEST_PHONE_NUMBERS.valid.us);
  
  // Test mute
  await callPage.mute();
  expect(await callPage.isMuted()).toBe(true);
  
  await callPage.unmute();
  expect(await callPage.isMuted()).toBe(false);
  
  // Test hold
  await callPage.hold();
  await authenticatedPage.waitForTimeout(2000);
  await callPage.resume();
  
  // Test volume
  if (await callPage.volumeSlider.isVisible()) {
    await callPage.setVolume(75);
  }
  
  // End call
  await callPage.endCall();
});
```

## Example 11: Taking Screenshots for Debugging

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';
import { takeScreenshot } from '../utils/helpers';

test('Debug dashboard layout', async ({ authenticatedPage }) => {
  const dashboardPage = new DashboardPage(authenticatedPage);
  
  await dashboardPage.goto();
  
  // Take screenshot of dashboard
  await takeScreenshot(authenticatedPage, 'dashboard-loaded');
  
  // Click something
  await dashboardPage.viewCalls();
  
  // Take another screenshot
  await takeScreenshot(authenticatedPage, 'calls-page');
});
```

## Example 12: Mocking API Responses

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';
import { MOCK_API_RESPONSES } from '../fixtures/test-data';
import { mockApiResponse } from '../utils/helpers';

test('Dashboard handles empty call list', async ({ authenticatedPage }) => {
  // Mock empty call list
  await mockApiResponse(authenticatedPage, '/api/v1/calls', []);
  
  const dashboardPage = new DashboardPage(authenticatedPage);
  await dashboardPage.goto();
  
  // Verify no calls displayed
  const callCount = await dashboardPage.getRecentCallsCount();
  expect(callCount).toBe(0);
});
```

## Example 13: Testing Form Validation

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { LoginPage } from '../pages/LoginPage';

test('Login form validates empty fields', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await loginPage.goto();
  
  // Try to submit empty form
  await loginPage.clickLogin();
  
  // Form should show validation errors or button should be disabled
  const isButtonEnabled = await loginPage.isLoginButtonEnabled();
  
  // Either button is disabled or error is shown
  if (isButtonEnabled) {
    expect(await loginPage.hasError()).toBe(true);
  }
});
```

## Example 14: Testing Logout

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';
import { assertNotAuthenticated } from '../utils/assertions';

test('User can logout successfully', async ({ authenticatedPage, logout }) => {
  const dashboardPage = new DashboardPage(authenticatedPage);
  
  // Navigate to dashboard
  await dashboardPage.goto();
  
  // Perform logout
  await logout();
  
  // Verify logged out
  await assertNotAuthenticated(authenticatedPage);
  expect(authenticatedPage.url()).toContain('/login');
});
```

## Example 15: Testing Cross-Tab Sync (Advanced)

```typescript
import { test, expect } from '../fixtures/auth.fixture';
import { DashboardPage } from '../pages/DashboardPage';

test('Call state syncs across tabs', async ({ authenticatedContext }) => {
  // Open two tabs
  const page1 = await authenticatedContext.newPage();
  const page2 = await authenticatedContext.newPage();
  
  const dashboard1 = new DashboardPage(page1);
  const dashboard2 = new DashboardPage(page2);
  
  // Navigate both to dashboard
  await dashboard1.goto();
  await dashboard2.goto();
  
  // Start call in tab 1
  await dashboard1.startCall();
  
  // Verify call appears in tab 2
  await page2.waitForTimeout(2000); // Wait for sync
  
  // Both tabs should show call in progress
  // (This depends on your implementation)
  
  await page1.close();
  await page2.close();
});
```

## Running These Examples

Save any example to a file in `e2e/tests/` with `.spec.ts` extension:

```bash
# Create new test file
touch e2e/tests/my-new-test.spec.ts

# Run specific test
npx playwright test e2e/tests/my-new-test.spec.ts

# Run with UI
npx playwright test e2e/tests/my-new-test.spec.ts --ui

# Run in debug mode
npx playwright test e2e/tests/my-new-test.spec.ts --debug
```

## Tips

1. **Always use Page Object Models** - Don't interact with page directly
2. **Use custom assertions** - More readable than raw expects
3. **Wait for elements** - Use waitFor* methods before interacting
4. **Reuse auth state** - Use authenticatedPage fixture
5. **Generate test data** - Use helpers for dynamic test data
6. **Take screenshots** - Debug issues with screenshots
7. **Mock when needed** - Mock API responses for edge cases
8. **Clean up** - End calls, logout when needed

## Need More Examples?

Check out the existing test files in `e2e/tests/` for more real-world examples.

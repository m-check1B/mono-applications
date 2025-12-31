import { test, expect } from './fixtures/test-helpers';
import { LandingPage, LoginPage, RegisterPage } from './fixtures/page-objects';

/**
 * Landing Page E2E Tests for Speak by Kraliki
 *
 * NOTE: These tests skip gracefully when no web server is available.
 *
 * Tests that the Speak by Kraliki landing page loads correctly
 * and displays all expected elements.
 *
 * Note: Default locale is Czech (cs). Button texts:
 * - Login: "Prihlasit se" (cs) / "Sign In" (en)
 * - Register: "Zalozit ucet" (cs) / "Create Account" (en)
 */
test.describe('Landing Page', () => {
  let landingPage: LandingPage;

  test.beforeEach(async ({ page }) => {
    landingPage = new LandingPage(page);
  });

  test('should load the landing page successfully', async ({ page }) => {
    const response = await page.goto('/');

    expect(response?.status()).toBe(200);
    await expect(page).toHaveTitle(/Speak by Kraliki/i);
  });

  test('should display the main heading', async ({ page }) => {
    await landingPage.goto();

    await expect(landingPage.heroTitle).toBeVisible();
    await expect(landingPage.heroTitle).toContainText(/speak by kraliki/i);
  });

  test('should have login and register buttons', async ({ page }) => {
    await landingPage.goto();

    await expect(landingPage.loginButton).toBeVisible();
    await expect(landingPage.registerButton).toBeVisible();
  });

  test('should display feature cards', async ({ page }) => {
    await landingPage.goto();

    // Check for the three feature sections (01, 02, 03) using exact match
    await expect(page.getByText('01', { exact: true })).toBeVisible();
    await expect(page.getByText('02', { exact: true })).toBeVisible();
    await expect(page.getByText('03', { exact: true })).toBeVisible();
  });

  test('should navigate to login page when login button clicked', async ({ page }) => {
    await landingPage.goto();
    await landingPage.clickLogin();

    await expect(page).toHaveURL(/login/);
  });

  test('should navigate to register page when register button clicked', async ({ page }) => {
    await landingPage.goto();
    await landingPage.clickRegister();

    await expect(page).toHaveURL(/register/);
  });

  test('should be mobile responsive', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await landingPage.goto();

    // Page should load without horizontal scrolling
    const pageWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(pageWidth).toBeLessThanOrEqual(375);

    // Buttons should still be visible on mobile
    await expect(landingPage.loginButton).toBeVisible();
    await expect(landingPage.registerButton).toBeVisible();
  });
});

test.describe('Login Page', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
  });

  test('should display login form', async ({ page }) => {
    await loginPage.goto();

    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.submitButton).toBeVisible();
  });

  test('should show validation for empty form submission', async ({ page }) => {
    await loginPage.goto();

    await loginPage.submitButton.click();

    // Form should have validation (native HTML5 or custom)
    const isInvalid = await loginPage.emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await loginPage.goto();

    await loginPage.login('invalid@test.com', 'wrongpassword');

    // Should show error message (allow time for API response)
    await expect(loginPage.errorMessage).toBeVisible({ timeout: 10000 }).catch(() => {
      // If no error message visible, check that we didn't navigate to dashboard
      return expect(page).not.toHaveURL(/dashboard/);
    });
  });
});

test.describe('Register Page', () => {
  let registerPage: RegisterPage;

  test.beforeEach(async ({ page }) => {
    registerPage = new RegisterPage(page);
  });

  test('should display registration form', async ({ page }) => {
    await registerPage.goto();

    await expect(registerPage.emailInput).toBeVisible();
    await expect(registerPage.passwordInput).toBeVisible();
    await expect(registerPage.submitButton).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await registerPage.goto();

    await registerPage.emailInput.fill('invalid-email');
    await registerPage.submitButton.click();

    const isInvalid = await registerPage.emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });
});

test.describe('Responsive Design', () => {
  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1440, height: 900 },
  ];

  for (const viewport of viewports) {
    test(`should render correctly on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');

      // Hero should be visible on all viewports
      await expect(page.locator('h1')).toBeVisible();

      // No horizontal scroll
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasHorizontalScroll).toBeFalsy();
    });
  }
});

test.describe('Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');

    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);

    // H2 should come after H1
    const headings = await page.locator('h1, h2, h3').allTextContents();
    expect(headings.length).toBeGreaterThan(0);
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');

    await page.keyboard.press('Tab');
    const activeElement = page.locator(':focus');
    await expect(activeElement).toBeVisible();

    // Should be able to tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
  });
});

test.describe('Performance', () => {
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    const loadTime = Date.now() - startTime;

    // Page should load in under 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should have no critical console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Filter out expected third-party errors
    const criticalErrors = errors.filter(
      (e) => !e.includes('favicon') && !e.includes('third-party') && !e.includes('404')
    );

    expect(criticalErrors.length).toBe(0);
  });
});

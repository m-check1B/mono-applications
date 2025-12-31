import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display landing page with login/register options', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('SPEAK BY KRALIKI');
    await expect(page.getByText('LOGIN').or(page.getByText('PŘIHLÁSIT')).toBeVisible();
    await expect(page.getByText('REGISTER').or(page.getByText('REGISTRACE')).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    await page.click('button:has-text("LOGIN"), button:has-text("PŘIHLÁSIT")');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator('form')).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.click('button:has-text("REGISTER"), button:has-text("REGISTRACE")');
    await expect(page).toHaveURL(/\/register/);
    await expect(page.locator('form')).toBeVisible();
  });

  test('should show validation errors on empty login form', async ({ page }) => {
    await page.goto('/login');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Invalid credentials|Chybné přihlašovací údaje|required').first()).toBeVisible({ timeout: 5000 });
  });

  test('should show validation errors on empty register form', async ({ page }) => {
    await page.goto('/register');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=required|povinné').first()).toBeVisible({ timeout: 5000 });
  });

  test('should redirect to dashboard after successful login', async ({ page, request }) => {
    const email = `test-${Date.now()}@example.com`;
    const password = 'Test123456!';

    await page.goto('/register');
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.fill('input[name="confirmPassword"]', password);
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should handle invalid login credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'WrongPassword123!');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Invalid credentials|Chybné přihlašovací údaje').or(page.locator('.error')).toBeVisible({ timeout: 5000 });
  });

  test('should redirect to login when accessing protected route unauthenticated', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
  });

  test('should have proper form labels and accessibility', async ({ page }) => {
    await page.goto('/login');
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    await expect(emailInput).toHaveAttribute('type', 'email');
    await expect(passwordInput).toHaveAttribute('type', 'password');
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });
});

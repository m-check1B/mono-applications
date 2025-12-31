import { test, expect } from '@playwright/test';
import { faker } from '@faker-js/faker';
import { getAdminCredentials } from './utils/test-credentials';

const adminCredentials = getAdminCredentials();

test.describe('Authentication Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/CC-Light/);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // Use seeded credentials
    await page.fill('input[type="email"]', adminCredentials.email);
    await page.fill('input[type="password"]', adminCredentials.password);
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await page.waitForURL('**/dashboard');
    await expect(page.locator('text=/CC-LIGHT/i')).toBeVisible();
    
    // Check for dashboard elements
    await expect(page.locator('text=/ACTIVE CALLS/i')).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', faker.internet.email());
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=/Invalid credentials/i')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"]', adminCredentials.email);
    await page.fill('input[type="password"]', adminCredentials.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Find and click logout
    await page.click('button[aria-label="User menu"]');
    await page.click('text=/Logout/i');

    // Should redirect to login
    await page.waitForURL('**/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('should handle session expiry', async ({ page, context }) => {
    // Login
    await page.fill('input[type="email"]', adminCredentials.email);
    await page.fill('input[type="password"]', adminCredentials.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Clear cookies to simulate session expiry
    await context.clearCookies();
    
    // Try to navigate to protected route
    await page.goto('/dashboard');
    
    // Should redirect to login
    await page.waitForURL('**/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('should handle multiple login attempts', async ({ page }) => {
    // Try invalid login multiple times
    for (let i = 0; i < 3; i++) {
      await page.fill('input[type="email"]', adminCredentials.email);
      await page.fill('input[type="password"]', 'wrong');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(500);
    }

    // Should still allow valid login
    await page.fill('input[type="email"]', adminCredentials.email);
    await page.fill('input[type="password"]', adminCredentials.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });
});

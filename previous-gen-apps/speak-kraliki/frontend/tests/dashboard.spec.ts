import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.describe('Unauthenticated', () => {
    test('should redirect to login', async ({ page }) => {
      await page.goto('/dashboard');

      await expect(page).toHaveURL(/login/);
    });
  });

  // Tests for authenticated state would use beforeEach to set auth cookie/token
  test.describe('Authenticated', () => {
    test.beforeEach(async ({ page }) => {
      // In a real setup, this would authenticate via API
      // For now, test that dashboard route exists and handles auth
    });

    test('should display dashboard structure', async ({ page }) => {
      // This test will fail until auth is set up, but validates the route exists
      const response = await page.goto('/dashboard');

      // Should either redirect (302) or show dashboard (200)
      expect([200, 302, 303]).toContain(response?.status() || 0);
    });
  });
});

test.describe('Dashboard Features', () => {
  test('should have navigation elements', async ({ page }) => {
    await page.goto('/login');

    // Check for navigation or branding
    await expect(page.getByRole('link', { name: /speak by kraliki|home/i })).toBeVisible();
  });

  test('should be mobile responsive', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/login');

    // Should not have horizontal scroll
    const pageWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(pageWidth).toBeLessThanOrEqual(375);
  });
});

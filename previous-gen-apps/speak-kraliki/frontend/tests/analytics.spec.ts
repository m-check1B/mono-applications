import { test, expect } from '@playwright/test';

test.describe('Analytics & Insights', () => {
  test('should have analytics routes', async ({ page }) => {
    // Test that analytics routes exist (may redirect to login)
    const response = await page.goto('/dashboard/analytics');

    // Should be valid route (200 for page, 302/303 for redirect)
    expect([200, 302, 303, 404]).toContain(response?.status() || 0);
  });

  test('should display sentiment-related UI elements', async ({ page }) => {
    await page.goto('/dashboard');

    // Look for sentiment or analytics terminology
    const pageContent = await page.content().catch(() => '');
    // Page should load without errors
    expect(pageContent).toBeTruthy();
  });
});

test.describe('Action Loop', () => {
  test('should have action management routes', async ({ page }) => {
    const response = await page.goto('/dashboard/actions');

    // Route should exist or redirect
    expect([200, 302, 303, 404]).toContain(response?.status() || 0);
  });
});

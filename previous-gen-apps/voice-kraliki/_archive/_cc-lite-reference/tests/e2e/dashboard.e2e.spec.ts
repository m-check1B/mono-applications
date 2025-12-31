import { test, expect } from '@playwright/test';

test.describe('Marketing landing smoke', () => {
  test('loads hero section on home page', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading')).toBeVisible();
  });
});

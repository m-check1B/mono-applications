import { test, expect } from '@playwright/test';

const DEMO_EMAIL = 'agent@cc-light.com';
const DEMO_PASSWORD = 'demo123';

test.describe('CC-Light E2E Smoke', () => {
  test('loads login screen and accepts demo credentials', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: /cc-light/i })).toBeVisible();

    await page.getByLabel(/email/i).fill(DEMO_EMAIL);
    await page.getByLabel(/password/i).fill(DEMO_PASSWORD);

    await expect(page.locator('form').getByRole('button', { name: /sign in/i })).toBeEnabled();
  });
});

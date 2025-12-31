import { test, expect } from '@playwright/test';

test.describe('Auth workflow smoke', () => {
  test('redirects unauthenticated user to login', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/login/);
  });

  test('shows validation message for empty submit', async ({ page }) => {
    await page.goto('/login');
    await page.locator('form').getByRole('button', { name: /sign in/i }).click();
    await expect(page.getByText('Please provide both email and password.')).toBeVisible();
  });
});

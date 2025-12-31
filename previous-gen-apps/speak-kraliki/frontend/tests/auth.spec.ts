import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');

    await expect(page).toHaveTitle(/Speak by Kraliki/);
    await expect(page.getByRole('heading', { name: /login|sign in/i })).toBeVisible();
  });

  test('should display registration page', async ({ page }) => {
    await page.goto('/register');

    await expect(page.getByRole('heading', { name: /register|sign up|create account/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/login/);
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.getByLabel(/email/i).fill('invalid@test.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    await page.getByRole('button', { name: /login|sign in/i }).click();

    // Should show error message
    await expect(page.getByText(/invalid|error|failed/i)).toBeVisible({ timeout: 5000 });
  });
});

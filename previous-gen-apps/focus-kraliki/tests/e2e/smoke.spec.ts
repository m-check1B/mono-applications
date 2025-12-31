import { test, expect } from '@playwright/test';

const API_BASE =
  process.env.FOCUS_KRALIKI_API_URL ||
  process.env.FOCUS_KRALIKI_API_URL || process.env.FOCUS_LITE_API_URL ||
  'http://127.0.0.1:3017';

test('API health endpoint responds with healthy or degraded', async ({ request }) => {
  const res = await request.get(`${API_BASE}/health`);
  expect(res.ok()).toBeTruthy();
  const json = await res.json();
  expect(json).toHaveProperty('status');
  expect(json).toHaveProperty('database');
});

test.describe('Auth + Task smoke (requires DB)', () => {
  test('register, login, see dashboard (UI)', async ({ page }) => {
    await page.goto('/login');

    // Switch to Sign Up
    await page.getByRole('button', { name: 'Sign Up' }).click();

    const email = `e2e+${Date.now()}@example.com`;
    await page.getByLabel('Name').fill('E2E User');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('e2e-test-password');
    await page.getByRole('button', { name: /Create Account|Sign Up|Create/i }).click();

    // After successful register, should navigate to app shell
    await page.waitForURL(url => !url.pathname.includes('/login'));
    await expect(page.getByRole('heading', { name: /Dashboard/i })).toBeVisible({ timeout: 10000 });
  });
});

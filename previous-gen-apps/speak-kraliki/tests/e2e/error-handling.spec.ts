import { test, expect } from '@playwright/test';

test.describe('Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    await page.route('**/api/**', route => route.abort('failed'));

    await page.goto('/');
    await page.click('button:has-text("LOGIN"), button:has-text("PŘIHLÁSIT")');

    await expect(page.locator('text=Network error|Chyba sítě|Failed to fetch').or(page.locator('.error, [role="alert"]')).toBeVisible({ timeout: 5000 });
  });

  test('should handle 404 pages', async ({ page }) => {
    await page.goto('/non-existent-page-404');

    await expect(page.locator('text=404|Not Found|Nenalezeno').or(page.locator('text=CHYBA')).toBeVisible({ timeout: 5000 });
  });

  test('should handle server errors (500)', async ({ page }) => {
    await page.route('**/api/auth/**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });

    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=500|Server error|Chyba serveru').or(page.locator('.error')).toBeVisible({ timeout: 5000 });
  });

  test('should handle invalid tokens in voice flow', async ({ page }) => {
    await page.route('**/api/speak/employee/consent/**', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid or expired token' })
      });
    });

    await page.goto('/v/invalid-token-123');

    await expect(page.locator('text=CHYBA|ERROR').or(page.locator('text=Neplatný nebo vypršel|Invalid or expired')).toBeVisible({ timeout: 5000 });
  });

  test('should handle microphone permission denial', async ({ page, context }) => {
    await context.clearPermissions();
    await page.goto(`/v/test-token-${Date.now()}`);
    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');

    await expect(page.getByText(/PŘEJÍT NA TEXT|SWITCH TO TEXT/)).toBeVisible({ timeout: 5000 });
  });

  test('should show loading states during API calls', async ({ page }) => {
    await page.route('**/api/speak/surveys*', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      route.continue();
    });

    await page.goto('/dashboard/surveys');

    await expect(page.locator('[class*="loading"], [class*="spinner"], [aria-busy="true"]')).toBeVisible({ timeout: 5000 });
  });

  test('should handle timeout errors', async ({ page }) => {
    await page.route('**/api/**', route => {
      route.abort('timedout');
    });

    await page.goto('/dashboard');

    await expect(page.locator('text=timeout|vypršel čas|Connection timeout').or(page.locator('.error')).toBeVisible({ timeout: 5000 });
  });

  test('should maintain user session on auth token expiration', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
    await expect(page.getByText(/login|přihlásit/i)).toBeVisible();
  });

  test('should handle malformed API responses', async ({ page }) => {
    await page.route('**/api/speak/surveys*', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: '{ invalid json '
      });
    });

    await page.goto('/dashboard/surveys');

    await expect(page.locator('text=Error|Chyba').or(page.locator('.error')).toBeVisible({ timeout: 5000 });
  });
});

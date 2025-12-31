import { test, expect } from '@playwright/test';

test.describe('Voice Feedback Flow', () => {
  const testToken = 'test-token-' + Date.now();

  test('should display consent screen on first visit', async ({ page }) => {
    await page.goto(`/v/${testToken}`);

    await expect(page.locator('h1')).toContainText('SPEAK BY KRALIKI');
    await expect(page.getByText(/ROZUMÍM|POJĎME|CONSENT/)).toBeVisible();
    await expect(page.getByText(/ANONYMNÍ|ANONYMOUS/)).toBeVisible();
  });

  test('should show trust layer messages', async ({ page }) => {
    await page.goto(`/v/${testToken}`);

    await expect(page.getByText(/nadřízený NEUVIDÍ|manager won't see/i)).toBeVisible();
    await expect(page.getByText(/agregované trendy|aggregated data/i)).toBeVisible();
    await expect(page.getByText(/přečíst a upravit přepis|review and edit transcript/i)).toBeVisible();
  });

  test('should allow skipping monthly check-in', async ({ page }) => {
    await page.goto(`/v/${testToken}`);

    await page.click('button:has-text("PŘESKOČIT"), button:has-text("SKIP")');
    
    await expect(page.locator('text=DĚKUJEME|THANK YOU').or(page.locator('.brutal-card'))).toBeVisible({ timeout: 5000 });
  });

  test('should activate voice interface after consent', async ({ page, context }) => {
    await context.grantPermissions(['microphone']);
    await page.goto(`/v/${testToken}`);

    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');

    await expect(page.locator('text=Hlasový režim|Voice mode')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/MLUV DO MIKROFONU|SPEAK INTO MICROPHONE/)).toBeVisible();
  });

  test('should display transcript area', async ({ page }) => {
    await page.goto(`/v/${testToken}`);
    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');

    await expect(page.locator('.overflow-y-auto, [class*="transcript"]')).toBeVisible({ timeout: 5000 });
  });

  test('should allow switching to text mode', async ({ page }) => {
    await page.goto(`/v/${testToken}`);
    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');

    await page.click('button:has-text("PŘEJÍT NA TEXT"), button:has-text("SWITCH TO TEXT")');

    await expect(page.locator('text=Textový režim|Text mode')).toBeVisible();
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('should allow sending text messages', async ({ page }) => {
    await page.goto(`/v/${testToken}`);
    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');
    await page.click('button:has-text("PŘEJÍT NA TEXT"), button:has-text("SWITCH TO TEXT")');

    await page.fill('input[type="text"]', 'Test message');
    await page.click('button:has-text("ODESLAT"), button:has-text("SEND")');

    await expect(page.locator('text=Test message').or(page.locator('[class*="transcript"]'))).toBeVisible({ timeout: 5000 });
  });

  test('should end conversation and show completion screen', async ({ page }) => {
    await page.goto(`/v/${testToken}`);
    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');

    await page.click('button:has-text("UKONČIT"), button:has-text("END")');

    await expect(page.locator('text=DĚKUJEME|THANK YOU')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('ZOBRAZIT PŘEPIS').or(page.getByText('VIEW TRANSCRIPT'))).toBeVisible();
  });

  test('should show action loop widget when public actions exist', async ({ page }) => {
    await page.route('**/api/speak/actions/public/*', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: '1', topic: 'Test Topic', status: 'in_progress', public_message: 'Working on it' }
        ])
      });
    });

    await page.goto(`/v/${testToken}`);

    await expect(page.getByText(/Co děláme s vaší zpětnou vazbou|What we do with your feedback/i)).toBeVisible();
    await expect(page.getByText(/Test Topic/)).toBeVisible();
  });

  test('should handle invalid/expired tokens', async ({ page }) => {
    await page.goto('/v/invalid-expired-token-12345');

    await expect(page.locator('text=CHYBA|ERROR').or(page.locator('text=Neplatný nebo vypršel|Invalid or expired')).toBeVisible({ timeout: 5000 });
  });

  test('should display AI indicator when processing', async ({ page }) => {
    await page.goto(`/v/${testToken}`);
    await page.click('button:has-text("ROZUMÍM"), button:has-text("UNDERSTAND")');

    await expect(page.locator('text=SPEAK BY KRALIKI')).toBeVisible();
    await expect(page.locator('text=Přemýšlím...|Thinking...').or(page.locator('[class*="animate-pulse"]')).toBeVisible({ timeout: 5000 });
  });
});

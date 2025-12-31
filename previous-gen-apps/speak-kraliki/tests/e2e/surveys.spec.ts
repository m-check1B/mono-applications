import { test, expect } from '@playwright/test';

test.describe('Surveys Management', () => {
  test('should display surveys list page', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    await expect(page.locator('text=Surveys|Průzkumy').or(page.locator('h1'))).toBeVisible();
  });

  test('should have create survey button', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    await expect(page.getByRole('button', { name: /create|new|nový|vytvořit/i })).toBeVisible({ timeout: 5000 });
  });

  test('should display survey cards', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    await expect(page.locator('.brutal-card, [class*="card"]').or(page.locator('[class*="survey"]')).toBeVisible({ timeout: 5000 });
  });

  test('should show survey status indicators', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    
    const statusElements = await page.locator('text=active|inactive|draft|completed|aktivní|neaktivní|koncept').all();
    expect(statusElements.length).toBeGreaterThan(0);
  });

  test('should have delete action for surveys', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    await expect(page.locator('button:has-text("Delete"), button:has-text("Smazat")').or(page.locator('[aria-label*="delete"]')).first()).toBeVisible({ timeout: 5000 });
  });

  test('should allow creating new survey', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    await page.click('button:has-text("Create"), button:has-text("Nový"), button:has-text("Vytvořit")');

    await expect(page.locator('input[name="title"]').or(page.locator('input[placeholder*="title"]'))).toBeVisible({ timeout: 5000 });
  });

  test('should validate survey title is required', async ({ page }) => {
    await page.goto('/dashboard/surveys');
    await page.click('button:has-text("Create"), button:has-text("Nový"), button:has-text("Vytvořit")');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=required|povinné').or(page.locator('.error')).toBeVisible({ timeout: 5000 });
  });

  test('should display empty state when no surveys exist', async ({ page }) => {
    await page.route('**/api/speak/surveys*', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.goto('/dashboard/surveys');
    await expect(page.getByText(/no surveys|žádné průzkumy/i).or(page.locator('text=empty')).or(page.locator('[class*="empty"]'))).toBeVisible({ timeout: 5000 });
  });
});

import { test, expect } from '@playwright/test';

test.describe('Actions Management', () => {
  test('should display actions list page', async ({ page }) => {
    await page.goto('/dashboard/actions');
    await expect(page.locator('text=Actions|Akce').or(page.locator('h1'))).toBeVisible();
  });

  test('should display action cards with status', async ({ page }) => {
    await page.goto('/dashboard/actions');
    
    await expect(page.locator('.brutal-card, [class*="card"]').or(page.locator('[class*="action"]')).toBeVisible({ timeout: 5000 });
  });

  test('should have status indicators for actions', async ({ page }) => {
    await page.goto('/dashboard/actions');

    const statusElements = await page.locator('text=new|heard|in_progress|resolved|nový|slyšíme|resíme|vyřešeno').all();
    expect(statusElements.length).toBeGreaterThan(0);
  });

  test('should allow updating action status', async ({ page }) => {
    await page.goto('/dashboard/actions');

    const actionCard = page.locator('.brutal-card, [class*="card"]').or(page.locator('[class*="action"]')).first();
    await actionCard.click({ timeout: 5000 });

    await expect(page.locator('button:has-text("Mark as Heard"), button:has-text("Slyšíme vás")').or(page.locator('button:has-text("Mark as Resolved"), button:has-text("Vyřešeno")')).toBeVisible({ timeout: 5000 });
  });

  test('should have public message field', async ({ page }) => {
    await page.goto('/dashboard/actions');

    const actionCard = page.locator('.brutal-card, [class*="card"]').or(page.locator('[class*="action"]')).first();
    await actionCard.click({ timeout: 5000 });

    await expect(page.locator('textarea[name="public_message"]').or(page.locator('[class*="public-message"]'))).toBeVisible({ timeout: 5000 });
  });

  test('should show empty state when no actions exist', async ({ page }) => {
    await page.route('**/api/speak/actions*', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await page.goto('/dashboard/actions');
    await expect(page.getByText(/no actions|žádné akce/i).or(page.locator('text=empty')).or(page.locator('[class*="empty"]'))).toBeVisible({ timeout: 5000 });
  });

  test('should display action topic and status badge', async ({ page }) => {
    await page.goto('/dashboard/actions');

    const actionCard = page.locator('.brutal-card, [class*="card"]').or(page.locator('[class*="action"]')).first();
    
    await expect(actionCard).toBeVisible({ timeout: 5000 });
    
    const cardText = await actionCard.textContent();
    expect(cardText?.length).toBeGreaterThan(0);
  });
});

import { test, expect } from '@playwright/test';

test.describe('Navigation smoke', () => {
  test('shows pricing plans on the marketing page', async ({ page }) => {
    await page.goto('/pricing');

    await expect(page.getByRole('heading', { name: /choose your plan/i })).toBeVisible();

    for (const plan of ['Starter', 'Professional', 'Enterprise']) {
      await expect(page.getByRole('heading', { name: plan })).toBeVisible();
    }

    await expect(page.getByText(/\$29\b/)).toBeVisible();
    await page.getByRole('button', { name: /yearly/i }).click();
    await expect(page.getByText(/\$290\b/)).toBeVisible();
    await page.getByRole('button', { name: /^Monthly$/i }).click();
    await expect(page.getByText(/\$29\b/)).toBeVisible();

    await expect(page.getByRole('heading', { name: /all plans include/i })).toBeVisible();
  });
});

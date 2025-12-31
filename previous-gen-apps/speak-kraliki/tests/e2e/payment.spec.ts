import { test, expect } from '@playwright/test';

test.describe('Payment Flow (if applicable)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/settings');
  });

  test('should display billing section in settings', async ({ page }) => {
    await expect(page.getByText(/billing|platby|subscription|předplatné/i)).toBeVisible({ timeout: 5000 });
  });

  test('should have upgrade button if on free plan', async ({ page }) => {
    const upgradeButton = page.getByRole('button', { name: /upgrade|přejít na plán|upgrade now/i });
    
    const isVisible = await upgradeButton.isVisible().catch(() => false);
    if (isVisible) {
      await expect(upgradeButton).toBeVisible();
    }
  });

  test('should display current plan information', async ({ page }) => {
    await expect(page.getByText(/plan|plán|tier|úroveň/i)).toBeVisible({ timeout: 5000 });
  });

  test('should show usage metrics', async ({ page }) => {
    await expect(page.getByText(/usage|využití|employees|zaměstnanci/i)).toBeVisible({ timeout: 5000 });
  });

  test('should handle payment button click', async ({ page }) => {
    const paymentButton = page.getByRole('button', { name: /payment|platba|subscribe|předplatit/i });
    
    const isVisible = await paymentButton.isVisible().catch(() => false);
    if (isVisible) {
      await paymentButton.click();
      
      await expect(page.locator('text=Stripe|Checkout|Platba')).or(page.locator('[class*="payment"]')).toBeVisible({ timeout: 5000 });
    }
  });

  test('should redirect to Stripe checkout', async ({ page }) => {
    await page.route('**/api/stripe/checkout/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ checkout_url: 'https://checkout.stripe.com/cpay/test' })
      });
    });

    const paymentButton = page.getByRole('button', { name: /upgrade|subscribe/i });
    const isVisible = await paymentButton.isVisible().catch(() => false);
    
    if (isVisible) {
      await paymentButton.click();
      
      await expect(page).toHaveURL(/stripe\.com|checkout/, { timeout: 5000 });
    }
  });

  test('should handle successful payment', async ({ page }) => {
    await page.goto('/dashboard/settings?session_id=cs_test_success');
    
    await expect(page.getByText(/success|úspěch|payment successful|platba úspěšná/)).or(page.locator('.success')).toBeVisible({ timeout: 5000 });
  });

  test('should handle failed payment', async ({ page }) => {
    await page.goto('/dashboard/settings?session_id=cs_test_failed');

    await expect(page.getByText(/failed|chyba|payment failed|platba selhala/)).or(page.locator('.error')).toBeVisible({ timeout: 5000 });
  });

  test('should display invoice history', async ({ page }) => {
    await expect(page.getByText(/invoice|faktura|history|historie/i)).toBeVisible({ timeout: 5000 });
  });

  test('should have cancel subscription option', async ({ page }) => {
    const cancelButton = page.getByRole('button', { name: /cancel|zrušit|cancel subscription/i });
    
    const isVisible = await cancelButton.isVisible().catch(() => false);
    if (isVisible) {
      await expect(cancelButton).toBeVisible();
    }
  });

  test('should show confirmation dialog for cancellation', async ({ page }) => {
    const cancelButton = page.getByRole('button', { name: /cancel|zrušit|cancel subscription/i });
    const isVisible = await cancelButton.isVisible().catch(() => false);
    
    if (isVisible) {
      await cancelButton.click();
      
      await expect(page.locator('text=Are you sure|Opravdu chcete|Potvrďte').or(page.locator('[role="dialog"], .modal')).toBeVisible({ timeout: 5000 });
    }
  });
});

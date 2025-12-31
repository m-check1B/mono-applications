import { test, expect } from '@playwright/test';

/**
 * Demo Request Form E2E Tests
 *
 * Tests the demo request flow for Lab by Kraliki.
 * Note: The demo request form is planned but not yet implemented.
 * These tests are prepared for when the form is added to the landing page.
 */

test.describe('Demo Request Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should have a Book Demo CTA button', async ({ page }) => {
    // Find the demo CTA button
    const demoCTA = page.locator('a[href*="demo"], .btn:has-text("Demo")');
    const demoButton = demoCTA.first();

    await expect(demoButton).toBeVisible();
  });

  test('should navigate to demo section when CTA is clicked', async ({ page }) => {
    // Find the demo CTA
    const demoCTA = page.locator('a[href="#demo"]');

    if (await demoCTA.count() > 0) {
      await demoCTA.click();

      // Check that URL now has #demo anchor
      await expect(page).toHaveURL(/#demo/);
    } else {
      // If no demo anchor link, check for demo-related text
      const demoText = page.getByText(/book.*demo|request.*demo|schedule.*demo/i);
      await expect(demoText.first()).toBeVisible();
    }
  });

  test('CTA section should be visible and have call-to-action', async ({ page }) => {
    const ctaSection = page.locator('.cta-section');
    await expect(ctaSection).toBeVisible();

    // Check for CTA heading
    const ctaHeading = ctaSection.locator('h2');
    await expect(ctaHeading).toBeVisible();

    // Check for CTA button
    const ctaButton = ctaSection.locator('.btn');
    await expect(ctaButton).toBeVisible();
  });

  // Future tests for when form is implemented
  test.describe('Demo Request Form - Future Implementation', () => {
    test.skip('should display demo request form with required fields', async ({ page }) => {
      // Navigate to demo section
      await page.goto('/sample-landing-page.html#demo');

      // Expected form fields for demo request
      const nameField = page.locator('input[name="name"], input#name');
      const emailField = page.locator('input[type="email"], input[name="email"]');
      const companyField = page.locator('input[name="company"]');
      const submitButton = page.locator('button[type="submit"], input[type="submit"]');

      await expect(nameField).toBeVisible();
      await expect(emailField).toBeVisible();
      await expect(companyField).toBeVisible();
      await expect(submitButton).toBeVisible();
    });

    test.skip('should validate email format in demo request form', async ({ page }) => {
      await page.goto('/sample-landing-page.html#demo');

      const emailField = page.locator('input[type="email"]');
      const submitButton = page.locator('button[type="submit"]');

      // Enter invalid email
      await emailField.fill('invalid-email');
      await submitButton.click();

      // Should show validation error
      const errorMessage = page.locator('.error-message, [role="alert"]');
      await expect(errorMessage).toBeVisible();
    });

    test.skip('should submit demo request form successfully', async ({ page }) => {
      await page.goto('/sample-landing-page.html#demo');

      // Fill out form
      await page.fill('input[name="name"]', 'Test User');
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[name="company"]', 'Test Company');

      // Submit
      await page.click('button[type="submit"]');

      // Should show success message
      const successMessage = page.locator('.success-message, [role="status"]');
      await expect(successMessage).toBeVisible();
      await expect(successMessage).toContainText(/thank|success|received/i);
    });
  });
});

test.describe('Trial Signup CTA', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should have Start Free Trial CTA in hero section', async ({ page }) => {
    const trialCTA = page.locator('.hero-ctas .btn-primary');
    await expect(trialCTA).toBeVisible();
    await expect(trialCTA).toHaveText(/Start Free Trial/i);
  });

  test('should have CTA in the CTA section', async ({ page }) => {
    const ctaSection = page.locator('.cta-section');
    const ctaButton = ctaSection.locator('.btn');

    await expect(ctaButton).toBeVisible();
    await expect(ctaButton).toHaveText(/Start|Trial|Demo|Apply/i);
  });
});

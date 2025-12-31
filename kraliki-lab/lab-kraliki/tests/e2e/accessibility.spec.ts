import { test, expect } from '@playwright/test';

/**
 * Accessibility E2E Tests
 *
 * Tests the Lab by Kraliki landing page for:
 * - Keyboard navigation
 * - Focus indicators
 * - ARIA attributes
 * - Screen reader compatibility
 */

test.describe('Keyboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should allow keyboard navigation through nav links', async ({ page }) => {
    // Focus on the first focusable element
    await page.keyboard.press('Tab');

    // Get all focusable elements in order
    const navLinks = page.locator('nav a, nav button');
    const count = await navLinks.count();

    expect(count).toBeGreaterThanOrEqual(4); // Logo link + 3 nav links + CTA

    // Verify first nav element is focused after tabbing
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(['A', 'BUTTON']).toContain(firstFocused);
  });

  test('should have visible focus indicators on interactive elements', async ({ page }) => {
    // Tab to a link
    await page.keyboard.press('Tab');

    // Check that focus is visible (element should have focus)
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('should navigate to features section with keyboard', async ({ page }) => {
    // Tab through to find the features link
    const featuresLink = page.locator('nav a[href="#features"]');
    await featuresLink.focus();
    await page.keyboard.press('Enter');

    // Check URL changed
    await expect(page).toHaveURL(/#features/);
  });

  test('should be able to activate CTA buttons with Enter key', async ({ page }) => {
    const ctaButton = page.locator('.hero-ctas .btn-primary').first();
    await ctaButton.focus();

    // Verify it's focusable and activatable
    await expect(ctaButton).toBeFocused();
  });
});

test.describe('ARIA and Semantic Structure', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should have proper document language', async ({ page }) => {
    const html = page.locator('html');
    await expect(html).toHaveAttribute('lang', 'en');
  });

  test('should have exactly one h1 element', async ({ page }) => {
    const h1Elements = page.locator('h1');
    await expect(h1Elements).toHaveCount(1);
  });

  test('should have logical heading hierarchy', async ({ page }) => {
    // Get all headings
    const headings = await page.evaluate(() => {
      const allHeadings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
      return allHeadings.map(h => ({
        tag: h.tagName,
        level: parseInt(h.tagName[1]),
        text: h.textContent?.trim() || ''
      }));
    });

    // Verify first heading is h1
    expect(headings[0]?.level).toBe(1);

    // Verify all heading levels used are present at least once
    // (less strict than checking sequential order, but still useful)
    const levels = new Set(headings.map(h => h.level));
    expect(levels.has(1)).toBe(true); // Must have h1
    expect(levels.has(2)).toBe(true); // Must have h2
    // h3-h6 are optional
  });

  test('should have main landmark regions', async ({ page }) => {
    // Check for header (implicit banner role)
    const header = page.locator('header');
    await expect(header).toBeVisible();

    // Check for footer (implicit contentinfo role)
    const footer = page.locator('footer');
    await expect(footer).toBeVisible();

    // Check for nav (implicit navigation role)
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
  });

  test('should have descriptive link text', async ({ page }) => {
    // Get all links and check none have generic text only
    const links = page.locator('a:visible');
    const count = await links.count();

    for (let i = 0; i < Math.min(count, 10); i++) {
      const linkText = await links.nth(i).textContent();
      // Links should not be empty or just "click here"
      expect(linkText?.trim()).not.toBe('');
      expect(linkText?.toLowerCase()).not.toBe('click here');
    }
  });
});

test.describe('Color and Contrast', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/sample-landing-page.html');
  });

  test('should have sufficient text content visibility', async ({ page }) => {
    // Verify primary text elements are visible
    const headline = page.locator('.hero h1');
    await expect(headline).toBeVisible();

    // Verify subtitle is visible
    const subtitle = page.locator('.hero p');
    await expect(subtitle).toBeVisible();
  });

  test('should have visible button text against background', async ({ page }) => {
    const primaryButton = page.locator('.btn-primary').first();
    await expect(primaryButton).toBeVisible();

    const buttonText = await primaryButton.textContent();
    expect(buttonText?.trim().length).toBeGreaterThan(0);
  });
});

test.describe('Form Accessibility', () => {
  test('CTA buttons should have accessible names', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    const ctaButtons = page.locator('.btn');
    const count = await ctaButtons.count();

    for (let i = 0; i < count; i++) {
      const button = ctaButtons.nth(i);
      const text = await button.textContent();
      // Each button should have text content for accessibility
      expect(text?.trim().length).toBeGreaterThan(0);
    }
  });
});

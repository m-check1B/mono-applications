import { test, expect } from '@playwright/test';

/**
 * Performance E2E Tests
 *
 * Tests the Lab by Kraliki landing page for:
 * - Page load performance
 * - Resource loading
 * - Interaction readiness
 */

test.describe('Page Load Performance', () => {
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/sample-landing-page.html');

    const loadTime = Date.now() - startTime;

    // Page should load in under 3 seconds for a static page
    expect(loadTime).toBeLessThan(3000);
  });

  test('should have content visible quickly (First Contentful Paint)', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    // Check that hero content is immediately visible
    const hero = page.locator('.hero');
    await expect(hero).toBeVisible({ timeout: 1000 });
  });

  test('should have all critical sections loaded', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    // All major sections should be present
    const sections = [
      'header',
      '.hero',
      '.features',
      '.social-proof',
      '.cta-section',
      'footer'
    ];

    for (const selector of sections) {
      const section = page.locator(selector);
      await expect(section).toBeVisible({ timeout: 2000 });
    }
  });
});

test.describe('Resource Loading', () => {
  test('should not have broken images', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    // Get all images and check they loaded
    const images = page.locator('img');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const naturalWidth = await img.evaluate(
        (el: HTMLImageElement) => el.naturalWidth
      );
      // Image should have loaded (naturalWidth > 0)
      expect(naturalWidth).toBeGreaterThan(0);
    }
  });

  test('should load stylesheets correctly', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    // Check that CSS is applied by verifying a styled element
    const logo = page.locator('.logo');
    const color = await logo.evaluate(el => getComputedStyle(el).color);

    // Color should be set (not default black)
    expect(color).not.toBe('rgb(0, 0, 0)');
  });
});

test.describe('Interaction Readiness', () => {
  test('should have clickable buttons immediately', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    const ctaButton = page.locator('.hero-ctas .btn-primary').first();

    // Button should be immediately interactive
    await expect(ctaButton).toBeEnabled({ timeout: 1000 });
  });

  test('should have scrollable content', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    // Page should be scrollable
    const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
    const viewportHeight = await page.evaluate(() => window.innerHeight);

    expect(scrollHeight).toBeGreaterThan(viewportHeight);
  });

  test('should handle rapid scrolling gracefully', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    // Scroll down rapidly
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.scrollBy(0, 500));
      await page.waitForTimeout(50);
    }

    // Scroll back up
    await page.evaluate(() => window.scrollTo(0, 0));

    // Page should still be functional
    const header = page.locator('header');
    await expect(header).toBeVisible();
  });
});

test.describe('DOM Size', () => {
  test('should have reasonable DOM complexity', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    const elementCount = await page.evaluate(
      () => document.querySelectorAll('*').length
    );

    // Landing page should not have excessive DOM elements
    // (Google recommends < 1500 for good performance)
    expect(elementCount).toBeLessThan(500);
  });

  test('should not have deeply nested elements', async ({ page }) => {
    await page.goto('/sample-landing-page.html');

    const maxDepth = await page.evaluate(() => {
      function getDepth(el: Element): number {
        let depth = 0;
        let current: Element | null = el;
        while (current) {
          depth++;
          current = current.parentElement;
        }
        return depth;
      }

      const allElements = document.querySelectorAll('*');
      let max = 0;
      allElements.forEach(el => {
        max = Math.max(max, getDepth(el));
      });
      return max;
    });

    // Should not have excessively deep nesting (> 32 is problematic)
    expect(maxDepth).toBeLessThan(20);
  });
});

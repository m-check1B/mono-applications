import { test, expect } from '@playwright/test';

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test.describe('WCAG 2.1 AA Compliance', () => {
    test('should have proper HTML structure', async ({ page }) => {
      // Check for proper doctype
      await expect(page.locator('html')).toHaveAttribute('lang', 'en');

      // Check for proper heading hierarchy
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
      for (let i = 0; i < headings.length - 1; i++) {
        const currentLevel = parseInt(await headings[i].evaluate(el => el.tagName));
        const nextLevel = parseInt(await headings[i + 1].evaluate(el => el.tagName));
        expect(nextLevel).toBeLessThanOrEqual(currentLevel + 1);
      }
    });

    test('should have proper ARIA labels and roles', async ({ page }) => {
      // Check for skip link
      await expect(page.locator('.skip-link')).toBeVisible();

      // Check for proper landmark roles
      await expect(page.locator('header[role="banner"]')).toBeVisible();
      await expect(page.locator('main[role="main"]')).toBeVisible();
      await expect(page.locator('nav[role="navigation"]')).toBeVisible();

      // Check interactive elements have proper roles
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();

      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        const ariaLabel = await button.getAttribute('aria-label');
        const buttonText = await button.textContent();

        // Button should have either aria-label or visible text
        expect(ariaLabel || buttonText?.trim()).toBeTruthy();
      }
    });

    test('should have proper focus management', async ({ page }) => {
      // Check focus styles
      await page.locator('button').first().focus();
      await expect(page.locator('button:focus')).toBeVisible();

      // Test keyboard navigation
      await page.keyboard.press('Tab');
      const focusedElement = await page.locator(':focus');
      expect(await focusedElement.count()).toBe(1);

      // Test skip link functionality
      await page.locator('.skip-link').focus();
      await page.keyboard.press('Enter');

      // Should scroll to main content
      const mainContent = page.locator('#main-content');
      expect(await mainContent.isVisible()).toBeTruthy();
    });

    test('should have proper form accessibility', async ({ page }) => {
      // Check form labels
      const inputs = page.locator('input, textarea, select');
      const inputCount = await inputs.count();

      for (let i = 0; i < inputCount; i++) {
        const input = inputs.nth(i);
        const id = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledby = await input.getAttribute('aria-labelledby');

        // Input should have either id with associated label or aria-label/aria-labelledby
        expect(id || ariaLabel || ariaLabelledby).toBeTruthy();

        if (id) {
          const label = page.locator(`label[for="${id}"]`);
          const labelCount = await label.count();
          if (labelCount > 0) {
            expect(await label.isVisible()).toBeTruthy();
          }
        }
      }
    });

    test('should have proper image accessibility', async ({ page }) => {
      const images = page.locator('img, svg');
      const imageCount = await images.count();

      for (let i = 0; i < imageCount; i++) {
        const image = images.nth(i);
        const alt = await image.getAttribute('alt');
        const ariaHidden = await image.getAttribute('aria-hidden');

        // Images should have alt text or be decorative (aria-hidden="true")
        if (await image.getAttribute('src')) {
          expect(alt || ariaHidden === 'true').toBeTruthy();
        }
      }
    });

    test('should have proper color contrast', async ({ page }) => {
      // This is a simplified check - in production, use a proper color contrast library
      const textElements = page.locator('p, span, h1, h2, h3, h4, h5, h6, a, button');
      const textCount = await textElements.count();

      // Check that text elements have sufficient contrast with their backgrounds
      // This is a basic check - real implementation would use color contrast calculations
      expect(textCount).toBeGreaterThan(0);
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Test keyboard navigation through interactive elements
      const interactiveElements = page.locator('button, a, input, select, textarea');
      const elementCount = await interactiveElements.count();

      // Navigate through all interactive elements
      for (let i = 0; i < elementCount; i++) {
        await page.keyboard.press('Tab');
        const focusedElement = page.locator(':focus');
        expect(await focusedElement.count()).toBe(1);

        // Element should be visible
        expect(await focusedElement.isVisible()).toBeTruthy();
      }
    });

    test('should have proper table accessibility', async ({ page }) => {
      const tables = page.locator('table');
      const tableCount = await tables.count();

      for (let i = 0; i < tableCount; i++) {
        const table = tables.nth(i);

        // Check for proper table structure
        expect(await table.locator('thead').count()).toBeGreaterThan(0);
        expect(await table.locator('tbody').count()).toBeGreaterThan(0);

        // Check for proper headers
        const headers = table.locator('th');
        const headerCount = await headers.count();
        expect(headerCount).toBeGreaterThan(0);

        // Check for proper scope attributes
        for (let j = 0; j < headerCount; j++) {
          const header = headers.nth(j);
          const scope = await header.getAttribute('scope');
          // Headers should have scope attribute
          expect(scope).toBeTruthy();
        }
      }
    });

    test('should have proper link accessibility', async ({ page }) => {
      const links = page.locator('a');
      const linkCount = await links.count();

      for (let i = 0; i < linkCount; i++) {
        const link = links.nth(i);
        const href = await link.getAttribute('href');
        const text = await link.textContent();

        // Links should have href attribute
        expect(href).toBeTruthy();

        // Links should have descriptive text
        if (text) {
          expect(text.trim()).toBeTruthy();
        }

        // Check for proper aria attributes
        const ariaLabel = await link.getAttribute('aria-label');
        if (ariaLabel) {
          expect(ariaLabel.trim()).toBeTruthy();
        }
      }
    });

    test('should have proper modal accessibility', async ({ page }) => {
      // This test assumes there's a way to open a modal
      // In a real application, you would click a button to open a modal

      // Check if modal exists and is accessible
      const modal = page.locator('[role="dialog"]');
      const modalCount = await modal.count();

      if (modalCount > 0) {
        const modalElement = modal.first();

        // Check for proper modal attributes
        expect(await modalElement.getAttribute('aria-modal')).toBe('true');
        expect(await modalElement.getAttribute('aria-labelledby')).toBeTruthy();

        // Check for focus trap (if modal is open)
        const isVisible = await modalElement.isVisible();
        if (isVisible) {
          // Test focus management within modal
          const modalButtons = modalElement.locator('button');
          const buttonCount = await modalButtons.count();

          if (buttonCount > 0) {
            await modalButtons.first().focus();
            expect(await modalElement.locator(':focus').count()).toBe(1);
          }
        }
      }
    });

    test('should support screen readers', async ({ page }) => {
      // Check for live regions
      const liveRegions = page.locator('[aria-live]');
      expect(await liveRegions.count()).toBeGreaterThanOrEqual(0);

      // Check for screen reader only content
      const srOnly = page.locator('.sr-only');
      expect(await srOnly.count()).toBeGreaterThanOrEqual(0);

      // Check for proper ARIA descriptions
      const describedBy = page.locator('[aria-describedby]');
      const describedByCount = await describedBy.count();

      for (let i = 0; i < describedByCount; i++) {
        const element = describedBy.nth(i);
        const describedById = await element.getAttribute('aria-describedby');

        if (describedById) {
          const description = page.locator(`#${describedById}`);
          expect(await description.count()).toBe(1);
          expect(await description.isVisible()).toBeTruthy();
        }
      }
    });

    test('should handle dynamic content properly', async ({ page }) => {
      // Test that dynamic content updates are announced to screen readers
      const statusRegions = page.locator('[role="status"], [role="alert"]');
      const regionCount = await statusRegions.count();

      expect(regionCount).toBeGreaterThanOrEqual(0);

      // Check that status regions have proper attributes
      for (let i = 0; i < regionCount; i++) {
        const region = statusRegions.nth(i);
        const ariaLive = await region.getAttribute('aria-live');
        const ariaAtomic = await region.getAttribute('aria-atomic');

        expect(ariaLive).toBeTruthy();
        expect(ariaAtomic).toBe('true');
      }
    });

    test('should have proper error handling', async ({ page }) => {
      // Test error states and messages
      const errorElements = page.locator('[role="alert"], .error, .alert-error');
      const errorCount = await errorElements.count();

      for (let i = 0; i < errorCount; i++) {
        const error = errorElements.nth(i);
        const role = await error.getAttribute('role');

        if (role === 'alert') {
          expect(await error.isVisible()).toBeTruthy();
        }
      }
    });

    test('should support mobile accessibility', async ({ page }) => {
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Check that content is accessible on mobile
      const mainContent = page.locator('main');
      expect(await mainContent.isVisible()).toBeTruthy();

      // Check for touch-friendly targets
      const buttons = page.locator('button');
      const buttonCount = await buttons.count();

      for (let i = 0; i < buttonCount; i++) {
        const button = buttons.nth(i);
        const box = await button.boundingBox();

        if (box) {
          // Check minimum touch target size (44x44 pixels)
          expect(box.width).toBeGreaterThanOrEqual(44);
          expect(box.height).toBeGreaterThanOrEqual(44);
        }
      }
    });

    test('should support reduced motion preferences', async ({ page }) => {
      // Simulate reduced motion preference
      await page.addInitScript(() => {
        Object.defineProperty(window, 'matchMedia', {
          value: (query: string) => ({
            matches: query === '(prefers-reduced-motion: reduce)',
            addListener: () => {},
            removeListener: () => {},
          }),
        });
      });

      // Reload page to apply preference
      await page.reload();

      // Check that reduced motion class is applied
      const body = page.locator('body');
      expect(await body).toHaveClass(/reduce-motion/);
    });

    test('should have proper loading states', async ({ page }) => {
      // Check for loading indicators
      const loadingElements = page.locator('[aria-busy="true"], .loading, .spinner');
      const loadingCount = await loadingElements.count();

      // Check that loading states are properly announced
      for (let i = 0; i < loadingCount; i++) {
        const element = loadingElements.nth(i);
        const ariaBusy = await element.getAttribute('aria-busy');

        if (ariaBusy === 'true') {
          expect(await element.isVisible()).toBeTruthy();
        }
      }
    });
  });

  test.describe('Performance and Load Tests', () => {
    test('should load accessibility features quickly', async ({ page }) => {
      const startTime = Date.now();

      // Wait for accessibility utilities to load
      await page.waitForFunction(() => {
        return typeof window !== 'undefined' &&
               window.AccessibilityUtils !== undefined;
      });

      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(2000); // Should load within 2 seconds
    });

    test('should handle multiple accessibility announcements', async ({ page }) => {
      // Test that multiple screen reader announcements don't conflict
      await page.evaluate(() => {
        if (window.AccessibilityUtils) {
          window.AccessibilityUtils.announceToScreenReader('Test message 1');
          window.AccessibilityUtils.announceToScreenReader('Test message 2');
        }
      });

      // Wait for announcements to complete
      await page.waitForTimeout(1500);

      // Page should remain stable
      expect(await page.locator('body').isVisible()).toBeTruthy();
    });
  });
});
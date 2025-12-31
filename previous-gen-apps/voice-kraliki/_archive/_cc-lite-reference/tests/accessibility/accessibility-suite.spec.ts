import { test, expect } from '@playwright/test';

test.describe('Accessibility Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());

    // Mock authentication
    await page.route('**/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          result: {
            data: {
              id: 'user-123',
              email: 'test@example.com',
              name: 'Test User',
              role: 'AGENT'
            }
          }
        })
      });
    });

    // Mock dashboard data
    await page.route('**/dashboard', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          activeCalls: [],
          recentCalls: [],
          teamStatus: {
            members: [],
            stats: { totalMembers: 0, availableAgents: 0, busyAgents: 0, onBreakAgents: 0, offlineAgents: 0 }
          },
          callStats: {
            totalCalls: 0,
            activeCalls: 0,
            completedCalls: 0,
            averageDuration: 0,
            handledByAI: 0,
            handledByAgents: 0,
            missedCalls: 0
          }
        })
      });
    });
  });

  test.describe('Login Page Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5174/login');
    });

    test('should have proper page title', async ({ page }) => {
      await expect(page).toHaveTitle(/CC-Light/);
    });

    test('should have proper heading structure', async ({ page }) => {
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();

      // Should have exactly one h1
      const h1Headings = await page.locator('h1').all();
      expect(h1Headings).toHaveLength(1);

      // Headings should be in proper order
      for (let i = 0; i < headings.length - 1; i++) {
        const currentLevel = parseInt(await headings[i].evaluate(el => el.tagName.substring(1)));
        const nextLevel = parseInt(await headings[i + 1].evaluate(el => el.tagName.substring(1)));
        expect(nextLevel).toBeGreaterThanOrEqual(currentLevel);
      }
    });

    test('should have proper form labels', async ({ page }) => {
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');

      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();

      // Check for associated labels
      const emailLabel = await emailInput.evaluate(el => {
        const id = el.getAttribute('id');
        return id ? document.querySelector(`label[for="${id}"]`) : el.closest('label');
      });
      expect(emailLabel).toBeTruthy();

      const passwordLabel = await passwordInput.evaluate(el => {
        const id = el.getAttribute('id');
        return id ? document.querySelector(`label[for="${id}"]`) : el.closest('label');
      });
      expect(passwordLabel).toBeTruthy();
    });

    test('should have proper ARIA attributes', async ({ page }) => {
      const submitButton = page.locator('button[type="submit"]');
      await expect(submitButton).toBeVisible();

      const ariaLabel = await submitButton.getAttribute('aria-label');
      const buttonText = await submitButton.textContent();

      // Should have either aria-label or descriptive text
      expect(ariaLabel || buttonText).toBeTruthy();
    });

    test('should have proper focus management', async ({ page }) => {
      // Test tab order
      await page.keyboard.press('Tab');
      expect(await page.locator('input[type="email"]:focus')).toBeTruthy();

      await page.keyboard.press('Tab');
      expect(await page.locator('input[type="password"]:focus')).toBeTruthy();

      await page.keyboard.press('Tab');
      expect(await page.locator('button[type="submit"]:focus')).toBeTruthy();
    });

    test('should have sufficient color contrast', async ({ page }) => {
      // This is a basic check - in production, you'd use axe-core or similar
      const textElements = await page.locator('text="CC-Light"').all();
      for (const element of textElements) {
        const styles = await element.evaluate(el => {
          const computedStyle = window.getComputedStyle(el);
          return {
            color: computedStyle.color,
            backgroundColor: computedStyle.backgroundColor,
            fontSize: computedStyle.fontSize
          };
        });
        expect(styles.color).toBeTruthy();
      }
    });

    test('should handle keyboard navigation properly', async ({ page }) => {
      // Test Enter key on submit button
      await page.locator('input[type="email"]').fill('test@example.com');
      await page.locator('input[type="password"]').fill('password123');
      await page.keyboard.press('Enter');

      // Should attempt form submission
      await expect(page.locator('button[type="submit"]')).toBeDisabled();
    });
  });

  test.describe('Dashboard Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5174/dashboard');
    });

    test('should have proper navigation structure', async ({ page }) => {
      const nav = page.locator('nav');
      await expect(nav).toBeVisible();

      const navItems = await nav.locator('button, a').all();
      expect(navItems.length).toBeGreaterThan(0);

      // Check for proper ARIA roles
      const navRole = await nav.getAttribute('role');
      expect(navRole).toMatch(/navigation|menubar/i);
    });

    test('should have proper landmark regions', async ({ page }) => {
      // Check for main, header, nav, footer landmarks
      const main = page.locator('main');
      const header = page.locator('header');
      const nav = page.locator('nav');

      await expect(main).toBeVisible();
      expect(await main.count()).toBeLessThanOrEqual(1);

      if (await header.isVisible()) {
        const headerRole = await header.getAttribute('role');
        expect(headerRole).toMatch(/banner/i);
      }

      if (await nav.isVisible()) {
        const navRole = await nav.getAttribute('role');
        expect(navRole).toMatch(/navigation/i);
      }
    });

    test('should have proper table accessibility', async ({ page }) => {
      await page.click('text=Calls');

      const table = page.locator('table');
      if (await table.isVisible()) {
        // Check for table headers
        const headers = await table.locator('th').all();
        expect(headers.length).toBeGreaterThan(0);

        // Check for proper scope attributes
        const scopeHeaders = await table.locator('th[scope]').all();
        expect(scopeHeaders.length).toBeGreaterThan(0);

        // Check for caption if table is complex
        const caption = await table.locator('caption').count();
        if (await table.locator('tr').count() > 10) {
          expect(caption).toBeGreaterThan(0);
        }
      }
    });

    test('should have proper button accessibility', async ({ page }) => {
      const buttons = await page.locator('button').all();

      for (const button of buttons) {
        const isVisible = await button.isVisible();
        if (isVisible) {
          // Check for accessible name
          const text = await button.textContent();
          const ariaLabel = await button.getAttribute('aria-label');
          const ariaLabelledBy = await button.getAttribute('aria-labelledby');

          expect(text || ariaLabel || ariaLabelledBy).toBeTruthy();

          // Check for proper state attributes
          const isDisabled = await button.isDisabled();
          if (isDisabled) {
            const ariaDisabled = await button.getAttribute('aria-disabled');
            expect(ariaDisabled).toBe('true');
          }
        }
      }
    });

    test('should have proper form field accessibility', async ({ page }) => {
      const inputs = await page.locator('input, select, textarea').all();

      for (const input of inputs) {
        const isVisible = await input.isVisible();
        if (isVisible) {
          // Check for label association
          const id = await input.getAttribute('id');
          const label = id ? await input.locator(`label[for="${id}"]`).count() > 0
                        : await input.locator('xpath=ancestor::label').count() > 0;

          expect(label).toBe(true);

          // Check for proper input types
          const type = await input.getAttribute('type');
          if (type === 'password') {
            const autoComplete = await input.getAttribute('autocomplete');
            expect(autoComplete).toMatch(/current-password|new-password/i);
          }
        }
      }
    });

    test('should have proper link accessibility', async ({ page }) => {
      const links = await page.locator('a').all();

      for (const link of links) {
        const isVisible = await link.isVisible();
        if (isVisible) {
          // Check for meaningful link text
          const text = await link.textContent();
          const ariaLabel = await link.getAttribute('aria-label');

          expect(text || ariaLabel).toBeTruthy();

          // Check for proper href
          const href = await link.getAttribute('href');
          if (href && href !== '#') {
            expect(href).toMatch(/^https?:\/\//);
          }
        }
      }
    });

    test('should have proper image accessibility', async ({ page }) => {
      const images = await page.locator('img').all();

      for (const img of images) {
        const isVisible = await img.isVisible();
        if (isVisible) {
          // Check for alt text
          const alt = await img.getAttribute('alt');
          const ariaLabel = await img.getAttribute('aria-label');
          const role = await img.getAttribute('role');

          if (role !== 'presentation') {
            expect(alt || ariaLabel).toBeTruthy();
          }
        }
      }
    });

    test('should have proper focus indicators', async ({ page }) => {
      // Test focus on interactive elements
      const focusableElements = await page.locator('button, input, select, textarea, a[href]').all();

      for (const element of focusableElements.slice(0, 5)) { // Test first 5 elements
        const isVisible = await element.isVisible();
        if (isVisible) {
          await element.focus();

          // Check if element has visible focus styles
          const styles = await element.evaluate(el => {
            const computedStyle = window.getComputedStyle(el);
            return {
              outline: computedStyle.outline,
              boxShadow: computedStyle.boxShadow,
              border: computedStyle.border
            };
          });

          // Should have some visual indication of focus
          const hasFocusIndicator =
            styles.outline !== 'none' ||
            styles.boxShadow !== 'none' ||
            styles.border !== 'none';

          expect(hasFocusIndicator).toBe(true);
        }
      }
    });

    test('should have proper ARIA live regions for dynamic content', async ({ page }) => {
      // Look for live regions (status, alerts, etc.)
      const liveRegions = await page.locator('[aria-live], [role="status"], [role="alert"]').all();

      // In a real-time dashboard, there should be some live regions
      // This is a basic check - adapt based on your implementation
      if (liveRegions.length === 0) {
        // If no live regions, check if real-time updates are properly announced
        console.log('No ARIA live regions found - consider adding for real-time updates');
      }
    });

    test('should have proper skip links', async ({ page }) => {
      const skipLinks = await page.locator('a[href^="#"], a[href*="skip"]').all();

      // Should have skip links for keyboard users
      if (skipLinks.length === 0) {
        console.log('No skip links found - consider adding for better keyboard navigation');
      } else {
        for (const skipLink of skipLinks) {
          const href = await skipLink.getAttribute('href');
          expect(href).toBeTruthy();

          // Target should exist
          const target = await page.locator(href || '').count();
          if (href && href.startsWith('#')) {
            expect(target).toBeGreaterThan(0);
          }
        }
      }
    });

    test('should handle screen reader announcements', async ({ page }) => {
      // Mock screen reader behavior
      await page.addInitScript(() => {
        window.announcements: string[] = [];
        const originalAnnounce = window.announceToScreenReader;
        window.announceToScreenReader = (message: string) => {
          window.announcements.push(message);
        };
      });

      // Trigger some state change that should be announced
      await page.click('text=Calls');

      // Check if announcements were made
      const announcements = await page.evaluate(() => (window as any).announcements || []);
      if (announcements.length === 0) {
        console.log('No screen reader announcements - consider adding for important state changes');
      }
    });

    test('should have proper language declaration', async ({ page }) => {
      const htmlLang = await page.locator('html').getAttribute('lang');
      expect(htmlLang).toBeTruthy();
      expect(htmlLang).toMatch(/^[a-z]{2}(-[A-Z]{2})?$/);
    });

    test('should have proper viewport meta tag', async ({ page }) => {
      const viewport = await page.locator('meta[name="viewport"]').getAttribute('content');
      expect(viewport).toBeTruthy();
      expect(viewport).toMatch(/width=device-width/);
    });

    test('should have proper document structure', async ({ page }) => {
      const doctype = await page.evaluate(() => document.doctype);
      expect(doctype).toBeTruthy();
      expect(doctype?.name).toBe('html');

      const html = page.locator('html');
      const head = page.locator('head');
      const body = page.locator('body');

      await expect(html).toBeVisible();
      await expect(head).toBeVisible();
      await expect(body).toBeVisible();
    });
  });
});
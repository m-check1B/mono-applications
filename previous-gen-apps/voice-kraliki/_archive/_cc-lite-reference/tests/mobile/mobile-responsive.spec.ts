import { test, expect } from '@playwright/test';

const viewports = [
  { name: 'iPhone 12', width: 390, height: 844 },
  { name: 'iPhone SE', width: 375, height: 667 },
  { name: 'iPad', width: 768, height: 1024 },
  { name: 'iPad Pro', width: 1024, height: 1366 },
  { name: 'Samsung Galaxy S21', width: 384, height: 854 },
  { name: 'Small Desktop', width: 1024, height: 768 },
  { name: 'Medium Desktop', width: 1366, height: 768 },
  { name: 'Large Desktop', width: 1920, height: 1080 }
];

test.describe('Mobile Responsive Testing', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  viewports.forEach(viewport => {
    test.describe(`${viewport.name} (${viewport.width}x${viewport.height})`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
      });

      test.describe('Login Page', () => {
        test.beforeEach(async ({ page }) => {
          await page.goto('http://localhost:5174/login');
        });

        test('should display login form correctly', async ({ page }) => {
          await expect(page.locator('h1')).toContainText('CC-Light');
          await expect(page.locator('input[type="email"]')).toBeVisible();
          await expect(page.locator('input[type="password"]')).toBeVisible();
          await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
        });

        test('should have proper form layout', async ({ page }) => {
          const form = page.locator('form').first();
          const boundingBox = await form.boundingBox();

          expect(boundingBox).toBeTruthy();
          if (boundingBox) {
            // Form should fit within viewport with reasonable padding
            expect(boundingBox.width).toBeLessThanOrEqual(viewport.width - 40);
            expect(boundingBox.height).toBeLessThanOrEqual(viewport.height - 40);
          }
        });

        test('should handle keyboard visibility', async ({ page }) => {
          // Focus on email input to trigger keyboard
          await page.locator('input[type="email"]').focus();

          // Check if content is still visible (not hidden by keyboard)
          await expect(page.locator('h1')).toBeVisible();
          await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
        });

        test('should have touch-friendly buttons', async ({ page }) => {
          const button = page.getByRole('button', { name: /sign in/i });
          const boundingBox = await button.boundingBox();

          expect(boundingBox).toBeTruthy();
          if (boundingBox) {
            // Buttons should have minimum touch target size (44x44 according to Apple HIG)
            expect(boundingBox.width).toBeGreaterThanOrEqual(44);
            expect(boundingBox.height).toBeGreaterThanOrEqual(44);
          }
        });

        test('should be scrollable if content exceeds viewport', async ({ page }) => {
          const documentHeight = await page.evaluate(() => document.documentElement.scrollHeight);
          const viewportHeight = viewport.height;

          if (documentHeight > viewportHeight) {
            expect(await page.locator('html')).toHaveCSS('overflow-y', /scroll|auto/);
          }
        });
      });

      test.describe('Dashboard', () => {
        test.beforeEach(async ({ page }) => {
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
                activeCalls: [
                  {
                    id: 'call-1',
                    phoneNumber: '+1234567890',
                    status: 'ACTIVE',
                    duration: 120,
                    agent: 'John Doe',
                    campaign: 'Sales Campaign',
                    startTime: new Date().toISOString()
                  }
                ],
                recentCalls: [],
                teamStatus: {
                  members: [],
                  stats: { totalMembers: 0, availableAgents: 0, busyAgents: 0, onBreakAgents: 0, offlineAgents: 0 }
                },
                callStats: {
                  totalCalls: 150,
                  activeCalls: 1,
                  completedCalls: 149,
                  averageDuration: 240,
                  handledByAI: 45,
                  handledByAgents: 105,
                  missedCalls: 5
                }
              })
            });
          });

          await page.goto('http://localhost:5174/dashboard');
          await page.waitForLoadState('networkidle');
        });

        test('should display dashboard correctly', async ({ page }) => {
          await expect(page.locator('text=CC-Light')).toBeVisible();
          await expect(page.locator('text=150')).toBeVisible(); // Total calls
          await expect(page.locator('text=1')).toBeVisible(); // Active calls
        });

        test('should have responsive navigation', async ({ page }) => {
          const nav = page.locator('nav').first();
          const navItems = await nav.locator('button, a').all();

          expect(navItems.length).toBeGreaterThan(0);

          if (viewport.width < 768) {
            // On mobile, navigation might be collapsed or in a hamburger menu
            const navContainer = await nav.boundingBox();
            expect(navContainer).toBeTruthy();
            if (navContainer) {
              expect(navContainer.width).toBeLessThanOrEqual(viewport.width);
            }
          }
        });

        test('should have touch-friendly navigation items', async ({ page }) => {
          const navItems = await page.locator('nav button, nav a').all();

          for (const item of navItems.slice(0, 3)) { // Test first 3 items
            const boundingBox = await item.boundingBox();
            expect(boundingBox).toBeTruthy();
            if (boundingBox) {
              expect(boundingBox.width).toBeGreaterThanOrEqual(44);
              expect(boundingBox.height).toBeGreaterThanOrEqual(44);
            }
          }
        });

        test('should handle data tables on mobile', async ({ page }) => {
          await page.click('text=Calls');

          const table = page.locator('table').first();
          if (await table.isVisible()) {
            // On mobile, tables might be horizontally scrollable
            const tableContainer = await table.locator('xpath=..').boundingBox();
            expect(tableContainer).toBeTruthy();
            if (tableContainer) {
              const hasHorizontalScroll = await table.evaluate(el => {
                return el.scrollWidth > el.clientWidth;
              });

              if (viewport.width < 768 && hasHorizontalScroll) {
                expect(await table.locator('xpath=..')).toHaveCSS('overflow-x', /scroll|auto/);
              }
            }
          }
        });

        test('should have readable text sizes', async ({ page }) => {
          const mainHeading = page.locator('h1').first();
          const fontSize = await mainHeading.evaluate(el => {
            return window.getComputedStyle(el).fontSize;
          });

          // Font size should be reasonable for the viewport size
          const fontSizeNum = parseFloat(fontSize);
          if (viewport.width < 768) {
            expect(fontSizeNum).toBeGreaterThanOrEqual(16); // At least 16px on mobile
          }
        });

        test('should have proper spacing', async ({ page }) => {
          const statsCards = page.locator('.stats-container, .grid > div').first();
          if (await statsCards.isVisible()) {
            const boundingBox = await statsCards.boundingBox();
            expect(boundingBox).toBeTruthy();
            if (boundingBox) {
              // Elements should have reasonable spacing
              expect(boundingBox.width).toBeLessThanOrEqual(viewport.width - 32); // Account for padding
            }
          }
        });
      });

      test.describe('Touch Interactions', () => {
        test.beforeEach(async ({ page }) => {
          await page.goto('http://localhost:5174/login');
        });

        test('should handle touch events on form fields', async ({ page }) => {
          const emailInput = page.locator('input[type="email"]');
          const passwordInput = page.locator('input[type="password"]');

          // Simulate touch events
          await emailInput.dispatchEvent('touchstart');
          await emailInput.dispatchEvent('touchend');

          await expect(emailInput).toBeFocused();

          await passwordInput.dispatchEvent('touchstart');
          await passwordInput.dispatchEvent('touchend');

          await expect(passwordInput).toBeFocused();
        });

        test('should handle touch events on buttons', async ({ page }) => {
          const button = page.getByRole('button', { name: /sign in/i });

          await button.dispatchEvent('touchstart');
          await button.dispatchEvent('touchend');

          // Button should respond to touch (visual feedback)
          const boundingBox = await button.boundingBox();
          expect(boundingBox).toBeTruthy();
        });

        test('should handle swipe gestures if applicable', async ({ page }) => {
          // Test if swipe gestures are implemented (e.g., for navigation)
          await page.goto('http://localhost:5174/dashboard');

          // Mock authentication and dashboard data
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

          await page.waitForLoadState('networkidle');

          // Test horizontal swipe (for carousel or tab navigation if implemented)
          const startX = viewport.width * 0.8;
          const startY = viewport.height / 2;
          const endX = viewport.width * 0.2;
          const endY = viewport.height / 2;

          await page.touchstart(startX, startY);
          await page.touchmove(endX, endY);
          await page.touchend(endX, endY);

          // The page should handle the swipe without errors
          await expect(page).not.toHaveTitle(/Error/);
        });
      });

      test.describe('Orientation Changes', () => {
        test.beforeEach(async ({ page }) => {
          await page.goto('http://localhost:5174/login');
        });

        test('should handle portrait to landscape rotation', async ({ page }) => {
          // Start in portrait
          await page.setViewportSize({ width: viewport.height, height: viewport.width });
          await expect(page.locator('h1')).toBeVisible();

          // Rotate to landscape
          await page.setViewportSize({ width: viewport.width, height: viewport.height });
          await expect(page.locator('h1')).toBeVisible();

          // Form should still be properly positioned
          const form = page.locator('form').first();
          await expect(form).toBeVisible();
        });

        test('should maintain functionality after orientation change', async ({ page }) => {
          await page.setViewportSize({ width: viewport.width, height: viewport.height });

          // Fill form
          await page.locator('input[type="email"]').fill('test@example.com');
          await page.locator('input[type="password"]').fill('password123');

          // Change orientation
          await page.setViewportSize({ width: viewport.height, height: viewport.width });

          // Form values should be preserved
          expect(await page.locator('input[type="email"]').inputValue()).toBe('test@example.com');
          expect(await page.locator('input[type="password"]').inputValue()).toBe('password123');

          // Button should still be clickable
          await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
        });
      });

      test.describe('Performance on Mobile', () => {
        test.beforeEach(async ({ page }) => {
          await page.goto('http://localhost:5174/login');
        });

        test('should load within acceptable time on mobile', async ({ page }) => {
          const startTime = Date.now();
          await page.goto('http://localhost:5174/login');
          const endTime = Date.now();

          const loadTime = endTime - startTime;
          console.log(`${viewport.name} load time: ${loadTime}ms`);

          // Mobile devices might be slower, so allow more time
          expect(loadTime).toBeLessThan(10000); // 10 seconds
        });

        test('should have smooth animations on mobile', async ({ page }) => {
          // Check if animations are properly optimized for mobile
          const animations = await page.evaluate(() => {
            const elements = document.querySelectorAll('*');
            let hasOptimizedAnimations = false;

            elements.forEach(el => {
              const style = window.getComputedStyle(el);
              if (style.transform !== 'none' || style.opacity !== '1') {
                hasOptimizedAnimations = true;
              }
            });

            return hasOptimizedAnimations;
          });

          // If animations exist, they should be performant
          if (animations) {
            const frameRates = await page.evaluate(async () => {
              const frames: number[] = [];
              let lastTime = performance.now();

              return new Promise((resolve) => {
                const measureFrame = (timestamp: number) => {
                  const deltaTime = timestamp - lastTime;
                  const fps = 1000 / deltaTime;
                  frames.push(fps);
                  lastTime = timestamp;

                  if (frames.length < 30) {
                    requestAnimationFrame(measureFrame);
                  } else {
                    resolve(frames);
                  }
                };

                requestAnimationFrame(measureFrame);
              });
            });

            const avgFps = frames.reduce((sum, fps) => sum + fps, 0) / frames.length;
            expect(avgFps).toBeGreaterThan(20); // Should maintain decent frame rate
          }
        });
      });
    });
  });
});
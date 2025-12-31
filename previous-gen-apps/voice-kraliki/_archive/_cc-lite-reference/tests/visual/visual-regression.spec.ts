import { test, expect } from '@playwright/test';

test.describe('Visual Regression Testing', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
  });

  test.describe('Login Page Visuals', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('http://localhost:5174/login');
    });

    test('should match login page screenshot', async ({ page }) => {
      await expect(page).toHaveScreenshot('login-page.png', {
        fullPage: true,
        animations: 'disabled',
        caret: 'hide'
      });
    });

    test('should match login form screenshot', async ({ page }) => {
      const loginForm = page.locator('form').first();
      await expect(loginForm).toHaveScreenshot('login-form.png', {
        animations: 'disabled'
      });
    });

    test('should match login page with form validation', async ({ page }) => {
      await page.click('button[type="submit"]');
      await expect(page.locator('text=Email is required')).toBeVisible();
      await expect(page.locator('text=Password is required')).toBeVisible();

      await expect(page).toHaveScreenshot('login-validation-errors.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match login page with filled form', async ({ page }) => {
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'password123');

      await expect(page).toHaveScreenshot('login-filled-form.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match login page loading state', async ({ page }) => {
      // Mock loading state
      await page.route('**/auth/login', async (route) => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.continue();
      });

      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');

      await expect(page.locator('button[type="submit"]')).toBeDisabled();
      await expect(page).toHaveScreenshot('login-loading.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });
  });

  test.describe('Dashboard Visuals', () => {
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
            recentCalls: [
              {
                id: 'call-2',
                phoneNumber: '+0987654321',
                status: 'COMPLETED',
                duration: 300,
                agent: 'Jane Smith',
                campaign: 'Support Campaign',
                timestamp: new Date().toISOString()
              }
            ],
            teamStatus: {
              members: [
                {
                  id: 'agent-1',
                  name: 'John Doe',
                  status: 'available',
                  activeCall: null,
                  skills: ['sales', 'support']
                },
                {
                  id: 'agent-2',
                  name: 'Jane Smith',
                  status: 'busy',
                  activeCall: 'call-1',
                  skills: ['support', 'technical']
                }
              ],
              stats: {
                totalMembers: 2,
                availableAgents: 1,
                busyAgents: 1,
                onBreakAgents: 0,
                offlineAgents: 0
              }
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

    test('should match dashboard overview screenshot', async ({ page }) => {
      await expect(page).toHaveScreenshot('dashboard-overview.png', {
        fullPage: true,
        animations: 'disabled',
        caret: 'hide'
      });
    });

    test('should match calls tab screenshot', async ({ page }) => {
      await page.click('text=Calls');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('dashboard-calls.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match team tab screenshot', async ({ page }) => {
      await page.click('text=Team');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('dashboard-team.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match analytics tab screenshot', async ({ page }) => {
      await page.click('text=Analytics');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('dashboard-analytics.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match navigation screenshot', async ({ page }) => {
      const nav = page.locator('nav').first();
      await expect(nav).toHaveScreenshot('dashboard-navigation.png', {
        animations: 'disabled'
      });
    });

    test('should match statistics cards screenshot', async ({ page }) => {
      const statsContainer = page.locator('.stats-container, .grid').first();
      await expect(statsContainer).toHaveScreenshot('dashboard-stats.png', {
        animations: 'disabled'
      });
    });

    test('should match active calls table screenshot', async ({ page }) => {
      await page.click('text=Calls');
      await page.waitForLoadState('networkidle');

      const table = page.locator('table').first();
      await expect(table).toHaveScreenshot('dashboard-calls-table.png', {
        animations: 'disabled'
      });
    });
  });

  test.describe('Mobile Visuals', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
    });

    test('should match mobile login page screenshot', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      await expect(page).toHaveScreenshot('mobile-login.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match mobile dashboard screenshot', async ({ page }) => {
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

      await page.goto('http://localhost:5174/dashboard');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('mobile-dashboard.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match mobile navigation screenshot', async ({ page }) => {
      // Mock authentication and load dashboard
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

      await page.goto('http://localhost:5174/dashboard');
      await page.waitForLoadState('networkidle');

      const nav = page.locator('nav').first();
      await expect(nav).toHaveScreenshot('mobile-navigation.png', {
        animations: 'disabled'
      });
    });
  });

  test.describe('Dark Mode Visuals', () => {
    test.beforeEach(async ({ page }) => {
      // Set dark mode preference
      await page.addInitScript(() => {
        localStorage.setItem('theme', 'dark');
      });

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

      await page.goto('http://localhost:5174/dashboard');
      await page.waitForLoadState('networkidle');
    });

    test('should match dark mode dashboard screenshot', async ({ page }) => {
      await expect(page).toHaveScreenshot('dark-mode-dashboard.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match dark mode login page screenshot', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      await expect(page).toHaveScreenshot('dark-mode-login.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });
  });

  test.describe('Loading and Error States', () => {
    test('should match loading state screenshot', async ({ page }) => {
      // Mock slow response
      await page.route('**/dashboard', async (route) => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.continue();
      });

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

      await page.goto('http://localhost:5174/dashboard');

      await expect(page).toHaveScreenshot('loading-state.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match error state screenshot', async ({ page }) => {
      // Mock API error
      await page.route('**/dashboard', async (route) => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' })
        });
      });

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

      await page.goto('http://localhost:5174/dashboard');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('error-state.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });
  });

  test.describe('Interactive States', () => {
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

      await page.goto('http://localhost:5174/dashboard');
      await page.waitForLoadState('networkidle');
    });

    test('should match hover states screenshot', async ({ page }) => {
      // Hover over navigation items
      await page.hover('text=Overview');
      await expect(page).toHaveScreenshot('hover-overview.png', {
        animations: 'disabled'
      });

      await page.hover('text=Calls');
      await expect(page).toHaveScreenshot('hover-calls.png', {
        animations: 'disabled'
      });
    });

    test('should match focus states screenshot', async ({ page }) => {
      // Focus on navigation items
      await page.press('Tab'); // Focus on first nav item
      await expect(page).toHaveScreenshot('focus-navigation.png', {
        animations: 'disabled'
      });
    });

    test('should match active tab screenshot', async ({ page }) => {
      await page.click('text=Calls');
      await page.waitForLoadState('networkidle');

      await expect(page).toHaveScreenshot('active-tab-calls.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });
  });
});
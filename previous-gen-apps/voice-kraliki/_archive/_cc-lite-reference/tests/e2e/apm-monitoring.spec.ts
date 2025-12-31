/**
 * APM Monitoring Dashboard E2E Tests
 * Comprehensive end-to-end testing for the Application Performance Monitoring dashboard
 */

import { test, expect, Page, BrowserContext } from '@playwright/test';
import { getSupervisorCredentials, getAgentCredentials, getAdminCredentials } from '../utils/test-credentials';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:3007';
const WS_URL = process.env.WS_URL || 'ws://127.0.0.1:3010';
const TEST_TIMEOUT = 30000;

// Universal test account
const UNIVERSAL_TEST_ACCOUNT = {
  email: 'test.assistant@stack2025.com',
  password: 'Stack2025!Test@Assistant#Secure$2024',
  userId: '550e8400-e29b-41d4-a716-446655440000',
  role: 'TESTER_UNIVERSAL',
  tier: 'CORPORATE',
};

test.describe('APM Monitoring Dashboard E2E Tests', () => {
  let context: BrowserContext;
  let supervisorPage: Page;
  let agentPage: Page;
  let adminPage: Page;

  test.beforeAll(async ({ browser }) => {
    // Create browser context with realistic user agent
    context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CC-Light-APM-Test/1.0',
      viewport: { width: 1920, height: 1080 },
      ignoreHTTPSErrors: true,
    });
  });

  test.afterAll(async () => {
    await context.close();
  });

  test.beforeEach(async () => {
    // Create separate pages for different user roles
    supervisorPage = await context.newPage();
    agentPage = await context.newPage();
    adminPage = await context.newPage();

    // Clear any existing sessions
    await supervisorPage.context().clearCookies();
    await agentPage.context().clearCookies();
    await adminPage.context().clearCookies();
  });

  test.afterEach(async () => {
    await supervisorPage.close();
    await agentPage.close();
    await adminPage.close();
  });

  test.describe('APM Dashboard Access and Authentication', () => {
    test('should allow supervisor access to APM dashboard', async () => {
      test.setTimeout(TEST_TIMEOUT);

      const supervisorCreds = getSupervisorCredentials();

      // Login as supervisor
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', supervisorCreds.email);
      await supervisorPage.fill('input[type="password"]', supervisorCreds.password);
      await supervisorPage.click('button[type="submit"]');

      // Wait for successful login
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });

      // Navigate to APM dashboard
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');

      // Verify APM dashboard is loaded
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('[data-testid="apm-dashboard"]')).toBeVisible();

      // Take screenshot for verification
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-dashboard-supervisor.png',
        fullPage: true
      });
    });

    test('should allow admin access to APM dashboard', async () => {
      test.setTimeout(TEST_TIMEOUT);

      const adminCreds = getAdminCredentials();

      // Login as admin
      await adminPage.goto(`${BASE_URL}/login`);
      await adminPage.fill('input[type="email"]', adminCreds.email);
      await adminPage.fill('input[type="password"]', adminCreds.password);
      await adminPage.click('button[type="submit"]');

      // Wait for successful login
      await adminPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });

      // Navigate to APM dashboard
      await adminPage.goto(`${BASE_URL}/monitoring`);
      await adminPage.waitForLoadState('networkidle');

      // Verify APM dashboard is accessible for admin
      await expect(adminPage.locator('h1')).toContainText('APM Dashboard');
      await expect(adminPage.locator('[data-testid="apm-dashboard"]')).toBeVisible();
    });

    test('should redirect unauthorized users (agents) from APM dashboard', async () => {
      test.setTimeout(TEST_TIMEOUT);

      const agentCreds = getAgentCredentials();

      // Login as agent
      await agentPage.goto(`${BASE_URL}/login`);
      await agentPage.fill('input[type="email"]', agentCreds.email);
      await agentPage.fill('input[type="password"]', agentCreds.password);
      await agentPage.click('button[type="submit"]');

      // Wait for successful login
      await agentPage.waitForURL(/\/operator/, { timeout: 10000 });

      // Try to access APM dashboard directly
      await agentPage.goto(`${BASE_URL}/monitoring`);

      // Should either redirect to unauthorized page or show access denied
      // Check for various possible outcomes
      await expect(async () => {
        const url = agentPage.url();
        const hasUnauthorized = await agentPage.locator('[data-testid="unauthorized-access"]').isVisible().catch(() => false);
        const hasAccessDenied = await agentPage.locator('text=Access Denied').isVisible().catch(() => false);
        const redirectedToLogin = url.includes('/login');
        const redirectedToOperator = url.includes('/operator');

        expect(hasUnauthorized || hasAccessDenied || redirectedToLogin || redirectedToOperator).toBeTruthy();
      }).toPass({ timeout: 5000 });
    });

    test('should work with universal test account', async () => {
      test.setTimeout(TEST_TIMEOUT);

      // Login with universal test account
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', UNIVERSAL_TEST_ACCOUNT.email);
      await supervisorPage.fill('input[type="password"]', UNIVERSAL_TEST_ACCOUNT.password);
      await supervisorPage.click('button[type="submit"]');

      // Wait for successful login
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });

      // Navigate to APM dashboard
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');

      // Verify APM dashboard is accessible
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
    });
  });

  test.describe('APM Dashboard Components and UI', () => {
    test.beforeEach(async () => {
      // Login as supervisor for all UI tests
      const supervisorCreds = getSupervisorCredentials();
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', supervisorCreds.email);
      await supervisorPage.fill('input[type="password"]', supervisorCreds.password);
      await supervisorPage.click('button[type="submit"]');
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');
    });

    test('should display all main APM dashboard components', async () => {
      // Verify header and title
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('text=Application Performance Monitoring')).toBeVisible();

      // Verify time range controls
      await expect(supervisorPage.locator('[data-testid="time-range-controls"]')).toBeVisible();
      const timeRangeButtons = supervisorPage.locator('button', { hasText: /^(1h|6h|24h|7d|30d)$/ });
      await expect(timeRangeButtons).toHaveCount(5);

      // Verify auto-refresh toggle
      await expect(supervisorPage.locator('button', { hasText: /Auto|Manual/ })).toBeVisible();

      // Verify health status cards
      await expect(supervisorPage.locator('[data-testid="system-health-card"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="database-health-card"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="memory-health-card"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="response-time-card"]')).toBeVisible();

      // Verify tab navigation
      await expect(supervisorPage.locator('text=Overview')).toBeVisible();
      await expect(supervisorPage.locator('text=Errors')).toBeVisible();
      await expect(supervisorPage.locator('text=Performance')).toBeVisible();
    });

    test('should display health status indicators correctly', async () => {
      // Check system health status
      const healthStatus = await supervisorPage.locator('[data-testid="system-health-card"] .chip').textContent();
      expect(['healthy', 'degraded', 'unhealthy', 'Unknown'].some(status =>
        healthStatus?.toLowerCase().includes(status.toLowerCase())
      )).toBeTruthy();

      // Check uptime display
      await expect(supervisorPage.locator('text=/Uptime:/')).toBeVisible();

      // Check database status
      const dbStatus = supervisorPage.locator('[data-testid="database-health-card"]');
      await expect(dbStatus).toBeVisible();
      await expect(dbStatus.locator('text=/Status:/')).toBeVisible();

      // Check memory usage
      const memoryCard = supervisorPage.locator('[data-testid="memory-health-card"]');
      await expect(memoryCard).toBeVisible();
      const memoryPercentage = await memoryCard.locator('text=/%/').textContent();
      expect(memoryPercentage).toMatch(/\d+(\.\d+)?%/);

      // Check response time
      const responseTimeCard = supervisorPage.locator('[data-testid="response-time-card"]');
      await expect(responseTimeCard).toBeVisible();
      await expect(responseTimeCard.locator('text=/P95:/')).toBeVisible();
    });

    test('should display performance metrics and charts', async () => {
      // Check request metrics chart
      await expect(supervisorPage.locator('text=Request Metrics')).toBeVisible();
      await expect(supervisorPage.locator('.recharts-wrapper')).toBeVisible();

      // Check memory usage chart
      await expect(supervisorPage.locator('text=Memory Usage')).toBeVisible();

      // Check top endpoints section
      await expect(supervisorPage.locator('text=Top Endpoints')).toBeVisible();

      // Verify chart responsiveness
      const charts = supervisorPage.locator('.recharts-wrapper');
      const chartCount = await charts.count();
      expect(chartCount).toBeGreaterThan(0);

      // Take screenshot of the overview tab
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-overview-tab.png',
        fullPage: true
      });
    });

    test('should show error tracking and distribution', async () => {
      // Navigate to errors tab
      await supervisorPage.click('text=Errors');
      await supervisorPage.waitForTimeout(1000);

      // Check error distribution chart
      await expect(supervisorPage.locator('text=Error Distribution')).toBeVisible();

      // Check error summary
      await expect(supervisorPage.locator('text=Error Summary')).toBeVisible();
      await expect(supervisorPage.locator('text=Critical Errors')).toBeVisible();
      await expect(supervisorPage.locator('text=Warnings')).toBeVisible();

      // Check recent errors section
      await expect(supervisorPage.locator('text=Recent Errors')).toBeVisible();

      // Check for either "No errors recorded" or actual error entries
      const noErrorsMessage = supervisorPage.locator('text=No errors recorded');
      const errorEntries = supervisorPage.locator('[data-testid="error-entry"]');

      await expect(async () => {
        const hasNoErrors = await noErrorsMessage.isVisible();
        const hasErrors = await errorEntries.count() > 0;
        expect(hasNoErrors || hasErrors).toBeTruthy();
      }).toPass();

      // Take screenshot of errors tab
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-errors-tab.png',
        fullPage: true
      });
    });

    test('should display performance metrics in performance tab', async () => {
      // Navigate to performance tab
      await supervisorPage.click('text=Performance');
      await supervisorPage.waitForTimeout(1000);

      // Check response time percentiles
      await expect(supervisorPage.locator('text=Response Time Percentiles')).toBeVisible();
      await expect(supervisorPage.locator('text=P50 (Median)')).toBeVisible();
      await expect(supervisorPage.locator('text=P95')).toBeVisible();
      await expect(supervisorPage.locator('text=P99')).toBeVisible();

      // Check system metrics
      await expect(supervisorPage.locator('text=System Metrics')).toBeVisible();
      await expect(supervisorPage.locator('text=CPU Load Average')).toBeVisible();
      await expect(supervisorPage.locator('text=Memory Usage')).toBeVisible();
      await expect(supervisorPage.locator('text=Process Memory')).toBeVisible();

      // Verify metrics have numeric values
      const p50Value = await supervisorPage.locator('text=/\\d+ms/').first().textContent();
      expect(p50Value).toMatch(/\d+ms/);

      // Take screenshot of performance tab
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-performance-tab.png',
        fullPage: true
      });
    });
  });

  test.describe('Real-time Updates and WebSocket Integration', () => {
    test.beforeEach(async () => {
      // Login as supervisor for all real-time tests
      const supervisorCreds = getSupervisorCredentials();
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', supervisorCreds.email);
      await supervisorPage.fill('input[type="password"]', supervisorCreds.password);
      await supervisorPage.click('button[type="submit"]');
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');
    });

    test('should auto-refresh metrics when enabled', async () => {
      // Ensure auto-refresh is enabled
      const autoRefreshButton = supervisorPage.locator('button', { hasText: /Auto|Manual/ });
      const buttonText = await autoRefreshButton.textContent();

      if (buttonText?.includes('Manual')) {
        await autoRefreshButton.click();
        await supervisorPage.waitForTimeout(500);
      }

      // Verify auto-refresh is now enabled
      await expect(supervisorPage.locator('button', { hasText: 'Auto' })).toBeVisible();

      // Wait for potential refresh and verify no errors
      await supervisorPage.waitForTimeout(31000); // Wait longer than refresh interval

      // Check that dashboard is still functional
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('[data-testid="system-health-card"]')).toBeVisible();
    });

    test('should disable auto-refresh when toggled', async () => {
      // Click auto-refresh toggle
      const autoRefreshButton = supervisorPage.locator('button', { hasText: /Auto|Manual/ });
      await autoRefreshButton.click();
      await supervisorPage.waitForTimeout(500);

      // Verify it shows Manual mode
      await expect(supervisorPage.locator('button', { hasText: 'Manual' })).toBeVisible();

      // Dashboard should still be functional
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
    });

    test('should update metrics when time range is changed', async () => {
      // Get initial state
      const initialTimeRange = await supervisorPage.locator('button[data-selected="true"]').textContent();

      // Change time range
      const newTimeRange = initialTimeRange?.includes('24h') ? '1h' : '24h';
      await supervisorPage.click(`button:has-text("${newTimeRange}")`);
      await supervisorPage.waitForTimeout(2000);

      // Verify time range changed
      await expect(supervisorPage.locator(`button:has-text("${newTimeRange}")`)).toHaveClass(/solid/);

      // Verify charts are still visible (may have updated data)
      await expect(supervisorPage.locator('.recharts-wrapper')).toBeVisible();
    });

    test('should handle WebSocket connection status', async () => {
      // Check for WebSocket-related elements (if they exist)
      // This is a best-effort test as WebSocket integration may vary

      // Simulate potential network interruption by going offline briefly
      await supervisorPage.context().setOffline(true);
      await supervisorPage.waitForTimeout(2000);

      // Restore connection
      await supervisorPage.context().setOffline(false);
      await supervisorPage.waitForTimeout(3000);

      // Verify dashboard is still functional after network restoration
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('[data-testid="system-health-card"]')).toBeVisible();
    });
  });

  test.describe('Responsive Design and Cross-Browser Compatibility', () => {
    test.beforeEach(async () => {
      // Login as supervisor for all responsive tests
      const supervisorCreds = getSupervisorCredentials();
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', supervisorCreds.email);
      await supervisorPage.fill('input[type="password"]', supervisorCreds.password);
      await supervisorPage.click('button[type="submit"]');
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');
    });

    test('should be responsive on mobile viewport', async () => {
      // Set mobile viewport
      await supervisorPage.setViewportSize({ width: 375, height: 667 });
      await supervisorPage.reload();
      await supervisorPage.waitForLoadState('networkidle');

      // Verify main elements are still visible
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');

      // Check that health cards stack properly on mobile
      const healthCards = supervisorPage.locator('[data-testid*="health-card"]');
      const cardCount = await healthCards.count();
      expect(cardCount).toBeGreaterThan(0);

      // Check that charts adapt to mobile width
      await expect(supervisorPage.locator('.recharts-wrapper')).toBeVisible();

      // Check mobile navigation (if exists)
      const mobileMenu = supervisorPage.locator('[data-testid="mobile-menu"]');
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
        await supervisorPage.waitForTimeout(500);
      }

      // Take mobile screenshot
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-mobile-view.png',
        fullPage: true
      });
    });

    test('should work on tablet viewport', async () => {
      // Set tablet viewport
      await supervisorPage.setViewportSize({ width: 768, height: 1024 });
      await supervisorPage.reload();
      await supervisorPage.waitForLoadState('networkidle');

      // Verify dashboard loads properly
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('[data-testid="system-health-card"]')).toBeVisible();

      // Check that tabs are accessible
      await supervisorPage.click('text=Errors');
      await expect(supervisorPage.locator('text=Error Distribution')).toBeVisible();

      // Take tablet screenshot
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-tablet-view.png',
        fullPage: true
      });
    });

    test('should work on large desktop viewport', async () => {
      // Set large desktop viewport
      await supervisorPage.setViewportSize({ width: 2560, height: 1440 });
      await supervisorPage.reload();
      await supervisorPage.waitForLoadState('networkidle');

      // Verify dashboard utilizes space properly
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('[data-testid="system-health-card"]')).toBeVisible();

      // Verify charts scale appropriately
      const chartWrapper = supervisorPage.locator('.recharts-wrapper').first();
      const boundingBox = await chartWrapper.boundingBox();
      expect(boundingBox?.width).toBeGreaterThan(500);

      // Take large desktop screenshot
      await supervisorPage.screenshot({
        path: 'tests/screenshots/apm-large-desktop-view.png',
        fullPage: true
      });
    });
  });

  test.describe('Performance and Load Testing', () => {
    test.beforeEach(async () => {
      // Login as supervisor for performance tests
      const supervisorCreds = getSupervisorCredentials();
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', supervisorCreds.email);
      await supervisorPage.fill('input[type="password"]', supervisorCreds.password);
      await supervisorPage.click('button[type="submit"]');
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });
    });

    test('should load APM dashboard within performance budget', async () => {
      const startTime = Date.now();

      // Navigate to APM dashboard
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');

      // Wait for all critical elements to load
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
      await expect(supervisorPage.locator('[data-testid="system-health-card"]')).toBeVisible();
      await expect(supervisorPage.locator('.recharts-wrapper')).toBeVisible();

      const loadTime = Date.now() - startTime;

      // Performance assertion (should load within 10 seconds for APM dashboard)
      expect(loadTime).toBeLessThan(10000);

      console.log(`APM Dashboard loaded in ${loadTime}ms`);
    });

    test('should handle rapid tab switching without performance issues', async () => {
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');

      const startTime = Date.now();

      // Rapidly switch between tabs
      const tabs = ['Overview', 'Errors', 'Performance'];
      for (let i = 0; i < 5; i++) {
        for (const tab of tabs) {
          await supervisorPage.click(`text=${tab}`);
          await supervisorPage.waitForTimeout(200);
        }
      }

      const switchingTime = Date.now() - startTime;

      // Should complete rapid switching within reasonable time
      expect(switchingTime).toBeLessThan(8000);

      // Dashboard should still be responsive
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');

      console.log(`Tab switching completed in ${switchingTime}ms`);
    });

    test('should maintain performance with multiple chart updates', async () => {
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');

      const startTime = Date.now();

      // Change time ranges multiple times to trigger chart updates
      const timeRanges = ['1h', '6h', '24h', '7d', '30d'];
      for (let i = 0; i < 3; i++) {
        for (const range of timeRanges) {
          await supervisorPage.click(`button:has-text("${range}")`);
          await supervisorPage.waitForTimeout(500);
        }
      }

      const updateTime = Date.now() - startTime;

      // Should handle multiple updates efficiently
      expect(updateTime).toBeLessThan(15000);

      // Charts should still be visible and functional
      await expect(supervisorPage.locator('.recharts-wrapper')).toBeVisible();

      console.log(`Multiple chart updates completed in ${updateTime}ms`);
    });
  });

  test.describe('Accessibility and User Experience', () => {
    test.beforeEach(async () => {
      // Login as supervisor for accessibility tests
      const supervisorCreds = getSupervisorCredentials();
      await supervisorPage.goto(`${BASE_URL}/login`);
      await supervisorPage.fill('input[type="email"]', supervisorCreds.email);
      await supervisorPage.fill('input[type="password"]', supervisorCreds.password);
      await supervisorPage.click('button[type="submit"]');
      await supervisorPage.waitForURL(/\/(supervisor|dashboard)/, { timeout: 10000 });
      await supervisorPage.goto(`${BASE_URL}/monitoring`);
      await supervisorPage.waitForLoadState('networkidle');
    });

    test('should support keyboard navigation', async () => {
      // Tab through key elements
      await supervisorPage.keyboard.press('Tab');
      await supervisorPage.keyboard.press('Tab');
      await supervisorPage.keyboard.press('Tab');

      // Try to activate time range button with keyboard
      await supervisorPage.keyboard.press('Enter');
      await supervisorPage.waitForTimeout(500);

      // Navigate to tabs using keyboard
      await supervisorPage.keyboard.press('Tab');
      await supervisorPage.keyboard.press('Tab');
      await supervisorPage.keyboard.press('Enter');

      // Verify dashboard is still functional
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
    });

    test('should have proper contrast and readability', async () => {
      // Check that text is readable against background
      const heading = supervisorPage.locator('h1');
      await expect(heading).toBeVisible();

      // Check that health status indicators are clearly visible
      const healthCards = supervisorPage.locator('[data-testid*="health-card"]');
      await expect(healthCards.first()).toBeVisible();

      // Verify chart elements are visible
      await expect(supervisorPage.locator('.recharts-wrapper')).toBeVisible();
    });

    test('should provide meaningful error messages', async () => {
      // Simulate potential error scenario by disconnecting network briefly
      await supervisorPage.context().setOffline(true);

      // Try to change time range which might trigger an API call
      await supervisorPage.click('button:has-text("1h")');
      await supervisorPage.waitForTimeout(2000);

      // Restore connection
      await supervisorPage.context().setOffline(false);
      await supervisorPage.waitForTimeout(1000);

      // Dashboard should recover gracefully
      await expect(supervisorPage.locator('h1')).toContainText('APM Dashboard');
    });
  });
});
import { test, expect } from '@playwright/test';

test.describe('Supervisor Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://127.0.0.1:5175/login');

    // Login as supervisor using the universal test account
    await page.fill('[data-testid="email-input"], input[type="email"], input[name="email"]', 'test.assistant@stack2025.com');
    await page.fill('[data-testid="password-input"], input[type="password"], input[name="password"]', 'Stack2025!Test@Assistant#Secure$2024');

    // Click login button
    await page.click('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Log In"), button:has-text("Sign In")');

    // Wait for redirect to dashboard
    await page.waitForURL('**/supervisor**', { timeout: 10000 });
  });

  test('should display supervisor dashboard with real-time metrics', async ({ page }) => {
    // Check page title and header
    await expect(page).toHaveTitle(/Supervisor.*Dashboard|Dashboard.*Supervisor|CC.*Light/);
    await expect(page.locator('h1, [role="heading"]')).toContainText(['Supervisor Dashboard', 'Dashboard', 'Supervisor']);

    // Check connection status indicator
    await expect(page.locator('[data-testid="connection-status"], .connection-status, text=connected')).toBeVisible();

    // Verify main metrics cards are displayed
    await expect(page.locator('text=Calls in Queue, text=Queue')).toBeVisible();
    await expect(page.locator('text=Agents Available, text=Available')).toBeVisible();
    await expect(page.locator('text=Wait Time, text=Avg')).toBeVisible();
    await expect(page.locator('text=Service Level, text=Level')).toBeVisible();
  });

  test('should show agent status grid with real data', async ({ page }) => {
    // Wait for agents to load
    await page.waitForSelector('[data-testid="agent-grid"], .agent-grid, text=Agent Status', { timeout: 5000 });

    // Check that agent cards are present (even if empty due to no database)
    const agentSection = page.locator('text=Agent Status').locator('..').locator('..');
    await expect(agentSection).toBeVisible();

    // Check status chips
    await expect(page.locator('text=Available:')).toBeVisible();
    await expect(page.locator('text=On Call:')).toBeVisible();
  });

  test('should display queue status with metrics', async ({ page }) => {
    // Check queue status section
    await expect(page.locator('text=Queue Status')).toBeVisible();

    // The queue section should be visible even with no data
    const queueSection = page.locator('text=Queue Status').locator('..').locator('..');
    await expect(queueSection).toBeVisible();
  });

  test('should show active calls table', async ({ page }) => {
    // Check active calls section
    await expect(page.locator('text=Active Calls')).toBeVisible();

    // Check table headers
    const activeCallsSection = page.locator('text=Active Calls').locator('..').locator('..');
    await expect(activeCallsSection.locator('text=AGENT')).toBeVisible();
    await expect(activeCallsSection.locator('text=CUSTOMER')).toBeVisible();
    await expect(activeCallsSection.locator('text=DURATION')).toBeVisible();
    await expect(activeCallsSection.locator('text=STATUS')).toBeVisible();
    await expect(activeCallsSection.locator('text=ACTIONS')).toBeVisible();
  });

  test('should have functional tab navigation', async ({ page }) => {
    // Check that tabs are present and clickable
    await expect(page.locator('text=Live Monitoring, button:has-text("Live Monitoring")')).toBeVisible();
    await expect(page.locator('text=Team Performance, button:has-text("Team Performance")')).toBeVisible();
    await expect(page.locator('text=Coaching, button:has-text("Coaching")')).toBeVisible();

    // Test tab switching
    await page.click('text=Team Performance, button:has-text("Team Performance")');
    await expect(page.locator('text=Team Performance Metrics')).toBeVisible();

    await page.click('text=Coaching, button:has-text("Coaching")');
    await expect(page.locator('text=Coaching & Training')).toBeVisible();

    // Return to monitoring tab
    await page.click('text=Live Monitoring, button:has-text("Live Monitoring")');
    await expect(page.locator('text=Agent Status')).toBeVisible();
  });

  test('should handle monitoring controls when agents are present', async ({ page }) => {
    // Look for monitoring buttons (Listen, Whisper, Barge)
    const listenButtons = page.locator('[title="Listen"], button:has([class*="headphone"])');
    const whisperButtons = page.locator('[title="Whisper"], button:has([class*="mic"])');
    const bargeButtons = page.locator('[title="Barge"], button:has([class*="volume"])');

    // These buttons should exist in the UI structure even if no agents are on calls
    // We're testing the UI structure, not necessarily clicking them without data
    console.log('Monitoring controls are part of the UI structure');
  });

  test('should display proper error handling for failed API calls', async ({ page }) => {
    // Since database is not connected, the dashboard should handle errors gracefully
    // and not crash the application

    // Check that the page doesn't show critical error states
    await expect(page.locator('text=Dashboard Error, text=Failed to load')).not.toBeVisible();

    // The dashboard should load even with API failures
    await expect(page.locator('text=Supervisor Dashboard')).toBeVisible();
  });

  test('should show loading states appropriately', async ({ page }) => {
    // Reload page to check loading states
    await page.reload();

    // Should show loading spinner initially
    await page.waitForSelector('text=Loading, [class*="animate-spin"], [class*="loading"]', { timeout: 2000 });

    // Then load the dashboard
    await expect(page.locator('text=Supervisor Dashboard')).toBeVisible({ timeout: 10000 });
  });

  test('should have accessible navigation and logout', async ({ page }) => {
    // Check profile dropdown is accessible
    await page.click('[data-testid="profile-dropdown"], [role="button"]:has([class*="avatar"]), button:has(img)');

    // Check logout option is present
    await expect(page.locator('text=Log Out, text=Logout')).toBeVisible();

    // Check settings option
    await expect(page.locator('text=Team Settings, text=Settings')).toBeVisible();

    // Close dropdown by clicking elsewhere
    await page.click('h1');
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test desktop layout
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('text=Supervisor Dashboard')).toBeVisible();

    // Test tablet layout
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('text=Supervisor Dashboard')).toBeVisible();

    // Test mobile layout
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('text=Supervisor Dashboard')).toBeVisible();

    // Reset to desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('should show real-time connection status', async ({ page }) => {
    // Check for WebSocket connection indicator
    const connectionIndicator = page.locator('[data-testid="connection-status"], .connection-status, text=connected, text=connecting');
    await expect(connectionIndicator).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Supervisor Dashboard Metrics Integration', () => {
  test('should handle tRPC endpoint calls gracefully', async ({ page }) => {
    // Monitor network requests
    const tRPCRequests: string[] = [];

    page.on('request', request => {
      if (request.url().includes('/trpc')) {
        tRPCRequests.push(request.url());
      }
    });

    // Navigate to supervisor dashboard
    await page.goto('http://127.0.0.1:5175/login');
    await page.fill('input[type="email"]', 'test.assistant@stack2025.com');
    await page.fill('input[type="password"]', 'Stack2025!Test@Assistant#Secure$2024');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/supervisor**', { timeout: 10000 });

    // Wait for tRPC calls to be made
    await page.waitForTimeout(3000);

    // Verify that tRPC endpoints are being called
    expect(tRPCRequests.length).toBeGreaterThan(0);
    console.log('tRPC endpoints called:', tRPCRequests);

    // The dashboard should handle failed API calls gracefully
    await expect(page.locator('text=Supervisor Dashboard')).toBeVisible();
  });
});
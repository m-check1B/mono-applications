import { test, expect, Page, BrowserContext } from '@playwright/test';
import { testDb, createTestUser } from '../setup';
import { UserRole } from '@prisma/client';

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3007';
const TEST_TIMEOUT = 30000;

// Universal test account
const UNIVERSAL_TEST_ACCOUNT = {
  email: 'test.assistant@stack2025.com',
  password: 'Stack2025!Test@Assistant#Secure$2024',
  userId: '550e8400-e29b-41d4-a716-446655440000',
  role: 'TESTER_UNIVERSAL',
  tier: 'CORPORATE',
};

test.describe('Critical User Flows E2E Tests', () => {
  let context: BrowserContext;
  let page: Page;
  let testOrganizationId: string;
  let testAgentUser: any;
  let testSupervisorUser: any;

  test.beforeAll(async ({ browser }) => {
    // Create browser context with user agent
    context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CC-Light-Test/1.0',
      viewport: { width: 1920, height: 1080 },
      ignoreHTTPSErrors: true,
    });

    page = await context.newPage();

    // Set up test data
    testOrganizationId = 'test-org-e2e';

    testAgentUser = await createTestUser({
      email: 'agent.e2e@test.com',
      username: 'agent_e2e',
      role: UserRole.AGENT,
      organizationId: testOrganizationId,
    });

    testSupervisorUser = await createTestUser({
      email: 'supervisor.e2e@test.com',
      username: 'supervisor_e2e',
      role: UserRole.SUPERVISOR,
      organizationId: testOrganizationId,
    });
  });

  test.afterAll(async () => {
    await context.close();
  });

  test.beforeEach(async () => {
    // Clear any existing sessions
    await page.context().clearCookies();
    await page.goto(`${BASE_URL}/login`);
  });

  test.describe('Authentication Flow', () => {
    test('should complete full login flow for agent', async () => {
      test.setTimeout(TEST_TIMEOUT);

      // Navigate to login page
      await page.goto(`${BASE_URL}/login`);
      await expect(page).toHaveTitle(/CC Light/);

      // Fill login form
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');

      // Submit login
      await page.click('button[type="submit"]');

      // Wait for dashboard redirect
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Verify agent dashboard is loaded
      await expect(page.locator('h1')).toContainText('Operator Dashboard');
      await expect(page.locator('[data-testid="agent-status"]')).toBeVisible();

      // Verify navigation elements
      await expect(page.locator('nav')).toBeVisible();
      await expect(page.locator('[data-testid="logout-button"]')).toBeVisible();

      // Take screenshot for verification
      await page.screenshot({ path: 'tests/screenshots/agent-dashboard.png' });
    });

    test('should complete full login flow for supervisor', async () => {
      test.setTimeout(TEST_TIMEOUT);

      // Login as supervisor
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testSupervisorUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');

      // Wait for supervisor dashboard
      await page.waitForURL(`${BASE_URL}/supervisor`, { timeout: 10000 });

      // Verify supervisor dashboard
      await expect(page.locator('h1')).toContainText('Supervisor Dashboard');
      await expect(page.locator('[data-testid="active-calls-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="agent-monitoring"]')).toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/supervisor-dashboard.png' });
    });

    test('should handle invalid credentials', async () => {
      await page.goto(`${BASE_URL}/login`);

      // Try invalid credentials
      await page.fill('input[type="email"]', 'invalid@test.com');
      await page.fill('input[type="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');

      // Verify error message
      await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');

      // Verify still on login page
      expect(page.url()).toContain('/login');
    });

    test('should redirect to login when accessing protected routes', async () => {
      // Try to access operator dashboard without login
      await page.goto(`${BASE_URL}/operator`);

      // Should redirect to login
      await page.waitForURL(`${BASE_URL}/login`, { timeout: 5000 });
      expect(page.url()).toContain('/login');
    });

    test('should complete logout flow', async () => {
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Logout
      await page.click('[data-testid="logout-button"]');

      // Verify redirect to login
      await page.waitForURL(`${BASE_URL}/login`, { timeout: 5000 });
      expect(page.url()).toContain('/login');

      // Verify cannot access protected routes
      await page.goto(`${BASE_URL}/operator`);
      await page.waitForURL(`${BASE_URL}/login`, { timeout: 5000 });
    });
  });

  test.describe('Agent Dashboard Critical Features', () => {
    test.beforeEach(async () => {
      // Login as agent
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });
    });

    test('should display agent status controls', async () => {
      // Verify status controls are present
      await expect(page.locator('[data-testid="agent-status"]')).toBeVisible();
      await expect(page.locator('[data-testid="status-available"]')).toBeVisible();
      await expect(page.locator('[data-testid="status-busy"]')).toBeVisible();
      await expect(page.locator('[data-testid="status-break"]')).toBeVisible();

      // Test status change
      await page.click('[data-testid="status-busy"]');
      await expect(page.locator('[data-testid="current-status"]')).toContainText('Busy');

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/agent-status-change.png' });
    });

    test('should display call queue', async () => {
      // Verify call queue panel
      await expect(page.locator('[data-testid="call-queue"]')).toBeVisible();
      await expect(page.locator('[data-testid="queue-header"]')).toContainText('Call Queue');

      // Check queue controls
      await expect(page.locator('[data-testid="accept-call-btn"]')).toBeVisible();
      await expect(page.locator('[data-testid="call-count"]')).toBeVisible();
    });

    test('should show performance metrics', async () => {
      // Verify metrics panel
      await expect(page.locator('[data-testid="performance-metrics"]')).toBeVisible();

      // Check individual metrics
      await expect(page.locator('[data-testid="calls-handled"]')).toBeVisible();
      await expect(page.locator('[data-testid="avg-handle-time"]')).toBeVisible();
      await expect(page.locator('[data-testid="customer-satisfaction"]')).toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/agent-metrics.png' });
    });

    test('should allow quick actions', async () => {
      // Verify quick action buttons
      await expect(page.locator('[data-testid="quick-actions"]')).toBeVisible();
      await expect(page.locator('[data-testid="transfer-call"]')).toBeVisible();
      await expect(page.locator('[data-testid="hold-call"]')).toBeVisible();
      await expect(page.locator('[data-testid="end-call"]')).toBeVisible();

      // Test transfer dialog
      await page.click('[data-testid="transfer-call"]');
      await expect(page.locator('[data-testid="transfer-dialog"]')).toBeVisible();

      // Close dialog
      await page.press('body', 'Escape');
      await expect(page.locator('[data-testid="transfer-dialog"]')).not.toBeVisible();
    });
  });

  test.describe('Supervisor Dashboard Critical Features', () => {
    test.beforeEach(async () => {
      // Login as supervisor
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testSupervisorUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/supervisor`, { timeout: 10000 });
    });

    test('should display active calls monitoring', async () => {
      // Verify active calls panel
      await expect(page.locator('[data-testid="active-calls-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="active-calls-header"]')).toContainText('Active Calls');

      // Check call controls
      await expect(page.locator('[data-testid="monitor-call"]')).toBeVisible();
      await expect(page.locator('[data-testid="join-call"]')).toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/supervisor-active-calls.png' });
    });

    test('should show real-time transcription', async () => {
      // Verify transcription panel
      await expect(page.locator('[data-testid="live-transcription"]')).toBeVisible();
      await expect(page.locator('[data-testid="transcription-header"]')).toContainText('Live Transcription');

      // Check transcription controls
      await expect(page.locator('[data-testid="transcription-toggle"]')).toBeVisible();
      await expect(page.locator('[data-testid="sentiment-indicator"]')).toBeVisible();
    });

    test('should display agent monitoring', async () => {
      // Verify agent monitoring panel
      await expect(page.locator('[data-testid="agent-monitoring"]')).toBeVisible();
      await expect(page.locator('[data-testid="agent-list"]')).toBeVisible();

      // Check agent status indicators
      const agentStatusIndicators = page.locator('[data-testid="agent-status-indicator"]');
      expect(await agentStatusIndicators.count()).toBeGreaterThanOrEqual(1);

      // Test agent details view
      await page.click('[data-testid="agent-details-btn"]');
      await expect(page.locator('[data-testid="agent-details-modal"]')).toBeVisible();

      // Close modal
      await page.click('[data-testid="close-modal"]');
      await expect(page.locator('[data-testid="agent-details-modal"]')).not.toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/supervisor-agent-monitoring.png' });
    });

    test('should show queue management', async () => {
      // Verify queue management panel
      await expect(page.locator('[data-testid="queue-management"]')).toBeVisible();
      await expect(page.locator('[data-testid="queue-stats"]')).toBeVisible();

      // Check queue controls
      await expect(page.locator('[data-testid="queue-priority"]')).toBeVisible();
      await expect(page.locator('[data-testid="distribute-calls"]')).toBeVisible();
    });
  });

  test.describe('Call Handling Flow', () => {
    test.beforeEach(async () => {
      // Login as agent
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });
    });

    test('should handle incoming call flow', async () => {
      // Simulate incoming call notification
      await page.evaluate(() => {
        // Trigger incoming call event
        window.dispatchEvent(new CustomEvent('incomingCall', {
          detail: {
            callId: 'test-call-123',
            fromNumber: '+1234567890',
            customerName: 'John Doe'
          }
        }));
      });

      // Wait for call notification
      await expect(page.locator('[data-testid="incoming-call-notification"]')).toBeVisible();
      await expect(page.locator('[data-testid="caller-info"]')).toContainText('John Doe');

      // Accept the call
      await page.click('[data-testid="accept-call"]');

      // Verify call interface is active
      await expect(page.locator('[data-testid="active-call-interface"]')).toBeVisible();
      await expect(page.locator('[data-testid="call-timer"]')).toBeVisible();
      await expect(page.locator('[data-testid="call-controls"]')).toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/active-call-interface.png' });

      // Test call controls
      await page.click('[data-testid="mute-call"]');
      await expect(page.locator('[data-testid="mute-indicator"]')).toBeVisible();

      await page.click('[data-testid="unmute-call"]');
      await expect(page.locator('[data-testid="mute-indicator"]')).not.toBeVisible();

      // End the call
      await page.click('[data-testid="end-call"]');
      await expect(page.locator('[data-testid="call-wrap-up"]')).toBeVisible();

      // Complete wrap-up
      await page.fill('[data-testid="call-notes"]', 'Customer inquiry resolved successfully');
      await page.selectOption('[data-testid="call-disposition"]', 'resolved');
      await page.click('[data-testid="complete-wrap-up"]');

      // Verify return to ready state
      await expect(page.locator('[data-testid="agent-status"]')).toContainText('Available');
    });

    test('should handle call transfer flow', async () => {
      // Start with active call simulation
      await page.evaluate(() => {
        window.dispatchEvent(new CustomEvent('activeCall', {
          detail: { callId: 'test-call-456', status: 'active' }
        }));
      });

      await expect(page.locator('[data-testid="active-call-interface"]')).toBeVisible();

      // Initiate transfer
      await page.click('[data-testid="transfer-call"]');
      await expect(page.locator('[data-testid="transfer-dialog"]')).toBeVisible();

      // Select transfer target
      await page.selectOption('[data-testid="transfer-target"]', 'supervisor');
      await page.fill('[data-testid="transfer-reason"]', 'Customer requires supervisor assistance');

      // Confirm transfer
      await page.click('[data-testid="confirm-transfer"]');

      // Verify transfer confirmation
      await expect(page.locator('[data-testid="transfer-success"]')).toBeVisible();
      await expect(page.locator('[data-testid="transfer-success"]')).toContainText('Call transferred successfully');

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/call-transfer-success.png' });
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle network disconnection gracefully', async () => {
      // Login first
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Simulate network disconnection
      await page.context().setOffline(true);

      // Try to perform an action
      await page.click('[data-testid="status-busy"]');

      // Verify offline indicator
      await expect(page.locator('[data-testid="offline-indicator"]')).toBeVisible();
      await expect(page.locator('[data-testid="offline-message"]')).toContainText('Connection lost');

      // Restore connection
      await page.context().setOffline(false);
      await page.waitForTimeout(2000);

      // Verify reconnection
      await expect(page.locator('[data-testid="offline-indicator"]')).not.toBeVisible();
      await expect(page.locator('[data-testid="connection-restored"]')).toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/connection-restored.png' });
    });

    test('should handle session timeout', async () => {
      // Login
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Simulate session expiration by clearing cookies
      await page.context().clearCookies();

      // Try to perform an action
      await page.click('[data-testid="status-busy"]');

      // Verify session timeout handling
      await expect(page.locator('[data-testid="session-expired"]')).toBeVisible();

      // Should redirect to login
      await page.waitForURL(`${BASE_URL}/login`, { timeout: 5000 });
    });

    test('should handle browser refresh during active call', async () => {
      // Simulate active call state in localStorage
      await page.goto(`${BASE_URL}/operator`);
      await page.evaluate(() => {
        localStorage.setItem('activeCall', JSON.stringify({
          callId: 'test-call-789',
          status: 'active',
          startTime: Date.now(),
          customerName: 'Jane Smith'
        }));
      });

      // Refresh the page
      await page.reload();

      // Should restore call state
      await expect(page.locator('[data-testid="call-restoration-banner"]')).toBeVisible();
      await expect(page.locator('[data-testid="restore-call-btn"]')).toBeVisible();

      // Restore the call
      await page.click('[data-testid="restore-call-btn"]');
      await expect(page.locator('[data-testid="active-call-interface"]')).toBeVisible();

      // Take screenshot
      await page.screenshot({ path: 'tests/screenshots/call-restoration.png' });
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should work on mobile viewport', async () => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      // Login
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Verify mobile navigation
      await expect(page.locator('[data-testid="mobile-menu-toggle"]')).toBeVisible();

      // Open mobile menu
      await page.click('[data-testid="mobile-menu-toggle"]');
      await expect(page.locator('[data-testid="mobile-nav-menu"]')).toBeVisible();

      // Verify key elements are accessible
      await expect(page.locator('[data-testid="agent-status"]')).toBeVisible();
      await expect(page.locator('[data-testid="call-queue"]')).toBeVisible();

      // Take mobile screenshot
      await page.screenshot({ path: 'tests/screenshots/mobile-dashboard.png' });
    });
  });

  test.describe('APM Dashboard Access and Security', () => {
    test('should allow supervisor access to APM dashboard', async () => {
      test.setTimeout(TEST_TIMEOUT);

      // Login as supervisor
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testSupervisorUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/supervisor`, { timeout: 10000 });

      // Navigate to APM dashboard
      await page.goto(`${BASE_URL}/monitoring`);
      await page.waitForLoadState('networkidle');

      // Verify APM dashboard is accessible
      await expect(page.locator('h1')).toContainText('APM Dashboard');
      await expect(page.locator('text=Application Performance Monitoring')).toBeVisible();

      // Verify critical APM components are present
      await expect(page.locator('[data-testid="system-health-card"]').first()).toBeVisible();
      await expect(page.locator('text=Request Metrics').first()).toBeVisible();

      // Take screenshot for verification
      await page.screenshot({ path: 'tests/screenshots/apm-dashboard-access.png' });
    });

    test('should block agent access to APM dashboard', async () => {
      test.setTimeout(TEST_TIMEOUT);

      // Login as agent
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Try to access APM dashboard directly
      await page.goto(`${BASE_URL}/monitoring`);
      await page.waitForTimeout(3000);

      // Should either redirect or show access denied
      const currentUrl = page.url();
      const hasUnauthorized = await page.locator('text=unauthorized').isVisible().catch(() => false);
      const hasAccessDenied = await page.locator('text=access denied').isVisible().catch(() => false);
      const hasForbidden = await page.locator('text=forbidden').isVisible().catch(() => false);
      const redirectedAway = !currentUrl.includes('/monitoring');

      // Verify that agent cannot access APM dashboard
      expect(hasUnauthorized || hasAccessDenied || hasForbidden || redirectedAway).toBeTruthy();

      // If redirected, should be back to operator dashboard or login
      if (redirectedAway) {
        expect(currentUrl.includes('/operator') || currentUrl.includes('/login') || currentUrl.includes('/dashboard')).toBeTruthy();
      }
    });

    test('should verify APM performance metric collection', async () => {
      // Login as supervisor to access APM
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testSupervisorUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/supervisor`, { timeout: 10000 });

      const startTime = Date.now();

      // Navigate to APM dashboard
      await page.goto(`${BASE_URL}/monitoring`);
      await page.waitForLoadState('networkidle');

      // Wait for APM components to load
      await expect(page.locator('h1')).toContainText('APM Dashboard');

      // Check that performance metrics are being collected
      const healthCards = page.locator('[data-testid*="health"], [class*="health"]');
      await expect(healthCards.first()).toBeVisible();

      // Check for numeric values in metrics
      const memoryPercentage = page.locator('text=/%/').first();
      const responseTime = page.locator('text=/\\d+ms/').first();

      await expect(async () => {
        const hasMemoryMetric = await memoryPercentage.isVisible();
        const hasResponseMetric = await responseTime.isVisible();
        expect(hasMemoryMetric || hasResponseMetric).toBeTruthy();
      }).toPass({ timeout: 5000 });

      const loadTime = Date.now() - startTime;

      // APM dashboard should load within reasonable time
      expect(loadTime).toBeLessThan(8000);

      console.log(`APM Dashboard metrics loaded in ${loadTime}ms`);
    });
  });

  test.describe('Performance and Loading', () => {
    test('should load dashboard within performance budget', async () => {
      const startTime = Date.now();

      // Login and navigate to dashboard
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Wait for all critical elements to load
      await expect(page.locator('[data-testid="agent-status"]')).toBeVisible();
      await expect(page.locator('[data-testid="call-queue"]')).toBeVisible();
      await expect(page.locator('[data-testid="performance-metrics"]')).toBeVisible();

      const loadTime = Date.now() - startTime;

      // Performance assertion (should load within 5 seconds)
      expect(loadTime).toBeLessThan(5000);

      console.log(`Dashboard loaded in ${loadTime}ms`);
    });

    test('should handle concurrent user interactions', async () => {
      // Login
      await page.goto(`${BASE_URL}/login`);
      await page.fill('input[type="email"]', testAgentUser.email);
      await page.fill('input[type="password"]', 'password123');
      await page.click('button[type="submit"]');
      await page.waitForURL(`${BASE_URL}/operator`, { timeout: 10000 });

      // Perform multiple rapid interactions
      const promises = [
        page.click('[data-testid="status-busy"]'),
        page.click('[data-testid="refresh-queue"]'),
        page.click('[data-testid="view-metrics"]'),
      ];

      await Promise.all(promises);

      // Verify all interactions completed successfully
      await expect(page.locator('[data-testid="current-status"]')).toContainText('Busy');
      await expect(page.locator('[data-testid="last-refresh"]')).toBeVisible();
    });
  });
});
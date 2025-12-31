import { test, expect, Page, BrowserContext } from '@playwright/test';
import { testDb, createTestUser, createTestCampaign } from '../setup';
import { UserRole, CallStatus, CampaignType, ContactStatus } from '@prisma/client';

// Test configuration
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174';
const TEST_ORG_ID = 'test-org-e2e-workflow';

// Test data
let testOrganization: any;
let adminUser: any;
let supervisorUser: any;
let agentUser: any;
let testCampaign: any;

test.describe('End-to-End User Workflow Tests', () => {
  test.beforeAll(async () => {
    // Skip if database setup is disabled
    if (process.env.SKIP_DB_TEST_SETUP === 'true') {
      test.skip();
      return;
    }

    // Create test organization
    testOrganization = await testDb.organization.create({
      data: {
        id: TEST_ORG_ID,
        name: 'E2E Workflow Test Organization',
        domain: 'e2e-workflow.local',
        settings: {
          timezone: 'UTC',
          enableRealTimeUpdates: true,
          maxConcurrentCalls: 10
        }
      }
    });

    // Create test users
    [adminUser, supervisorUser, agentUser] = await Promise.all([
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.ADMIN,
        email: 'admin@e2e-workflow.local',
        firstName: 'Admin',
        lastName: 'User',
        passwordHash: await require('bcrypt').hash('TestPassword123!', 10)
      }),
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.SUPERVISOR,
        email: 'supervisor@e2e-workflow.local',
        firstName: 'Supervisor',
        lastName: 'User',
        passwordHash: await require('bcrypt').hash('TestPassword123!', 10)
      }),
      createTestUser({
        organizationId: testOrganization.id,
        role: UserRole.AGENT,
        email: 'agent@e2e-workflow.local',
        firstName: 'Agent',
        lastName: 'User',
        passwordHash: await require('bcrypt').hash('TestPassword123!', 10)
      })
    ]);

    // Create agent record
    await testDb.agent.create({
      data: {
        userId: agentUser.id,
        status: 'AVAILABLE',
        capacity: 3,
        currentLoad: 0,
        skills: ['sales', 'support']
      }
    });

    // Create test campaign
    testCampaign = await createTestCampaign({
      organizationId: testOrganization.id,
      name: 'E2E Test Campaign',
      type: CampaignType.OUTBOUND,
      active: false
    });

    // Create test contacts for the campaign
    await Promise.all([
      testDb.contact.create({
        data: {
          campaignId: testCampaign.id,
          phoneNumber: '+1234567890',
          name: 'Test Contact 1',
          email: 'contact1@test.com',
          status: ContactStatus.PENDING
        }
      }),
      testDb.contact.create({
        data: {
          campaignId: testCampaign.id,
          phoneNumber: '+1234567891',
          name: 'Test Contact 2',
          email: 'contact2@test.com',
          status: ContactStatus.PENDING
        }
      })
    ]);
  });

  test.afterAll(async () => {
    if (process.env.SKIP_DB_TEST_SETUP !== 'true') {
      // Cleanup test data
      await testDb.organization.delete({ where: { id: TEST_ORG_ID } }).catch(() => {});
    }
  });

  test('Admin Complete Workflow: Login → Dashboard → Campaign Management → Settings', async ({ page, context }) => {
    // Step 1: Login as Admin
    await page.goto(`${BASE_URL}/login`);
    await expect(page).toHaveTitle(/CC Light/);
    
    // Fill login form
    await page.fill('[data-testid="email-input"]', adminUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    // Wait for successful login and redirect
    await expect(page).toHaveURL(/\/admin/);
    await expect(page.locator('[data-testid="welcome-message"]')).toContainText('Admin');
    
    // Step 2: Navigate to Dashboard
    await page.click('[data-testid="dashboard-nav"]');
    await expect(page).toHaveURL(/\/admin\/dashboard/);
    
    // Verify dashboard components are loaded
    await expect(page.locator('[data-testid="call-stats-widget"]')).toBeVisible();
    await expect(page.locator('[data-testid="team-status-widget"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-calls-widget"]')).toBeVisible();
    
    // Check dashboard statistics
    const totalCallsElement = page.locator('[data-testid="total-calls-count"]');
    await expect(totalCallsElement).toBeVisible();
    
    // Step 3: Campaign Management
    await page.click('[data-testid="campaigns-nav"]');
    await expect(page).toHaveURL(/\/admin\/campaigns/);
    
    // Verify existing campaign is listed
    await expect(page.locator(`[data-testid="campaign-${testCampaign.id}"]`)).toBeVisible();
    await expect(page.locator(`[data-testid="campaign-${testCampaign.id}"]`)).toContainText('E2E Test Campaign');
    
    // Create new campaign
    await page.click('[data-testid="create-campaign-button"]');
    await expect(page.locator('[data-testid="campaign-form-modal"]')).toBeVisible();
    
    // Fill campaign form
    await page.fill('[data-testid="campaign-name-input"]', 'New E2E Campaign');
    await page.fill('[data-testid="campaign-description-input"]', 'Created during E2E testing');
    await page.selectOption('[data-testid="campaign-type-select"]', 'OUTBOUND');
    await page.click('[data-testid="save-campaign-button"]');
    
    // Verify campaign was created
    await expect(page.locator('[data-testid="success-notification"]')).toBeVisible();
    await expect(page.locator('[data-testid="campaign-list"]')).toContainText('New E2E Campaign');
    
    // Step 4: Campaign Configuration
    await page.click('[data-testid="campaign-config-button"]:first-child');
    await expect(page.locator('[data-testid="campaign-settings-form"]')).toBeVisible();
    
    // Update campaign settings
    await page.fill('[data-testid="max-concurrent-calls-input"]', '5');
    await page.fill('[data-testid="max-attempts-input"]', '3');
    await page.check('[data-testid="enable-ai-assist-checkbox"]');
    await page.click('[data-testid="save-settings-button"]');
    
    // Verify settings saved
    await expect(page.locator('[data-testid="settings-saved-notification"]')).toBeVisible();
    
    // Step 5: User Management
    await page.click('[data-testid="users-nav"]');
    await expect(page).toHaveURL(/\/admin\/users/);
    
    // Verify users are listed
    await expect(page.locator(`[data-testid="user-${adminUser.id}"]`)).toContainText('Admin User');
    await expect(page.locator(`[data-testid="user-${supervisorUser.id}"]`)).toContainText('Supervisor User');
    await expect(page.locator(`[data-testid="user-${agentUser.id}"]`)).toContainText('Agent User');
    
    // Step 6: System Settings
    await page.click('[data-testid="settings-nav"]');
    await expect(page).toHaveURL(/\/admin\/settings/);
    
    // Update organization settings
    await page.fill('[data-testid="org-name-input"]', 'Updated E2E Test Org');
    await page.selectOption('[data-testid="timezone-select"]', 'America/New_York');
    await page.check('[data-testid="enable-recording-checkbox"]');
    await page.click('[data-testid="save-org-settings-button"]');
    
    // Verify settings updated
    await expect(page.locator('[data-testid="org-settings-saved"]')).toBeVisible();
    
    // Step 7: Logout
    await page.click('[data-testid="user-menu-button"]');
    await page.click('[data-testid="logout-button"]');
    await expect(page).toHaveURL(/\/login/);
  });

  test('Supervisor Workflow: Monitoring → Call Supervision → Reporting', async ({ page }) => {
    // Create active calls for monitoring
    const activeCalls = await Promise.all([
      testDb.call.create({
        data: {
          fromNumber: '+1800555000',
          toNumber: '+1234567890',
          direction: 'OUTBOUND',
          provider: 'TWILIO',
          organizationId: testOrganization.id,
          agentId: agentUser.id,
          campaignId: testCampaign.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 180000), // 3 minutes ago
          metadata: { supervised: false }
        }
      }),
      testDb.call.create({
        data: {
          fromNumber: '+1800555001',
          toNumber: '+1234567891',
          direction: 'INBOUND',
          provider: 'TWILIO',
          organizationId: testOrganization.id,
          agentId: agentUser.id,
          status: CallStatus.IN_PROGRESS,
          startTime: new Date(Date.now() - 120000), // 2 minutes ago
          metadata: { priority: 'high' }
        }
      })
    ]);

    // Login as Supervisor
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[data-testid="email-input"]', supervisorUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/\/supervisor/);
    await expect(page.locator('[data-testid="supervisor-dashboard"]')).toBeVisible();
    
    // Step 1: Monitor Active Calls
    await expect(page.locator('[data-testid="active-calls-section"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-calls-list"]')).toContainText('Agent User');
    
    // Verify call information is displayed
    const callElement = page.locator(`[data-testid="call-${activeCalls[0].id}"]`);
    await expect(callElement).toBeVisible();
    await expect(callElement).toContainText('+1234567890');
    await expect(callElement).toContainText('IN_PROGRESS');
    
    // Step 2: Join Call for Supervision
    await page.click(`[data-testid="supervise-call-${activeCalls[0].id}"]`);
    await expect(page.locator('[data-testid="supervision-modal"]')).toBeVisible();
    
    // Supervision controls
    await expect(page.locator('[data-testid="mute-agent-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="whisper-agent-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="barge-in-button"]')).toBeVisible();
    
    // Monitor call transcript
    await expect(page.locator('[data-testid="live-transcript"]')).toBeVisible();
    
    // Leave supervision
    await page.click('[data-testid="leave-supervision-button"]');
    await expect(page.locator('[data-testid="supervision-modal"]')).not.toBeVisible();
    
    // Step 3: Team Performance
    await page.click('[data-testid="team-performance-tab"]');
    await expect(page.locator('[data-testid="team-stats-widget"]')).toBeVisible();
    
    // Check agent statistics
    const agentStats = page.locator(`[data-testid="agent-stats-${agentUser.id}"]`);
    await expect(agentStats).toBeVisible();
    await expect(agentStats).toContainText('Agent User');
    
    // Step 4: Campaign Monitoring
    await page.click('[data-testid="campaigns-tab"]');
    await expect(page.locator('[data-testid="campaign-performance-section"]')).toBeVisible();
    
    // View campaign metrics
    const campaignMetrics = page.locator(`[data-testid="campaign-metrics-${testCampaign.id}"]`);
    await expect(campaignMetrics).toBeVisible();
    await expect(campaignMetrics).toContainText('E2E Test Campaign');
    
    // Step 5: Generate Report
    await page.click('[data-testid="reports-nav"]');
    await expect(page).toHaveURL(/\/supervisor\/reports/);
    
    // Select report parameters
    await page.selectOption('[data-testid="report-type-select"]', 'daily_summary');
    await page.fill('[data-testid="date-from-input"]', new Date().toISOString().split('T')[0]);
    await page.fill('[data-testid="date-to-input"]', new Date().toISOString().split('T')[0]);
    await page.click('[data-testid="generate-report-button"]');
    
    // Verify report is generated
    await expect(page.locator('[data-testid="report-results"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="report-download-button"]')).toBeVisible();
  });

  test('Agent Workflow: Login → Handle Calls → Update Status', async ({ page }) => {
    // Create incoming call for agent
    const incomingCall = await testDb.call.create({
      data: {
        fromNumber: '+1234567890',
        toNumber: '+1800555000',
        direction: 'INBOUND',
        provider: 'TWILIO',
        organizationId: testOrganization.id,
        status: CallStatus.RINGING,
        providerCallId: 'test-call-sid-123',
        metadata: { customerInfo: { name: 'John Doe', priority: 'high' } }
      }
    });

    // Login as Agent
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[data-testid="email-input"]', agentUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/\/operator/);
    await expect(page.locator('[data-testid="agent-dashboard"]')).toBeVisible();
    
    // Step 1: Set Agent Status
    await expect(page.locator('[data-testid="agent-status-control"]')).toBeVisible();
    await page.click('[data-testid="status-available-button"]');
    await expect(page.locator('[data-testid="current-status"]')).toContainText('Available');
    
    // Step 2: Handle Incoming Call
    await expect(page.locator('[data-testid="incoming-call-notification"]')).toBeVisible();
    await expect(page.locator('[data-testid="caller-name"]')).toContainText('John Doe');
    
    // Answer the call
    await page.click('[data-testid="answer-call-button"]');
    await expect(page.locator('[data-testid="active-call-interface"]')).toBeVisible();
    
    // Verify call controls are available
    await expect(page.locator('[data-testid="mute-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="hold-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="transfer-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="hangup-button"]')).toBeVisible();
    
    // Step 3: Use Call Features
    // Mute call
    await page.click('[data-testid="mute-button"]');
    await expect(page.locator('[data-testid="mute-status"]')).toContainText('Muted');
    
    // Unmute call
    await page.click('[data-testid="mute-button"]');
    await expect(page.locator('[data-testid="mute-status"]')).toContainText('Unmuted');
    
    // Add call notes
    await page.fill('[data-testid="call-notes-input"]', 'Customer inquiring about billing. Resolved payment issue.');
    
    // Step 4: View Customer Information
    await expect(page.locator('[data-testid="customer-info-panel"]')).toBeVisible();
    await expect(page.locator('[data-testid="customer-name"]')).toContainText('John Doe');
    await expect(page.locator('[data-testid="customer-phone"]')).toContainText('+1234567890');
    
    // Step 5: Complete Call
    await page.selectOption('[data-testid="call-disposition-select"]', 'resolved');
    await page.click('[data-testid="hangup-button"]');
    
    // Verify call completion
    await expect(page.locator('[data-testid="call-completed-notification"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-call-interface"]')).not.toBeVisible();
    
    // Step 6: Handle Queue
    await expect(page.locator('[data-testid="call-queue-widget"]')).toBeVisible();
    const queueLength = await page.locator('[data-testid="queue-length"]').textContent();
    console.log('Current queue length:', queueLength);
    
    // Step 7: Break Time
    await page.click('[data-testid="status-break-button"]');
    await page.selectOption('[data-testid="break-reason-select"]', 'lunch');
    await page.click('[data-testid="confirm-break-button"]');
    
    await expect(page.locator('[data-testid="current-status"]')).toContainText('Break');
    await expect(page.locator('[data-testid="break-timer"]')).toBeVisible();
    
    // Return from break
    await page.click('[data-testid="end-break-button"]');
    await expect(page.locator('[data-testid="current-status"]')).toContainText('Available');
  });

  test('Campaign Execution Workflow: Setup → Launch → Monitor → Results', async ({ page, context }) => {
    // Login as Admin for campaign setup
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[data-testid="email-input"]', adminUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/\/admin/);
    
    // Step 1: Campaign Setup
    await page.click('[data-testid="campaigns-nav"]');
    await page.click(`[data-testid="edit-campaign-${testCampaign.id}"]`);
    
    // Configure campaign script
    await page.fill('[data-testid="campaign-script-input"]', 
      'Hello {customerName}, this is {agentName} from E2E Test Company. How are you today?'
    );
    
    // Set campaign settings
    await page.fill('[data-testid="max-concurrent-calls-input"]', '2');
    await page.fill('[data-testid="max-attempts-input"]', '3');
    await page.fill('[data-testid="time-between-attempts-input"]', '15');
    
    // Set dialing hours
    await page.fill('[data-testid="dialing-start-time"]', '09:00');
    await page.fill('[data-testid="dialing-end-time"]', '17:00');
    
    await page.click('[data-testid="save-campaign-button"]');
    await expect(page.locator('[data-testid="campaign-saved-notification"]')).toBeVisible();
    
    // Step 2: Review Contacts
    await page.click(`[data-testid="view-contacts-${testCampaign.id}"]`);
    await expect(page.locator('[data-testid="contacts-list"]')).toBeVisible();
    
    // Verify contacts are loaded
    await expect(page.locator('[data-testid="contact-count"]')).toContainText('2'); // 2 test contacts
    await expect(page.locator('[data-testid="contacts-table"]')).toContainText('Test Contact 1');
    await expect(page.locator('[data-testid="contacts-table"]')).toContainText('Test Contact 2');
    
    // Step 3: Launch Campaign
    await page.click('[data-testid="back-to-campaigns"]');
    await page.click(`[data-testid="start-campaign-${testCampaign.id}"]`);
    
    // Confirm campaign launch
    await expect(page.locator('[data-testid="launch-confirmation-modal"]')).toBeVisible();
    await page.click('[data-testid="confirm-launch-button"]');
    
    // Verify campaign is active
    await expect(page.locator('[data-testid="campaign-started-notification"]')).toBeVisible();
    await expect(page.locator(`[data-testid="campaign-status-${testCampaign.id}"]`)).toContainText('Active');
    
    // Step 4: Monitor Campaign Progress
    await page.click(`[data-testid="monitor-campaign-${testCampaign.id}"]`);
    await expect(page.locator('[data-testid="campaign-monitor-dashboard"]')).toBeVisible();
    
    // Check real-time metrics
    await expect(page.locator('[data-testid="contacts-dialed-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="contacts-connected-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="conversion-rate"]')).toBeVisible();
    
    // Monitor active calls
    await expect(page.locator('[data-testid="campaign-active-calls"]')).toBeVisible();
    
    // Step 5: Campaign Analytics
    await page.click('[data-testid="campaign-analytics-tab"]');
    await expect(page.locator('[data-testid="analytics-dashboard"]')).toBeVisible();
    
    // Check analytics widgets
    await expect(page.locator('[data-testid="call-volume-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-rate-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="agent-performance-table"]')).toBeVisible();
    
    // Step 6: Pause/Stop Campaign
    await page.click('[data-testid="campaign-controls-tab"]');
    await page.click('[data-testid="pause-campaign-button"]');
    
    await expect(page.locator('[data-testid="campaign-paused-notification"]')).toBeVisible();
    await expect(page.locator(`[data-testid="campaign-status-${testCampaign.id}"]`)).toContainText('Paused');
    
    // Resume campaign
    await page.click('[data-testid="resume-campaign-button"]');
    await expect(page.locator('[data-testid="campaign-resumed-notification"]')).toBeVisible();
    
    // Stop campaign
    await page.click('[data-testid="stop-campaign-button"]');
    await page.click('[data-testid="confirm-stop-button"]');
    
    await expect(page.locator('[data-testid="campaign-stopped-notification"]')).toBeVisible();
    await expect(page.locator(`[data-testid="campaign-status-${testCampaign.id}"]`)).toContainText('Stopped');
  });

  test('Cross-Browser Compatibility: Dashboard Functionality', async ({ page, browserName }) => {
    // Test core functionality across different browsers
    console.log(`Testing on browser: ${browserName}`);
    
    // Login
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[data-testid="email-input"]', supervisorUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/\/supervisor/);
    
    // Test responsive layout
    await page.setViewportSize({ width: 1920, height: 1080 }); // Desktop
    await expect(page.locator('[data-testid="sidebar-nav"]')).toBeVisible();
    
    await page.setViewportSize({ width: 768, height: 1024 }); // Tablet
    await expect(page.locator('[data-testid="mobile-nav-toggle"]')).toBeVisible();
    
    await page.setViewportSize({ width: 375, height: 667 }); // Mobile
    await page.click('[data-testid="mobile-nav-toggle"]');
    await expect(page.locator('[data-testid="mobile-nav-menu"]')).toBeVisible();
    
    // Reset to desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Test interactive features
    await expect(page.locator('[data-testid="dashboard-widgets"]')).toBeVisible();
    
    // Test WebSocket connections (if available)
    const hasWebSocket = await page.evaluate(() => {
      return typeof WebSocket !== 'undefined';
    });
    
    if (hasWebSocket) {
      // Verify real-time updates work
      await expect(page.locator('[data-testid="realtime-indicator"]')).toBeVisible();
    }
    
    // Test browser-specific features
    if (browserName === 'chromium') {
      // Test Chrome-specific features
      const notificationPermission = await page.evaluate(() => {
        return Notification.permission;
      });
      console.log('Notification permission:', notificationPermission);
    }
    
    if (browserName === 'firefox') {
      // Test Firefox-specific compatibility
      const userAgent = await page.evaluate(() => navigator.userAgent);
      expect(userAgent).toContain('Firefox');
    }
    
    if (browserName === 'webkit') {
      // Test Safari/WebKit compatibility
      const isSafari = await page.evaluate(() => {
        return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
      });
      // Note: Playwright's webkit is not exactly Safari
    }
  });

  test('Performance and Load Testing', async ({ page }) => {
    // Create large dataset for performance testing
    const largeCampaign = await createTestCampaign({
      organizationId: testOrganization.id,
      name: 'Performance Test Campaign',
      active: true
    });

    // Create many test calls
    const callsData = [];
    for (let i = 0; i < 100; i++) {
      callsData.push({
        fromNumber: `+180055${i.toString().padStart(4, '0')}`,
        toNumber: `+198765${i.toString().padStart(4, '0')}`,
        direction: i % 2 === 0 ? 'INBOUND' : 'OUTBOUND',
        provider: 'TWILIO',
        organizationId: testOrganization.id,
        campaignId: largeCampaign.id,
        status: ['COMPLETED', 'IN_PROGRESS', 'QUEUED', 'FAILED'][i % 4],
        startTime: new Date(Date.now() - (i * 60000)),
        duration: i % 4 === 0 ? 60 + (i % 300) : null
      });
    }
    
    await testDb.call.createMany({ data: callsData });
    
    // Login and measure performance
    const startTime = Date.now();
    
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[data-testid="email-input"]', supervisorUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    await expect(page).toHaveURL(/\/supervisor/);
    
    // Measure dashboard load time
    const dashboardLoadTime = Date.now() - startTime;
    expect(dashboardLoadTime).toBeLessThan(5000); // Should load within 5 seconds
    
    // Test pagination with large dataset
    await page.click('[data-testid="calls-history-tab"]');
    await expect(page.locator('[data-testid="calls-table"]')).toBeVisible();
    
    // Test filtering performance
    const filterStartTime = Date.now();
    await page.selectOption('[data-testid="status-filter"]', 'COMPLETED');
    await expect(page.locator('[data-testid="filtered-results"]')).toBeVisible();
    const filterTime = Date.now() - filterStartTime;
    expect(filterTime).toBeLessThan(2000); // Filtering should be fast
    
    // Test sorting performance
    const sortStartTime = Date.now();
    await page.click('[data-testid="sort-by-date"]');
    await page.waitForTimeout(500); // Allow for sort to complete
    const sortTime = Date.now() - sortStartTime;
    expect(sortTime).toBeLessThan(1000); // Sorting should be very fast
    
    // Check memory usage (if available)
    const memoryInfo = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize
      } : null;
    });
    
    if (memoryInfo) {
      console.log('Memory usage:', memoryInfo);
      // Basic memory sanity check
      expect(memoryInfo.usedJSHeapSize).toBeLessThan(100 * 1024 * 1024); // < 100MB
    }
  });

  test('Error Handling and Recovery', async ({ page }) => {
    // Test network error handling
    await page.goto(`${BASE_URL}/login`);
    
    // Simulate network failure
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    await page.fill('[data-testid="email-input"]', adminUser.email);
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.click('[data-testid="login-button"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="network-error-message"]')).toBeVisible();
    
    // Restore network and retry
    await page.unroute('**/api/**');
    await page.click('[data-testid="retry-button"]');
    
    // Should succeed now
    await expect(page).toHaveURL(/\/admin/);
    
    // Test invalid data handling
    await page.goto(`${BASE_URL}/admin/campaigns`);
    
    // Try to create campaign with invalid data
    await page.click('[data-testid="create-campaign-button"]');
    await page.click('[data-testid="save-campaign-button"]'); // Submit without filling required fields
    
    // Should show validation errors
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="campaign-form-modal"]')).toBeVisible(); // Modal should stay open
    
    // Fix errors and submit
    await page.fill('[data-testid="campaign-name-input"]', 'Error Test Campaign');
    await page.selectOption('[data-testid="campaign-type-select"]', 'OUTBOUND');
    await page.click('[data-testid="save-campaign-button"]');
    
    // Should succeed now
    await expect(page.locator('[data-testid="success-notification"]')).toBeVisible();
  });
});

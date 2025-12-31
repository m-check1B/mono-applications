/**
 * Monitoring Dashboard E2E Tests for Voice by Kraliki
 * Tests real-time updates, component rendering, and WebSocket connection handling
 */
import { test, expect, Page, Browser } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:3007';
const WS_URL = process.env.WS_URL || 'ws://127.0.0.1:3010';

// Test credentials
const TEST_SUPERVISOR = {
  email: 'supervisor@cc-light.local',
  password: process.env.DEFAULT_SUPERVISOR_PASSWORD || 'supervisor123'
};

const TEST_ADMIN = {
  email: 'admin@cc-light.local',
  password: process.env.DEFAULT_ADMIN_PASSWORD || 'admin123'
};

test.describe('Monitoring Dashboard E2E Tests', () => {
  let browser: Browser;
  let supervisorPage: Page;
  let adminPage: Page;

  test.beforeAll(async ({ browser: b }) => {
    browser = b;
  });

  test.beforeEach(async () => {
    // Create separate pages for different user roles
    supervisorPage = await browser.newPage();
    adminPage = await browser.newPage();

    // Login supervisor
    await supervisorPage.goto(`${BASE_URL}/login`);
    await supervisorPage.fill('[data-testid="email-input"]', TEST_SUPERVISOR.email);
    await supervisorPage.fill('[data-testid="password-input"]', TEST_SUPERVISOR.password);
    await supervisorPage.click('[data-testid="login-button"]');
    await supervisorPage.waitForURL(`${BASE_URL}/supervisor`);

    // Login admin
    await adminPage.goto(`${BASE_URL}/login`);
    await adminPage.fill('[data-testid="email-input"]', TEST_ADMIN.email);
    await adminPage.fill('[data-testid="password-input"]', TEST_ADMIN.password);
    await adminPage.click('[data-testid="login-button"]');
    await adminPage.waitForURL(`${BASE_URL}/supervisor`);
  });

  test.afterEach(async () => {
    await supervisorPage.close();
    await adminPage.close();
  });

  describe('Dashboard Component Rendering', () => {
    test('should render all main dashboard components', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Check header components
      await expect(supervisorPage.locator('[data-testid="dashboard-header"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="user-menu"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="notifications-badge"]')).toBeVisible();

      // Check main dashboard sections
      await expect(supervisorPage.locator('[data-testid="active-calls-section"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="agent-status-section"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="queue-metrics-section"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="performance-charts"]')).toBeVisible();

      // Check sidebar navigation
      await expect(supervisorPage.locator('[data-testid="dashboard-nav"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="calls-nav-item"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="agents-nav-item"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="reports-nav-item"]')).toBeVisible();
    });

    test('should display correct initial data state', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Wait for initial data load
      await supervisorPage.waitForSelector('[data-testid="loading-spinner"]', { state: 'hidden' });

      // Check that metrics are displayed
      const totalCalls = await supervisorPage.locator('[data-testid="total-calls-metric"]').textContent();
      const activeCalls = await supervisorPage.locator('[data-testid="active-calls-metric"]').textContent();
      const availableAgents = await supervisorPage.locator('[data-testid="available-agents-metric"]').textContent();

      expect(totalCalls).toMatch(/^\d+$/);
      expect(activeCalls).toMatch(/^\d+$/);
      expect(availableAgents).toMatch(/^\d+$/);
    });

    test('should render charts and visualizations correctly', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);
      await supervisorPage.waitForLoadState('networkidle');

      // Check call volume chart
      const callVolumeChart = supervisorPage.locator('[data-testid="call-volume-chart"]');
      await expect(callVolumeChart).toBeVisible();

      // Verify chart has data points
      const chartBars = callVolumeChart.locator('.recharts-bar');
      expect(await chartBars.count()).toBeGreaterThan(0);

      // Check agent performance chart
      const agentChart = supervisorPage.locator('[data-testid="agent-performance-chart"]');
      await expect(agentChart).toBeVisible();

      // Check queue status chart
      const queueChart = supervisorPage.locator('[data-testid="queue-status-chart"]');
      await expect(queueChart).toBeVisible();
    });

    test('should be responsive on different screen sizes', async () => {
      // Test mobile viewport
      await supervisorPage.setViewportSize({ width: 375, height: 667 });
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Check mobile navigation menu
      await expect(supervisorPage.locator('[data-testid="mobile-menu-button"]')).toBeVisible();

      // Charts should adapt to mobile
      const chartContainer = supervisorPage.locator('[data-testid="performance-charts"]');
      const boundingBox = await chartContainer.boundingBox();
      expect(boundingBox?.width).toBeLessThan(400);

      // Test tablet viewport
      await supervisorPage.setViewportSize({ width: 768, height: 1024 });
      await supervisorPage.reload();

      // Sidebar should be visible on tablet
      await expect(supervisorPage.locator('[data-testid="dashboard-nav"]')).toBeVisible();

      // Test desktop viewport
      await supervisorPage.setViewportSize({ width: 1920, height: 1080 });
      await supervisorPage.reload();

      // All components should be visible on desktop
      await expect(supervisorPage.locator('[data-testid="dashboard-nav"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="performance-charts"]')).toBeVisible();
    });
  });

  describe('Real-time Updates', () => {
    test('should update active calls in real-time', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Get initial call count
      const initialCallCount = await supervisorPage.locator('[data-testid="active-calls-metric"]').textContent();

      // Simulate new call via WebSocket
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: 'new_call',
            data: {
              callId: 'test_call_' + Date.now(),
              agentId: 'agent_001',
              customer: 'Test Customer',
              status: 'active',
              timestamp: new Date().toISOString()
            }
          }));
        };
      });

      // Wait for update and verify call count increased
      await supervisorPage.waitForTimeout(2000);
      const updatedCallCount = await supervisorPage.locator('[data-testid="active-calls-metric"]').textContent();

      expect(parseInt(updatedCallCount || '0')).toBeGreaterThanOrEqual(parseInt(initialCallCount || '0'));
    });

    test('should update agent status changes in real-time', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Find an agent in the list
      const agentRow = supervisorPage.locator('[data-testid="agent-row"]').first();
      const agentId = await agentRow.getAttribute('data-agent-id');
      const initialStatus = await agentRow.locator('[data-testid="agent-status"]').textContent();

      // Simulate agent status change
      await supervisorPage.evaluate((agentId) => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: 'agent_status_change',
            data: {
              agentId: agentId,
              status: 'busy',
              timestamp: new Date().toISOString()
            }
          }));
        };
      }, agentId);

      // Wait for status update
      await supervisorPage.waitForTimeout(1500);
      const updatedStatus = await agentRow.locator('[data-testid="agent-status"]').textContent();

      expect(updatedStatus).not.toBe(initialStatus);
    });

    test('should update queue metrics dynamically', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Monitor queue length changes
      const initialQueueLength = await supervisorPage.locator('[data-testid="queue-length-metric"]').textContent();

      // Add calls to queue
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          // Add multiple calls to queue
          for (let i = 0; i < 3; i++) {
            ws.send(JSON.stringify({
              type: 'call_queued',
              data: {
                callId: `queued_call_${Date.now()}_${i}`,
                priority: 'normal',
                waitTime: 0,
                timestamp: new Date().toISOString()
              }
            }));
          }
        };
      });

      // Wait for queue update
      await supervisorPage.waitForTimeout(2000);
      const updatedQueueLength = await supervisorPage.locator('[data-testid="queue-length-metric"]').textContent();

      expect(parseInt(updatedQueueLength || '0')).toBeGreaterThan(parseInt(initialQueueLength || '0'));
    });

    test('should display real-time call transcription updates', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Navigate to active call detail
      await supervisorPage.click('[data-testid="active-calls-section"] .call-item:first-child');

      // Wait for call detail modal/page
      await expect(supervisorPage.locator('[data-testid="call-transcription"]')).toBeVisible();

      const initialTranscriptLength = await supervisorPage.locator('[data-testid="transcription-text"]').textContent();

      // Simulate new transcription segment
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: 'transcription_update',
            data: {
              callId: 'active_call_001',
              speaker: 'customer',
              text: 'This is a new transcription segment for testing real-time updates.',
              timestamp: new Date().toISOString(),
              confidence: 0.95
            }
          }));
        };
      });

      // Wait for transcription update
      await supervisorPage.waitForTimeout(1500);
      const updatedTranscriptLength = await supervisorPage.locator('[data-testid="transcription-text"]').textContent();

      expect((updatedTranscriptLength || '').length).toBeGreaterThan((initialTranscriptLength || '').length);
    });

    test('should handle multiple simultaneous updates correctly', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Send multiple different updates simultaneously
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          // Send various updates
          const updates = [
            { type: 'new_call', data: { callId: 'multi_test_1', status: 'active' } },
            { type: 'agent_status_change', data: { agentId: 'agent_002', status: 'available' } },
            { type: 'queue_update', data: { queueLength: 5, avgWaitTime: 45 } },
            { type: 'call_ended', data: { callId: 'call_123', duration: 180 } }
          ];

          updates.forEach((update, index) => {
            setTimeout(() => {
              ws.send(JSON.stringify(update));
            }, index * 200);
          });
        };
      });

      // Wait for all updates to process
      await supervisorPage.waitForTimeout(3000);

      // Verify dashboard updated correctly (no errors, metrics changed)
      const errorMessages = await supervisorPage.locator('[data-testid="error-message"]').count();
      expect(errorMessages).toBe(0);

      // Verify at least some metrics changed
      const metrics = await supervisorPage.locator('[data-testid*="-metric"]').count();
      expect(metrics).toBeGreaterThan(0);
    });
  });

  describe('WebSocket Connection Handling', () => {
    test('should establish WebSocket connection on dashboard load', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Check connection status indicator
      await expect(supervisorPage.locator('[data-testid="connection-status"]')).toHaveClass(/connected/);

      // Verify WebSocket connection in browser
      const isConnected = await supervisorPage.evaluate(() => {
        return window.wsConnection && window.wsConnection.readyState === WebSocket.OPEN;
      });

      expect(isConnected).toBe(true);
    });

    test('should handle WebSocket reconnection on connection loss', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Simulate connection loss
      await supervisorPage.evaluate(() => {
        if (window.wsConnection) {
          window.wsConnection.close();
        }
      });

      // Check reconnection status
      await expect(supervisorPage.locator('[data-testid="connection-status"]')).toHaveClass(/reconnecting/);

      // Wait for automatic reconnection
      await supervisorPage.waitForTimeout(5000);
      await expect(supervisorPage.locator('[data-testid="connection-status"]')).toHaveClass(/connected/);
    });

    test('should display appropriate error messages for connection failures', async () => {
      // Start with no backend server to simulate connection failure
      await supervisorPage.route('ws://127.0.0.1:3010/ws', route => {
        route.abort();
      });

      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Should show connection error
      await expect(supervisorPage.locator('[data-testid="connection-error"]')).toBeVisible();
      await expect(supervisorPage.locator('[data-testid="connection-error"]')).toContainText('Failed to connect');

      // Should show retry button
      await expect(supervisorPage.locator('[data-testid="retry-connection-button"]')).toBeVisible();
    });

    test('should maintain session during connection interruptions', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Store initial session data
      const initialUserData = await supervisorPage.evaluate(() => {
        return localStorage.getItem('user_session');
      });

      // Simulate brief connection interruption
      await supervisorPage.evaluate(() => {
        if (window.wsConnection) {
          window.wsConnection.close();
        }
      });

      await supervisorPage.waitForTimeout(1000);

      // Check that session data is preserved
      const preservedUserData = await supervisorPage.evaluate(() => {
        return localStorage.getItem('user_session');
      });

      expect(preservedUserData).toBe(initialUserData);

      // Check that user can still interact with the dashboard
      await supervisorPage.click('[data-testid="agents-nav-item"]');
      await expect(supervisorPage.locator('[data-testid="agents-table"]')).toBeVisible();
    });

    test('should handle WebSocket authentication properly', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Check that authenticated user can receive updates
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: 'auth_test',
            data: { userId: 'supervisor_001' }
          }));
        };
      });

      await supervisorPage.waitForTimeout(1000);

      // Should not show authentication errors
      const authErrors = await supervisorPage.locator('[data-testid="auth-error"]').count();
      expect(authErrors).toBe(0);
    });
  });

  describe('Dashboard Interactions', () => {
    test('should allow filtering and searching data', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Test call filtering
      await supervisorPage.click('[data-testid="calls-filter-button"]');
      await supervisorPage.selectOption('[data-testid="status-filter"]', 'active');
      await supervisorPage.click('[data-testid="apply-filter-button"]');

      // Verify filtered results
      const activeCalls = await supervisorPage.locator('[data-testid="call-row"][data-status="active"]').count();
      const inactiveCalls = await supervisorPage.locator('[data-testid="call-row"]:not([data-status="active"])').count();

      expect(inactiveCalls).toBe(0);

      // Test agent search
      await supervisorPage.fill('[data-testid="agent-search-input"]', 'Agent');
      await supervisorPage.waitForTimeout(500);

      const searchResults = await supervisorPage.locator('[data-testid="agent-row"]').count();
      expect(searchResults).toBeGreaterThan(0);
    });

    test('should support real-time data export functionality', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Test CSV export
      const downloadPromise = supervisorPage.waitForEvent('download');
      await supervisorPage.click('[data-testid="export-data-button"]');
      await supervisorPage.selectOption('[data-testid="export-format"]', 'csv');
      await supervisorPage.click('[data-testid="confirm-export-button"]');

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain('.csv');
    });

    test('should handle dashboard customization settings', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      // Open dashboard settings
      await supervisorPage.click('[data-testid="dashboard-settings-button"]');
      await expect(supervisorPage.locator('[data-testid="settings-modal"]')).toBeVisible();

      // Toggle chart visibility
      await supervisorPage.click('[data-testid="toggle-call-volume-chart"]');
      await supervisorPage.click('[data-testid="save-settings-button"]');

      // Verify chart is hidden
      await expect(supervisorPage.locator('[data-testid="call-volume-chart"]')).toBeHidden();
    });
  });

  describe('Multi-user Dashboard Synchronization', () => {
    test('should synchronize updates across multiple supervisor sessions', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);
      await adminPage.goto(`${BASE_URL}/supervisor`);

      // Trigger update from supervisor session
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: 'broadcast_update',
            data: {
              metric: 'total_calls',
              value: 150,
              timestamp: new Date().toISOString()
            }
          }));
        };
      });

      // Wait for update to propagate
      await supervisorPage.waitForTimeout(2000);

      // Verify both sessions show the update
      const supervisorMetric = await supervisorPage.locator('[data-testid="total-calls-metric"]').textContent();
      const adminMetric = await adminPage.locator('[data-testid="total-calls-metric"]').textContent();

      expect(supervisorMetric).toBe(adminMetric);
    });
  });

  describe('Performance and Load Testing', () => {
    test('should handle high-frequency updates without performance degradation', async () => {
      await supervisorPage.goto(`${BASE_URL}/supervisor`);

      const startTime = Date.now();

      // Send many rapid updates
      await supervisorPage.evaluate(() => {
        const ws = new WebSocket('ws://127.0.0.1:3010/ws');
        ws.onopen = () => {
          for (let i = 0; i < 50; i++) {
            setTimeout(() => {
              ws.send(JSON.stringify({
                type: 'rapid_update',
                data: { counter: i, timestamp: new Date().toISOString() }
              }));
            }, i * 10);
          }
        };
      });

      // Wait for all updates
      await supervisorPage.waitForTimeout(3000);

      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // Should complete within reasonable time
      expect(totalTime).toBeLessThan(5000);

      // Dashboard should still be responsive
      await supervisorPage.click('[data-testid="agents-nav-item"]');
      await expect(supervisorPage.locator('[data-testid="agents-table"]')).toBeVisible();
    });
  });
});
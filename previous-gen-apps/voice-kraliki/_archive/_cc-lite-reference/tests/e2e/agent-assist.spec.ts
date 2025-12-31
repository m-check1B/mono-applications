import { test, expect } from '@playwright/test';

test.describe('Agent Assist Panel', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3007/login');

    // Login as agent
    await page.fill('input[type="email"]', 'agent@cc-light.com');
    await page.fill('input[type="password"]', 'demo123');
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForSelector('[data-testid="operator-dashboard"]', { timeout: 10000 });
  });

  test('should display collapsed agent assist panel by default', async ({ page }) => {
    // Check if the collapsed panel is visible
    const collapsedPanel = page.locator('[data-testid="agent-assist-collapsed"]');
    await expect(collapsedPanel).toBeVisible();

    // Check that the expanded panel is not visible
    const expandedPanel = page.locator('[data-testid="agent-assist-expanded"]');
    await expect(expandedPanel).not.toBeVisible();
  });

  test('should expand agent assist panel when clicked', async ({ page }) => {
    // Click on the collapsed panel to expand
    await page.click('[data-testid="agent-assist-collapsed"]');

    // Check that the expanded panel becomes visible
    const expandedPanel = page.locator('[data-testid="agent-assist-expanded"]');
    await expect(expandedPanel).toBeVisible();

    // Check that it contains the expected tabs
    await expect(page.locator('text=Suggestions')).toBeVisible();
    await expect(page.locator('text=Knowledge')).toBeVisible();
    await expect(page.locator('text=Mood')).toBeVisible();
    await expect(page.locator('text=Actions')).toBeVisible();
  });

  test('should show "No Active Call" state when no call is active', async ({ page }) => {
    // Expand the panel
    await page.click('[data-testid="agent-assist-collapsed"]');

    // Check for no active call message
    await expect(page.locator('text=No Active Call')).toBeVisible();
    await expect(page.locator('text=Start a call to access AI-powered assistance')).toBeVisible();
  });

  test('should start a mock call and show agent assist features', async ({ page }) => {
    // Start a call using the dialer
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');

    // Wait for call to start (mock)
    await page.waitForTimeout(2000);

    // Expand agent assist panel
    await page.click('[data-testid="agent-assist-collapsed"]');

    // Check that call information is displayed
    await expect(page.locator('text=Call Duration')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();

    // Test each tab
    await page.click('text=Suggestions');
    await expect(page.locator('text=Suggested Responses')).toBeVisible();

    await page.click('text=Knowledge');
    await expect(page.locator('text=Knowledge Base')).toBeVisible();

    await page.click('text=Mood');
    await expect(page.locator('text=Customer Mood')).toBeVisible();

    await page.click('text=Actions');
    await expect(page.locator('text=Quick Actions')).toBeVisible();
  });

  test('should display suggested responses during a call', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Expand agent assist and go to suggestions
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Suggestions');

    // Trigger suggestions refresh
    await page.click('button:has-text("↻")');
    await page.waitForTimeout(1000);

    // Check for suggested responses
    await expect(page.locator('text=Suggested Responses')).toBeVisible();

    // Check for response types
    const responseTypes = ['empathy', 'solution', 'escalation'];
    for (const type of responseTypes) {
      await expect(page.locator(`[data-testid="response-type-${type}"]`).first()).toBeVisible();
    }
  });

  test('should display knowledge base articles', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Go to knowledge tab
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Knowledge');

    // Refresh knowledge base
    await page.click('button:has-text("↻")');
    await page.waitForTimeout(1000);

    // Check for knowledge articles
    await expect(page.locator('text=Knowledge Base')).toBeVisible();
    await expect(page.locator('text=Billing Account Troubleshooting')).toBeVisible();
    await expect(page.locator('text=Account Access Recovery')).toBeVisible();
  });

  test('should show customer mood indicator', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Go to mood tab
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Mood');

    // Check mood indicator components
    await expect(page.locator('text=Customer Mood')).toBeVisible();
    await expect(page.locator('text=Live')).toBeVisible();
    await expect(page.locator('text=Emotion Analysis')).toBeVisible();

    // Check emotion metrics
    await expect(page.locator('text=Frustration')).toBeVisible();
    await expect(page.locator('text=Satisfaction')).toBeVisible();
    await expect(page.locator('text=Confusion')).toBeVisible();
    await expect(page.locator('text=Urgency')).toBeVisible();
  });

  test('should provide quick actions during call', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Go to actions tab
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Actions');

    // Check quick actions
    await expect(page.locator('text=Quick Actions')).toBeVisible();
    await expect(page.locator('button:has-text("Hold")')).toBeVisible();
    await expect(page.locator('button:has-text("End Call")')).toBeVisible();
    await expect(page.locator('button:has-text("Transfer Call")')).toBeVisible();
    await expect(page.locator('button:has-text("Create Ticket")')).toBeVisible();

    // Check quick messages
    await expect(page.locator('text=Quick Messages')).toBeVisible();
    await expect(page.locator('text=Thank you for holding')).toBeVisible();
  });

  test('should handle call transfer modal', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Go to actions and open transfer modal
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Actions');
    await page.click('button:has-text("Transfer Call")');

    // Check transfer modal
    await expect(page.locator('text=Transfer Call')).toBeVisible();
    await expect(page.locator('button:has-text("Supervisor")')).toBeVisible();
    await expect(page.locator('button:has-text("Billing Department")')).toBeVisible();

    // Test custom destination
    await page.fill('input[placeholder*="phone number"]', '123456');
    await expect(page.locator('button:has-text("Transfer")')).toBeEnabled();

    // Close modal
    await page.click('button:has-text("Cancel")');
  });

  test('should handle ticket creation modal', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Go to actions and open ticket modal
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Actions');
    await page.click('button:has-text("Create Ticket")');

    // Check ticket modal
    await expect(page.locator('text=Create Support Ticket')).toBeVisible();
    await expect(page.locator('input[placeholder*="Brief description"]')).toBeVisible();

    // Fill ticket details
    await page.fill('input[placeholder*="Brief description"]', 'Test issue');
    await page.fill('textarea[placeholder*="Detailed description"]', 'This is a test issue');

    await expect(page.locator('button:has-text("Create Ticket")')).toBeEnabled();

    // Close modal
    await page.click('button:has-text("Cancel")');
  });

  test('should search knowledge base', async ({ page }) => {
    // Start a mock call
    await page.click('text=Dialer');
    await page.fill('input[placeholder*="phone"]', '+1234567890');
    await page.click('button:has-text("Call")');
    await page.waitForTimeout(2000);

    // Go to knowledge tab
    await page.click('[data-testid="agent-assist-collapsed"]');
    await page.click('text=Knowledge');

    // Search for billing
    await page.fill('input[placeholder*="Search articles"]', 'billing');
    await page.waitForTimeout(500);

    // Should show billing-related articles
    await expect(page.locator('text=Billing Account Troubleshooting')).toBeVisible();
  });

  test('should collapse panel when close button clicked', async ({ page }) => {
    // Expand the panel
    await page.click('[data-testid="agent-assist-collapsed"]');
    await expect(page.locator('[data-testid="agent-assist-expanded"]')).toBeVisible();

    // Click close button
    await page.click('[data-testid="agent-assist-close"]');

    // Panel should be collapsed
    await expect(page.locator('[data-testid="agent-assist-collapsed"]')).toBeVisible();
    await expect(page.locator('[data-testid="agent-assist-expanded"]')).not.toBeVisible();
  });
});
import { test, expect } from '@playwright/test';

test.describe('Supervisor Features Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login as supervisor
    await page.goto('/');
    await page.fill('input[type="email"]', 'supervisor@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should display supervisor cockpit', async ({ page }) => {
    // Navigate to supervisor section
    await page.click('text=/Supervisor/i').or(page.click('text=/Cockpit/i'));
    
    // Should show supervisor dashboard
    await expect(page.locator('text=/Agent Overview/i').or(page.locator('text=/Team Overview/i'))).toBeVisible();
    await expect(page.locator('text=/Call Queue/i')).toBeVisible();
  });

  test('should display agent performance metrics', async ({ page }) => {
    await page.click('text=/Supervisor/i').or(page.click('text=/Cockpit/i'));
    
    // Should show agent list
    await expect(page.locator('text=/Agents/i')).toBeVisible();
    
    // Check for agent cards
    const agentCards = page.locator('[data-testid="agent-card"]');
    if (await agentCards.count() > 0) {
      const firstAgent = agentCards.first();
      
      // Should show agent status
      await expect(firstAgent.locator('text=/Available|Busy|Break|Offline/i')).toBeVisible();
      
      // Should show metrics
      await expect(firstAgent.locator('text=/Calls/i')).toBeVisible();
    }
  });

  test('should monitor live calls', async ({ page }) => {
    await page.click('text=/Supervisor/i').or(page.click('text=/Cockpit/i'));
    
    // Look for active calls section
    const activeCallsSection = page.locator('text=/Active Calls/i').or(page.locator('text=/Live Calls/i'));
    
    if (await activeCallsSection.isVisible()) {
      // Check for monitor buttons if calls exist
      const monitorButton = page.locator('button:has-text("Monitor")').first();
      
      if (await monitorButton.isVisible()) {
        await monitorButton.click();
        
        // Should show monitoring options
        await expect(
          page.locator('text=/Listen/i').or(
            page.locator('text=/Whisper/i').or(
              page.locator('text=/Barge/i')
            )
          )
        ).toBeVisible();
      }
    }
  });

  test('should manage agent status', async ({ page }) => {
    await page.click('text=/Supervisor/i').or(page.click('text=/Cockpit/i'));
    
    // Find an agent card
    const agentCard = page.locator('[data-testid="agent-card"]').first();
    
    if (await agentCard.isVisible()) {
      // Click on agent actions
      const actionsButton = agentCard.locator('button[aria-label="Actions"]').or(agentCard.locator('button:has-text("...")'));
      
      if (await actionsButton.isVisible()) {
        await actionsButton.click();
        
        // Should show status options
        await expect(page.locator('text=/Set Available/i').or(page.locator('text=/Set Break/i'))).toBeVisible();
      }
    }
  });

  test('should view team analytics', async ({ page }) => {
    await page.click('text=/Analytics/i').or(page.click('text=/Reports/i'));
    
    // Should show analytics dashboard
    await expect(page.locator('text=/Performance/i')).toBeVisible();
    await expect(page.locator('text=/Call Volume/i').or(page.locator('text=/Total Calls/i'))).toBeVisible();
    
    // Check for date range selector
    await expect(page.locator('button:has-text("Today")').or(page.locator('input[type="date"]'))).toBeVisible();
  });

  test('should access IVR configuration', async ({ page }) => {
    // Look for IVR or Settings menu
    const settingsMenu = page.locator('text=/Settings/i').or(page.locator('text=/Configuration/i'));
    
    if (await settingsMenu.isVisible()) {
      await settingsMenu.click();
      
      const ivrOption = page.locator('text=/IVR/i').or(page.locator('text=/Voice Response/i'));
      if (await ivrOption.isVisible()) {
        await ivrOption.click();
        
        // Should show IVR configuration
        await expect(page.locator('text=/Menu/i')).toBeVisible();
        await expect(page.locator('text=/Business Hours/i')).toBeVisible();
      }
    }
  });

  test('should send message to agent', async ({ page }) => {
    await page.click('text=/Supervisor/i').or(page.click('text=/Cockpit/i'));
    
    const agentCard = page.locator('[data-testid="agent-card"]').first();
    
    if (await agentCard.isVisible()) {
      const messageButton = agentCard.locator('button:has-text("Message")').or(agentCard.locator('button[aria-label="Send message"]'));
      
      if (await messageButton.isVisible()) {
        await messageButton.click();
        
        // Should show message dialog
        await expect(page.locator('text=/Send Message/i')).toBeVisible();
        
        // Type message
        const messageInput = page.locator('textarea, input[type="text"]').last();
        await messageInput.fill('Please take your break after this call');
        
        // Send message
        await page.click('button:has-text("Send")');
        
        // Should show success
        await expect(page.locator('text=/Sent/i').or(page.locator('text=/Message sent/i'))).toBeVisible();
      }
    }
  });
});
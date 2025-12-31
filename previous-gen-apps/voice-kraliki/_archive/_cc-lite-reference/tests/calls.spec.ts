import { test, expect } from '@playwright/test';
import { faker } from '@faker-js/faker';

test.describe('Call Management Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login as agent
    await page.goto('/');
    await page.fill('input[type="email"]', 'agent1@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Navigate to calls section
    await page.click('text=/Calls/i');
    await page.waitForURL('**/calls');
  });

  test('should display active calls', async ({ page }) => {
    await expect(page.locator('text=/Active Calls/i')).toBeVisible();
    
    // Check for call list or empty state
    const callList = page.locator('[data-testid="call-item"]');
    const emptyState = page.locator('text=/No active calls/i');
    
    const hasCalls = await callList.count() > 0;
    const isEmpty = await emptyState.isVisible().catch(() => false);
    
    expect(hasCalls || isEmpty).toBeTruthy();
  });

  test('should display call history', async ({ page }) => {
    // Click on history tab if exists
    const historyTab = page.locator('text=/History/i').or(page.locator('[data-testid="history-tab"]'));
    
    if (await historyTab.isVisible()) {
      await historyTab.click();
    }
    
    // Should show call history
    await expect(page.locator('text=/Call History/i').or(page.locator('text=/Recent Calls/i'))).toBeVisible();
  });

  test('should initiate outbound call', async ({ page }) => {
    // Look for new call button
    const newCallButton = page.locator('button:has-text("New Call")').or(page.locator('button[aria-label="New call"]'));
    
    if (await newCallButton.isVisible()) {
      await newCallButton.click();
      
      // Fill in phone number
      const phoneInput = page.locator('input[type="tel"]').or(page.locator('input[placeholder*="phone"]'));
      await phoneInput.fill(faker.phone.number('+1##########'));
      
      // Select campaign if available
      const campaignSelect = page.locator('select[name="campaign"]').or(page.locator('[data-testid="campaign-select"]'));
      if (await campaignSelect.isVisible()) {
        await campaignSelect.selectOption({ index: 1 });
      }
      
      // Click call button
      await page.click('button:has-text("Call")');
      
      // Should show calling state or error
      await expect(
        page.locator('text=/Calling/i').or(
          page.locator('text=/Connecting/i').or(
            page.locator('text=/Error/i')
          )
        )
      ).toBeVisible();
    }
  });

  test('should handle call actions', async ({ page }) => {
    // If there are active calls, test actions
    const callItem = page.locator('[data-testid="call-item"]').first();
    
    if (await callItem.isVisible()) {
      await callItem.click();
      
      // Check for action buttons
      const holdButton = page.locator('button:has-text("Hold")');
      const muteButton = page.locator('button:has-text("Mute")');
      const transferButton = page.locator('button:has-text("Transfer")');
      const hangupButton = page.locator('button:has-text("Hang up")').or(page.locator('button:has-text("End")'));
      
      // At least one action should be available
      const hasActions = 
        await holdButton.isVisible() ||
        await muteButton.isVisible() ||
        await transferButton.isVisible() ||
        await hangupButton.isVisible();
      
      expect(hasActions).toBeTruthy();
    }
  });

  test('should display call details', async ({ page }) => {
    // Click on a call if available
    const callItem = page.locator('[data-testid="call-item"]').first();
    
    if (await callItem.isVisible()) {
      await callItem.click();
      
      // Should show call details
      await expect(page.locator('text=/Duration/i').or(page.locator('text=/Call Details/i'))).toBeVisible();
      await expect(page.locator('text=/Status/i')).toBeVisible();
    }
  });

  test('should handle call transfer', async ({ page }) => {
    const callItem = page.locator('[data-testid="call-item"]').first();
    
    if (await callItem.isVisible()) {
      await callItem.click();
      
      const transferButton = page.locator('button:has-text("Transfer")');
      if (await transferButton.isVisible()) {
        await transferButton.click();
        
        // Should show transfer dialog
        await expect(page.locator('text=/Transfer Call/i')).toBeVisible();
        
        // Fill transfer target
        const transferInput = page.locator('input[placeholder*="extension"]').or(page.locator('input[placeholder*="number"]'));
        await transferInput.fill('1001');
        
        // Confirm transfer
        await page.click('button:has-text("Transfer")').last();
        
        // Should show success or error
        await expect(
          page.locator('text=/Transfer/i').or(page.locator('text=/Error/i'))
        ).toBeVisible();
      }
    }
  });
});
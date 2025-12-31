import { test, expect } from '@playwright/test';

test.describe('AI Features', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@focus-kraliki.app');
    await page.fill('input[type="password"]', 'test123');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
  });

  test('should access AI Chat', async ({ page }) => {
    // Navigate to AI Chat
    await page.click('text=AI Chat');
    
    // Verify AI Chat interface
    await expect(page.locator('h2:has-text("AI Assistant")')).toBeVisible();
    await expect(page.locator('text=How can I help you today?')).toBeVisible();
    
    // Check mode buttons
    await expect(page.locator('button:has-text("Standard")')).toBeVisible();
    await expect(page.locator('button:has-text("High Reasoning")')).toBeVisible();
    await expect(page.locator('button:has-text("Collaborative")')).toBeVisible();
  });

  test('should send message to AI', async ({ page }) => {
    await page.click('text=AI Chat');
    
    // Type message
    const message = 'Help me organize my tasks';
    await page.fill('textarea[placeholder*="Ask me anything"]', message);
    
    // Send message
    await page.click('button:has-text("Send")');
    
    // Verify message appears
    await expect(page.locator(`text=${message}`)).toBeVisible({ timeout: 5000 });
    
    // Wait for AI response
    await expect(page.locator('.bg-gray-100, .dark\\:bg-gray-800').last()).toBeVisible({ timeout: 10000 });
  });

  test('should toggle AI modes', async ({ page }) => {
    await page.click('text=AI Chat');
    
    // Test High Reasoning mode
    await page.click('button:has-text("High Reasoning")');
    await expect(page.locator('textarea[placeholder*="high-reasoning"]')).toBeVisible();
    
    // Test Collaborative mode
    await page.click('button:has-text("Collaborative")');
    await expect(page.locator('textarea[placeholder*="collaborative"]')).toBeVisible();
    
    // Test Standard mode
    await page.click('button:has-text("Standard")');
    await expect(page.locator('textarea[placeholder*="standard"]')).toBeVisible();
  });

  test('should access Shadow Work', async ({ page }) => {
    // Navigate to Shadow Work
    await page.click('text=Shadow Work');
    
    // Verify Shadow Work interface
    await expect(page.locator('h1:has-text("Shadow Work")')).toBeVisible();
    await expect(page.locator('text=Explore your unconscious patterns')).toBeVisible();
    
    // Check progress indicator
    await expect(page.locator('text=Day')).toBeVisible();
    await expect(page.locator('text=of 30')).toBeVisible();
  });

  test('should view Cognitive Status', async ({ page }) => {
    // Navigate to Cognitive Status
    await page.click('text=Cognitive');
    
    // Verify Cognitive Status interface
    await expect(page.locator('h1:has-text("Cognitive Status")')).toBeVisible();
    await expect(page.locator('text=Monitor your mental state')).toBeVisible();
    
    // Check cognitive metrics
    await expect(page.locator('text=Energy')).toBeVisible();
    await expect(page.locator('text=Focus')).toBeVisible();
    await expect(page.locator('text=Creativity')).toBeVisible();
    await expect(page.locator('text=Stress')).toBeVisible();
  });

  test('should manage Type System', async ({ page }) => {
    // Navigate to Types
    await page.click('text=Types');
    
    // Verify Type Manager interface
    await expect(page.locator('h2:has-text("Type Manager")')).toBeVisible();
    await expect(page.locator('text=Customize your mental model')).toBeVisible();
    
    // Check for type items
    await expect(page.locator('text=Task')).toBeVisible();
    await expect(page.locator('text=Event')).toBeVisible();
    await expect(page.locator('text=Note')).toBeVisible();
  });

  test('should test voice input button', async ({ page }) => {
    await page.click('text=AI Chat');
    
    // Check voice button exists
    const voiceButton = page.locator('button:has(svg[class*="Mic"])');
    await expect(voiceButton).toBeVisible();
    
    // Click voice button (won't actually record without permissions)
    await voiceButton.click();
    
    // Button should indicate recording state
    await expect(voiceButton.locator('svg')).toHaveClass(/animate-pulse|text-red/, { timeout: 2000 });
  });
});
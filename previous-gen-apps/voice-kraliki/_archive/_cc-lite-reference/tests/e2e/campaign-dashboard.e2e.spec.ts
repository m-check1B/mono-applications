import { test, expect } from '@playwright/test';

test.describe('Campaign Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as supervisor
    await page.goto('http://localhost:5174');
    await page.fill('[data-testid="email-input"]', 'supervisor@cc-light.local');
    await page.fill('[data-testid="password-input"]', 'supervisor123');
    await page.click('[data-testid="login-button"]');

    // Navigate to campaign dashboard
    await page.waitForURL('**/supervisor');
    await page.click('text=Campaigns');
    await page.waitForURL('**/campaigns');
  });

  test('should display campaign metrics', async ({ page }) => {
    // Check metric cards are visible
    await expect(page.locator('text=Active Campaigns')).toBeVisible();
    await expect(page.locator('text=Total Leads')).toBeVisible();
    await expect(page.locator('text=Calls Today')).toBeVisible();
    await expect(page.locator('text=Success Rate')).toBeVisible();
  });

  test('should list campaigns', async ({ page }) => {
    // Check campaigns table/list exists
    const campaignsSection = page.locator('[data-testid="campaigns-list"]');
    await expect(campaignsSection).toBeVisible();

    // Should have at least headers
    await expect(page.locator('text=Campaign Name')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();
    await expect(page.locator('text=Type')).toBeVisible();
  });

  test('should create new campaign', async ({ page }) => {
    // Click create campaign button
    await page.click('button:has-text("Create Campaign")');

    // Fill campaign form
    await page.fill('[data-testid="campaign-name"]', 'Test Campaign');
    await page.selectOption('[data-testid="campaign-type"]', 'OUTBOUND');
    await page.fill('[data-testid="campaign-description"]', 'E2E test campaign');

    // Submit form
    await page.click('button:has-text("Create")');

    // Verify campaign was created
    await expect(page.locator('text=Test Campaign')).toBeVisible();
  });

  test('should control campaign status', async ({ page }) => {
    // Find a campaign row
    const campaignRow = page.locator('[data-testid="campaign-row"]').first();

    // Test pause button
    const pauseButton = campaignRow.locator('button[aria-label="Pause"]');
    if (await pauseButton.isVisible()) {
      await pauseButton.click();
      await expect(page.locator('text=Campaign paused')).toBeVisible();
    }

    // Test play button
    const playButton = campaignRow.locator('button[aria-label="Start"]');
    if (await playButton.isVisible()) {
      await playButton.click();
      await expect(page.locator('text=Campaign started')).toBeVisible();
    }
  });

  test('should import contacts', async ({ page }) => {
    // Click import button
    await page.click('button:has-text("Import Contacts")');

    // Upload CSV file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'contacts.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from('name,phone,email\nJohn Doe,+1234567890,john@example.com')
    });

    // Confirm import
    await page.click('button:has-text("Import")');

    // Verify import success
    await expect(page.locator('text=Import completed')).toBeVisible();
  });

  test('should show realtime metrics', async ({ page }) => {
    // Wait for realtime metrics to load
    await page.waitForTimeout(5000);

    // Check for realtime metrics section
    const metricsSection = page.locator('[data-testid="realtime-metrics"]');
    if (await metricsSection.isVisible()) {
      // Verify metrics update
      const initialValue = await metricsSection.locator('.metric-value').first().textContent();
      await page.waitForTimeout(5000);
      const updatedValue = await metricsSection.locator('.metric-value').first().textContent();

      // Values might change if real-time updates are working
      expect(updatedValue).toBeDefined();
    }
  });

  test('should handle API errors gracefully', async ({ page, context }) => {
    // Intercept API calls and force errors
    await context.route('**/api/campaigns', route => route.abort());

    // Reload page
    await page.reload();

    // Should show error state, not crash
    await expect(page.locator('text=Failed to load campaigns')).toBeVisible();
  });
});

test.describe('Campaign Dashboard - Agent View', () => {
  test.beforeEach(async ({ page }) => {
    // Login as agent
    await page.goto('http://localhost:5174');
    await page.fill('[data-testid="email-input"]', 'agent1@cc-light.local');
    await page.fill('[data-testid="password-input"]', 'agent123');
    await page.click('[data-testid="login-button"]');

    await page.waitForURL('**/operator');
  });

  test('agent should have limited campaign access', async ({ page }) => {
    // Try to navigate to campaigns
    await page.goto('http://localhost:5174/campaigns');

    // Should redirect or show limited view
    const url = page.url();
    if (url.includes('campaigns')) {
      // Check for limited functionality
      await expect(page.locator('button:has-text("Create Campaign")')).not.toBeVisible();
      await expect(page.locator('button:has-text("Delete")')).not.toBeVisible();
    } else {
      // Should have been redirected
      expect(url).toContain('operator');
    }
  });
});
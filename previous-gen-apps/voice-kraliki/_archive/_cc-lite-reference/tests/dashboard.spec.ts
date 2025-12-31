import { test, expect } from '@playwright/test';

test.describe('Dashboard Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should display dashboard metrics', async ({ page }) => {
    // Check for metric cards
    await expect(page.locator('text=/Total Calls/i')).toBeVisible();
    await expect(page.locator('text=/Active Calls/i')).toBeVisible();
    await expect(page.locator('text=/Completed Calls/i')).toBeVisible();
    await expect(page.locator('text=/Completion Rate/i')).toBeVisible();
    
    // Check for performance metrics
    await expect(page.locator('text=/Avg Handle Time/i')).toBeVisible();
    await expect(page.locator('text=/First Call Resolution/i')).toBeVisible();
    await expect(page.locator('text=/Customer Satisfaction/i')).toBeVisible();
  });

  test('should display team status', async ({ page }) => {
    // Check for team section
    await expect(page.locator('text=/Team Status/i')).toBeVisible();
    await expect(page.locator('text=/Available/i')).toBeVisible();
    await expect(page.locator('text=/Busy/i')).toBeVisible();
    await expect(page.locator('text=/On Break/i')).toBeVisible();
    await expect(page.locator('text=/Offline/i')).toBeVisible();
  });

  test('should display recent activity', async ({ page }) => {
    // Check for activity feed
    await expect(page.locator('text=/Recent Activity/i')).toBeVisible();
    
    // Should have activity items or empty state
    const activityItems = page.locator('[data-testid="activity-item"]');
    const emptyState = page.locator('text=/No recent activity/i');
    
    const hasActivity = await activityItems.count() > 0;
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    
    expect(hasActivity || hasEmptyState).toBeTruthy();
  });

  test('should display performance trends chart', async ({ page }) => {
    // Check for trends section
    await expect(page.locator('text=/Performance Trends/i')).toBeVisible();
    
    // Check for period selector
    await expect(page.locator('button:has-text("Day")').or(page.locator('button:has-text("Week")')).or(page.locator('button:has-text("Month")'))).toBeVisible();
    
    // Check for chart or empty state
    const chart = page.locator('canvas, svg').first();
    const noData = page.locator('text=/No data available/i');
    
    const hasChart = await chart.isVisible().catch(() => false);
    const hasNoData = await noData.isVisible().catch(() => false);
    
    expect(hasChart || hasNoData).toBeTruthy();
  });

  test('should refresh metrics', async ({ page }) => {
    // Look for refresh button
    const refreshButton = page.locator('button[aria-label="Refresh"]').or(page.locator('button:has-text("Refresh")'));
    
    if (await refreshButton.isVisible()) {
      // Get initial metric value
      const initialCallCount = await page.locator('text=/Total Calls/i').locator('..').locator('text=/\\d+/').textContent();
      
      // Click refresh
      await refreshButton.click();
      
      // Wait for potential update
      await page.waitForTimeout(1000);
      
      // Metric should still be visible (may or may not change)
      await expect(page.locator('text=/Total Calls/i')).toBeVisible();
    }
  });

  test('should navigate to different sections', async ({ page }) => {
    // Check navigation menu
    const nav = page.locator('nav, [role="navigation"]');
    
    // Should have main navigation items
    await expect(nav.locator('text=/Dashboard/i')).toBeVisible();
    await expect(nav.locator('text=/Calls/i')).toBeVisible();
    await expect(nav.locator('text=/Team/i')).toBeVisible();
    
    // Click on Calls
    await nav.locator('text=/Calls/i').click();
    await page.waitForURL('**/calls');
    
    // Navigate back to dashboard
    await nav.locator('text=/Dashboard/i').click();
    await page.waitForURL('**/dashboard');
  });

  test('should display alerts if any', async ({ page }) => {
    // Check for alerts section
    const alertsSection = page.locator('text=/System Alerts/i').or(page.locator('text=/Alerts/i'));
    
    if (await alertsSection.isVisible()) {
      // Should show alerts or no alerts message
      const alerts = page.locator('[data-testid="alert-item"]');
      const noAlerts = page.locator('text=/No active alerts/i');
      
      const hasAlerts = await alerts.count() > 0;
      const hasNoAlerts = await noAlerts.isVisible().catch(() => false);
      
      expect(hasAlerts || hasNoAlerts).toBeTruthy();
    }
  });

  test('should handle responsive layout', async ({ page, viewport }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Mobile menu should be visible
    const mobileMenuButton = page.locator('button[aria-label="Menu"]').or(page.locator('[data-testid="mobile-menu"]'));
    
    if (await mobileMenuButton.isVisible()) {
      await mobileMenuButton.click();
      // Navigation should be visible in mobile menu
      await expect(page.locator('text=/Dashboard/i')).toBeVisible();
    }
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Desktop navigation should be visible
    await expect(page.locator('nav, [role="navigation"]')).toBeVisible();
  });
});
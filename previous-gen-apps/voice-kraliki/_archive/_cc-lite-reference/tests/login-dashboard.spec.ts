import { test, expect } from '@playwright/test';
import { getAdminCredentials, getAgentCredentials } from './utils/test-credentials';

const adminCredentials = getAdminCredentials();
const agentCredentials = getAgentCredentials();

test.describe('Login and Dashboard Tests', () => {
  test('login as admin and verify supervisor dashboard', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill in admin credentials
    await page.fill('input[type="email"]', adminCredentials.email);
    await page.fill('input[type="password"]', adminCredentials.password);
    
    // Click sign in
    await page.click('button[type="submit"]');
    
    // Wait for navigation
    await page.waitForURL('**/supervisor', { timeout: 10000 });
    
    // Verify we're on supervisor page
    expect(page.url()).toContain('/supervisor');
    
    // Check for dashboard elements
    await expect(page.locator('text=CC-LIGHT SUPERVISOR')).toBeVisible({ timeout: 10000 });
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/admin-dashboard.png' });
  });
  
  test('login as agent and verify operator dashboard', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill in agent credentials
    await page.fill('input[type="email"]', agentCredentials.email);
    await page.fill('input[type="password"]', agentCredentials.password);
    
    // Click sign in
    await page.click('button[type="submit"]');
    
    // Wait for navigation
    await page.waitForURL('**/operator', { timeout: 10000 });
    
    // Verify we're on operator page
    expect(page.url()).toContain('/operator');
    
    // Check for dashboard elements
    await expect(page.locator('text=CC-Light Operator')).toBeVisible({ timeout: 10000 });
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/operator-dashboard.png' });
  });
  
  test('demo login buttons work', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Click the admin demo login button
    const adminCard = page.locator('text=admin@cc-light.local').locator('..');
    await adminCard.locator('button:text("Login")').click();
    
    // Wait for navigation
    await page.waitForURL('**/supervisor', { timeout: 10000 });
    
    // Verify we're on supervisor page
    expect(page.url()).toContain('/supervisor');
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/demo-login-dashboard.png' });
  });
});

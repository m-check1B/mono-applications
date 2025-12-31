import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should show login page', async ({ page }) => {
    await expect(page).toHaveTitle(/Focus by Kraliki/);
    await expect(page.locator('h1')).toContainText('Focus by Kraliki');
    await expect(page.locator('text=AI-First Productivity System')).toBeVisible();
  });

  test('should display login form', async ({ page }) => {
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button:has-text("Sign In")')).toBeVisible();
  });

  test('should toggle between login and register', async ({ page }) => {
    // Click Sign Up
    await page.click('button:has-text("Sign Up")');
    await expect(page.locator('input[placeholder="Your name"]')).toBeVisible();
    
    // Click Sign In
    await page.click('button:has-text("Sign In")');
    await expect(page.locator('input[placeholder="Your name"]')).not.toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.bg-red-50, .bg-red-900\\/20')).toBeVisible();
  });

  test('should login with demo credentials', async ({ page }) => {
    // Fill demo credentials
    await page.fill('input[type="email"]', 'test@focus-kraliki.app');
    await page.fill('input[type="password"]', 'test123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/', { timeout: 10000 });
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
  });

  test('should register new user', async ({ page }) => {
    await page.click('button:has-text("Sign Up")');
    
    const randomEmail = `test${Date.now()}@example.com`;
    await page.fill('input[placeholder="Your name"]', 'Test User');
    await page.fill('input[type="email"]', randomEmail);
    await page.fill('input[type="password"]', 'password123');
    
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard after registration
    await expect(page).toHaveURL('/', { timeout: 10000 });
  });
});
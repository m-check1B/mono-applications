import { test, expect } from '@playwright/test';

test.describe('Performance and Load Tests', () => {
  test('should load dashboard within acceptable time', async ({ page }) => {
    // Login
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    
    // Measure dashboard load time
    const startTime = Date.now();
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Dashboard should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // All critical elements should be visible
    await expect(page.locator('text=/Dashboard/i')).toBeVisible();
    await expect(page.locator('text=/Total Calls/i')).toBeVisible();
  });

  test('should handle rapid navigation', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Rapidly navigate between sections
    const sections = ['Calls', 'Team', 'Dashboard'];
    
    for (let i = 0; i < 10; i++) {
      const section = sections[i % sections.length];
      await page.click(`text=/${section}/i`);
      await page.waitForTimeout(100);
    }
    
    // Should still be responsive
    await expect(page.locator('text=/Dashboard/i')).toBeVisible();
  });

  test('should handle multiple concurrent API calls', async ({ page, request }) => {
    // Get auth token
    const loginResponse = await request.post('http://localhost:3010/trpc/auth.login', {
      data: {
        json: {
          email: 'admin@demo.com',
          password: 'demo123!'
        }
      }
    });
    
    const cookies = await loginResponse.headers();
    const authToken = cookies['set-cookie']?.match(/vd_session=([^;]+)/)?.[1] || '';
    
    // Make multiple concurrent requests
    const requests = [];
    for (let i = 0; i < 20; i++) {
      requests.push(
        request.get('http://localhost:3010/trpc/dashboard.getMetrics', {
          headers: { 'Cookie': `vd_session=${authToken}` }
        })
      );
    }
    
    const startTime = Date.now();
    const responses = await Promise.all(requests);
    const totalTime = Date.now() - startTime;
    
    // All requests should succeed
    responses.forEach(response => {
      expect(response.ok()).toBeTruthy();
    });
    
    // Should handle 20 concurrent requests within 5 seconds
    expect(totalTime).toBeLessThan(5000);
  });

  test('should handle large data sets', async ({ page, request }) => {
    // Get auth token
    const loginResponse = await request.post('http://localhost:3010/trpc/auth.login', {
      data: {
        json: {
          email: 'admin@demo.com',
          password: 'demo123!'
        }
      }
    });
    
    const cookies = await loginResponse.headers();
    const authToken = cookies['set-cookie']?.match(/vd_session=([^;]+)/)?.[1] || '';
    
    // Request large dataset
    const response = await request.get('http://localhost:3010/trpc/telephony.getCallHistory?input=' + encodeURIComponent(JSON.stringify({
      limit: 100,
      offset: 0
    })), {
      headers: { 'Cookie': `vd_session=${authToken}` }
    });
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.result?.data).toHaveProperty('calls');
    expect(data.result?.data).toHaveProperty('total');
  });

  test('should maintain performance with multiple tabs', async ({ browser }) => {
    // Create multiple contexts (tabs)
    const contexts = [];
    const pages = [];
    
    for (let i = 0; i < 3; i++) {
      const context = await browser.newContext();
      const page = await context.newPage();
      contexts.push(context);
      pages.push(page);
      
      // Login in each tab
      await page.goto('/');
      await page.fill('input[type="email"]', 'admin@demo.com');
      await page.fill('input[type="password"]', 'demo123!');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');
    }
    
    // All tabs should remain responsive
    for (const page of pages) {
      await expect(page.locator('text=/Dashboard/i')).toBeVisible();
    }
    
    // Clean up
    for (const context of contexts) {
      await context.close();
    }
  });

  test('should handle session timeout gracefully', async ({ page, context }) => {
    // Login
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@demo.com');
    await page.fill('input[type="password"]', 'demo123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    
    // Simulate session timeout by clearing cookies
    await context.clearCookies();
    
    // Try to perform an action
    await page.reload();
    
    // Should redirect to login
    await page.waitForURL('/');
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('should measure API response times', async ({ request }) => {
    // Get auth token
    const loginResponse = await request.post('http://localhost:3010/trpc/auth.login', {
      data: {
        json: {
          email: 'admin@demo.com',
          password: 'demo123!'
        }
      }
    });
    
    const cookies = await loginResponse.headers();
    const authToken = cookies['set-cookie']?.match(/vd_session=([^;]+)/)?.[1] || '';
    
    // Test various endpoints
    const endpoints = [
      'dashboard.getMetrics',
      'team.getAvailability',
      'analytics.getRealtimeMetrics',
      'telephony.getActiveCalls'
    ];
    
    for (const endpoint of endpoints) {
      const startTime = Date.now();
      const response = await request.get(`http://localhost:3010/trpc/${endpoint}`, {
        headers: { 'Cookie': `vd_session=${authToken}` }
      });
      const responseTime = Date.now() - startTime;
      
      expect(response.ok()).toBeTruthy();
      // Each API call should respond within 1 second
      expect(responseTime).toBeLessThan(1000);
    }
  });
});
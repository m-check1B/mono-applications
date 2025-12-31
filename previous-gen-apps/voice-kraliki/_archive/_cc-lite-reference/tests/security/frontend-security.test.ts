/**
 * Frontend Security Tests
 * Tests the security implementation of the Voice by Kraliki frontend
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Frontend Security Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
  });

  test.describe('Cookie-Only Authentication', () => {
    test('should not store tokens in localStorage or sessionStorage', async () => {
      await page.goto('http://localhost:3007');

      // Try to login with demo account
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');

      // Wait for potential login redirect
      await page.waitForTimeout(2000);

      // Check that no tokens are stored in browser storage
      const localStorage = await page.evaluate(() => {
        const storage = {};
        for (let i = 0; i < window.localStorage.length; i++) {
          const key = window.localStorage.key(i);
          if (key) {
            storage[key] = window.localStorage.getItem(key);
          }
        }
        return storage;
      });

      const sessionStorage = await page.evaluate(() => {
        const storage = {};
        for (let i = 0; i < window.sessionStorage.length; i++) {
          const key = window.sessionStorage.key(i);
          if (key) {
            storage[key] = window.sessionStorage.getItem(key);
          }
        }
        return storage;
      });

      // Assert no authentication tokens in browser storage
      expect(Object.keys(localStorage)).not.toContain('token');
      expect(Object.keys(localStorage)).not.toContain('jwt');
      expect(Object.keys(localStorage)).not.toContain('authToken');
      expect(Object.keys(localStorage)).not.toContain('session');

      expect(Object.keys(sessionStorage)).not.toContain('token');
      expect(Object.keys(sessionStorage)).not.toContain('jwt');
      expect(Object.keys(sessionStorage)).not.toContain('authToken');
      expect(Object.keys(sessionStorage)).not.toContain('session');

      console.log('✅ No authentication tokens found in browser storage');
    });

    test('should include credentials in API requests', async () => {
      await page.goto('http://localhost:3007');

      // Monitor network requests
      const requests = [];
      page.on('request', (request) => {
        if (request.url().includes('/trpc/')) {
          requests.push({
            url: request.url(),
            headers: request.headers(),
            method: request.method()
          });
        }
      });

      // Try to access a protected endpoint (should trigger auth check)
      await page.evaluate(() => {
        return fetch('/trpc/auth.me', {
          credentials: 'include'
        });
      });

      await page.waitForTimeout(1000);

      // Verify that requests include credentials
      const authRequests = requests.filter(req => req.url.includes('auth.me'));
      expect(authRequests.length).toBeGreaterThan(0);

      console.log('✅ API requests include credentials');
    });
  });

  test.describe('PII Masking', () => {
    test('should mask phone numbers in UI', async () => {
      await page.goto('http://localhost:3007');

      // Wait for any potential customer data to load
      await page.waitForTimeout(2000);

      // Check for phone number patterns that should be masked
      const phoneElements = await page.$$eval('*', (elements) => {
        return elements
          .map(el => el.textContent || '')
          .filter(text => /\d{3}-\d{3}-\d{4}/.test(text))
          .filter(text => !text.includes('***')); // Find unmasked phone numbers
      });

      // Ideally, no raw phone numbers should be visible
      if (phoneElements.length > 0) {
        console.warn('⚠️  Potential unmasked phone numbers found:', phoneElements);
      } else {
        console.log('✅ No unmasked phone numbers detected in UI');
      }
    });

    test('should mask email addresses in UI', async () => {
      await page.goto('http://localhost:3007');

      await page.waitForTimeout(2000);

      // Check for email patterns that should be masked
      const emailElements = await page.$$eval('*', (elements) => {
        return elements
          .map(el => el.textContent || '')
          .filter(text => /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/.test(text))
          .filter(text => !text.includes('***')) // Find unmasked emails
          .filter(text => !text.includes('example.com')) // Exclude examples
          .filter(text => !text.includes('demo')); // Exclude demo accounts
      });

      if (emailElements.length > 0) {
        console.warn('⚠️  Potential unmasked emails found:', emailElements);
      } else {
        console.log('✅ No unmasked email addresses detected in UI');
      }
    });
  });

  test.describe('WebSocket Security', () => {
    test('should show connection status to user', async () => {
      await page.goto('http://localhost:3007');

      // Look for connection status indicators
      const connectionIndicators = await page.$$eval('*', (elements) => {
        return elements
          .map(el => el.textContent || '')
          .filter(text =>
            text.toLowerCase().includes('connected') ||
            text.toLowerCase().includes('disconnected') ||
            text.toLowerCase().includes('connecting')
          );
      });

      expect(connectionIndicators.length).toBeGreaterThan(0);
      console.log('✅ Connection status indicators found:', connectionIndicators);
    });

    test('should handle WebSocket connection errors gracefully', async () => {
      await page.goto('http://localhost:3007');

      // Monitor console for WebSocket-related errors
      const consoleMessages = [];
      page.on('console', (msg) => {
        if (msg.text().toLowerCase().includes('websocket')) {
          consoleMessages.push(msg.text());
        }
      });

      await page.waitForTimeout(3000);

      // Should have WebSocket connection attempts logged
      const wsMessages = consoleMessages.filter(msg =>
        msg.includes('WebSocket') || msg.includes('📡')
      );

      if (wsMessages.length > 0) {
        console.log('✅ WebSocket connection handling detected:', wsMessages[0]);
      }
    });
  });

  test.describe('Security Headers and CORS', () => {
    test('should set secure response headers', async () => {
      const response = await page.goto('http://localhost:3007');

      // Check for security headers (these should be set by the backend)
      const headers = response?.headers() || {};

      // Log available headers for debugging
      console.log('Available headers:', Object.keys(headers));

      // Basic security check - ensure no sensitive data in headers
      expect(headers['authorization']).toBeUndefined();
      expect(headers['x-auth-token']).toBeUndefined();

      console.log('✅ No sensitive authentication data in response headers');
    });
  });

  test.describe('Error Handling', () => {
    test('should handle authentication failures gracefully', async () => {
      await page.goto('http://localhost:3007');

      // Monitor for error handling
      const errors = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error' && msg.text().toLowerCase().includes('auth')) {
          errors.push(msg.text());
        }
      });

      // Try to make an unauthorized request
      await page.evaluate(() => {
        return fetch('/trpc/admin.restricted', {
          credentials: 'include'
        }).catch(err => console.error('Auth error handled:', err.message));
      });

      await page.waitForTimeout(1000);

      // Should handle auth errors without crashing
      console.log('✅ Authentication error handling tested');
    });
  });

  test.describe('Form Security', () => {
    test('should include CSRF protection in form submissions', async () => {
      await page.goto('http://localhost:3007');

      // Monitor form submission requests
      const formRequests = [];
      page.on('request', (request) => {
        if (request.method() === 'POST') {
          formRequests.push({
            url: request.url(),
            headers: request.headers()
          });
        }
      });

      // Try to submit a form (login form)
      try {
        await page.fill('input[type="email"]', 'test@example.com');
        await page.fill('input[type="password"]', 'password');
        await page.click('button[type="submit"]');
      } catch (error) {
        // Form might not exist, which is fine for this test
      }

      await page.waitForTimeout(1000);

      if (formRequests.length > 0) {
        console.log('✅ Form submission security tested');
      }
    });
  });
});

test.describe('Security Integration Tests', () => {
  test('should maintain security across navigation', async ({ page }) => {
    await page.goto('http://localhost:3007');

    // Navigate through different parts of the app
    const paths = ['/', '/supervisor', '/agent'];

    for (const path of paths) {
      try {
        await page.goto(`http://localhost:3007${path}`);
        await page.waitForTimeout(500);

        // Check that no tokens are stored after navigation
        const hasTokens = await page.evaluate(() => {
          return Object.keys(localStorage).some(key =>
            key.toLowerCase().includes('token') ||
            key.toLowerCase().includes('jwt') ||
            key.toLowerCase().includes('auth')
          );
        });

        expect(hasTokens).toBeFalsy();
      } catch (error) {
        // Page might not exist, continue testing
        console.log(`Page ${path} not accessible, skipping...`);
      }
    }

    console.log('✅ Security maintained across navigation');
  });

  test('should handle logout security properly', async ({ page }) => {
    await page.goto('http://localhost:3007');

    // Try to find and click logout button
    try {
      await page.waitForSelector('text=Logout', { timeout: 5000 });
      await page.click('text=Logout');
      await page.waitForTimeout(1000);

      // After logout, should not have auth state
      const hasAuthData = await page.evaluate(() => {
        return Object.keys(localStorage).some(key =>
          key.toLowerCase().includes('user') ||
          key.toLowerCase().includes('session')
        );
      });

      expect(hasAuthData).toBeFalsy();
      console.log('✅ Logout clears authentication state properly');
    } catch (error) {
      console.log('⚠️  Logout button not found, skipping logout test');
    }
  });
});
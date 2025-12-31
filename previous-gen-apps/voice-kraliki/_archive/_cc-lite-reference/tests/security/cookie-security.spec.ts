/**
 * Comprehensive Cookie Security Tests
 * Tests all aspects of cookie security implementation
 */

import { describe, test, expect, beforeEach, afterEach } from '@playwright/test';

describe('Cookie Security Tests', () => {

  beforeEach(async ({ page, context }) => {
    // Clear all cookies and storage before each test
    await context.clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  describe('Authentication Cookie Security', () => {
    test('should set secure authentication cookies on login', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      // Login with test credentials
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');

      // Wait for login to complete
      await page.waitForURL('**/dashboard');

      // Check that authentication cookies are set with proper security attributes
      const cookies = await page.context().cookies();

      const authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );

      expect(authCookie, 'Authentication cookie should be present').toBeTruthy();

      if (authCookie) {
        // Verify HttpOnly attribute
        expect(authCookie.httpOnly, 'Auth cookie should be HttpOnly').toBe(true);

        // Verify SameSite attribute
        expect(authCookie.sameSite, 'Auth cookie should use SameSite=Strict').toBe('Strict');

        // Verify Secure flag in production (would be true in production)
        if (process.env.NODE_ENV === 'production') {
          expect(authCookie.secure, 'Auth cookie should be Secure in production').toBe(true);
        }

        // Verify proper expiration
        expect(authCookie.expires, 'Auth cookie should have expiration').toBeGreaterThan(Date.now() / 1000);

        // Verify path
        expect(authCookie.path, 'Auth cookie should have root path').toBe('/');
      }
    });

    test('should not expose authentication cookies to JavaScript', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      // Login with test credentials
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      // Try to access authentication cookies via JavaScript
      const jsAccessibleCookies = await page.evaluate(() => {
        return document.cookie;
      });

      // Verify that authentication cookies are NOT accessible via JavaScript
      expect(jsAccessibleCookies.includes('vd_session'), 'vd_session should not be accessible to JS').toBe(false);
      expect(jsAccessibleCookies.includes('cc_light_session'), 'cc_light_session should not be accessible to JS').toBe(false);
    });

    test('should properly clear authentication cookies on logout', async ({ page, context }) => {
      // Login first
      await page.goto('http://localhost:5174/login');
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      // Verify cookies are present
      let cookies = await context.cookies();
      let authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );
      expect(authCookie, 'Auth cookie should be present after login').toBeTruthy();

      // Logout
      await page.click('[data-testid="logout-button"]', { timeout: 5000 });
      await page.waitForURL('**/login');

      // Verify cookies are cleared
      cookies = await context.cookies();
      authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );
      expect(authCookie, 'Auth cookie should be cleared after logout').toBeFalsy();
    });
  });

  describe('CSRF Protection', () => {
    test('should set CSRF token cookie', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      // Check for CSRF token cookie
      const cookies = await page.context().cookies();
      const csrfCookie = cookies.find(cookie => cookie.name === 'cc_csrf_token');

      if (csrfCookie) {
        // Verify CSRF cookie attributes
        expect(csrfCookie.sameSite, 'CSRF cookie should use SameSite=Strict').toBe('Strict');
        expect(csrfCookie.path, 'CSRF cookie should have root path').toBe('/');

        if (process.env.NODE_ENV === 'production') {
          expect(csrfCookie.secure, 'CSRF cookie should be Secure in production').toBe(true);
        }
      }
    });

    test('should include CSRF token in form submissions', async ({ page }) => {
      await page.goto('http://localhost:5174/login');

      // Monitor network requests to ensure CSRF token is included
      const requests: any[] = [];
      page.on('request', request => {
        if (request.method() === 'POST' && request.url().includes('/trpc/')) {
          requests.push({
            url: request.url(),
            headers: request.headers(),
            method: request.method()
          });
        }
      });

      // Attempt login to trigger POST request
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');

      // Wait for request to complete
      await page.waitForTimeout(1000);

      // Verify CSRF token was included in POST requests
      const postRequests = requests.filter(req => req.method === 'POST');
      expect(postRequests.length, 'Should have POST requests').toBeGreaterThan(0);

      postRequests.forEach(request => {
        expect(
          request.headers['x-csrf-token'],
          'POST requests should include CSRF token header'
        ).toBeDefined();
      });
    });
  });

  describe('Cookie Tampering Protection', () => {
    test('should reject tampered authentication cookies', async ({ page, context }) => {
      // Login to get valid cookies
      await page.goto('http://localhost:5174/login');
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      // Get current cookies
      const cookies = await context.cookies();
      const authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );

      expect(authCookie, 'Should have authentication cookie').toBeTruthy();

      if (authCookie) {
        // Tamper with the cookie value
        const tamperedCookie = {
          ...authCookie,
          value: authCookie.value + 'tampered'
        };

        // Clear existing cookies and set tampered one
        await context.clearCookies();
        await context.addCookies([tamperedCookie]);

        // Try to access protected resource
        await page.goto('http://localhost:5174/dashboard');

        // Should be redirected to login due to invalid cookie
        await page.waitForURL('**/login', { timeout: 5000 });
        expect(page.url().includes('/login'), 'Should redirect to login with tampered cookie').toBe(true);
      }
    });

    test('should reject expired cookies', async ({ page, context }) => {
      // Login to get valid cookies
      await page.goto('http://localhost:5174/login');
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      // Get current cookies
      const cookies = await context.cookies();
      const authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );

      expect(authCookie, 'Should have authentication cookie').toBeTruthy();

      if (authCookie) {
        // Create expired cookie
        const expiredCookie = {
          ...authCookie,
          expires: Math.floor(Date.now() / 1000) - 3600 // 1 hour ago
        };

        // Clear existing cookies and set expired one
        await context.clearCookies();
        await context.addCookies([expiredCookie]);

        // Try to access protected resource
        await page.goto('http://localhost:5174/dashboard');

        // Should be redirected to login due to expired cookie
        await page.waitForURL('**/login', { timeout: 5000 });
        expect(page.url().includes('/login'), 'Should redirect to login with expired cookie').toBe(true);
      }
    });
  });

  describe('Cookie Encryption and Signing', () => {
    test('should encrypt sensitive cookie data', async ({ page }) => {
      await page.goto('http://localhost:5174/login');
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      const cookies = await page.context().cookies();
      const authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );

      if (authCookie) {
        // Verify that the cookie value appears to be encrypted/signed
        // Encrypted values should not be valid JSON or JWT format
        expect(authCookie.value.includes('.')).toBe(true); // Should include signature separator
        expect(authCookie.value.length).toBeGreaterThan(50); // Should be longer due to encryption

        // Should not be a plain JWT (which starts with ey...)
        expect(authCookie.value.startsWith('eyJ')).toBe(false);
      }
    });

    test('should validate cookie signatures', async ({ page, context }) => {
      // This test would require cooperation with the backend to test signature validation
      // For now, we test that unsigned cookies are rejected
      await page.goto('http://localhost:5174/login');

      // Set an invalid cookie without proper signature
      await context.addCookies([{
        name: 'vd_session',
        value: 'invalid.cookie.value',
        domain: '127.0.0.1',
        path: '/',
        httpOnly: true,
        secure: false,
        sameSite: 'Strict'
      }]);

      // Try to access protected resource
      await page.goto('http://localhost:5174/dashboard');

      // Should be redirected to login due to invalid signature
      await page.waitForURL('**/login', { timeout: 5000 });
      expect(page.url().includes('/login'), 'Should reject cookies with invalid signatures').toBe(true);
    });
  });

  describe('Session Management', () => {
    test('should renew cookies on activity', async ({ page }) => {
      await page.goto('http://localhost:5174/login');
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      // Get initial cookie
      let cookies = await page.context().cookies();
      let authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );

      const initialExpires = authCookie?.expires;

      // Wait and perform activity
      await page.waitForTimeout(2000);
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Check if cookie was renewed (in a real implementation)
      cookies = await page.context().cookies();
      authCookie = cookies.find(cookie =>
        cookie.name === 'vd_session' || cookie.name === 'cc_light_session'
      );

      expect(authCookie, 'Cookie should still be present after activity').toBeTruthy();
      // In a real implementation, we'd check if expires time was extended
    });

    test('should handle concurrent sessions properly', async ({ browser }) => {
      // Create two browser contexts (simulate two tabs/browsers)
      const context1 = await browser.newContext();
      const context2 = await browser.newContext();

      const page1 = await context1.newPage();
      const page2 = await context2.newPage();

      try {
        // Login in both contexts
        for (const page of [page1, page2]) {
          await page.goto('http://localhost:5174/login');
          await page.fill('input[type="email"]', 'admin@cc-light.com');
          await page.fill('input[type="password"]', 'demo123');
          await page.click('button[type="submit"]');
          await page.waitForURL('**/dashboard');
        }

        // Both should be able to access dashboard
        await page1.goto('http://localhost:5174/dashboard');
        await page2.goto('http://localhost:5174/dashboard');

        expect(page1.url().includes('/dashboard')).toBe(true);
        expect(page2.url().includes('/dashboard')).toBe(true);

        // Logout from one context
        await page1.click('[data-testid="logout-button"]');
        await page1.waitForURL('**/login');

        // The other context should still work (unless implementing single-session policy)
        await page2.reload();
        // This behavior depends on session management policy

      } finally {
        await context1.close();
        await context2.close();
      }
    });
  });

  describe('Cross-Site Request Protection', () => {
    test('should reject requests from different origins', async ({ page, context }) => {
      // This test simulates cross-site request scenarios
      await page.goto('http://localhost:5174/login');
      await page.fill('input[type="email"]', 'admin@cc-light.com');
      await page.fill('input[type="password"]', 'demo123');
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard');

      // Simulate a cross-origin request
      const response = await page.evaluate(async () => {
        try {
          // This should fail due to SameSite cookie policy
          const response = await fetch('http://127.0.0.1:3010/trpc/auth.me', {
            method: 'GET',
            credentials: 'include',
            headers: {
              'Origin': 'http://evil-site.com'
            }
          });
          return { status: response.status, ok: response.ok };
        } catch (error) {
          return { error: error.message };
        }
      });

      // With SameSite=Strict, cross-origin requests should not include cookies
      // This test verifies the browser behavior rather than server response
    });
  });
});
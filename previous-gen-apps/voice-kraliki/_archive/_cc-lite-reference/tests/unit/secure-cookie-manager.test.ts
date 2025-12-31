/**
 * Unit Tests for SecureCookieManager
 * Tests encryption, signing, and cookie security features
 */

import { describe, test, expect, beforeEach, vi } from 'vitest';
import * as crypto from 'crypto';

// Mock environment variables
const mockEnv = {
  NODE_ENV: 'development',
  COOKIE_SECRET: 'test-cookie-secret-32-chars-long',
  COOKIE_ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex'),
  FRONTEND_URL: 'http://localhost:5174',
  COOKIE_DOMAIN: undefined
};

vi.stubEnv('NODE_ENV', mockEnv.NODE_ENV);
vi.stubEnv('COOKIE_SECRET', mockEnv.COOKIE_SECRET);
vi.stubEnv('COOKIE_ENCRYPTION_KEY', mockEnv.COOKIE_ENCRYPTION_KEY);
vi.stubEnv('FRONTEND_URL', mockEnv.FRONTEND_URL);

describe('SecureCookieManager', () => {
  let SecureCookieManager: any;
  let cookieManager: any;
  let mockReply: any;
  let mockRequest: any;

  beforeEach(async () => {
    // Reset environment variables to their original values
    vi.stubEnv('NODE_ENV', mockEnv.NODE_ENV);
    vi.stubEnv('COOKIE_SECRET', mockEnv.COOKIE_SECRET);
    vi.stubEnv('COOKIE_ENCRYPTION_KEY', mockEnv.COOKIE_ENCRYPTION_KEY);
    vi.stubEnv('FRONTEND_URL', mockEnv.FRONTEND_URL);

    // Import after env variables are set
    const module = await import('../../server/utils/secure-cookie-manager');
    SecureCookieManager = module.SecureCookieManager;
    cookieManager = new SecureCookieManager();

    // Mock Fastify reply
    mockReply = {
      setCookie: vi.fn(),
      clearCookie: vi.fn(),
    };

    // Mock request
    mockRequest = {
      cookies: {},
    };
  });

  describe('Cookie Setting', () => {
    test('should set cookies with secure defaults', () => {
      const cookieName = 'test_cookie';
      const cookieValue = 'test_value';

      cookieManager.setCookie(mockReply, cookieName, cookieValue);

      expect(mockReply.setCookie).toHaveBeenCalledWith(
        cookieName,
        expect.any(String),
        expect.objectContaining({
          httpOnly: true,
          secure: false, // false in development
          sameSite: 'strict',
          path: '/',
          maxAge: 7 * 24 * 60 * 60, // 7 days
        })
      );
    });

    test('should apply custom options', () => {
      const options = {
        httpOnly: false,
        secure: true,
        sameSite: 'lax' as const,
        maxAge: 3600,
      };

      cookieManager.setCookie(mockReply, 'test', 'value', options);

      expect(mockReply.setCookie).toHaveBeenCalledWith(
        'test',
        expect.any(String),
        expect.objectContaining({
          httpOnly: false,
          secure: true,
          sameSite: 'lax',
          maxAge: 3600,
        })
      );
    });

    test('should sign cookies by default', () => {
      cookieManager.setCookie(mockReply, 'test', 'value');

      const [[, actualValue]] = mockReply.setCookie.mock.calls;

      // Signed cookies should have a signature separated by dot
      expect(actualValue).toMatch(/^.+\..+$/);
      expect(actualValue.split('.').length).toBeGreaterThanOrEqual(2);
    });

    test('should encrypt cookies when requested', () => {
      cookieManager.setCookie(mockReply, 'test', 'sensitive_data', {
        encrypted: true,
      });

      const [[, actualValue]] = mockReply.setCookie.mock.calls;

      // Encrypted + signed cookies should not contain original value
      expect(actualValue).not.toContain('sensitive_data');
      expect(actualValue.length).toBeGreaterThan(20); // Should be longer due to encryption
    });
  });

  describe('Cookie Reading', () => {
    test('should read and validate signed cookies', () => {
      const testValue = 'test_value';

      // First set a cookie to get the signed value
      cookieManager.setCookie(mockReply, 'test', testValue);
      const [[, signedValue]] = mockReply.setCookie.mock.calls;

      // Mock request with the signed cookie
      mockRequest.cookies = { test: signedValue };

      // Should successfully read and verify the cookie
      const result = cookieManager.getCookie(mockRequest, 'test');
      expect(result).toBe(testValue);
    });

    test('should reject tampered cookies', () => {
      const testValue = 'test_value';

      // Set original cookie
      cookieManager.setCookie(mockReply, 'test', testValue);
      const [[, signedValue]] = mockReply.setCookie.mock.calls;

      // Tamper with the cookie
      const tamperedValue = signedValue + 'tampered';
      mockRequest.cookies = { test: tamperedValue };

      // Should reject tampered cookie
      const result = cookieManager.getCookie(mockRequest, 'test');
      expect(result).toBeNull();
    });

    test('should handle encrypted cookies', () => {
      const sensitiveData = 'secret_information';

      // Set encrypted cookie
      cookieManager.setCookie(mockReply, 'secret', sensitiveData, {
        encrypted: true,
      });
      const [[, encryptedValue]] = mockReply.setCookie.mock.calls;

      // Mock request with encrypted cookie
      mockRequest.cookies = { secret: encryptedValue };

      // Should successfully decrypt and return original value
      const result = cookieManager.getCookie(mockRequest, 'secret', {
        encrypted: true,
      });
      expect(result).toBe(sensitiveData);
    });

    test('should return null for missing cookies', () => {
      mockRequest.cookies = {};

      const result = cookieManager.getCookie(mockRequest, 'nonexistent');
      expect(result).toBeNull();
    });

    test('should handle malformed cookie values gracefully', () => {
      mockRequest.cookies = { malformed: 'invalid.cookie.format' };

      const result = cookieManager.getCookie(mockRequest, 'malformed');
      expect(result).toBeNull();
    });
  });

  describe('Authentication Cookies', () => {
    test('should set authentication cookies with maximum security', () => {
      const token = 'jwt_token_here';

      cookieManager.setAuthCookie(mockReply, token);

      // Should set both primary and backup cookies
      expect(mockReply.setCookie).toHaveBeenCalledTimes(2);

      const calls = mockReply.setCookie.mock.calls;
      const [vdSessionCall, ccLightCall] = calls;

      expect(vdSessionCall[0]).toBe('vd_session');
      expect(ccLightCall[0]).toBe('cc_light_session');

      // Both should have maximum security settings
      [vdSessionCall, ccLightCall].forEach(([, , options]) => {
        expect(options).toMatchObject({
          httpOnly: true,
          secure: false, // false in development
          sameSite: 'strict',
          maxAge: 24 * 60 * 60, // 24 hours
        });
      });
    });

    test('should read authentication cookies with decryption', () => {
      const token = 'test_jwt_token';

      // Set auth cookie
      cookieManager.setAuthCookie(mockReply, token);
      const [[, primaryValue], [, backupValue]] = mockReply.setCookie.mock.calls;

      // Mock request with primary cookie
      mockRequest.cookies = { vd_session: primaryValue };

      const result = cookieManager.getAuthCookie(mockRequest);
      expect(result).toBe(token);

      // Test fallback to backup cookie
      mockRequest.cookies = { cc_light_session: backupValue };
      delete mockRequest.cookies.vd_session;

      const fallbackResult = cookieManager.getAuthCookie(mockRequest);
      expect(fallbackResult).toBe(token);
    });

    test('should clear authentication cookies', () => {
      cookieManager.clearAuthCookies(mockReply);

      expect(mockReply.clearCookie).toHaveBeenCalledTimes(2);
      expect(mockReply.clearCookie).toHaveBeenCalledWith('vd_session', {
        path: '/',
        domain: undefined,
        secure: false,
        sameSite: 'strict',
      });
      expect(mockReply.clearCookie).toHaveBeenCalledWith('cc_light_session', {
        path: '/',
        domain: undefined,
        secure: false,
        sameSite: 'strict',
      });
    });
  });

  describe('CSRF Cookies', () => {
    test('should set CSRF cookies with appropriate settings', () => {
      const csrfToken = 'csrf_token_value';

      cookieManager.setCSRFCookie(mockReply, csrfToken);

      expect(mockReply.setCookie).toHaveBeenCalledWith(
        'cc_csrf_token',
        expect.any(String),
        expect.objectContaining({
          httpOnly: false, // CSRF tokens need to be readable by JS
          secure: false, // false in development
          sameSite: 'strict',
          maxAge: 60 * 60, // 1 hour
        })
      );
    });

    test('should read and validate CSRF cookies', () => {
      const csrfToken = 'csrf_token_value';

      // Set CSRF cookie
      cookieManager.setCSRFCookie(mockReply, csrfToken);
      const [[, signedValue]] = mockReply.setCookie.mock.calls;

      // Mock request
      mockRequest.cookies = { cc_csrf_token: signedValue };

      const result = cookieManager.getCSRFCookie(mockRequest);
      expect(result).toBe(csrfToken);
    });
  });

  describe('Security Compliance', () => {
    test('should validate security compliance in development', () => {
      const compliance = cookieManager.validateSecurityCompliance();

      // Should be compliant in development with mock env
      expect(compliance.compliant).toBe(true);
      expect(compliance.issues).toHaveLength(0);
    });

    test('should detect missing production requirements', () => {
      vi.stubEnv('NODE_ENV', 'production');
      vi.stubEnv('COOKIE_DOMAIN', undefined);
      vi.stubEnv('COOKIE_ENCRYPTION_KEY', undefined);

      const prodCookieManager = new SecureCookieManager();
      const compliance = prodCookieManager.validateSecurityCompliance();

      expect(compliance.compliant).toBe(false);
      expect(compliance.issues).toContain('COOKIE_ENCRYPTION_KEY not set for production');
      expect(compliance.issues).toContain('COOKIE_DOMAIN not set for production');
    });
  });

  describe('Error Handling', () => {
    test('should handle encryption errors gracefully', () => {
      // Create manager with invalid encryption key
      vi.stubEnv('COOKIE_ENCRYPTION_KEY', 'invalid_key');

      const invalidManager = new SecureCookieManager();

      // Should not throw but should handle errors internally
      expect(() => {
        invalidManager.setCookie(mockReply, 'test', 'value', { encrypted: true });
      }).not.toThrow();
    });

    test('should handle missing cookie secret in production', () => {
      vi.stubEnv('NODE_ENV', 'production');
      vi.stubEnv('COOKIE_SECRET', undefined);

      expect(() => {
        new SecureCookieManager();
      }).toThrow('COOKIE_SECRET environment variable is required in production');
    });

    test('should handle malformed encrypted cookies', () => {
      mockRequest.cookies = {
        encrypted: 'malformed:encrypted:data:with:many:colons'
      };

      const result = cookieManager.getCookie(mockRequest, 'encrypted', {
        encrypted: true,
      });

      expect(result).toBeNull();
    });
  });
});
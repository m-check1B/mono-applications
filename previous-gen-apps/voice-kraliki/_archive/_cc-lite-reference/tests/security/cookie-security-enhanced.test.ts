/**
 * Enhanced Cookie Security Tests
 * Comprehensive testing of cookie security features
 * Tests httpOnly, secure, sameSite, encryption, and CSRF protection
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { SecureCookieManager } from '../../server/utils/secure-cookie-manager';
import * as crypto from 'crypto';

const originalEnv = process.env;

const mockEnvSecure = {
  NODE_ENV: 'production',
  COOKIE_SECRET: crypto.randomBytes(32).toString('hex'),
  COOKIE_ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex'),
  COOKIE_DOMAIN: '.cc-light.com',
  FRONTEND_URL: 'https://app.cc-light.com'
};

const mockEnvDev = {
  NODE_ENV: 'development',
  COOKIE_SECRET: 'development-cookie-secret-32-chars-long',
  COOKIE_ENCRYPTION_KEY: crypto.randomBytes(32).toString('hex'),
  FRONTEND_URL: 'http://localhost:5174'
};

describe('Enhanced Cookie Security Tests', () => {
  let cookieManager: SecureCookieManager;
  let mockReply: any;
  let mockRequest: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockReply = {
      setCookie: vi.fn(),
      clearCookie: vi.fn(),
    };

    mockRequest = {
      cookies: {},
      headers: {
        'user-agent': 'Mozilla/5.0 (Test Browser)',
        'x-forwarded-for': '192.168.1.100',
        'host': 'app.cc-light.com'
      }
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Production Cookie Security', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
    });

    it('should set cookies with maximum security in production', () => {
      cookieManager.setCookie(mockReply, 'secure_cookie', 'sensitive_data');

      expect(mockReply.setCookie).toHaveBeenCalledWith(
        'secure_cookie',
        expect.any(String),
        expect.objectContaining({
          httpOnly: true,
          secure: true,      // MUST be true in production
          sameSite: 'strict',
          domain: '.cc-light.com',
          path: '/',
          maxAge: expect.any(Number)
        })
      );
    });

    it('should encrypt sensitive authentication cookies', () => {
      const jwtToken = 'eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.sensitive.data';
      
      cookieManager.setAuthCookie(mockReply, jwtToken);

      // Should set both primary and backup cookies
      expect(mockReply.setCookie).toHaveBeenCalledTimes(2);
      
      const calls = mockReply.setCookie.mock.calls;
      const [vdSessionCall, ccLightCall] = calls;
      
      // Primary cookie (vd_session)
      expect(vdSessionCall[0]).toBe('vd_session');
      expect(vdSessionCall[1]).not.toContain(jwtToken); // Should be encrypted
      expect(vdSessionCall[2]).toMatchObject({
        httpOnly: true,
        secure: true,
        sameSite: 'strict',
        maxAge: 24 * 60 * 60 // 24 hours
      });
      
      // Backup cookie (cc_light_session)
      expect(ccLightCall[0]).toBe('cc_light_session');
      expect(ccLightCall[1]).not.toContain(jwtToken); // Should be encrypted
      expect(ccLightCall[2]).toMatchObject({
        httpOnly: true,
        secure: true,
        sameSite: 'strict',
        maxAge: 24 * 60 * 60
      });
    });

    it('should set CSRF cookies with appropriate security', () => {
      const csrfToken = crypto.randomBytes(32).toString('hex');
      
      cookieManager.setCSRFCookie(mockReply, csrfToken);

      expect(mockReply.setCookie).toHaveBeenCalledWith(
        'cc_csrf_token',
        expect.any(String),
        expect.objectContaining({
          httpOnly: false, // CSRF tokens need to be readable by JS
          secure: true,
          sameSite: 'strict',
          maxAge: 60 * 60, // 1 hour
          domain: '.cc-light.com'
        })
      );
    });

    it('should validate domain restrictions', () => {
      const compliance = cookieManager.validateSecurityCompliance();
      
      expect(compliance.compliant).toBe(true);
      expect(compliance.issues).toHaveLength(0);
      expect(compliance.securityLevel).toBe('production');
    });
  });

  describe('Development Cookie Security', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvDev };
      cookieManager = new SecureCookieManager();
    });

    it('should adapt security for development environment', () => {
      cookieManager.setCookie(mockReply, 'dev_cookie', 'test_data');

      expect(mockReply.setCookie).toHaveBeenCalledWith(
        'dev_cookie',
        expect.any(String),
        expect.objectContaining({
          httpOnly: true,
          secure: false,     // false for localhost
          sameSite: 'strict',
          path: '/'
          // No domain restriction for localhost
        })
      );
    });

    it('should still sign cookies in development', () => {
      cookieManager.setCookie(mockReply, 'dev_cookie', 'test_data');
      
      const [[, actualValue]] = mockReply.setCookie.mock.calls;
      
      // Should contain signature even in development
      expect(actualValue).toMatch(/^.+\..+$/);
      expect(actualValue).not.toBe('test_data'); // Should be signed
    });
  });

  describe('Cookie Encryption', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
    });

    it('should encrypt and decrypt sensitive data correctly', () => {
      const sensitiveData = JSON.stringify({
        userId: 'user-123',
        sessionId: 'session-456',
        permissions: ['read', 'write']
      });
      
      // Set encrypted cookie
      cookieManager.setCookie(mockReply, 'encrypted_data', sensitiveData, {
        encrypted: true
      });
      
      const [[, encryptedValue]] = mockReply.setCookie.mock.calls;
      
      // Should not contain original data
      expect(encryptedValue).not.toContain('user-123');
      expect(encryptedValue).not.toContain('session-456');
      expect(encryptedValue).not.toContain('permissions');
      
      // Should be significantly longer due to encryption
      expect(encryptedValue.length).toBeGreaterThan(sensitiveData.length * 2);
      
      // Mock request with encrypted cookie
      mockRequest.cookies = { encrypted_data: encryptedValue };
      
      // Should decrypt correctly
      const decryptedData = cookieManager.getCookie(mockRequest, 'encrypted_data', {
        encrypted: true
      });
      
      expect(decryptedData).toBe(sensitiveData);
      
      // Should parse back to original object
      const parsedData = JSON.parse(decryptedData!);
      expect(parsedData.userId).toBe('user-123');
      expect(parsedData.sessionId).toBe('session-456');
      expect(parsedData.permissions).toEqual(['read', 'write']);
    });

    it('should reject tampered encrypted cookies', () => {
      const sensitiveData = 'secret_information';
      
      // Set encrypted cookie
      cookieManager.setCookie(mockReply, 'secret', sensitiveData, {
        encrypted: true
      });
      
      const [[, encryptedValue]] = mockReply.setCookie.mock.calls;
      
      // Tamper with encrypted value
      const tamperedValue = encryptedValue.slice(0, -5) + 'TAMPR';
      mockRequest.cookies = { secret: tamperedValue };
      
      // Should return null for tampered cookie
      const result = cookieManager.getCookie(mockRequest, 'secret', {
        encrypted: true
      });
      
      expect(result).toBeNull();
    });

    it('should handle encryption errors gracefully', () => {
      // Create manager with invalid encryption key
      process.env.COOKIE_ENCRYPTION_KEY = 'invalid_key_too_short';
      
      const invalidManager = new SecureCookieManager();
      
      // Should not crash but handle error internally
      expect(() => {
        invalidManager.setCookie(mockReply, 'test', 'value', { encrypted: true });
      }).not.toThrow();
      
      // Should fallback to signed-only if encryption fails
      expect(mockReply.setCookie).toHaveBeenCalled();
    });
  });

  describe('CSRF Protection', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
    });

    it('should generate cryptographically secure CSRF tokens', () => {
      const token1 = cookieManager.generateCSRFToken();
      const token2 = cookieManager.generateCSRFToken();
      
      expect(token1).not.toBe(token2);
      expect(token1).toMatch(/^[a-f0-9]{64}$/); // 32 bytes hex
      expect(token2).toMatch(/^[a-f0-9]{64}$/); // 32 bytes hex
      
      // Should be URL-safe
      expect(token1).not.toContain('+');
      expect(token1).not.toContain('/');
      expect(token1).not.toContain('=');
    });

    it('should validate CSRF tokens correctly', () => {
      const csrfToken = cookieManager.generateCSRFToken();
      
      // Set CSRF cookie
      cookieManager.setCSRFCookie(mockReply, csrfToken);
      const [[, cookieValue]] = mockReply.setCookie.mock.calls;
      
      // Mock request with CSRF cookie
      mockRequest.cookies = { cc_csrf_token: cookieValue };
      
      // Should validate correctly
      const isValid = cookieManager.validateCSRFToken(mockRequest, csrfToken);
      expect(isValid).toBe(true);
      
      // Should reject wrong token
      const wrongToken = cookieManager.generateCSRFToken();
      const isInvalid = cookieManager.validateCSRFToken(mockRequest, wrongToken);
      expect(isInvalid).toBe(false);
    });

    it('should reject CSRF validation without cookie', () => {
      const csrfToken = cookieManager.generateCSRFToken();
      
      // No CSRF cookie set
      mockRequest.cookies = {};
      
      const isValid = cookieManager.validateCSRFToken(mockRequest, csrfToken);
      expect(isValid).toBe(false);
    });

    it('should handle double-submit cookie pattern', () => {
      const csrfToken = cookieManager.generateCSRFToken();
      
      // Set CSRF cookie
      cookieManager.setCSRFCookie(mockReply, csrfToken);
      const [[, cookieValue]] = mockReply.setCookie.mock.calls;
      
      // Mock request with CSRF cookie and header
      mockRequest.cookies = { cc_csrf_token: cookieValue };
      mockRequest.headers['x-csrf-token'] = csrfToken;
      
      // Should validate double-submit pattern
      const isValid = cookieManager.validateDoubleSubmitCSRF(mockRequest);
      expect(isValid).toBe(true);
      
      // Should fail if header doesn't match cookie
      mockRequest.headers['x-csrf-token'] = 'different_token';
      const isInvalid = cookieManager.validateDoubleSubmitCSRF(mockRequest);
      expect(isInvalid).toBe(false);
    });
  });

  describe('Cookie Signing Security', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
    });

    it('should sign cookies with HMAC-SHA256', () => {
      const testValue = 'test_cookie_value';
      
      cookieManager.setCookie(mockReply, 'signed_cookie', testValue);
      
      const [[, signedValue]] = mockReply.setCookie.mock.calls;
      
      // Should have signature format: value.signature
      const parts = signedValue.split('.');
      expect(parts.length).toBeGreaterThanOrEqual(2);
      
      // Signature should be base64url encoded
      const signature = parts[parts.length - 1];
      expect(signature).toMatch(/^[A-Za-z0-9_-]+$/);
      
      // Should be able to verify
      mockRequest.cookies = { signed_cookie: signedValue };
      const verified = cookieManager.getCookie(mockRequest, 'signed_cookie');
      expect(verified).toBe(testValue);
    });

    it('should reject cookies with invalid signatures', () => {
      const testValue = 'test_cookie_value';
      
      // Set valid cookie
      cookieManager.setCookie(mockReply, 'signed_cookie', testValue);
      const [[, signedValue]] = mockReply.setCookie.mock.calls;
      
      // Tamper with signature
      const parts = signedValue.split('.');
      parts[parts.length - 1] = 'tampered_signature';
      const tamperedValue = parts.join('.');
      
      mockRequest.cookies = { signed_cookie: tamperedValue };
      const result = cookieManager.getCookie(mockRequest, 'signed_cookie');
      
      expect(result).toBeNull();
    });

    it('should use timing-safe comparison for signature verification', () => {
      const testValue = 'test_value';
      
      // Set cookie
      cookieManager.setCookie(mockReply, 'timed_cookie', testValue);
      const [[, signedValue]] = mockReply.setCookie.mock.calls;
      
      // Test multiple times to ensure consistent timing
      const times: number[] = [];
      
      for (let i = 0; i < 10; i++) {
        // Slightly different invalid signatures
        const parts = signedValue.split('.');
        parts[parts.length - 1] = `invalid_${i}`;
        const invalidValue = parts.join('.');
        
        mockRequest.cookies = { timed_cookie: invalidValue };
        
        const start = process.hrtime.bigint();
        cookieManager.getCookie(mockRequest, 'timed_cookie');
        const end = process.hrtime.bigint();
        
        times.push(Number(end - start));
      }
      
      // Verification times should be consistent (no early exit on mismatch)
      const avgTime = times.reduce((a, b) => a + b) / times.length;
      const maxDeviation = Math.max(...times.map(t => Math.abs(t - avgTime)));
      const deviationPercent = (maxDeviation / avgTime) * 100;
      
      // Should have low timing variation (less than 50% deviation)
      expect(deviationPercent).toBeLessThan(50);
    });
  });

  describe('Cookie Security Headers', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
    });

    it('should set appropriate SameSite values for different cookie types', () => {
      // Auth cookies should be Strict
      cookieManager.setAuthCookie(mockReply, 'jwt_token');
      const authCalls = mockReply.setCookie.mock.calls;
      authCalls.forEach(([, , options]) => {
        expect(options.sameSite).toBe('strict');
      });
      
      vi.clearAllMocks();
      
      // CSRF cookies should be Strict for security
      cookieManager.setCSRFCookie(mockReply, 'csrf_token');
      const [[, , csrfOptions]] = mockReply.setCookie.mock.calls;
      expect(csrfOptions.sameSite).toBe('strict');
      
      vi.clearAllMocks();
      
      // General cookies can be customized
      cookieManager.setCookie(mockReply, 'general', 'value', {
        sameSite: 'lax'
      });
      const [[, , generalOptions]] = mockReply.setCookie.mock.calls;
      expect(generalOptions.sameSite).toBe('lax');
    });

    it('should enforce HttpOnly for sensitive cookies', () => {
      // Auth cookies must be HttpOnly
      cookieManager.setAuthCookie(mockReply, 'jwt_token');
      const authCalls = mockReply.setCookie.mock.calls;
      authCalls.forEach(([, , options]) => {
        expect(options.httpOnly).toBe(true);
      });
      
      vi.clearAllMocks();
      
      // CSRF cookies should not be HttpOnly (need JS access)
      cookieManager.setCSRFCookie(mockReply, 'csrf_token');
      const [[, , csrfOptions]] = mockReply.setCookie.mock.calls;
      expect(csrfOptions.httpOnly).toBe(false);
    });

    it('should set secure flag based on environment', () => {
      // Production should enforce secure
      cookieManager.setCookie(mockReply, 'prod_cookie', 'value');
      const [[, , prodOptions]] = mockReply.setCookie.mock.calls;
      expect(prodOptions.secure).toBe(true);
      
      vi.clearAllMocks();
      
      // Development should allow non-secure for localhost
      process.env.NODE_ENV = 'development';
      const devManager = new SecureCookieManager();
      devManager.setCookie(mockReply, 'dev_cookie', 'value');
      const [[, , devOptions]] = mockReply.setCookie.mock.calls;
      expect(devOptions.secure).toBe(false);
    });
  });

  describe('Session Cookie Security', () => {
    beforeEach(() => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
    });

    it('should implement redundant session storage', () => {
      const sessionToken = 'jwt.session.token';
      
      cookieManager.setAuthCookie(mockReply, sessionToken);
      
      // Should set both primary and backup cookies
      expect(mockReply.setCookie).toHaveBeenCalledTimes(2);
      
      const calls = mockReply.setCookie.mock.calls;
      expect(calls[0][0]).toBe('vd_session');      // Primary
      expect(calls[1][0]).toBe('cc_light_session'); // Backup
      
      // Both should have the same security settings
      calls.forEach(([, , options]) => {
        expect(options.httpOnly).toBe(true);
        expect(options.secure).toBe(true);
        expect(options.sameSite).toBe('strict');
      });
    });

    it('should support session cookie fallback', () => {
      const sessionToken = 'jwt.session.token';
      
      // Set auth cookies
      cookieManager.setAuthCookie(mockReply, sessionToken);
      const calls = mockReply.setCookie.mock.calls;
      const [primaryValue, backupValue] = calls.map(call => call[1]);
      
      // Test primary cookie retrieval
      mockRequest.cookies = { vd_session: primaryValue };
      let retrieved = cookieManager.getAuthCookie(mockRequest);
      expect(retrieved).toBe(sessionToken);
      
      // Test fallback to backup cookie
      mockRequest.cookies = { cc_light_session: backupValue };
      retrieved = cookieManager.getAuthCookie(mockRequest);
      expect(retrieved).toBe(sessionToken);
      
      // Test no cookies available
      mockRequest.cookies = {};
      retrieved = cookieManager.getAuthCookie(mockRequest);
      expect(retrieved).toBeNull();
    });

    it('should clear all session cookies on logout', () => {
      cookieManager.clearAuthCookies(mockReply);
      
      expect(mockReply.clearCookie).toHaveBeenCalledTimes(2);
      expect(mockReply.clearCookie).toHaveBeenCalledWith('vd_session');
      expect(mockReply.clearCookie).toHaveBeenCalledWith('cc_light_session');
    });
  });

  describe('Security Compliance Validation', () => {
    it('should detect missing production requirements', () => {
      process.env = {
        ...originalEnv,
        NODE_ENV: 'production'
        // Missing COOKIE_SECRET, COOKIE_ENCRYPTION_KEY, COOKIE_DOMAIN
      };
      
      expect(() => {
        new SecureCookieManager();
      }).toThrow('COOKIE_SECRET environment variable is required in production');
    });

    it('should validate environment security compliance', () => {
      process.env = { ...originalEnv, ...mockEnvSecure };
      cookieManager = new SecureCookieManager();
      
      const compliance = cookieManager.validateSecurityCompliance();
      
      expect(compliance).toMatchObject({
        compliant: true,
        securityLevel: 'production',
        issues: [],
        recommendations: expect.any(Array)
      });
    });

    it('should provide security recommendations', () => {
      process.env = {
        ...originalEnv,
        NODE_ENV: 'production',
        COOKIE_SECRET: 'weak-secret', // Too short
        COOKIE_ENCRYPTION_KEY: mockEnvSecure.COOKIE_ENCRYPTION_KEY,
        COOKIE_DOMAIN: '.cc-light.com'
      };
      
      cookieManager = new SecureCookieManager();
      const compliance = cookieManager.validateSecurityCompliance();
      
      expect(compliance.compliant).toBe(false);
      expect(compliance.issues).toContain(
        expect.stringContaining('COOKIE_SECRET should be at least 32 characters')
      );
    });
  });
});

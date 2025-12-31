/**
 * Cookie Security Tests
 * Tests secure cookie management including httpOnly, secure, sameSite settings
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import type { FastifyReply, FastifyRequest } from 'fastify';

// Mock the secure cookie manager
const mockSecureCookieManager = {
  setAuthCookie: vi.fn(),
  clearAuthCookies: vi.fn(),
  getAuthCookie: vi.fn(),
  validateCookieSettings: vi.fn()
};

vi.mock('@server/utils/secure-cookie-manager', () => ({
  secureCookieManager: mockSecureCookieManager
}));

describe('Cookie Security Tests', () => {
  let mockReply: Partial<FastifyReply>;
  let mockRequest: Partial<FastifyRequest>;

  beforeEach(() => {
    vi.clearAllMocks();

    mockReply = {
      cookie: vi.fn().mockReturnThis(),
      clearCookie: vi.fn().mockReturnThis(),
      send: vi.fn().mockReturnThis(),
      code: vi.fn().mockReturnThis(),
      header: vi.fn().mockReturnThis()
    };

    mockRequest = {
      cookies: {},
      headers: {},
      hostname: 'localhost',
      protocol: 'https'
    };
  });

  describe('Secure Cookie Configuration', () => {
    it('should set httpOnly flag for auth cookies', async () => {
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token);

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.objectContaining({
          httpOnly: true
        })
      );
    });

    it('should set secure flag for HTTPS connections', async () => {
      mockRequest.protocol = 'https';
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token, {
        request: mockRequest as FastifyRequest
      });

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.objectContaining({
          secure: true
        })
      );
    });

    it('should not set secure flag for HTTP in development', async () => {
      mockRequest.protocol = 'http';
      mockRequest.hostname = 'localhost';
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token, {
        request: mockRequest as FastifyRequest
      });

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.objectContaining({
          secure: false // Should be false for HTTP in development
        })
      );

      process.env.NODE_ENV = originalEnv;
    });

    it('should enforce secure flag in production even for HTTP', async () => {
      mockRequest.protocol = 'http';
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'production';

      const token = 'valid_jwt_token_12345';

      expect(() => {
        setSecureAuthCookie(mockReply as FastifyReply, token, {
          request: mockRequest as FastifyRequest
        });
      }).toThrow('HTTPS required in production');

      process.env.NODE_ENV = originalEnv;
    });

    it('should set appropriate SameSite policy', async () => {
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token);

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.objectContaining({
          sameSite: 'strict'
        })
      );
    });

    it('should set appropriate cookie expiration', async () => {
      const token = 'valid_jwt_token_12345';
      const expectedMaxAge = 7 * 24 * 60 * 60 * 1000; // 7 days

      setSecureAuthCookie(mockReply as FastifyReply, token);

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.objectContaining({
          maxAge: expectedMaxAge
        })
      );
    });

    it('should set cookie path restriction', async () => {
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token);

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.objectContaining({
          path: '/'
        })
      );
    });
  });

  describe('Cookie Domain Security', () => {
    it('should validate cookie domain against request hostname', async () => {
      const testCases = [
        { hostname: 'localhost', domain: undefined, valid: true },
        { hostname: 'cc-light.com', domain: 'cc-light.com', valid: true },
        { hostname: 'sub.cc-light.com', domain: '.cc-light.com', valid: true },
        { hostname: 'evil.com', domain: 'cc-light.com', valid: false },
        { hostname: 'cc-light.com', domain: 'evil.com', valid: false }
      ];

      for (const testCase of testCases) {
        mockRequest.hostname = testCase.hostname;
        const token = 'valid_jwt_token_12345';

        if (testCase.valid) {
          expect(() => {
            setSecureAuthCookie(mockReply as FastifyReply, token, {
              request: mockRequest as FastifyRequest,
              domain: testCase.domain
            });
          }).not.toThrow();
        } else {
          expect(() => {
            setSecureAuthCookie(mockReply as FastifyReply, token, {
              request: mockRequest as FastifyRequest,
              domain: testCase.domain
            });
          }).toThrow('Domain mismatch');
        }
      }
    });

    it('should prevent subdomain takeover attacks', async () => {
      mockRequest.hostname = 'malicious.cc-light.com';
      const token = 'valid_jwt_token_12345';

      // Should not allow setting domain for parent domain from subdomain
      expect(() => {
        setSecureAuthCookie(mockReply as FastifyReply, token, {
          request: mockRequest as FastifyRequest,
          domain: 'cc-light.com' // Trying to set parent domain
        });
      }).toThrow();
    });
  });

  describe('Cookie Value Security', () => {
    it('should validate JWT token format before setting cookie', async () => {
      const invalidTokens = [
        '',
        'not.a.jwt',
        'invalid-token-format',
        '<script>alert("xss")</script>',
        '../../etc/passwd',
        null,
        undefined
      ];

      for (const token of invalidTokens) {
        expect(() => {
          setSecureAuthCookie(mockReply as FastifyReply, token as any);
        }).toThrow('Invalid token format');
      }
    });

    it('should accept valid JWT token formats', async () => {
      const validTokens = [
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNjM5NjA5NjAwfQ.L8i6g3PZSUb4t8QK_p7bBa2N4-K2g9rZz0z3M_4p8qM'
      ];

      for (const token of validTokens) {
        expect(() => {
          setSecureAuthCookie(mockReply as FastifyReply, token);
        }).not.toThrow();
      }
    });

    it('should sanitize cookie values to prevent injection', async () => {
      const maliciousValues = [
        'token; path=/; domain=evil.com',
        'token\r\nSet-Cookie: evil=value',
        'token\nLocation: http://evil.com',
        'token; HttpOnly=false; Secure=false'
      ];

      for (const value of maliciousValues) {
        expect(() => {
          setSecureAuthCookie(mockReply as FastifyReply, value);
        }).toThrow('Invalid token format');
      }
    });
  });

  describe('Cookie Clearing Security', () => {
    it('should clear all auth cookies securely', async () => {
      clearAllAuthCookies(mockReply as FastifyReply);

      const expectedCookies = [
        'cc_light_session',
        'cc_light_refresh',
        '__session', // Auth session cookie
        'vd_session' // Stack 2025 SSO cookie
      ];

      for (const cookieName of expectedCookies) {
        expect(mockReply.clearCookie).toHaveBeenCalledWith(
          cookieName,
          expect.objectContaining({
            httpOnly: true,
            secure: true,
            sameSite: 'strict',
            path: '/'
          })
        );
      }
    });

    it('should clear cookies with all possible paths', async () => {
      clearAllAuthCookies(mockReply as FastifyReply);

      // Should clear cookies from different paths to prevent leaks
      const paths = ['/', '/api', '/auth'];

      for (const path of paths) {
        expect(mockReply.clearCookie).toHaveBeenCalledWith(
          'cc_light_session',
          expect.objectContaining({
            path
          })
        );
      }
    });
  });

  describe('Cookie Reading Security', () => {
    it('should safely extract auth tokens from cookies', async () => {
      mockRequest.cookies = {
        'cc_light_session': 'valid.jwt.token',
        'other_cookie': 'other_value',
        'malicious_cookie': '<script>alert("xss")</script>'
      };

      const token = getSecureAuthCookie(mockRequest as FastifyRequest);

      expect(token).toBe('valid.jwt.token');
      expect(token).not.toContain('<script>');
    });

    it('should validate cookie names to prevent confusion attacks', async () => {
      mockRequest.cookies = {
        'cc_light_session ': 'fake_token', // Trailing space
        'cc_light_session': 'real_token',
        'CC_LIGHT_SESSION': 'case_attack', // Different case
        'cc-light-session': 'dash_attack' // Different separator
      };

      const token = getSecureAuthCookie(mockRequest as FastifyRequest);

      expect(token).toBe('real_token'); // Should get the exact match only
    });

    it('should handle missing or empty cookies gracefully', async () => {
      const testCases = [
        { cookies: undefined },
        { cookies: {} },
        { cookies: { other: 'value' } },
        { cookies: { 'cc_light_session': '' } },
        { cookies: { 'cc_light_session': null } }
      ];

      for (const testCase of testCases) {
        mockRequest.cookies = testCase.cookies as any;
        const token = getSecureAuthCookie(mockRequest as FastifyRequest);
        expect(token).toBeNull();
      }
    });
  });

  describe('Cross-Site Request Forgery (CSRF) Protection', () => {
    it('should set CSRF token cookie alongside auth cookie', async () => {
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token, {
        includeCsrfProtection: true
      });

      // Should set both auth cookie and CSRF token
      expect(mockReply.cookie).toHaveBeenCalledWith(
        'cc_light_session',
        token,
        expect.any(Object)
      );

      expect(mockReply.cookie).toHaveBeenCalledWith(
        'csrf_token',
        expect.stringMatching(/^[a-zA-Z0-9+/]+=*$/), // Base64 pattern
        expect.objectContaining({
          httpOnly: false, // CSRF token needs to be readable by JS
          secure: true,
          sameSite: 'strict'
        })
      );
    });

    it('should generate unique CSRF tokens', async () => {
      const tokens = new Set();
      const token = 'valid_jwt_token_12345';

      // Generate multiple CSRF tokens
      for (let i = 0; i < 10; i++) {
        vi.clearAllMocks();
        setSecureAuthCookie(mockReply as FastifyReply, token, {
          includeCsrfProtection: true
        });

        const csrfCall = (mockReply.cookie as any).mock.calls.find((call: any) =>
          call[0] === 'csrf_token'
        );

        if (csrfCall) {
          tokens.add(csrfCall[1]);
        }
      }

      expect(tokens.size).toBe(10); // All tokens should be unique
    });
  });

  describe('Cookie Security Headers', () => {
    it('should set security headers when setting cookies', async () => {
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token, {
        setSecurityHeaders: true
      });

      // Should set relevant security headers
      expect(mockReply.header).toHaveBeenCalledWith(
        'X-Content-Type-Options',
        'nosniff'
      );

      expect(mockReply.header).toHaveBeenCalledWith(
        'X-Frame-Options',
        'DENY'
      );

      expect(mockReply.header).toHaveBeenCalledWith(
        'Strict-Transport-Security',
        'max-age=31536000; includeSubDomains; preload'
      );
    });

    it('should set appropriate Cache-Control headers for auth endpoints', async () => {
      const token = 'valid_jwt_token_12345';

      setSecureAuthCookie(mockReply as FastifyReply, token);

      expect(mockReply.header).toHaveBeenCalledWith(
        'Cache-Control',
        'no-store, no-cache, must-revalidate, private'
      );

      expect(mockReply.header).toHaveBeenCalledWith(
        'Pragma',
        'no-cache'
      );
    });
  });

  describe('Cookie Size and Performance Security', () => {
    it('should reject oversized cookie values', async () => {
      // HTTP cookies have a 4KB limit
      const oversizedToken = 'x'.repeat(5000);

      expect(() => {
        setSecureAuthCookie(mockReply as FastifyReply, oversizedToken);
      }).toThrow('Cookie value too large');
    });

    it('should limit total number of cookies', async () => {
      // Set up a request with many existing cookies
      const manyCookies: Record<string, string> = {};
      for (let i = 0; i < 100; i++) {
        manyCookies[`cookie_${i}`] = `value_${i}`;
      }

      mockRequest.cookies = manyCookies;
      const token = 'valid_jwt_token_12345';

      expect(() => {
        setSecureAuthCookie(mockReply as FastifyReply, token, {
          request: mockRequest as FastifyRequest
        });
      }).toThrow('Too many cookies');
    });
  });
});

// Helper functions for cookie security
function setSecureAuthCookie(
  reply: FastifyReply,
  token: string,
  options: {
    request?: FastifyRequest;
    domain?: string;
    includeCsrfProtection?: boolean;
    setSecurityHeaders?: boolean;
  } = {}
): void {
  // Validate token format
  if (!token || typeof token !== 'string' || !isValidJWT(token)) {
    throw new Error('Invalid token format');
  }

  // Check cookie size
  if (token.length > 4000) {
    throw new Error('Cookie value too large');
  }

  // Check total cookies if request provided
  if (options.request?.cookies && Object.keys(options.request.cookies).length > 50) {
    throw new Error('Too many cookies');
  }

  // Determine security settings
  const isProduction = process.env.NODE_ENV === 'production';
  const isSecure = options.request?.protocol === 'https';
  const isLocalhost = options.request?.hostname === 'localhost';

  if (isProduction && !isSecure) {
    throw new Error('HTTPS required in production');
  }

  // Validate domain if provided
  if (options.domain && options.request) {
    if (!isValidCookieDomain(options.domain, options.request.hostname)) {
      throw new Error('Domain mismatch');
    }
  }

  const cookieOptions = {
    httpOnly: true,
    secure: isSecure || isProduction,
    sameSite: 'strict' as const,
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    path: '/',
    ...(options.domain && { domain: options.domain })
  };

  reply.cookie('cc_light_session', token, cookieOptions);

  // Set CSRF protection if requested
  if (options.includeCsrfProtection) {
    const csrfToken = generateCSRFToken();
    reply.cookie('csrf_token', csrfToken, {
      ...cookieOptions,
      httpOnly: false // CSRF token needs to be readable by JS
    });
  }

  // Set security headers if requested
  if (options.setSecurityHeaders) {
    reply.header('X-Content-Type-Options', 'nosniff');
    reply.header('X-Frame-Options', 'DENY');
    reply.header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  }

  // Always set cache control headers for auth endpoints
  reply.header('Cache-Control', 'no-store, no-cache, must-revalidate, private');
  reply.header('Pragma', 'no-cache');
}

function clearAllAuthCookies(reply: FastifyReply): void {
  const cookieNames = [
    'cc_light_session',
    'cc_light_refresh',
    '__session', // Auth session cookie
    'vd_session', // Stack 2025 SSO cookie
    'csrf_token'
  ];

  const paths = ['/', '/api', '/auth'];
  const clearOptions = {
    httpOnly: true,
    secure: true,
    sameSite: 'strict' as const
  };

  for (const cookieName of cookieNames) {
    for (const path of paths) {
      reply.clearCookie(cookieName, { ...clearOptions, path });
    }
  }
}

function getSecureAuthCookie(request: FastifyRequest): string | null {
  const cookies = request.cookies;
  if (!cookies) return null;

  const token = cookies['cc_light_session'];
  if (!token || typeof token !== 'string') return null;

  // Validate token format
  if (!isValidJWT(token)) return null;

  return token;
}

function isValidJWT(token: string): boolean {
  if (!token || typeof token !== 'string') return false;

  // Check for malicious patterns
  if (token.includes('\n') || token.includes('\r') || token.includes(';')) {
    return false;
  }

  // Basic JWT format check (3 parts separated by dots)
  const parts = token.split('.');
  if (parts.length !== 3) return false;

  // Check each part is base64url encoded
  return parts.every(part => /^[A-Za-z0-9_-]*$/.test(part));
}

function isValidCookieDomain(domain: string, hostname: string): boolean {
  if (!domain || !hostname) return false;

  // Exact match
  if (domain === hostname) return true;

  // Subdomain match (domain starts with dot)
  if (domain.startsWith('.')) {
    const parentDomain = domain.substring(1);
    return hostname === parentDomain || hostname.endsWith('.' + parentDomain);
  }

  return false;
}

function generateCSRFToken(): string {
  const crypto = require('crypto');
  return crypto.randomBytes(32).toString('base64');
}
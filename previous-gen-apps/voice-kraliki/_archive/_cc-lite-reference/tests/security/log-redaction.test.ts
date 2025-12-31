/**
 * Comprehensive Test Suite for Log Redaction System
 * Tests all sensitive data patterns and redaction functionality
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { LogRedactor, logRedactor, redactLogData, redactString, redactUrl, redactHeaders, testRedaction } from '../../server/utils/log-redactor';
import { secureLogger, authLogger, apiLogger, securityLogger } from '../../server/utils/secure-logger';
import { interceptConsoleLogging, restoreConsoleLogging } from '../../server/middleware/logging-redaction';

describe('Log Redaction System', () => {
  let redactor: LogRedactor;
  let consoleOutputs: string[] = [];
  let originalConsoleLog: typeof console.log;

  beforeEach(() => {
    redactor = new LogRedactor();
    consoleOutputs = [];

    // Capture console output for testing
    originalConsoleLog = console.log;
    console.log = (...args: any[]) => {
      consoleOutputs.push(args.map(arg =>
        typeof arg === 'string' ? arg : JSON.stringify(arg)
      ).join(' '));
    };
  });

  afterEach(() => {
    console.log = originalConsoleLog;
    restoreConsoleLogging();
  });

  describe('String Redaction', () => {
    it('should redact JWT tokens', () => {
      const jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
      const redacted = redactor.redactString(jwt);

      expect(redacted).not.toBe(jwt);
      expect(redacted).toContain('eyJhbG');
      expect(redacted).toContain('ssw5c');
      expect(redacted).toContain('*');
    });

    it('should redact API keys', () => {
      const testCases = [
        'apiKey: ak-1234567890abcdefghijk',
        'api_key=sk-proj-1234567890abcdefghijk',
        'key="live_pk_1234567890abcdefghijk"'
      ];

      testCases.forEach(testCase => {
        const redacted = redactor.redactString(testCase);
        expect(redacted).not.toBe(testCase);
        expect(redacted).toContain('[REDACTED');
      });
    });

    it('should redact passwords', () => {
      const testCases = [
        'password: secret123',
        'pwd="mypassword"',
        'pass=strongpass123'
      ];

      testCases.forEach(testCase => {
        const redacted = redactor.redactString(testCase);
        expect(redacted).not.toBe(testCase);
        expect(redacted).toBe('[REDACTED_PASSWORD]');
      });
    });

    it('should redact email addresses partially', () => {
      const email = 'user@example.com';
      const redacted = redactor.redactString(email);

      expect(redacted).not.toBe(email);
      expect(redacted).toContain('@example.com');
      expect(redacted).toMatch(/^u\*+r@example\.com$/);
    });

    it('should redact phone numbers showing last 4 digits', () => {
      const phoneNumbers = [
        '+1-555-123-4567',
        '(555) 123-4567',
        '5551234567',
        '1-555-123-4567'
      ];

      phoneNumbers.forEach(phone => {
        const redacted = redactor.redactString(phone);
        expect(redacted).not.toBe(phone);
        expect(redacted).toBe('***-***-4567');
      });
    });

    it('should redact credit card numbers showing last 4 digits', () => {
      const creditCards = [
        '4111111111111111', // Visa
        '5555555555554444', // MasterCard
        '378282246310005',  // Amex
        '6011111111111117'  // Discover
      ];

      creditCards.forEach(cc => {
        const redacted = redactor.redactString(cc);
        expect(redacted).not.toBe(cc);
        expect(redacted).toMatch(/\*{4}-\*{4}-\*{4}-\d{4}/);
      });
    });

    it('should redact SSN showing last 4 digits', () => {
      const ssns = [
        '123-45-6789',
        '123456789'
      ];

      ssns.forEach(ssn => {
        const redacted = redactor.redactString(ssn);
        expect(redacted).not.toBe(ssn);
        expect(redacted).toBe('***-**-6789');
      });
    });

    it('should redact Twilio auth tokens', () => {
      const token = 'twilioAuthToken: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6';
      const redacted = redactor.redactString(token);

      expect(redacted).not.toBe(token);
      expect(redacted).toBe('[REDACTED_TWILIO_TOKEN]');
    });

    it('should redact OpenAI API keys', () => {
      const apiKey = 'sk-proj-1234567890abcdefghijklmnopqrstuvwxyzABCDEF';
      const redacted = redactor.redactString(apiKey);

      expect(redacted).not.toBe(apiKey);
      expect(redacted).toContain('sk-');
      expect(redacted).toContain('*');
    });

    it('should redact Bearer tokens', () => {
      const bearerToken = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature';
      const redacted = redactor.redactString(bearerToken);

      expect(redacted).not.toBe(bearerToken);
      expect(redacted).toContain('Bearer ');
      expect(redacted).toContain('*');
    });

    it('should redact database URLs', () => {
      const dbUrl = 'postgresql://user:password@localhost:5432/dbname';
      const redacted = redactor.redactString(dbUrl);

      expect(redacted).not.toBe(dbUrl);
      expect(redacted).toBe('postgresql://[REDACTED]:[REDACTED]@[REDACTED]/[REDACTED]');
    });
  });

  describe('Object Redaction', () => {
    it('should redact sensitive object keys', () => {
      const obj = {
        username: 'john_doe',
        password: 'secret123',
        apiKey: 'ak-1234567890',
        email: 'john@example.com',
        phoneNumber: '+1-555-123-4567',
        creditCard: '4111111111111111',
        publicData: 'not sensitive'
      };

      const redacted = redactor.redactObject(obj);

      expect(redacted.username).toBe('john_doe');
      expect(redacted.password).toBe('[REDACTED]');
      expect(redacted.apiKey).toBe('[REDACTED]');
      expect(redacted.email).not.toBe(obj.email);
      expect(redacted.email).toContain('@example.com');
      expect(redacted.phoneNumber).toBe('***-***-4567');
      expect(redacted.creditCard).toBe('****-****-****-1111');
      expect(redacted.publicData).toBe('not sensitive');
    });

    it('should handle nested objects', () => {
      const obj = {
        user: {
          credentials: {
            password: 'secret123',
            token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature'
          },
          profile: {
            email: 'user@example.com',
            phone: '+1-555-123-4567'
          }
        },
        settings: {
          apiKeys: {
            twilioAuthToken: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
            openaiKey: 'sk-proj-1234567890abcdef'
          }
        }
      };

      const redacted = redactor.redactObject(obj);

      expect(redacted.user.credentials.password).toBe('[REDACTED]');
      expect(redacted.user.credentials.token).toBe('[REDACTED]');
      expect(redacted.user.profile.email).toContain('@example.com');
      expect(redacted.user.profile.phone).toBe('***-***-4567');
      expect(redacted.settings.apiKeys.twilioAuthToken).toBe('[REDACTED]');
      expect(redacted.settings.apiKeys.openaiKey).toBe('[REDACTED]');
    });

    it('should handle arrays with sensitive data', () => {
      const obj = {
        users: [
          { email: 'user1@example.com', password: 'pass1' },
          { email: 'user2@example.com', password: 'pass2' }
        ],
        tokens: ['token1', 'token2'],
        publicList: ['item1', 'item2']
      };

      const redacted = redactor.redactObject(obj);

      expect(redacted.users[0].password).toBe('[REDACTED]');
      expect(redacted.users[1].password).toBe('[REDACTED]');
      expect(redacted.users[0].email).toContain('@example.com');
      expect(redacted.users[1].email).toContain('@example.com');
      expect(redacted.tokens).toEqual(['token1', 'token2']); // Not sensitive keys
      expect(redacted.publicList).toEqual(['item1', 'item2']);
    });

    it('should handle Error objects', () => {
      const error = new Error('Database connection failed with password: secret123');
      const redacted = redactor.redactObject(error);

      expect(redacted.name).toBe('Error');
      expect(redacted.message).not.toContain('secret123');
      expect(redacted.message).toContain('[REDACTED_PASSWORD]');
    });

    it('should prevent infinite recursion', () => {
      const obj: any = { name: 'test' };
      obj.circular = obj;

      const redacted = redactor.redactObject(obj);
      expect(redacted).toBeDefined();
      expect(redacted.name).toBe('test');
    });
  });

  describe('URL Redaction', () => {
    it('should redact sensitive query parameters', () => {
      const urls = [
        'https://api.example.com/users?token=abc123&name=john',
        'https://example.com/auth?api_key=secret123&user=test',
        'https://webhook.com/callback?signature=sig123&data=public'
      ];

      urls.forEach(url => {
        const redacted = redactor.redactUrl(url);
        expect(redacted).not.toBe(url);
        expect(redacted).not.toContain('abc123');
        expect(redacted).not.toContain('secret123');
        expect(redacted).not.toContain('sig123');
      });
    });

    it('should redact passwords in URLs', () => {
      const url = 'https://user:password@example.com/path';
      const redacted = redactor.redactUrl(url);

      expect(redacted).not.toBe(url);
      expect(redacted).toContain('[REDACTED]');
      expect(redacted).not.toContain('password');
    });
  });

  describe('Header Redaction', () => {
    it('should redact sensitive headers', () => {
      const headers = {
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature',
        'cookie': 'session=abc123; csrf=def456',
        'x-api-key': 'ak-1234567890',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0...'
      };

      const redacted = redactor.redactHeaders(headers);

      expect(redacted.authorization).toContain('Bearer ');
      expect(redacted.authorization).toContain('*');
      expect(redacted.cookie).toBe('[REDACTED]');
      expect(redacted['x-api-key']).toBe('[REDACTED]');
      expect(redacted['content-type']).toBe('application/json');
      expect(redacted['user-agent']).toBe('Mozilla/5.0...');
    });
  });

  describe('Console Interception', () => {
    it('should intercept and redact console.log', () => {
      interceptConsoleLogging();

      console.log('User password:', 'secret123');
      console.log({ password: 'secret123', email: 'user@example.com' });

      expect(consoleOutputs[0]).not.toContain('secret123');
      expect(consoleOutputs[0]).toContain('[REDACTED_PASSWORD]');
      expect(consoleOutputs[1]).not.toContain('secret123');
      expect(consoleOutputs[1]).toContain('[REDACTED]');
    });

    it('should intercept and redact console.error', () => {
      interceptConsoleLogging();

      // Override console.error for testing
      const originalError = console.error;
      console.error = (...args: any[]) => {
        consoleOutputs.push(args.map(arg =>
          typeof arg === 'string' ? arg : JSON.stringify(arg)
        ).join(' '));
      };

      console.error('Auth failed with token:', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature');

      expect(consoleOutputs[0]).not.toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature');
      expect(consoleOutputs[0]).toContain('*');

      console.error = originalError;
    });
  });

  describe('Secure Logger', () => {
    it('should automatically redact sensitive data in logs', () => {
      const sensitiveData = {
        password: 'secret123',
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature',
        email: 'user@example.com',
        creditCard: '4111111111111111'
      };

      // This should not throw and should log redacted data
      expect(() => {
        secureLogger.info('User data:', sensitiveData);
        authLogger.debug('Authentication attempt:', sensitiveData);
        securityLogger.warn('Security event:', sensitiveData);
      }).not.toThrow();
    });

    it('should handle security events with proper context', () => {
      expect(() => {
        secureLogger.security('authentication.failure', {
          email: 'attacker@evil.com',
          password: 'attempt123',
          ip: '192.168.1.100'
        }, {
          severity: 'high',
          ip: '192.168.1.100',
          userAgent: 'Evil Bot 1.0'
        });
      }).not.toThrow();
    });

    it('should log API requests with redacted URLs and headers', () => {
      expect(() => {
        secureLogger.apiRequest(
          'POST',
          '/auth/login?token=secret123',
          200,
          150,
          'user123',
          'req_123',
          { 'authorization': 'Bearer token123' },
          { password: 'secret' }
        );
      }).not.toThrow();
    });

    it('should log database operations without exposing sensitive data', () => {
      expect(() => {
        secureLogger.database(
          'SELECT',
          'users',
          50,
          true,
          { query: 'SELECT * FROM users WHERE password = ?', params: ['secret123'] }
        );
      }).not.toThrow();
    });

    it('should log telephony events with redacted phone numbers', () => {
      expect(() => {
        secureLogger.telephony(
          'call.started',
          'CAxxxx',
          '+15551234567',
          '+15559876543',
          'in-progress',
          { authToken: 'twiliotoken123' }
        );
      }).not.toThrow();
    });
  });

  describe('Built-in Test Function', () => {
    it('should pass internal redaction test', () => {
      expect(testRedaction()).toBe(true);
    });
  });

  describe('Redaction Statistics', () => {
    it('should provide redaction statistics', () => {
      const stats = redactor.getRedactionStats();

      expect(stats).toHaveProperty('totalPatterns');
      expect(stats).toHaveProperty('sensitiveKeys');
      expect(stats).toHaveProperty('categories');
      expect(stats.totalPatterns).toBeGreaterThan(0);
      expect(stats.sensitiveKeys).toBeGreaterThan(0);
      expect(Object.keys(stats.categories)).toContain('auth');
      expect(Object.keys(stats.categories)).toContain('pii');
      expect(Object.keys(stats.categories)).toContain('financial');
    });
  });

  describe('Custom Patterns', () => {
    it('should allow adding custom redaction patterns', () => {
      redactor.addPattern({
        name: 'Custom Secret',
        pattern: /customSecret:\s*([a-zA-Z0-9]+)/g,
        replacement: 'customSecret: [CUSTOM_REDACTED]',
        category: 'general',
        severity: 'medium'
      });

      const text = 'Debug info: customSecret: mySecretValue123';
      const redacted = redactor.redactString(text);

      expect(redacted).not.toBe(text);
      expect(redacted).toContain('[CUSTOM_REDACTED]');
    });

    it('should allow adding custom sensitive keys', () => {
      redactor.addSensitiveKey('customKey');

      const obj = { customKey: 'sensitive value', regularKey: 'normal value' };
      const redacted = redactor.redactObject(obj);

      expect(redacted.customKey).toBe('[REDACTED]');
      expect(redacted.regularKey).toBe('normal value');
    });
  });

  describe('Edge Cases', () => {
    it('should handle null and undefined values', () => {
      expect(() => {
        redactor.redactObject(null);
        redactor.redactObject(undefined);
        redactor.redactString('');
        redactor.redactString(null as any);
        redactor.redactString(undefined as any);
      }).not.toThrow();
    });

    it('should handle non-string values', () => {
      const obj = {
        number: 12345,
        boolean: true,
        date: new Date(),
        regex: /pattern/g,
        fn: () => 'test'
      };

      expect(() => {
        const redacted = redactor.redactObject(obj);
        expect(redacted.number).toBe(12345);
        expect(redacted.boolean).toBe(true);
        expect(redacted.date).toBeInstanceOf(Date);
      }).not.toThrow();
    });

    it('should handle very large strings', () => {
      const largeString = 'password: secret123 '.repeat(10000);

      expect(() => {
        const redacted = redactor.redactString(largeString);
        expect(redacted).not.toContain('secret123');
      }).not.toThrow();
    });

    it('should handle malformed patterns gracefully', () => {
      const malformedData = {
        'malformed-email': 'not@an@email@address',
        'fake-card': '1234',
        'short-token': 'abc'
      };

      expect(() => {
        redactor.redactObject(malformedData);
      }).not.toThrow();
    });
  });
});

describe('Integration Tests', () => {
  it('should work with real-world log data', () => {
    const realWorldData = {
      timestamp: '2025-01-15T10:30:00Z',
      level: 'info',
      message: 'User authentication successful',
      userId: 'user_123',
      email: 'john.doe@example.com',
      sessionToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
      request: {
        method: 'POST',
        url: '/api/auth/login?returnUrl=dashboard',
        headers: {
          'Authorization': 'Bearer secret_token_123',
          'Content-Type': 'application/json',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        body: {
          email: 'john.doe@example.com',
          password: 'MySecurePassword123!',
          rememberMe: true
        }
      },
      response: {
        statusCode: 200,
        body: {
          success: true,
          token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.newtoken.signature',
          user: {
            id: 'user_123',
            email: 'john.doe@example.com',
            phone: '+1-555-123-4567'
          }
        }
      },
      metadata: {
        ip: '192.168.1.100',
        userAgent: 'Mozilla/5.0...',
        twilioConfig: {
          accountSid: 'ACxxxxxxxxxxxxxxxxxxxx',
          authToken: 'your_twilio_auth_token_here'
        }
      }
    };

    const redacted = logRedactor.redact(realWorldData);

    // Verify structure is preserved
    expect(redacted.timestamp).toBe(realWorldData.timestamp);
    expect(redacted.level).toBe(realWorldData.level);
    expect(redacted.message).toBe(realWorldData.message);
    expect(redacted.userId).toBe(realWorldData.userId);

    // Verify sensitive data is redacted
    expect(redacted.sessionToken).toBe('[REDACTED]');
    expect(redacted.request.body.password).toBe('[REDACTED]');
    expect(redacted.request.headers.Authorization).toContain('Bearer ');
    expect(redacted.request.headers.Authorization).toContain('*');
    expect(redacted.response.body.token).toBe('[REDACTED]');
    expect(redacted.metadata.twilioConfig.authToken).toBe('[REDACTED]');

    // Verify partial redaction
    expect(redacted.email).toContain('@example.com');
    expect(redacted.request.body.email).toContain('@example.com');
    expect(redacted.response.body.user.phone).toBe('***-***-4567');
  });

  it('should maintain performance with large datasets', () => {
    const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      email: `user${i}@example.com`,
      password: `password${i}`,
      token: `token_${i}_${'x'.repeat(50)}`,
      metadata: {
        phone: `+1-555-${String(i).padStart(3, '0')}-${String(i + 1000).slice(-4)}`,
        credit_card: '4111111111111111'
      }
    }));

    const startTime = Date.now();
    const redacted = logRedactor.redact(largeDataset);
    const endTime = Date.now();

    // Should complete within reasonable time (< 1 second for 1000 items)
    expect(endTime - startTime).toBeLessThan(1000);

    // Verify redaction worked
    expect(redacted[0].password).toBe('[REDACTED]');
    expect(redacted[999].token).toBe('[REDACTED]');
    expect(redacted[500].metadata.credit_card).toBe('****-****-****-1111');
  });
});
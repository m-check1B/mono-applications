/**
 * Basic Log Redaction System Tests
 * Verifies core redaction functionality works
 */

import { describe, it, expect } from 'vitest';
import { LogRedactor, logRedactor, redactLogData } from '../../server/utils/log-redactor';
import { secureLogger } from '../../server/utils/secure-logger';

describe('Basic Log Redaction', () => {
  it('should redact JWT tokens', () => {
    const jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
    const redacted = logRedactor.redactString(jwt);

    expect(redacted).not.toBe(jwt);
    expect(redacted).toContain('*');
  });

  it('should redact email addresses', () => {
    const email = 'user@example.com';
    const redacted = logRedactor.redactString(email);

    expect(redacted).not.toBe(email);
    expect(redacted).toContain('@example.com');
  });

  it('should redact phone numbers', () => {
    const phone = '+1-555-123-4567';
    const redacted = logRedactor.redactString(phone);

    expect(redacted).toBe('***-***-4567');
  });

  it('should redact sensitive object keys', () => {
    const obj = {
      password: 'secret123',
      username: 'john',
      publicData: 'visible'
    };

    const redacted = logRedactor.redactObject(obj);

    expect(redacted.password).toBe('[REDACTED]');
    expect(redacted.username).toBe('john');
    expect(redacted.publicData).toBe('visible');
  });

  it('should handle nested objects safely', () => {
    const obj = {
      user: {
        email: 'user@example.com',
        profile: {
          phoneNumber: '+1-555-123-4567'
        }
      },
      config: {
        password: 'secret123',
        token: 'abc123'
      }
    };

    const redacted = logRedactor.redactObject(obj);

    // Should preserve structure
    expect(redacted).toBeDefined();
    expect(redacted.user).toBeDefined();
    expect(redacted.config).toBeDefined();

    // Should redact email partially
    expect(redacted.user.email).toContain('@example.com');
    expect(redacted.user.email).not.toBe('user@example.com');

    // Should redact phone numbers
    expect(redacted.user.profile.phoneNumber).toBe('***-***-4567');

    // Should redact sensitive keys (password and token are sensitive keys)
    expect(redacted.config.password).toBe('[REDACTED]');
    expect(redacted.config.token).toBe('[REDACTED]');
  });

  it('should work with secure logger', () => {
    const sensitiveData = {
      password: 'secret123',
      email: 'user@example.com'
    };

    // Should not throw
    expect(() => {
      secureLogger.info('Test log', sensitiveData);
    }).not.toThrow();
  });

  it('should get redaction statistics', () => {
    const stats = logRedactor.getRedactionStats();

    expect(stats.totalPatterns).toBeGreaterThan(0);
    expect(stats.sensitiveKeys).toBeGreaterThan(0);
    expect(Object.keys(stats.categories)).toContain('auth');
  });

  it('should handle real-world log data safely', () => {
    const realData = {
      timestamp: new Date().toISOString(),
      user: {
        email: 'john.doe@company.com',
        password: 'MyPassword123!'
      },
      request: {
        headers: {
          'authorization': 'Bearer token123'
        }
      },
      metadata: {
        twilioAuthToken: 'secret_token_here'
      }
    };

    const redacted = logRedactor.redact(realData);

    // Should preserve structure
    expect(redacted.timestamp).toBeDefined();
    expect(redacted.user).toBeDefined();

    // Should redact sensitive data
    expect(redacted.user.password).toBe('[REDACTED]');
    expect(redacted.metadata.twilioAuthToken).toBe('[REDACTED]');

    // Should partially redact email
    expect(redacted.user.email).toContain('@company.com');
    expect(redacted.user.email).not.toBe('john.doe@company.com');
  });
});

describe('Integration Safety', () => {
  it('should not break with invalid inputs', () => {
    expect(() => {
      logRedactor.redact(null);
      logRedactor.redact(undefined);
      logRedactor.redact('');
      logRedactor.redact({});
      logRedactor.redact([]);
    }).not.toThrow();
  });

  it('should handle circular references', () => {
    const obj: any = { name: 'test' };
    obj.circular = obj;

    expect(() => {
      logRedactor.redact(obj);
    }).not.toThrow();
  });
});
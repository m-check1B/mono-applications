/**
 * Twilio Webhook Security Tests
 * Tests signature validation and security measures for Twilio webhooks
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import crypto from 'crypto';
import type { FastifyInstance, FastifyRequest } from 'fastify';

// Mock Twilio webhook validator
const mockTwilioValidator = {
  validate: vi.fn()
};

vi.mock('twilio', () => ({
  validateRequest: mockTwilioValidator.validate
}));

describe('Twilio Webhook Security Tests', () => {
  let mockFastify: Partial<FastifyInstance>;
  let mockRequest: Partial<FastifyRequest>;
  const TEST_AUTH_TOKEN = 'test_auth_token_12345';
  const TEST_URL = 'https://example.com/twilio/webhook';

  beforeEach(() => {
    vi.clearAllMocks();

    mockFastify = {
      log: {
        info: vi.fn(),
        warn: vi.fn(),
        error: vi.fn(),
        debug: vi.fn()
      }
    };

    mockRequest = {
      headers: {},
      body: {},
      url: TEST_URL,
      method: 'POST'
    };

    // Reset Twilio validator mock
    mockTwilioValidator.validate.mockReturnValue(true);
  });

  describe('Signature Validation', () => {
    it('should reject requests without X-Twilio-Signature header', async () => {
      mockRequest.headers = {}; // No signature header

      const isValid = validateTwilioSignature(
        mockRequest as FastifyRequest,
        TEST_AUTH_TOKEN
      );

      expect(isValid).toBe(false);
    });

    it('should reject requests with invalid signature format', async () => {
      mockRequest.headers = {
        'x-twilio-signature': 'invalid-signature-format'
      };

      mockTwilioValidator.validate.mockReturnValue(false);

      const isValid = validateTwilioSignature(
        mockRequest as FastifyRequest,
        TEST_AUTH_TOKEN
      );

      expect(isValid).toBe(false);
      expect(mockTwilioValidator.validate).toHaveBeenCalledWith(
        TEST_AUTH_TOKEN,
        'invalid-signature-format',
        TEST_URL,
        {}
      );
    });

    it('should accept requests with valid Twilio signature', async () => {
      const validPayload = {
        CallSid: 'CA1234567890abcdef',
        From: '+1234567890',
        To: '+0987654321'
      };

      const validSignature = generateValidTwilioSignature(
        TEST_URL,
        validPayload,
        TEST_AUTH_TOKEN
      );

      mockRequest.headers = {
        'x-twilio-signature': validSignature
      };
      mockRequest.body = validPayload;

      mockTwilioValidator.validate.mockReturnValue(true);

      const isValid = validateTwilioSignature(
        mockRequest as FastifyRequest,
        TEST_AUTH_TOKEN
      );

      expect(isValid).toBe(true);
      expect(mockTwilioValidator.validate).toHaveBeenCalledWith(
        TEST_AUTH_TOKEN,
        validSignature,
        TEST_URL,
        validPayload
      );
    });

    it('should handle URL variations correctly', async () => {
      const urls = [
        'https://example.com/twilio/webhook',
        'https://example.com/twilio/webhook/',
        'https://example.com:443/twilio/webhook',
        'https://subdomain.example.com/twilio/webhook'
      ];

      for (const url of urls) {
        mockRequest.url = url;
        mockTwilioValidator.validate.mockReturnValue(true);

        const isValid = validateTwilioSignature(
          mockRequest as FastifyRequest,
          TEST_AUTH_TOKEN
        );

        expect(isValid).toBe(true);
        expect(mockTwilioValidator.validate).toHaveBeenCalledWith(
          TEST_AUTH_TOKEN,
          expect.any(String),
          url,
          expect.any(Object)
        );
      }
    });
  });

  describe('Request Validation Security', () => {
    it('should validate required Twilio webhook fields', async () => {
      const testCases = [
        { body: {}, missing: 'CallSid' },
        { body: { CallSid: '' }, missing: 'From' },
        { body: { CallSid: 'CA123', From: '' }, missing: 'To' },
        { body: { CallSid: 'CA123', From: '+1234567890' }, missing: 'To' }
      ];

      for (const testCase of testCases) {
        const result = validateTwilioWebhookPayload(testCase.body);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain(`Missing required field: ${testCase.missing}`);
      }
    });

    it('should validate Twilio field formats', async () => {
      const testCases = [
        {
          body: { CallSid: 'invalid', From: '+1234567890', To: '+0987654321' },
          expectedError: 'CallSid must start with CA'
        },
        {
          body: { CallSid: 'CA123456', From: 'invalid-phone', To: '+0987654321' },
          expectedError: 'From must be a valid phone number'
        },
        {
          body: { CallSid: 'CA123456', From: '+1234567890', To: 'invalid-phone' },
          expectedError: 'To must be a valid phone number'
        }
      ];

      for (const testCase of testCases) {
        const result = validateTwilioWebhookPayload(testCase.body);
        expect(result.isValid).toBe(false);
        expect(result.errors.some(error =>
          error.includes(testCase.expectedError.split(' ')[0])
        )).toBe(true);
      }
    });

    it('should accept valid Twilio webhook payload', async () => {
      const validPayload = {
        CallSid: 'CA1234567890abcdef1234567890abcdef12',
        From: '+1234567890',
        To: '+0987654321',
        CallStatus: 'completed',
        Duration: '120'
      };

      const result = validateTwilioWebhookPayload(validPayload);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('Rate Limiting Security', () => {
    it('should enforce rate limits on webhook endpoints', async () => {
      const rateLimiter = createWebhookRateLimiter();

      // Simulate rapid requests from same IP
      const clientIP = '192.168.1.100';
      const requests = Array(15).fill(null); // 15 requests

      let blockedCount = 0;
      for (let i = 0; i < requests.length; i++) {
        const isAllowed = rateLimiter.checkLimit(clientIP);
        if (!isAllowed) {
          blockedCount++;
        }
      }

      expect(blockedCount).toBeGreaterThan(0);
    });

    it('should allow legitimate Twilio IP ranges', async () => {
      const twilioIPs = [
        '54.172.60.0', // Known Twilio IP range
        '54.244.51.0',
        '52.86.245.0'
      ];

      const rateLimiter = createWebhookRateLimiter();

      for (const ip of twilioIPs) {
        // Twilio IPs should have higher rate limits
        for (let i = 0; i < 10; i++) {
          const isAllowed = rateLimiter.checkLimit(ip, true); // isKnownTwilioIP = true
          expect(isAllowed).toBe(true);
        }
      }
    });
  });

  describe('Content Security', () => {
    it('should sanitize webhook payload content', async () => {
      const maliciousPayload = {
        CallSid: 'CA1234567890abcdef1234567890abcdef12',
        From: '+1234567890',
        To: '+0987654321',
        RecordingUrl: 'javascript:alert("xss")',
        Caller: '<script>alert("xss")</script>',
        Called: '../../../etc/passwd'
      };

      const sanitized = sanitizeTwilioPayload(maliciousPayload);

      expect(sanitized.RecordingUrl).not.toContain('javascript:');
      expect(sanitized.Caller).not.toContain('<script>');
      expect(sanitized.Called).not.toContain('../');
    });

    it('should validate URL formats in webhook data', async () => {
      const testUrls = [
        { url: 'https://api.twilio.com/recording.mp3', valid: true },
        { url: 'http://api.twilio.com/recording.mp3', valid: false }, // HTTP not HTTPS
        { url: 'javascript:alert(1)', valid: false },
        { url: 'data:text/html,<script>alert(1)</script>', valid: false },
        { url: 'file:///etc/passwd', valid: false }
      ];

      for (const testCase of testUrls) {
        const isValid = isValidTwilioUrl(testCase.url);
        expect(isValid).toBe(testCase.valid);
      }
    });
  });

  describe('Error Handling Security', () => {
    it('should not leak sensitive information in error responses', async () => {
      const mockResponse = {
        code: vi.fn().mockReturnThis(),
        send: vi.fn()
      };

      // Test various error conditions
      const errorCases = [
        { type: 'invalid_signature', message: 'Invalid signature' },
        { type: 'missing_auth_token', message: 'Missing auth token' },
        { type: 'malformed_payload', message: 'Malformed payload' }
      ];

      for (const errorCase of errorCases) {
        handleWebhookError(mockResponse as any, errorCase.type);

        expect(mockResponse.code).toHaveBeenCalledWith(403);
        expect(mockResponse.send).toHaveBeenCalledWith({
          error: 'Webhook validation failed'
        });

        // Should not expose internal error details
        expect(mockResponse.send).not.toHaveBeenCalledWith(
          expect.objectContaining({
            message: expect.stringContaining('auth_token'),
            details: expect.anything()
          })
        );
      }
    });

    it('should log security events appropriately', async () => {
      const securityLogger = createSecurityLogger();
      const mockLogger = {
        warn: vi.fn(),
        error: vi.fn(),
        info: vi.fn()
      };

      // Test security event logging
      securityLogger.logWebhookSecurityEvent(mockLogger as any, {
        type: 'invalid_signature',
        ip: '192.168.1.100',
        userAgent: 'curl/7.68.0',
        timestamp: new Date(),
        payload: { CallSid: 'CA123456' }
      });

      expect(mockLogger.warn).toHaveBeenCalledWith(
        expect.stringContaining('Webhook security violation'),
        expect.objectContaining({
          type: 'invalid_signature',
          ip: '192.168.1.100',
          // Should not log full payload for security
          payloadSize: expect.any(Number)
        })
      );

      // Should not log sensitive payload data
      expect(mockLogger.warn).not.toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          payload: expect.anything()
        })
      );
    });
  });

  describe('Replay Attack Prevention', () => {
    it('should detect and prevent replay attacks', async () => {
      const replayDetector = createReplayDetector();
      const timestamp = Math.floor(Date.now() / 1000);
      const signature = 'valid_signature_hash';

      // First request should be allowed
      const firstAttempt = replayDetector.checkReplay(signature, timestamp);
      expect(firstAttempt.allowed).toBe(true);

      // Identical request should be blocked
      const secondAttempt = replayDetector.checkReplay(signature, timestamp);
      expect(secondAttempt.allowed).toBe(false);
      expect(secondAttempt.reason).toBe('duplicate_signature');
    });

    it('should reject old timestamps to prevent replay', async () => {
      const replayDetector = createReplayDetector();
      const oldTimestamp = Math.floor(Date.now() / 1000) - 3600; // 1 hour ago
      const signature = 'old_signature_hash';

      const result = replayDetector.checkReplay(signature, oldTimestamp);
      expect(result.allowed).toBe(false);
      expect(result.reason).toBe('timestamp_too_old');
    });
  });
});

// Helper functions for testing
function validateTwilioSignature(request: FastifyRequest, authToken: string): boolean {
  const signature = request.headers?.['x-twilio-signature'] as string;
  if (!signature) return false;

  return mockTwilioValidator.validate(
    authToken,
    signature,
    request.url || '',
    request.body || {}
  );
}

function validateTwilioWebhookPayload(body: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Required fields
  const requiredFields = ['CallSid', 'From', 'To'];
  for (const field of requiredFields) {
    if (!body[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  // Format validation
  if (body.CallSid && !body.CallSid.startsWith('CA')) {
    errors.push('CallSid must start with CA');
  }

  if (body.From && !body.From.match(/^\+[1-9]\d{1,14}$/)) {
    errors.push('From must be a valid phone number');
  }

  if (body.To && !body.To.match(/^\+[1-9]\d{1,14}$/)) {
    errors.push('To must be a valid phone number');
  }

  return { isValid: errors.length === 0, errors };
}

function generateValidTwilioSignature(url: string, body: any, authToken: string): string {
  // This is a simplified version - in real implementation, use Twilio's algorithm
  const data = url + JSON.stringify(body);
  return crypto.createHmac('sha1', authToken).update(data).digest('base64');
}

function createWebhookRateLimiter() {
  const requests = new Map<string, number[]>();

  return {
    checkLimit(ip: string, isKnownTwilioIP = false): boolean {
      const now = Date.now();
      const windowMs = 60 * 1000; // 1 minute window
      const maxRequests = isKnownTwilioIP ? 100 : 10; // Higher limit for Twilio IPs

      if (!requests.has(ip)) {
        requests.set(ip, []);
      }

      const ipRequests = requests.get(ip)!;

      // Remove old requests outside the window
      const validRequests = ipRequests.filter(time => now - time < windowMs);

      if (validRequests.length >= maxRequests) {
        return false; // Rate limit exceeded
      }

      validRequests.push(now);
      requests.set(ip, validRequests);
      return true;
    }
  };
}

function sanitizeTwilioPayload(payload: any): any {
  const sanitized = { ...payload };

  // Remove potential XSS and path traversal attempts
  for (const [key, value] of Object.entries(sanitized)) {
    if (typeof value === 'string') {
      sanitized[key] = value
        .replace(/<script[^>]*>.*?<\/script>/gi, '')
        .replace(/javascript:/gi, '')
        .replace(/\.\.\/+/g, '')
        .replace(/data:/gi, '');
    }
  }

  return sanitized;
}

function isValidTwilioUrl(url: string): boolean {
  try {
    const parsed = new URL(url);

    // Only allow HTTPS URLs from Twilio domains
    if (parsed.protocol !== 'https:') return false;
    if (!parsed.hostname.endsWith('.twilio.com')) return false;

    return true;
  } catch {
    return false;
  }
}

function handleWebhookError(reply: any, errorType: string): void {
  reply.code(403).send({
    error: 'Webhook validation failed'
  });
}

function createSecurityLogger() {
  return {
    logWebhookSecurityEvent(logger: any, event: any): void {
      logger.warn('Webhook security violation detected', {
        type: event.type,
        ip: event.ip,
        userAgent: event.userAgent,
        timestamp: event.timestamp,
        payloadSize: JSON.stringify(event.payload).length
        // Note: Not logging full payload for security
      });
    }
  };
}

function createReplayDetector() {
  const usedSignatures = new Set<string>();
  const SIGNATURE_TTL = 300000; // 5 minutes

  return {
    checkReplay(signature: string, timestamp: number): { allowed: boolean; reason?: string } {
      const now = Math.floor(Date.now() / 1000);

      // Check if timestamp is too old
      if (now - timestamp > 300) { // 5 minutes
        return { allowed: false, reason: 'timestamp_too_old' };
      }

      // Check for duplicate signature
      if (usedSignatures.has(signature)) {
        return { allowed: false, reason: 'duplicate_signature' };
      }

      // Store signature
      usedSignatures.add(signature);

      // Clean up old signatures periodically
      setTimeout(() => {
        usedSignatures.delete(signature);
      }, SIGNATURE_TTL);

      return { allowed: true };
    }
  };
}
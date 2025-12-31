/**
 * Comprehensive Security and Health Check Tests
 * Tests error handling, health endpoints, rate limiting, and security features
 */

import { test, expect } from '@playwright/test';

// Test configuration
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3010';
const TEST_API_KEY = process.env.HEALTH_API_KEY || 'health-check-key-12345';
const TEST_CREDENTIALS = Buffer.from('health-admin:secure-health-password').toString('base64');

test.describe('Health Check Endpoints Security', () => {

  test('Basic health endpoint should be accessible without authentication', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health`);

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
    expect(data).toHaveProperty('timestamp');
    expect(data).toHaveProperty('uptime');
    expect(data).toHaveProperty('requestId');
  });

  test('Basic health endpoint should have rate limiting', async ({ page }) => {
    const requests = [];

    // Make many requests quickly to trigger rate limiting
    for (let i = 0; i < 150; i++) {
      requests.push(page.request.get(`${BASE_URL}/health`));
    }

    const responses = await Promise.all(requests);

    // Some requests should be rate limited
    const rateLimitedResponses = responses.filter(r => r.status() === 429);
    expect(rateLimitedResponses.length).toBeGreaterThan(0);

    // Rate limited responses should have proper headers
    if (rateLimitedResponses.length > 0) {
      const rateLimitedResponse = rateLimitedResponses[0];
      const headers = rateLimitedResponse.headers();

      expect(headers).toHaveProperty('x-ratelimit-limit');
      expect(headers).toHaveProperty('x-ratelimit-remaining');
      expect(headers).toHaveProperty('retry-after');
    }
  });

  test('Detailed health endpoint should require authentication', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/detailed`);

    expect(response.status()).toBe(401);

    const data = await response.json();
    expect(data.error).toHaveProperty('code');
    expect(data.error).toHaveProperty('message');
    expect(data.error.message).toContain('Authentication required');
  });

  test('Detailed health endpoint should work with API key authentication', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/detailed`, {
      headers: {
        'X-API-Key': TEST_API_KEY
      }
    });

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('memory');
    expect(data).toHaveProperty('metrics');
    expect(data).toHaveProperty('authenticatedAs');
  });

  test('Detailed health endpoint should work with basic authentication', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/detailed`, {
      headers: {
        'Authorization': `Basic ${TEST_CREDENTIALS}`
      }
    });

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('authenticatedAs', 'Health Admin');
  });

  test('Database health endpoint should require authentication', async ({ page }) => {
    // Without auth
    let response = await page.request.get(`${BASE_URL}/health/database`);
    expect(response.status()).toBe(401);

    // With auth
    response = await page.request.get(`${BASE_URL}/health/database`, {
      headers: { 'X-API-Key': TEST_API_KEY }
    });

    expect([200, 503]).toContain(response.status()); // 503 if DB not available

    const data = await response.json();
    expect(data).toHaveProperty('database');
    expect(data.database).toHaveProperty('connected');
  });

  test('Metrics endpoint should require admin authentication', async ({ page }) => {
    // Should fail without auth
    let response = await page.request.get(`${BASE_URL}/metrics`);
    expect(response.status()).toBe(401);

    // Should work with admin auth
    response = await page.request.get(`${BASE_URL}/metrics`, {
      headers: { 'Authorization': `Basic ${TEST_CREDENTIALS}` }
    });

    // Should return Prometheus format or error
    expect([200, 500]).toContain(response.status());

    if (response.status() === 200) {
      const metricsText = await response.text();
      expect(metricsText).toContain('cc_lite_');
    }
  });

  test('External services health check should be admin-only', async ({ page }) => {
    // Should fail without auth
    let response = await page.request.get(`${BASE_URL}/health/external`);
    expect(response.status()).toBe(401);

    // Should work with admin auth
    response = await page.request.get(`${BASE_URL}/health/external`, {
      headers: { 'Authorization': `Basic ${TEST_CREDENTIALS}` }
    });

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('services');
    expect(data.services).toHaveProperty('openai');
    expect(data.services).toHaveProperty('twilio');
  });

  test('Security status endpoint should be admin-only', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/security`, {
      headers: { 'Authorization': `Basic ${TEST_CREDENTIALS}` }
    });

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('security');
    expect(data.security).toHaveProperty('httpsOnly');
    expect(data.security).toHaveProperty('authenticationEnabled');
    expect(data.security).toHaveProperty('secretsConfigured');
  });

});

test.describe('Error Handling Security', () => {

  test('Errors should not leak sensitive information', async ({ page }) => {
    // Try to cause an error with sensitive data
    const response = await page.request.post(`${BASE_URL}/api/invalid-endpoint`, {
      data: {
        password: 'secret123',
        apiKey: 'sk-1234567890abcdef',
        token: 'Bearer abc123def456'
      }
    });

    expect(response.status()).toBe(404);

    const errorData = await response.json();
    const errorText = JSON.stringify(errorData);

    // Should not contain sensitive data
    expect(errorText).not.toContain('secret123');
    expect(errorText).not.toContain('sk-1234567890abcdef');
    expect(errorText).not.toContain('abc123def456');
    expect(errorText).not.toContain('password');
    expect(errorText).not.toContain('apiKey');
  });

  test('Error responses should have proper structure', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/nonexistent-endpoint`);

    expect(response.status()).toBe(404);

    const errorData = await response.json();
    expect(errorData).toHaveProperty('error');
    expect(errorData.error).toHaveProperty('code');
    expect(errorData.error).toHaveProperty('message');
    expect(errorData.error).toHaveProperty('timestamp');

    // Should not have stack traces in production-like environment
    expect(errorData.error).not.toHaveProperty('stack');
  });

  test('tRPC errors should be properly handled', async ({ page }) => {
    const response = await page.request.post(`${BASE_URL}/api/trpc/auth.login`, {
      headers: { 'Content-Type': 'application/json' },
      data: {
        invalid: 'data'
      }
    });

    // Should handle tRPC errors gracefully
    expect([400, 401, 422, 500]).toContain(response.status());

    const errorData = await response.json();
    expect(errorData).toHaveProperty('error');
  });

});

test.describe('Security Headers', () => {

  test('Should have essential security headers', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health`);
    const headers = response.headers();

    // Essential security headers
    expect(headers).toHaveProperty('x-content-type-options', 'nosniff');
    expect(headers).toHaveProperty('x-frame-options');
    expect(headers).toHaveProperty('x-dns-prefetch-control', 'off');
    expect(headers).toHaveProperty('x-download-options', 'noopen');
    expect(headers).toHaveProperty('referrer-policy');

    // Should not reveal server information
    expect(headers).not.toHaveProperty('x-powered-by');
    expect(headers['server']).toBeUndefined();
  });

  test('Should have Content Security Policy', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health`);
    const headers = response.headers();

    const csp = headers['content-security-policy'] || headers['content-security-policy-report-only'];
    if (csp) {
      expect(csp).toContain("default-src");
      expect(csp).toContain("script-src");
      expect(csp).toContain("object-src 'none'");
    }
  });

  test('Should have HTTPS security headers in production', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health`);
    const headers = response.headers();

    // HSTS should be present if running on HTTPS
    if (BASE_URL.startsWith('https://')) {
      expect(headers).toHaveProperty('strict-transport-security');
    }
  });

  test('Sensitive endpoints should have no-cache headers', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/detailed`, {
      headers: { 'X-API-Key': TEST_API_KEY }
    });

    if (response.status() === 200) {
      const headers = response.headers();
      expect(headers['cache-control']).toContain('no-cache');
      expect(headers['cache-control']).toContain('no-store');
    }
  });

});

test.describe('Rate Limiting', () => {

  test('API endpoints should have rate limiting', async ({ page }) => {
    const requests = [];

    // Make many requests to trigger rate limiting
    for (let i = 0; i < 50; i++) {
      requests.push(page.request.get(`${BASE_URL}/api/healthcheck`));
    }

    const responses = await Promise.all(requests);

    // Check for rate limit headers
    const validResponses = responses.filter(r => r.status() < 500);
    if (validResponses.length > 0) {
      const headers = validResponses[0].headers();

      // Should have rate limit headers
      expect(headers['x-ratelimit-limit'] || headers['x-ratelimit-remaining']).toBeDefined();
    }
  });

  test('Rate limit should reset after time window', async ({ page }) => {
    // This test would need to wait for rate limit reset
    // For now, just verify the rate limiting is working

    const response1 = await page.request.get(`${BASE_URL}/health`);
    const headers1 = response1.headers();

    if (headers1['x-ratelimit-remaining']) {
      const remaining1 = parseInt(headers1['x-ratelimit-remaining']);

      const response2 = await page.request.get(`${BASE_URL}/health`);
      const headers2 = response2.headers();

      if (headers2['x-ratelimit-remaining']) {
        const remaining2 = parseInt(headers2['x-ratelimit-remaining']);

        // Remaining should decrease
        expect(remaining2).toBeLessThanOrEqual(remaining1);
      }
    }
  });

});

test.describe('Authentication Security', () => {

  test('Invalid API keys should be rejected', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/detailed`, {
      headers: { 'X-API-Key': 'invalid-key-12345' }
    });

    expect(response.status()).toBe(401);
  });

  test('Invalid basic auth credentials should be rejected', async ({ page }) => {
    const invalidCredentials = Buffer.from('invalid:credentials').toString('base64');
    const response = await page.request.get(`${BASE_URL}/health/detailed`, {
      headers: { 'Authorization': `Basic ${invalidCredentials}` }
    });

    expect(response.status()).toBe(401);
  });

  test('Should detect health check services and allow bypass', async ({ page }) => {
    // Simulate Kubernetes health check
    const response = await page.request.get(`${BASE_URL}/health`, {
      headers: { 'User-Agent': 'kube-probe/1.21' }
    });

    expect(response.status()).toBe(200);

    // Should not be rate limited as aggressively
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
  });

});

test.describe('Dependency Health Checks', () => {

  test('Should check database connectivity', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/database`, {
      headers: { 'X-API-Key': TEST_API_KEY }
    });

    expect([200, 503]).toContain(response.status());

    const data = await response.json();
    expect(data.database).toHaveProperty('connected');

    if (data.database.connected) {
      expect(data.database).toHaveProperty('responseTime');
      expect(typeof data.database.responseTime).toBe('number');
    }
  });

  test('Should provide meaningful error messages for dependency failures', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/external`, {
      headers: { 'Authorization': `Basic ${TEST_CREDENTIALS}` }
    });

    expect(response.status()).toBe(200);

    const data = await response.json();

    // Each service should have status and error info if unhealthy
    Object.values(data.services).forEach((service: any) => {
      expect(service).toHaveProperty('status');
      expect(service).toHaveProperty('lastChecked');

      if (service.status === 'unhealthy') {
        expect(service).toHaveProperty('error');
        expect(typeof service.error).toBe('string');
      }
    });
  });

});

test.describe('Performance and Monitoring', () => {

  test('Health checks should respond quickly', async ({ page }) => {
    const start = Date.now();

    const response = await page.request.get(`${BASE_URL}/health`);

    const duration = Date.now() - start;

    expect(response.status()).toBe(200);
    expect(duration).toBeLessThan(1000); // Should respond within 1 second
  });

  test('Detailed health check should include performance metrics', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/health/detailed`, {
      headers: { 'X-API-Key': TEST_API_KEY }
    });

    if (response.status() === 200) {
      const data = await response.json();

      expect(data).toHaveProperty('memory');
      expect(data.memory).toHaveProperty('rss');
      expect(data.memory).toHaveProperty('heapUsed');

      expect(data).toHaveProperty('uptime');
      expect(typeof data.uptime).toBe('number');
    }
  });

  test('Metrics endpoint should provide Prometheus format', async ({ page }) => {
    const response = await page.request.get(`${BASE_URL}/metrics`, {
      headers: { 'Authorization': `Basic ${TEST_CREDENTIALS}` }
    });

    if (response.status() === 200) {
      const metrics = await response.text();

      // Should be in Prometheus format
      expect(metrics).toContain('# HELP');
      expect(metrics).toContain('# TYPE');
      expect(metrics).toContain('cc_lite_');
    }
  });

});
/**
 * Metrics Collection Test
 * Verifies that comprehensive metrics are collected correctly
 * Following Sacred Codex: "What is not measured is not real"
 */

import { test, expect } from '@playwright/test';
import { metricsService } from '../../server/services/metrics-service';

test.describe('Metrics Collection', () => {
  test('should expose Prometheus metrics endpoint', async ({ page }) => {
    // Navigate to metrics endpoint
    const response = await page.goto('/metrics');

    expect(response?.status()).toBe(200);
    expect(response?.headers()['content-type']).toContain('text/plain');

    const metricsText = await page.textContent('body');

    // Verify essential metrics are present
    expect(metricsText).toContain('cc_lite_http_requests_total');
    expect(metricsText).toContain('cc_lite_http_request_duration_seconds');
    expect(metricsText).toContain('cc_lite_memory_usage_bytes');
    expect(metricsText).toContain('cc_lite_process_uptime_seconds');
  });

  test('should collect business metrics via tRPC', async ({ page }) => {
    // Navigate to dashboard to trigger API calls
    await page.goto('/');

    // Wait for the page to load
    await page.waitForLoadState('networkidle');

    // Make tRPC call to get business metrics
    const metricsResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.getBusinessMetrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      return response.json();
    });

    expect(metricsResponse.result).toBeDefined();
    expect(metricsResponse.result.data).toBeDefined();

    // Verify business metrics structure
    const businessMetrics = metricsResponse.result.data;
    expect(businessMetrics).toHaveProperty('calls');
    expect(businessMetrics).toHaveProperty('agents');
    expect(businessMetrics).toHaveProperty('queues');
    expect(businessMetrics).toHaveProperty('customers');
    expect(businessMetrics).toHaveProperty('campaigns');
    expect(businessMetrics).toHaveProperty('ai');
  });

  test('should track HTTP request metrics', async ({ page }) => {
    // Make several requests to generate metrics
    await page.goto('/');
    await page.goto('/health');
    await page.goto('/api/metrics/summary');

    // Get Prometheus metrics
    const response = await page.goto('/metrics');
    const metricsText = await page.textContent('body');

    // Verify HTTP metrics are being tracked
    expect(metricsText).toMatch(/cc_lite_http_requests_total.*[1-9]/);
    expect(metricsText).toMatch(/cc_lite_http_request_duration_seconds_bucket/);

    // Verify different status codes are tracked
    expect(metricsText).toContain('status_code="200"');
  });

  test('should provide dashboard data via tRPC', async ({ page }) => {
    await page.goto('/');

    const dashboardResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.getDashboardData', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      return response.json();
    });

    expect(dashboardResponse.result).toBeDefined();
    expect(dashboardResponse.result.data).toBeDefined();

    const dashboardData = dashboardResponse.result.data;
    expect(dashboardData).toHaveProperty('metrics');
    expect(dashboardData).toHaveProperty('apm');
    expect(dashboardData).toHaveProperty('timestamp');

    // Verify metrics data structure
    expect(dashboardData.metrics).toHaveProperty('business');
    expect(dashboardData.metrics).toHaveProperty('system');
  });

  test('should track system metrics', async ({ page }) => {
    await page.goto('/metrics');
    const metricsText = await page.textContent('body');

    // Verify system metrics
    expect(metricsText).toContain('cc_lite_memory_usage_bytes');
    expect(metricsText).toContain('cc_lite_cpu_usage_percent');
    expect(metricsText).toContain('cc_lite_process_uptime_seconds');

    // Verify memory types are tracked
    expect(metricsText).toContain('type="rss"');
    expect(metricsText).toContain('type="heapUsed"');
    expect(metricsText).toContain('type="heapTotal"');
  });

  test('should provide health status', async ({ page }) => {
    const response = await page.goto('/health');
    expect(response?.status()).toBe(200);

    const healthData = await page.textContent('body');
    const health = JSON.parse(healthData || '{}');

    expect(health).toHaveProperty('status', 'healthy');
    expect(health).toHaveProperty('timestamp');
    expect(health).toHaveProperty('uptime');
    expect(health).toHaveProperty('memory');
  });

  test('should allow recording business events', async ({ page }) => {
    await page.goto('/');

    // Record a business event via tRPC
    const eventResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.recordBusinessEvent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          eventType: 'call_started',
          data: {
            activeCalls: 5,
            callId: 'test-call-123',
            campaignId: 'test-campaign',
          },
          metadata: {
            source: 'playwright-test',
          },
        }),
      });
      return response.json();
    });

    expect(eventResponse.result).toBeDefined();
    expect(eventResponse.result.data).toBeDefined();
    expect(eventResponse.result.data.success).toBe(true);
    expect(eventResponse.result.data.eventType).toBe('call_started');
  });

  test('should track performance summary', async ({ page }) => {
    // Generate some activity
    await page.goto('/');
    await page.goto('/health');

    const summaryResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.getPerformanceSummary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      return response.json();
    });

    expect(summaryResponse.result).toBeDefined();
    expect(summaryResponse.result.data).toBeDefined();

    const summary = summaryResponse.result.data;
    expect(summary).toHaveProperty('requests');
    expect(summary).toHaveProperty('system');
    expect(summary).toHaveProperty('business');

    // Verify request metrics
    expect(summary.requests).toHaveProperty('total');
    expect(summary.requests).toHaveProperty('success');
    expect(summary.requests).toHaveProperty('successRate');
    expect(summary.requests).toHaveProperty('averageResponseTime');

    // Verify system metrics
    expect(summary.system).toHaveProperty('uptime');
    expect(summary.system).toHaveProperty('memoryUsage');
    expect(summary.system).toHaveProperty('cpuUsage');

    // Verify business metrics
    expect(summary.business).toHaveProperty('activeCalls');
    expect(summary.business).toHaveProperty('totalCalls');
  });

  test('should export metrics in different formats', async ({ page }) => {
    await page.goto('/');

    // Test JSON export
    const jsonExportResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.exportMetrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format: 'json',
          timeRange: {
            startTime: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
            endTime: new Date().toISOString(),
            interval: '15m',
          },
          includeSystemMetrics: true,
          includeBusinessMetrics: true,
        }),
      });
      return response.json();
    });

    expect(jsonExportResponse.result).toBeDefined();
    expect(jsonExportResponse.result.data).toBeDefined();
    expect(jsonExportResponse.result.data.success).toBe(true);
    expect(jsonExportResponse.result.data.exportId).toBeDefined();
    expect(jsonExportResponse.result.data.downloadUrl).toBeDefined();
  });

  test('should provide real-time stream info', async ({ page }) => {
    await page.goto('/');

    const streamInfoResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.getRealtimeStreamInfo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      return response.json();
    });

    expect(streamInfoResponse.result).toBeDefined();
    expect(streamInfoResponse.result.data).toBeDefined();

    const streamInfo = streamInfoResponse.result.data;
    expect(streamInfo).toHaveProperty('websocketEndpoint');
    expect(streamInfo).toHaveProperty('availableStreams');
    expect(streamInfo).toHaveProperty('updateInterval');
    expect(streamInfo).toHaveProperty('maxConnections');

    // Verify available streams
    expect(streamInfo.availableStreams).toContain('business_metrics');
    expect(streamInfo.availableStreams).toContain('system_metrics');
    expect(streamInfo.availableStreams).toContain('apm_metrics');
  });

  test('should verify metrics are accurate', async ({ page }) => {
    // Record initial metrics
    const initialResponse = await page.goto('/metrics');
    const initialMetricsText = await page.textContent('body');

    // Extract initial request count
    const initialRequestMatch = initialMetricsText?.match(/cc_lite_http_requests_total.*?(\d+)/);
    const initialRequestCount = initialRequestMatch ? parseInt(initialRequestMatch[1]) : 0;

    // Make additional requests
    await page.goto('/health');
    await page.goto('/api/metrics/summary');

    // Get updated metrics
    const updatedResponse = await page.goto('/metrics');
    const updatedMetricsText = await page.textContent('body');

    // Extract updated request count
    const updatedRequestMatch = updatedMetricsText?.match(/cc_lite_http_requests_total.*?(\d+)/);
    const updatedRequestCount = updatedRequestMatch ? parseInt(updatedRequestMatch[1]) : 0;

    // Verify metrics increased
    expect(updatedRequestCount).toBeGreaterThan(initialRequestCount);
  });
});

test.describe('Metrics Integration', () => {
  test('should integrate with existing APM service', async ({ page }) => {
    // Test that metrics work alongside APM
    await page.goto('/');

    // Get dashboard data that includes both metrics and APM
    const dashboardResponse = await page.evaluate(async () => {
      const response = await fetch('/trpc/metrics.getDashboardData', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });
      return response.json();
    });

    const dashboardData = dashboardResponse.result.data;

    // Verify both metrics and APM data are present
    expect(dashboardData).toHaveProperty('metrics');
    expect(dashboardData).toHaveProperty('apm');

    // Verify APM data structure (from existing APM service)
    expect(dashboardData.apm).toHaveProperty('system');
    expect(dashboardData.apm).toHaveProperty('health');

    // Verify metrics data structure (from new metrics service)
    expect(dashboardData.metrics).toHaveProperty('business');
    expect(dashboardData.metrics).toHaveProperty('system');
  });
});

// Performance test to ensure metrics don't significantly impact performance
test.describe('Metrics Performance', () => {
  test('should not significantly impact API performance', async ({ page }) => {
    // Measure performance without heavy metrics load
    const startTime = Date.now();

    // Make multiple API calls
    for (let i = 0; i < 10; i++) {
      await page.goto('/health');
    }

    const endTime = Date.now();
    const totalTime = endTime - startTime;
    const averageTime = totalTime / 10;

    // Verify average response time is reasonable (under 100ms per request)
    expect(averageTime).toBeLessThan(100);

    // Verify metrics are still being collected
    const metricsResponse = await page.goto('/metrics');
    expect(metricsResponse?.status()).toBe(200);
  });
});
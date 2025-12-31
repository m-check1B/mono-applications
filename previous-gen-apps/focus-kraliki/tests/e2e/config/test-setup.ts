import { test as base } from '@playwright/test';
import { chromium, type Browser, type Page } from '@playwright/test';

// Extend base test with custom fixtures
export const test = base.extend<{
  page: Page;
  authenticatedPage: Page;
}>({
  // Custom authenticated page fixture
  authenticatedPage: async ({}, use) => {
    const browser = await chromium.launch();
    const context = await browser.newContext();

    // Login with test credentials
    const page = await context.newPage();
    await page.goto('/login');

    await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
    await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test123');
    await page.click('button[type="submit"]');

    // Wait for successful login
    await page.waitForURL('/', { timeout: 10000 });

    await use(page);

    // Cleanup
    await context.close();
    await browser.close();
  },
});

// Test utilities
export const TestUtils = {
  async waitForAPIResponse(page: Page, endpoint: string, timeout = 5000): Promise<any> {
    return await page.waitForResponse(response =>
      response.url().includes(endpoint) && response.status() === 200,
      { timeout }
    );
  },

  async mockAPIResponse(page: Page, endpoint: string, responseData: any): Promise<void> {
    await page.route(`**/${endpoint}**`, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(responseData),
      });
    });
  },

  async captureConsoleLogs(page: Page): Promise<string[]> {
    const logs: string[] = [];

    page.on('console', msg => {
      logs.push(msg.text());
    });

    return logs;
  },

  async checkAccessibility(page: Page): Promise<void> {
    // This would integrate with axe-core or similar accessibility testing tool
    const accessibilityIssues = await page.evaluate(() => {
      // Placeholder for accessibility checks
      return [];
    });

    if (accessibilityIssues.length > 0) {
      console.warn('Accessibility issues found:', accessibilityIssues);
    }
  },

  async measurePerformance(page: Page): Promise<PerformanceEntry[]> {
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');

      return [
        { name: 'FCP', value: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0 },
        { name: 'LCP', value: paint.find(p => p.name === 'largest-contentful-paint')?.startTime || 0 },
        { name: 'TTFB', value: navigation.responseStart - navigation.requestStart },
        { name: 'Load', value: navigation.loadEventEnd - navigation.loadEventStart },
      ];
    });

    return metrics;
  },

  async generateTestUser(): Promise<{ email: string; password: string; name: string }> {
    const timestamp = Date.now();
    return {
      email: `testuser_${timestamp}@focus-kraliki.test`,
      password: `TestPassword_${timestamp}!`,
      name: `Test User ${timestamp}`,
    };
  },

  async cleanupTestData(page: Page, userEmail: string): Promise<void> {
    // Cleanup test data after tests
    await page.request.delete(`/api/test/cleanup?email=${encodeURIComponent(userEmail)}`);
  },
};

// Custom matchers
expect.extend({
  toBeAccessible(received: Page) {
    const issues = []; // Would be populated by actual accessibility check
    const pass = issues.length === 0;

    return {
      pass,
      message: () =>
        pass
          ? 'Expected page to be accessible'
          : `Page has accessibility issues: ${issues.join(', ')}`,
    };
  },

  toPerformWell(received: Page, threshold = 3000) {
    // Placeholder for performance assertions
    const pass = true; // Would be populated by actual performance metrics

    return {
      pass,
      message: () =>
        pass
          ? 'Expected page to perform well'
          : 'Page performance is below threshold',
    };
  },
});

export default test;
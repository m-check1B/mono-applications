import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Lab by Kraliki E2E tests.
 *
 * Tests are designed to run against:
 * 1. Static HTML files in demo/outputs/
 * 2. Local development server (when available)
 * 3. Staging environment at lab.verduona.dev (future)
 *
 * By default, only runs Chromium tests. Set FULL_BROWSER_TESTS=true
 * to run Firefox and WebKit tests (requires browsers to be installed).
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'test-results/reports' }],
    ['list']
  ],
  use: {
    // Base URL for tests - uses local file server or environment variable
    baseURL: process.env.MAGIC_BOX_URL || 'http://127.0.0.1:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    // Primary browser - always runs
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Mobile viewport for responsive testing
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    // Additional browsers - only run with FULL_BROWSER_TESTS=true
    ...(process.env.FULL_BROWSER_TESTS ? [
      {
        name: 'firefox',
        use: { ...devices['Desktop Firefox'] },
      },
      {
        name: 'webkit',
        use: { ...devices['Desktop Safari'] },
      },
      {
        name: 'mobile-safari',
        use: { ...devices['iPhone 12'] },
      },
    ] : []),
  ],

  // Local development server
  webServer: {
    command: 'npx http-server ./demo/outputs/before-after -p 3000 -c-1',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
});

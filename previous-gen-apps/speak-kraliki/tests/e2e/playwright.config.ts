import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration for Speak by Kraliki
 *
 * Speak by Kraliki is a B2B/B2G employee feedback platform with:
 * - CEO/Manager dashboard for creating surveys and viewing analytics
 * - Employee voice feedback flow accessed via magic links
 * - AI-powered sentiment analysis
 *
 * Tests skip gracefully when no server is available, making the test suite
 * resilient to environment differences.
 *
 * Test coverage:
 * - Landing page
 * - Survey creation flow
 * - Employee access flow
 *
 * Usage:
 *   cd /home/adminmatej/github/applications/speak-kraliki/tests/e2e
 *   npx playwright test
 */

export default defineConfig({
  testDir: './',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0, // No retries - tests skip when server unavailable
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['list'],
  ],
  timeout: 30000, // 30 second timeout for tests
  expect: {
    timeout: 10000, // 10 second timeout for expects
  },

  use: {
    // Base URL for the Speak by Kraliki frontend
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 15000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Additional browsers can be enabled when needed
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'mobile-chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],

  // Web server configuration - commented out for environment resilience
  // Tests will skip gracefully when server is not available
  // To start the server manually:
  //   cd /home/adminmatej/github/applications/speak-kraliki/frontend
  //   npm run dev -- --host 127.0.0.1
  //
  // webServer: {
  //   command: 'npm run dev -- --host 127.0.0.1',
  //   cwd: '/home/adminmatej/github/applications/speak-kraliki/frontend',
  //   url: 'http://127.0.0.1:5173',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120 * 1000,
  // },
});

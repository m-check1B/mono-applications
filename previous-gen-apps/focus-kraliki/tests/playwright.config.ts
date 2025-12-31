/**
 * Playwright E2E Test Configuration for Focus by Kraliki
 *
 * VD-151: Playwright E2E Tests for Focus by Kraliki
 *
 * Test Suites:
 * - Authentication Flow (auth.spec.ts)
 * - Task Management (tasks.spec.ts)
 * - Timer Functionality (timer.spec.ts)
 *
 * Run tests:
 *   npx playwright test                          # Run all tests
 *   npx playwright test e2e/focus-kraliki/          # Run VD-151 tests only
 *   npx playwright test --ui                     # Run with UI mode
 *   FOCUS_KRALIKI_BASE_URL=https://focus.verduona.dev npx playwright test  # Test staging
 */

import { defineConfig, devices } from '@playwright/test';

const base =
  process.env.FOCUS_KRALIKI_BASE_URL ||
  process.env.FOCUS_KRALIKI_BASE_URL || process.env.FOCUS_LITE_BASE_URL ||
  process.env.BASE_URL ||
  'http://127.0.0.1:5173';
const apiUrl =
  process.env.FOCUS_KRALIKI_API_URL ||
  process.env.FOCUS_KRALIKI_API_URL || process.env.FOCUS_LITE_API_URL ||
  'http://127.0.0.1:8000';
const useExternal = !!(
  process.env.FOCUS_KRALIKI_BASE_URL ||
  process.env.FOCUS_KRALIKI_BASE_URL || process.env.FOCUS_LITE_BASE_URL ||
  process.env.BASE_URL
);

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],
  timeout: 30000,
  expect: {
    timeout: 10000,
  },
  use: {
    baseURL: base,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  /* Configure web server for local development */
  webServer: useExternal
    ? undefined
    : [
        {
          command: 'cd ../frontend && pnpm dev --port 5173 --host 127.0.0.1',
          url: 'http://127.0.0.1:5173',
          timeout: 120000,
          reuseExistingServer: !process.env.CI,
          stdout: 'pipe',
          stderr: 'pipe',
        },
        {
          command: 'cd ../backend && PYTHONPATH=. uv run uvicorn app.main:app --host 127.0.0.1 --port 8000',
          url: 'http://127.0.0.1:8000/health',
          timeout: 120000,
          reuseExistingServer: !process.env.CI,
          stdout: 'pipe',
          stderr: 'pipe',
        },
      ],

  /* Output directory for test artifacts */
  outputDir: 'test-results',
});

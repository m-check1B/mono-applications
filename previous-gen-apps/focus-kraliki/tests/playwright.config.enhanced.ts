import { defineConfig, devices } from '@playwright/test';

const base =
  process.env.FOCUS_KRALIKI_BASE_URL ||
  process.env.FOCUS_KRALIKI_BASE_URL || process.env.FOCUS_LITE_BASE_URL ||
  process.env.BASE_URL ||
  'http://127.0.0.1:5173';
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
    ['html'],
    ['json', { outputFile: 'test-results/test-results.json' }],
    ['list'],
    ['junit', { outputFile: 'test-results/test-results.xml' }]
  ],
  use: {
    baseURL: base,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 30000,
    navigationTimeout: 60000,
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--no-sandbox', '--disable-setuid-sandbox']
        }
      },
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
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: useExternal
    ? []
    : [
        {
          command: 'cd frontend && pnpm dev --port 5173',
          port: 5173,
          reuseExistingServer: !process.env.CI,
          timeout: 120000,
        },
        {
          command: 'cd backend && pnpm dev',
          port: 3017,
          reuseExistingServer: !process.env.CI,
          timeout: 120000,
        },
      ],

  // Global setup and teardown
  globalSetup: require.resolve('./e2e/global-setup.ts'),
  globalTeardown: require.resolve('./e2e/global-teardown.ts'),

  // Output directory
  outputDir: 'test-results/',

  // Test timeout
  timeout: 60000,

  // Expect timeout
  expect: {
    timeout: 10000,
  },

  // Metadata
  metadata: {
    testEnvironment: 'focus-kraliki',
    testType: 'e2e',
    browser: 'playwright',
  },
});

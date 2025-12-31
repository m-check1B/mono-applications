import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 3 : 1,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/business-ops-results.json' }],
    ['list'],
    ['junit', { outputFile: 'test-results/business-ops-results.xml' }],
    ['allure-playwright']
  ],
  use: {
    baseURL: process.env.BUSINESS_OPS_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 45000,
    navigationTimeout: 90000,
  },

  projects: [
    {
      name: 'chromium-business-ops',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        }
      },
      testMatch: [
        '**/business-operations.spec.ts',
        '**/advanced-ai-automation.spec.ts'
      ]
    },
    {
      name: 'firefox-business-ops',
      use: { ...devices['Desktop Firefox'] },
      testMatch: [
        '**/business-operations.spec.ts',
        '**/advanced-ai-automation.spec.ts'
      ]
    },
    {
      name: 'webkit-business-ops',
      use: { ...devices['Desktop Safari'] },
      testMatch: [
        '**/business-operations.spec.ts'
      ]
    },
    {
      name: 'mobile-business-ops',
      use: { ...devices['iPhone 12'] },
      testMatch: [
        '**/accessibility-mobile.spec.ts'
      ]
    },
    {
      name: 'accessibility-business-ops',
      use: {
        ...devices['Desktop Chrome'],
        viewport: null, // Use default viewport for accessibility
      },
      testMatch: [
        '**/accessibility-mobile.spec.ts'
      ]
    }
  ],

  webServer: [
    {
      command: 'cd ../frontend && pnpm dev --port 5173',
      port: 5173,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: 'cd ../backend && pnpm dev',
      port: 3017,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: 'cd ../operations/business-ops/planning && npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
  ],

  globalSetup: require.resolve('./global-setup.ts'),
  globalTeardown: require.resolve('./global-teardown.ts'),

  outputDir: 'test-results/business-ops/',

  timeout: 90000,

  expect: {
    timeout: 15000,
  },

  metadata: {
    testEnvironment: 'business-operations',
    testType: 'e2e-integration',
    focusAreas: ['plane', 'notion', 'automation', 'ai', 'accessibility']
  },
});
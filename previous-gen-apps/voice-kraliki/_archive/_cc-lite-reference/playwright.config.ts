import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: ['**/*.spec.ts'],
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['list'],
    ['json', { outputFile: 'test-results.json' }]
  ],
  use: {
    baseURL: 'http://127.0.0.1:3007',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 CCLight/Test'
      },
    },
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0 CCLight/Test'
      },
    },
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15 CCLight/Test'
      },
    },
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36 CCLight/Mobile'
      },
    },
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1 CCLight/Mobile'
      },
    },
  ],

  webServer: {
    command: 'pnpm dev',
    url: 'http://127.0.0.1:3007',
    reuseExistingServer: true,
    timeout: 120000,
  },
});

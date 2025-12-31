import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration for Sense by Kraliki
 *
 * Sense by Kraliki is a Telegram sensitivity tracking bot that combines:
 * - NOAA space weather data
 * - USGS seismic activity
 * - Schumann resonance
 * - Moon phases and astrology
 * - Personal biorhythm
 *
 * NOTE: Sense by Kraliki is currently a Telegram bot without a web UI.
 * These tests are designed for a future web dashboard implementation.
 * Tests will skip gracefully when no web server is available.
 *
 * Tests cover: Landing page, Sensor Dashboard, Alert Configuration
 */

export default defineConfig({
  testDir: './',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0, // No retries - tests skip when server unavailable
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],
  timeout: 15000, // Shorter timeout for faster skip detection

  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 5000,
    navigationTimeout: 10000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Web server configuration - commented out as Sense by Kraliki is a Telegram bot
  // Uncomment when web UI is implemented
  // webServer: {
  //   command: 'cd ../.. && python -m app.web',
  //   url: 'http://127.0.0.1:3000',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
});

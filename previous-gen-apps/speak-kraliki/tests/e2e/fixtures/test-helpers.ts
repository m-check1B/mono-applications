import { test as base, Page } from '@playwright/test';

/**
 * Server Availability Helpers for Speak by Kraliki E2E Tests
 *
 * Speak by Kraliki is a B2B/B2G employee feedback platform with:
 * - CEO/Manager dashboard for creating surveys and viewing analytics
 * - Employee voice feedback flow accessed via magic links
 * - AI-powered sentiment analysis
 *
 * These helpers allow tests to skip gracefully when no server is running,
 * making the test suite resilient to environment differences.
 */

export const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:5173';

let serverAvailable: boolean | null = null;

/**
 * Check if the Speak by Kraliki web server is available
 * Caches the result to avoid repeated checks
 */
export async function isServerAvailable(): Promise<boolean> {
  if (serverAvailable !== null) {
    return serverAvailable;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const response = await fetch(BASE_URL, {
      method: 'HEAD',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    serverAvailable = response.ok || response.status < 500;
  } catch {
    serverAvailable = false;
  }

  return serverAvailable;
}

/**
 * Reset server availability cache (useful for testing)
 */
export function resetServerCache(): void {
  serverAvailable = null;
}

/**
 * Extended test that skips when server is unavailable
 */
export const test = base.extend<{ serverCheck: void }>({
  serverCheck: [
    async ({}, use, testInfo) => {
      const available = await isServerAvailable();
      if (!available) {
        testInfo.skip(true, 'Speak by Kraliki web server not available');
      }
      await use();
    },
    { auto: true },
  ],
});

/**
 * Safe page navigation that handles server unavailability
 */
export async function safeGoto(page: Page, path: string): Promise<boolean> {
  try {
    const response = await page.goto(path, { timeout: 10000 });
    return response !== null && response.ok();
  } catch {
    return false;
  }
}

export { expect } from '@playwright/test';

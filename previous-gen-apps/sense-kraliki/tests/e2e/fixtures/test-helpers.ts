import { test as base, Page } from '@playwright/test';

/**
 * Server Availability Helpers for Sense by Kraliki E2E Tests
 *
 * Sense by Kraliki is currently a Telegram bot without a web UI.
 * These helpers allow tests to skip gracefully when no server is running,
 * making the test suite resilient to environment differences.
 */

export const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:3000';

let serverAvailable: boolean | null = null;

/**
 * Check if the Sense by Kraliki web server is available
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
        testInfo.skip(true, 'Sense by Kraliki web server not available - this is a Telegram bot project');
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
    const response = await page.goto(path, { timeout: 5000 });
    return response !== null && response.ok();
  } catch {
    return false;
  }
}

export { expect } from '@playwright/test';

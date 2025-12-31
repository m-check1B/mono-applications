/**
 * Focus by Kraliki E2E Test Fixtures
 * Shared utilities and helper functions for Playwright tests
 *
 * VD-151: Playwright E2E Tests for Focus by Kraliki
 */

import { test as base, expect, Page } from '@playwright/test';

// Test user credentials
export const TEST_USER = {
  email: 'test@focus-kraliki.app',
  password: 'test123',
  name: 'Test User'
};

// Base URLs
export const BASE_URL =
  process.env.FOCUS_KRALIKI_BASE_URL ||
  process.env.FOCUS_KRALIKI_BASE_URL || process.env.FOCUS_LITE_BASE_URL ||
  'http://127.0.0.1:5173';
export const API_URL =
  process.env.FOCUS_KRALIKI_API_URL ||
  process.env.FOCUS_KRALIKI_API_URL || process.env.FOCUS_LITE_API_URL ||
  'http://127.0.0.1:8000';

/**
 * Helper to login user
 */
export async function loginUser(page: Page, user = TEST_USER): Promise<void> {
  await page.goto('/login');

  // Clear any existing session
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.reload();

  // Fill login form
  await page.fill('input#email', user.email);
  await page.fill('input#password', user.password);
  await page.click('button[type="submit"]');

  // Wait for dashboard
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 15000 });
}

/**
 * Helper to generate unique identifiers
 */
export function generateUniqueId(prefix = 'test'): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Helper to generate unique task titles
 */
export function generateTaskTitle(): string {
  return `E2E Test Task ${generateUniqueId()}`;
}

/**
 * Helper to generate unique user email
 */
export function generateUserEmail(): string {
  return `test.${generateUniqueId('user')}@example.com`;
}

/**
 * Helper to wait for network idle
 */
export async function waitForNetworkIdle(page: Page, timeout = 5000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Helper to clear auth state
 */
export async function clearAuthState(page: Page): Promise<void> {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
    // Clear cookies
    document.cookie.split(';').forEach((c) => {
      document.cookie = c
        .replace(/^ +/, '')
        .replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/');
    });
  });
}

/**
 * Helper to check if element exists
 */
export async function elementExists(page: Page, selector: string, timeout = 3000): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { timeout });
    return true;
  } catch {
    return false;
  }
}

/**
 * Helper to get visible text content
 */
export async function getVisibleText(page: Page, selector: string): Promise<string | null> {
  const element = page.locator(selector).first();
  if (await element.isVisible({ timeout: 3000 }).catch(() => false)) {
    return await element.textContent();
  }
  return null;
}

/**
 * Helper to fill form field if visible
 */
export async function fillIfVisible(
  page: Page,
  selector: string,
  value: string,
  timeout = 3000
): Promise<boolean> {
  const element = page.locator(selector).first();
  if (await element.isVisible({ timeout }).catch(() => false)) {
    await element.fill(value);
    return true;
  }
  return false;
}

/**
 * Helper to click if visible
 */
export async function clickIfVisible(
  page: Page,
  selector: string,
  timeout = 3000
): Promise<boolean> {
  const element = page.locator(selector).first();
  if (await element.isVisible({ timeout }).catch(() => false)) {
    await element.click();
    return true;
  }
  return false;
}

/**
 * Helper to take screenshot on failure
 */
export async function screenshotOnFailure(
  page: Page,
  testName: string
): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `test-results/failures/${testName}-${timestamp}.png`,
    fullPage: true
  });
}

/**
 * Helper to wait for toast/notification
 */
export async function waitForToast(
  page: Page,
  text: string,
  timeout = 5000
): Promise<boolean> {
  const toastSelectors = [
    '.toast',
    '[role="alert"]',
    '.notification',
    '[data-testid="toast"]'
  ];

  for (const selector of toastSelectors) {
    const toast = page.locator(selector).filter({ hasText: text });
    if (await toast.isVisible({ timeout: timeout / toastSelectors.length }).catch(() => false)) {
      return true;
    }
  }
  return false;
}

/**
 * Helper to verify page loaded successfully
 */
export async function verifyPageLoaded(page: Page): Promise<void> {
  await expect(page.locator('body')).toBeVisible();
  await page.waitForLoadState('domcontentloaded');
}

/**
 * Helper to create task via fast path
 */
export async function createTaskViaFastPath(page: Page, title: string): Promise<boolean> {
  const inputSelectors = [
    'input[placeholder*="type" i]',
    'input[placeholder*="ask" i]',
    'textarea[placeholder*="message" i]',
    'input[placeholder*="task" i]'
  ];

  for (const selector of inputSelectors) {
    const input = page.locator(selector).first();
    if (await input.isVisible({ timeout: 3000 }).catch(() => false)) {
      await input.fill(`+ ${title}`);
      await input.press('Enter');
      await page.waitForTimeout(2000);
      return true;
    }
  }
  return false;
}

/**
 * Helper to navigate to panel
 */
export async function navigateToPanel(
  page: Page,
  panelName: 'tasks' | 'time' | 'calendar' | 'knowledge' | 'settings'
): Promise<boolean> {
  // Try direct navigation first
  await page.goto(`/dashboard/${panelName}`);
  await page.waitForTimeout(1000);

  // Check if we're on dashboard (panel routes redirect)
  const currentUrl = page.url();
  if (currentUrl.includes('/dashboard')) {
    return true;
  }

  // Try clicking panel trigger
  const panelTrigger = page.locator(
    `button:has-text("${panelName}"), nav a:has-text("${panelName}")`
  ).first();

  if (await panelTrigger.isVisible({ timeout: 3000 })) {
    await panelTrigger.click();
    await page.waitForTimeout(500);
    return true;
  }

  return false;
}

/**
 * Custom test fixture with authenticated page
 */
export const test = base.extend<{
  authenticatedPage: Page;
}>({
  authenticatedPage: async ({ page }, use) => {
    await loginUser(page);
    await use(page);
  }
});

export { expect };

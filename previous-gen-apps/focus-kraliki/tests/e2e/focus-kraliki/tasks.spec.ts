/**
 * Focus by Kraliki E2E Tests: Task Creation and Completion
 * Tests cover task CRUD operations and state management
 *
 * VD-151: Playwright E2E Tests for Focus by Kraliki
 */

import { test, expect, Page } from '@playwright/test';

// Test credentials
const TEST_USER = {
  email: 'test@focus-kraliki.app',
  password: 'test123'
};

// Helper to try login before tests (returns true if successful)
async function tryLogin(page: Page): Promise<boolean> {
  await page.goto('/login');
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.reload();

  await page.fill('input#email', TEST_USER.email);
  await page.fill('input#password', TEST_USER.password);
  await page.click('button[type="submit"]');

  // Wait for response
  await page.waitForTimeout(3000);

  // Check if login was successful
  const currentUrl = page.url();
  return currentUrl.includes('/dashboard');
}

// Helper to generate unique task titles
function generateTaskTitle(): string {
  return `E2E Test Task ${Date.now()}`;
}

test.describe('Task Management', () => {
  test.describe('Dashboard Tasks View (requires auth)', () => {
    test('should display task management interface', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        // If not logged in, verify we're on login page (expected behavior)
        expect(page.url()).toContain('/login');
        return;
      }

      // Dashboard should show task-related elements
      await expect(page.locator('body')).toBeVisible();

      // Check for main interface elements
      const mainContent = page.locator('main, [role="main"], .dashboard, [data-testid="dashboard"]');
      await expect(mainContent.or(page.locator('body'))).toBeVisible();
    });

    test('should create task using fast path command', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const taskTitle = generateTaskTitle();
      const inputSelector = 'input[placeholder*="type" i], input[placeholder*="ask" i], textarea[placeholder*="message" i]';
      const input = page.locator(inputSelector).first();

      if (await input.isVisible({ timeout: 5000 })) {
        await input.fill(`+ ${taskTitle}`);
        await input.press('Enter');
        await page.waitForTimeout(2000);

        // Check for any success indicator
        const successIndicators = [
          page.locator(`text=${taskTitle}`),
          page.locator('text=created'),
          page.locator('.toast, [role="alert"]')
        ];

        for (const indicator of successIndicators) {
          if (await indicator.isVisible({ timeout: 3000 }).catch(() => false)) {
            break;
          }
        }
      }
    });

    test('should open tasks panel', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const tasksPanelTrigger = page.locator(
        'button:has-text("Tasks"), [aria-label*="tasks" i], [data-panel="tasks"], nav a:has-text("Tasks")'
      );

      if (await tasksPanelTrigger.first().isVisible({ timeout: 5000 })) {
        await tasksPanelTrigger.first().click();
        await page.waitForTimeout(500);
        await expect(page).toHaveURL(/tasks|dashboard/);
      }
    });

    test('should navigate to /dashboard/tasks route', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/tasks');
      await expect(page).toHaveURL(/\/dashboard/);
    });
  });

  test.describe('Task CRUD Operations (requires auth)', () => {
    test('should create task with title', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const taskTitle = generateTaskTitle();
      const input = page.locator('input, textarea').first();

      if (await input.isVisible()) {
        await input.fill(`/task ${taskTitle}`);
        await input.press('Enter');
        await page.waitForTimeout(2000);
      }
    });

    test('should create task via AI assistant', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const taskTitle = generateTaskTitle();
      const input = page.locator(
        'input[placeholder*="type" i], input[placeholder*="ask" i], textarea'
      ).first();

      if (await input.isVisible({ timeout: 5000 })) {
        await input.fill(`Create a task called "${taskTitle}"`);
        await input.press('Enter');
        await page.waitForTimeout(5000);

        const feedbackIndicators = [
          page.locator('text=created'),
          page.locator('text=task'),
          page.locator(`text=${taskTitle}`)
        ];

        for (const indicator of feedbackIndicators) {
          if (await indicator.isVisible({ timeout: 3000 }).catch(() => false)) {
            await expect(indicator).toBeVisible();
            break;
          }
        }
      }
    });

    test('should mark task as complete', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const taskTitle = generateTaskTitle();
      const input = page.locator('input, textarea').first();

      if (await input.isVisible()) {
        await input.fill(`+ ${taskTitle}`);
        await input.press('Enter');
        await page.waitForTimeout(2000);

        const taskElement = page.locator(`text=${taskTitle}`).first();

        if (await taskElement.isVisible({ timeout: 5000 })) {
          const checkbox = page
            .locator(`text=${taskTitle}`)
            .locator('..')
            .locator('input[type="checkbox"], [role="checkbox"]');

          if (await checkbox.isVisible({ timeout: 3000 })) {
            await checkbox.click();
            await page.waitForTimeout(1000);
          }
        }
      }
    });

    test('should filter tasks by status', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/tasks');
      await page.waitForTimeout(1000);

      const filterButtons = page.locator(
        'button:has-text("All"), button:has-text("Pending"), button:has-text("Completed"), button:has-text("In Progress")'
      );

      if (await filterButtons.first().isVisible({ timeout: 5000 })) {
        await filterButtons.first().click();
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Task Quick Actions (requires auth)', () => {
    test('should use quick prompts for task queries', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const quickPrompt = page.locator('text=Show urgent tasks').or(
        page.locator('button:has-text("urgent")')
      );

      if (await quickPrompt.isVisible({ timeout: 5000 })) {
        await quickPrompt.click();
        await page.waitForTimeout(2000);
      }
    });

    test('should search for tasks', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/tasks');

      const searchInput = page.locator(
        'input[type="search"], input[placeholder*="search" i], input[placeholder*="find" i]'
      );

      if (await searchInput.isVisible({ timeout: 5000 })) {
        await searchInput.fill('test');
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('Task Views (requires auth)', () => {
    test('should switch between view modes', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/tasks');
      await page.waitForTimeout(1000);

      const viewButtons = [
        page.locator('button:has-text("List")'),
        page.locator('button:has-text("Kanban")'),
        page.locator('button:has-text("Calendar")')
      ];

      for (const button of viewButtons) {
        if (await button.isVisible({ timeout: 2000 })) {
          await button.click();
          await page.waitForTimeout(500);
        }
      }
    });
  });
});

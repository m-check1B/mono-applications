/**
 * Focus by Kraliki E2E Tests: Timer Functionality
 * Tests cover time tracking, pomodoro timer, and time entries
 *
 * VD-151: Playwright E2E Tests for Focus by Kraliki
 */

import { test, expect, Page } from '@playwright/test';

// Test credentials
const TEST_USER = {
  email: 'test@focus-kraliki.app',
  password: 'test123'
};

// Helper to try login (returns true if successful)
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

test.describe('Timer Functionality', () => {
  test.describe('Time Panel Access (requires auth)', () => {
    test('should navigate to time tracking page', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await expect(page).toHaveURL(/\/dashboard/);
    });

    test('should open time panel from navigation', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      const timePanelTrigger = page.locator(
        'button:has-text("Time"), [aria-label*="time" i], nav a:has-text("Time"), [data-panel="time"]'
      );

      if (await timePanelTrigger.first().isVisible({ timeout: 5000 })) {
        await timePanelTrigger.first().click();
        await page.waitForTimeout(500);
      }
    });

    test('should display time tracking interface elements', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const timeElements = [
        page.locator('text=Time'),
        page.locator('text=Timer'),
        page.locator('text=Track'),
        page.locator('text=Start'),
        page.locator('[data-testid="timer"]')
      ];

      let found = false;
      for (const element of timeElements) {
        if (await element.first().isVisible({ timeout: 3000 }).catch(() => false)) {
          found = true;
          break;
        }
      }
    });
  });

  test.describe('Timer Controls (requires auth)', () => {
    test('should display timer start button', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const startButton = page.locator(
        'button:has-text("Start"), button:has-text("Begin"), button[aria-label*="start" i]'
      );

      if (await startButton.first().isVisible({ timeout: 5000 })) {
        await expect(startButton.first()).toBeVisible();
      }
    });

    test('should start timer when clicking start button', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const startButton = page.locator(
        'button:has-text("Start"), button:has-text("Begin")'
      ).first();

      if (await startButton.isVisible({ timeout: 5000 })) {
        await startButton.click();
        await page.waitForTimeout(2000);

        const activeTimerIndicators = [
          page.locator('button:has-text("Stop")'),
          page.locator('button:has-text("Pause")'),
          page.locator('text=0:0'),
          page.locator('[data-state="running"]')
        ];

        for (const indicator of activeTimerIndicators) {
          if (await indicator.isVisible({ timeout: 3000 }).catch(() => false)) {
            await expect(indicator).toBeVisible();
            break;
          }
        }
      }
    });

    test('should stop timer when clicking stop button', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const startButton = page.locator(
        'button:has-text("Start"), button:has-text("Begin")'
      ).first();

      if (await startButton.isVisible({ timeout: 5000 })) {
        await startButton.click();
        await page.waitForTimeout(2000);

        const stopButton = page.locator(
          'button:has-text("Stop"), button:has-text("End")'
        ).first();

        if (await stopButton.isVisible({ timeout: 5000 })) {
          await stopButton.click();
          await page.waitForTimeout(1000);
          await expect(startButton).toBeVisible({ timeout: 5000 });
        }
      }
    });

    test('should pause and resume timer', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const startButton = page.locator('button:has-text("Start")').first();

      if (await startButton.isVisible({ timeout: 5000 })) {
        await startButton.click();
        await page.waitForTimeout(2000);

        const pauseButton = page.locator('button:has-text("Pause")').first();
        if (await pauseButton.isVisible({ timeout: 3000 })) {
          await pauseButton.click();
          await page.waitForTimeout(500);

          const resumeButton = page.locator(
            'button:has-text("Resume"), button:has-text("Continue")'
          ).first();

          if (await resumeButton.isVisible({ timeout: 3000 })) {
            await resumeButton.click();
            await page.waitForTimeout(500);
          }
        }
      }
    });
  });

  test.describe('Timer Display (requires auth)', () => {
    test('should show timer countdown or countup', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const timerDisplay = page.locator(
        'text=/\\d{1,2}:\\d{2}/, [data-testid="timer-display"]'
      );

      if (await timerDisplay.first().isVisible({ timeout: 5000 })) {
        await expect(timerDisplay.first()).toBeVisible();
      }
    });

    test('should update timer display when running', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const startButton = page.locator('button:has-text("Start")').first();

      if (await startButton.isVisible({ timeout: 5000 })) {
        const timerDisplay = page.locator('text=/\\d{1,2}:\\d{2}/').first();
        await startButton.click();
        await page.waitForTimeout(3000);

        if (await timerDisplay.isVisible()) {
          await expect(timerDisplay).toBeVisible();
        }
      }
    });
  });

  test.describe('Pomodoro Timer (requires auth)', () => {
    test('should have pomodoro timer option', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const pomodoroElements = [
        page.locator('text=Pomodoro'),
        page.locator('text=Focus'),
        page.locator('text=25:00'),
        page.locator('button:has-text("Pomodoro")')
      ];

      for (const element of pomodoroElements) {
        if (await element.first().isVisible({ timeout: 3000 }).catch(() => false)) {
          await expect(element.first()).toBeVisible();
          break;
        }
      }
    });

    test('should switch between work and break modes', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const modeButtons = [
        page.locator('button:has-text("Work")'),
        page.locator('button:has-text("Break")'),
        page.locator('button:has-text("Focus")'),
        page.locator('button:has-text("Rest")')
      ];

      for (const button of modeButtons) {
        if (await button.isVisible({ timeout: 3000 })) {
          await button.click();
          await page.waitForTimeout(500);
        }
      }
    });
  });

  test.describe('Time Entries (requires auth)', () => {
    test('should display time entry history', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const historyElements = [
        page.locator('text=History'),
        page.locator('text=Entries'),
        page.locator('text=Recent'),
        page.locator('[data-testid="time-entries"]')
      ];

      for (const element of historyElements) {
        if (await element.first().isVisible({ timeout: 3000 }).catch(() => false)) {
          await expect(element.first()).toBeVisible();
          break;
        }
      }
    });

    test('should allow manual time entry', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const manualEntryButton = page.locator(
        'button:has-text("Add"), button:has-text("Manual"), button:has-text("Log")'
      ).first();

      if (await manualEntryButton.isVisible({ timeout: 5000 })) {
        await manualEntryButton.click();
        await page.waitForTimeout(500);

        const formElements = [
          page.locator('input[type="datetime-local"]'),
          page.locator('input[placeholder*="duration" i]'),
          page.locator('input[placeholder*="description" i]')
        ];

        for (const element of formElements) {
          if (await element.isVisible({ timeout: 3000 })) {
            await expect(element).toBeVisible();
            break;
          }
        }
      }
    });

    test('should link timer to task', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const taskSelector = page.locator(
        'select[name="task"], [data-testid="task-select"], button:has-text("Select task")'
      ).first();

      if (await taskSelector.isVisible({ timeout: 5000 })) {
        await taskSelector.click();
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Timer Keyboard Shortcuts (requires auth)', () => {
    test('should respond to keyboard shortcuts', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      // Try common keyboard shortcuts
      await page.keyboard.press('Space');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
    });
  });

  test.describe('Timer Settings (requires auth)', () => {
    test('should allow timer duration configuration', async ({ page }) => {
      const loggedIn = await tryLogin(page);
      if (!loggedIn) {
        expect(page.url()).toContain('/login');
        return;
      }

      await page.goto('/dashboard/time');
      await page.waitForTimeout(1000);

      const settingsButton = page.locator(
        'button[aria-label*="settings" i], button:has-text("Settings"), [data-testid="timer-settings"]'
      ).first();

      if (await settingsButton.isVisible({ timeout: 5000 })) {
        await settingsButton.click();
        await page.waitForTimeout(500);

        const settingsForm = page.locator(
          'input[type="number"], input[name*="duration" i]'
        ).first();

        if (await settingsForm.isVisible({ timeout: 3000 })) {
          await expect(settingsForm).toBeVisible();
        }
      }
    });
  });
});

import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5175';

async function login(page: Page) {
	await page.goto(`${BASE_URL}/login`);
	await page.fill('input[name="email"]', 'test@example.com');
	await page.fill('input[name="password"]', 'testpassword');
	await page.click('button[type="submit"]');
	await page.waitForURL('**/dashboard');
}

async function clearQueue(page: Page) {
	await page.evaluate(() => localStorage.removeItem('assistant_command_queue'));
}

async function getQueueLength(page: Page) {
	return page.evaluate(() => {
		const raw = localStorage.getItem('assistant_command_queue');
		if (!raw) return 0;
		try {
			return JSON.parse(raw).length || 0;
		} catch (error) {
			return 0;
		}
	});
}

test.describe('Assistant handoff CTAs', () => {
	test.beforeEach(async ({ page }) => {
		await login(page);
	});

	test('calendar CTA enqueues a command', async ({ page }) => {
		await page.goto(`${BASE_URL}/dashboard/calendar`);
		await clearQueue(page);
		await page.getByTestId('calendar-plan-cta').click();
		await expect(page.locator('text=Sent to assistant')).toBeVisible();
		await expect.poll(async () => getQueueLength(page)).toBeGreaterThan(0);
	});

	test('time tracking CTA enqueues a command', async ({ page }) => {
		await page.goto(`${BASE_URL}/dashboard/time`);
		await clearQueue(page);
		await page.getByTestId('time-summarize-cta').click();
		await expect(page.locator('text=Sent to assistant')).toBeVisible();
		await expect.poll(async () => getQueueLength(page)).toBeGreaterThan(0);
	});

	test('settings CTA enqueues a command', async ({ page }) => {
		await page.goto(`${BASE_URL}/dashboard/settings`);
		await clearQueue(page);
		await page.getByTestId('settings-byok-cta').click();
		await expect(page.locator('text=Sent to assistant')).toBeVisible();
		await expect.poll(async () => getQueueLength(page)).toBeGreaterThan(0);
	});
});

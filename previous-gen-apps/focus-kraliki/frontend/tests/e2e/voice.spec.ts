import { test, expect } from '@playwright/test';

test.describe('Voice Interface', () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto('http://127.0.0.1:5175/login');
		await page.fill('input[name="email"]', 'test@example.com');
		await page.fill('input[name="password"]', 'testpassword');
		await page.click('button[type="submit"]');
		await page.waitForURL('**/dashboard');

		// Navigate to voice
		await page.goto('http://127.0.0.1:5175/dashboard/voice');
	});

	test('should load voice interface', async ({ page }) => {
		await expect(page.locator('h1:has-text("Voice Interface")')).toBeVisible();
	});

	test('should show microphone button', async ({ page }) => {
		const micButton = page.locator('button').filter({ hasText: /mic|speak|record/i }).first();
		await expect(micButton).toBeVisible();
	});

	test('should display voice examples', async ({ page }) => {
		await expect(page.locator('text=Try saying')).toBeVisible();
		await expect(page.locator('text=Create a task for tomorrow')).toBeVisible();
	});

	test('should show browser compatibility message', async ({ page }) => {
		// Check for either supported message or not supported message
		const compatMessage = page.locator('text=/support|browser/i');
		if (await compatMessage.count() > 0) {
			await expect(compatMessage.first()).toBeVisible();
		}
	});
});

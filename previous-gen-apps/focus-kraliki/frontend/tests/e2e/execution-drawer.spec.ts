import { test, expect, type Page } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5175';

async function login(page: Page) {
	await page.goto(`${BASE_URL}/login`);
	await page.fill('input[name="email"]', 'test@example.com');
	await page.fill('input[name="password"]', 'testpassword');
	await page.click('button[type="submit"]');
	await page.waitForURL('**/dashboard');
}

test.describe('Execution drawer editing', () => {
	test.beforeEach(async ({ page }) => {
		await login(page);
	});

	test('edits a task from the execution drawer', async ({ page }) => {
		await page.goto(`${BASE_URL}/dashboard`);
		await page.waitForSelector('[data-testid="execution-entry"]', { timeout: 15000 });
		const entries = page.locator('[data-testid="execution-entry"]');
		const count = await entries.count();
		let edited = false;

		for (let index = 0; index < count; index++) {
			await entries.nth(index).click();
			await page.waitForSelector('button:has-text("Close")', { timeout: 5000 });
			const editButton = page.getByRole('button', { name: 'Edit details' });
			if (await editButton.isVisible()) {
				await editButton.click();
				const titleInput = page.locator('input[placeholder="Task title"]');
				if (!(await titleInput.isVisible())) {
					await page.getByRole('button', { name: 'Close' }).click();
					continue;
				}
				const newTitle = `Smoke Test ${Date.now()}`;
				await titleInput.fill(newTitle);
				await page.getByRole('button', { name: 'Save changes' }).click();
				await expect(page.locator('text=Task updated.')).toBeVisible();
				edited = true;
				await page.getByRole('button', { name: 'Close' }).click();
				break;
			}
			await page.getByRole('button', { name: 'Close' }).click();
		}

		expect(edited).toBeTruthy();
	});
});

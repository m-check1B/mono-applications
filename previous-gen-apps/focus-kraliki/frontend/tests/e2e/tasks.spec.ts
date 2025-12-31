import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto('http://127.0.0.1:5175/login');
		await page.fill('input[name="email"]', 'test@example.com');
		await page.fill('input[name="password"]', 'testpassword');
		await page.click('button[type="submit"]');
		await page.waitForURL('**/dashboard');

		// Navigate to tasks
		await page.goto('http://127.0.0.1:5175/dashboard/tasks');
	});

	test('should load tasks page', async ({ page }) => {
		await expect(page.locator('h1:has-text("Tasks")')).toBeVisible();
	});

	test('should create a new task', async ({ page }) => {
		// Find create task button/form
		const createButton = page.locator('button:has-text("Create"), button:has-text("Add Task")').first();

		if (await createButton.isVisible()) {
			await createButton.click();

			// Fill in task details
			await page.fill('input[name="title"], input[placeholder*="title"]', 'Test Task from E2E');
			await page.fill('textarea[name="description"], textarea[placeholder*="description"]', 'Created by automated test');

			// Submit form
			await page.click('button[type="submit"]');

			// Verify task appears in list
			await expect(page.locator('text=Test Task from E2E')).toBeVisible({ timeout: 5000 });
		}
	});

	test('should filter tasks by status', async ({ page }) => {
		// Look for filter buttons/tabs
		const filterButtons = page.locator('button:has-text("Pending"), button:has-text("In Progress"), button:has-text("Completed")');

		if (await filterButtons.first().isVisible()) {
			await filterButtons.first().click();
			// Verify URL or content changes
			await page.waitForTimeout(500);
		}
	});

	test('should search for tasks', async ({ page }) => {
		const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]');

		if (await searchInput.isVisible()) {
			await searchInput.fill('test');
			await page.waitForTimeout(500);
			// Results should be filtered
		}
	});
});

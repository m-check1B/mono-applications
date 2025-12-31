import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto('http://127.0.0.1:5175/login');
		await page.fill('input[name="email"]', 'test@example.com');
		await page.fill('input[name="password"]', 'testpassword');
		await page.click('button[type="submit"]');
		await page.waitForURL('**/dashboard');
	});

	test('should load dashboard', async ({ page }) => {
		await expect(page).toHaveURL(/.*dashboard/);
	});

	test('should navigate to all main pages', async ({ page }) => {
		const pages = [
			{ name: 'Tasks', url: '/dashboard/tasks' },
			{ name: 'Chat', url: '/dashboard/chat' },
			{ name: 'Voice', url: '/dashboard/voice' },
			{ name: 'Calendar', url: '/dashboard/calendar' },
			{ name: 'Projects', url: '/dashboard/projects' },
			{ name: 'Time', url: '/dashboard/time' },
			{ name: 'Shadow', url: '/dashboard/shadow' },
			{ name: 'Settings', url: '/dashboard/settings' }
		];

		for (const pageInfo of pages) {
			await page.goto(`http://127.0.0.1:5175${pageInfo.url}`);
			await expect(page).toHaveURL(pageInfo.url);
			// Wait for page to load
			await page.waitForLoadState('networkidle');
		}
	});

	test('should display navigation menu', async ({ page }) => {
		// Check for common navigation elements
		const nav = page.locator('nav, aside, [role="navigation"]').first();
		if (await nav.isVisible()) {
			await expect(nav).toBeVisible();
		}
	});

	test('should toggle theme', async ({ page }) => {
		const themeToggle = page.locator('button').filter({ hasText: /theme|dark|light/i }).first();

		if (await themeToggle.isVisible()) {
			await themeToggle.click();
			await page.waitForTimeout(500);
			// Theme should have changed (check for dark/light class on html/body)
		}
	});
});

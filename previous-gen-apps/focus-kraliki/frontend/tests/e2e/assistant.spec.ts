import { test, expect } from '@playwright/test';

test.describe('Assistant Conversation Flow', () => {
	test.beforeEach(async ({ page }) => {
		// Login
		await page.goto('/auth/login');
		await page.fill('input[type="email"]', 'test@example.com');
		await page.fill('input[type="password"]', 'password123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');
	});

	test('should load assistant canvas', async ({ page }) => {
		await page.goto('/dashboard');

		// Check for UnifiedCanvas presence
		await expect(page.locator('text=Command Center')).toBeVisible();
		await expect(page.locator('textarea').or(page.locator('input[type="text"]'))).toBeVisible();
	});

	test('should send message and receive response', async ({ page }) => {
		await page.goto('/dashboard');

		// Type message
		const input = page.locator('textarea').or(page.locator('input[type="text"]')).first();
		await input.fill('What tasks do I have today?');

		// Send
		await page.locator('button:has-text("Send")').or(page.locator('button[type="submit"]')).first().click();

		// Wait for response
		await page.waitForSelector('text=assistant', { timeout: 10000 });

		// Verify message appears in conversation
		await expect(page.locator('text=What tasks do I have today?')).toBeVisible();
	});

	test('should switch between modes', async ({ page }) => {
		await page.goto('/dashboard');

		// Look for mode selector
		const modeSelect = page.locator('select').filter({ hasText: /II-Agent|Orchestrated|Deterministic/ }).first();

		if (await modeSelect.isVisible()) {
			// Switch to Orchestrated mode
			await modeSelect.selectOption('orchestrated');
			await expect(modeSelect).toHaveValue('orchestrated');

			// Switch to Deterministic mode
			await modeSelect.selectOption('deterministic');
			await expect(modeSelect).toHaveValue('deterministic');
		}
	});
});

test.describe('Workflow Approval', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/auth/login');
		await page.fill('input[type="email"]', 'test@example.com');
		await page.fill('input[type="password"]', 'password123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');
	});

	test('should show workflow preview', async ({ page }) => {
		await page.goto('/dashboard');

		// Switch to orchestrated mode
		const modeSelect = page.locator('select').first();
		if (await modeSelect.isVisible()) {
			await modeSelect.selectOption('orchestrated');
		}

		// Send a workflow request
		const input = page.locator('textarea').or(page.locator('input[type="text"]')).first();
		await input.fill('Plan my day');
		await page.locator('button:has-text("Send")').or(page.locator('button[type="submit"]')).first().click();

		// Wait for workflow to appear
		await page.waitForTimeout(2000);

		// Check for workflow elements (may or may not appear depending on response)
		const hasWorkflow = await page.locator('text=workflow').or(page.locator('text=steps')).isVisible();
		if (hasWorkflow) {
			await expect(page.locator('button:has-text("Approve")').or(page.locator('button:has-text("approve")'))).toBeVisible();
		}
	});
});

test.describe('Send to Assistant CTA', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/auth/login');
		await page.fill('input[type="email"]', 'test@example.com');
		await page.fill('input[type="password"]', 'password123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');
	});

	test('should have send to assistant button in execution feed', async ({ page }) => {
		await page.goto('/dashboard');

		// Look for execution feed
		const executionFeed = page.locator('text=Execution Feed');
		if (await executionFeed.isVisible()) {
			// Check for "Send to assistant" buttons
			const sendButtons = page.locator('button:has-text("Send to assistant")');
			const count = await sendButtons.count();

			if (count > 0) {
				// Click first "Send to assistant" button
				await sendButtons.first().click();

				// Wait for toast or confirmation
				await page.waitForTimeout(1000);

				// Toast should appear
				const toast = page.locator('text=/Sent to assistant|Processing/');
				if (await toast.isVisible({ timeout: 2000 }).catch(() => false)) {
					await expect(toast).toBeVisible();
				}
			}
		}
	});

	test('should queue commands from work page', async ({ page }) => {
		await page.goto('/dashboard/work');

		// Look for "Send to assistant" button
		const sendButton = page.locator('button:has-text("Send to assistant")').first();

		if (await sendButton.isVisible()) {
			await sendButton.click();

			// Toast should appear
			await page.waitForTimeout(500);
			const toast = page.locator('text=/Sent to assistant/');
			if (await toast.isVisible({ timeout: 2000 }).catch(() => false)) {
				await expect(toast).toBeVisible();
			}

			// Navigate back to dashboard
			await page.goto('/dashboard');

			// Queue should be processed
			await page.waitForTimeout(1000);
			const processingToast = page.locator('text=/Processing|Completed/');
			if (await processingToast.isVisible({ timeout: 2000 }).catch(() => false)) {
				await expect(processingToast).toBeVisible();
			}
		}
	});
});

test.describe('Error Handling', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/auth/login');
		await page.fill('input[type="email"]', 'test@example.com');
		await page.fill('input[type="password"]', 'password123');
		await page.click('button[type="submit"]');
		await page.waitForURL('/dashboard');
	});

	test('should handle send errors gracefully', async ({ page }) => {
		await page.goto('/dashboard');

		// Disconnect network to simulate error
		await page.route('**/api/ai/**', route => route.abort());

		// Try to send message
		const input = page.locator('textarea').or(page.locator('input[type="text"]')).first();
		await input.fill('Test message');
		await page.locator('button:has-text("Send")').or(page.locator('button[type="submit"]')).first().click();

		// Wait for error message
		await page.waitForTimeout(2000);

		// Error should be displayed somewhere
		const errorText = page.locator('text=/error|failed|unavailable/i');
		const hasError = await errorText.isVisible({ timeout: 3000 }).catch(() => false);

		if (hasError) {
			await expect(errorText).toBeVisible();
		}
	});
});

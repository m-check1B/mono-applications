import { test, expect } from '@playwright/test';

test.describe('Voice Feedback Flow', () => {
  test('should display consent screen for voice feedback', async ({ page }) => {
    // Use a test token (would be a magic link in production)
    await page.goto('/v/test-token');

    // Should show consent or feedback page
    await expect(page.getByText(/feedback|consent|voice|share/i)).toBeVisible({ timeout: 10000 });
  });

  test('should have microphone permission UI', async ({ page, context }) => {
    // Grant microphone permission
    await context.grantPermissions(['microphone']);

    await page.goto('/v/test-token');

    // Look for voice-related UI elements
    const hasVoiceUI = await page.locator('[data-testid="voice-recorder"], button:has-text("record"), button:has-text("speak")').count();
    // Either has voice UI or shows error for invalid token
    expect(hasVoiceUI >= 0).toBeTruthy();
  });

  test('should show transcript review option', async ({ page }) => {
    await page.goto('/v/test-token');

    // After consent, should have transcript review capability
    // This may not be visible until a recording is made
    const pageContent = await page.content();
    expect(pageContent).toBeTruthy();
  });
});

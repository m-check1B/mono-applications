import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('should display dashboard overview', async ({ page }) => {
    await expect(page.locator('text=Dashboard|Přehled').or(page.locator('h1'))).toBeVisible();
  });

  test('should show navigation menu', async ({ page }) => {
    await expect(page.locator('nav').or(page.locator('[class*="navigation"]'))).toBeVisible();
  });

  test('should have surveys link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /surveys|průzkumy/i })).toBeVisible();
  });

  test('should have employees link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /employees|zaměstnanci/i })).toBeVisible();
  });

  test('should have actions link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /actions|akce/i })).toBeVisible();
  });

  test('should have alerts link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /alerts|výstrahy/i })).toBeVisible();
  });

  test('should have settings link', async ({ page }) => {
    await expect(page.getByRole('link', { name: /settings|nastavení/i })).toBeVisible();
  });

  test('should navigate to surveys page', async ({ page }) => {
    await page.click('a:has-text("surveys"), a:has-text("průzkumy")');
    await expect(page).toHaveURL(/\/dashboard\/surveys/);
  });

  test('should navigate to employees page', async ({ page }) => {
    await page.click('a:has-text("employees"), a:has-text("zaměstnanci")');
    await expect(page).toHaveURL(/\/dashboard\/employees/);
  });

  test('should navigate to actions page', async ({ page }) => {
    await page.click('a:has-text("actions"), a:has-text("akce")');
    await expect(page).toHaveURL(/\/dashboard\/actions/);
  });

  test('should navigate to alerts page', async ({ page }) => {
    await page.click('a:has-text("alerts"), a:has-text("výstrahy")');
    await expect(page).toHaveURL(/\/dashboard\/alerts/);
  });

  test('should navigate to settings page', async ({ page }) => {
    await page.click('a:has-text("settings"), a:has-text("nastavení")');
    await expect(page).toHaveURL(/\/dashboard\/settings/);
  });
});

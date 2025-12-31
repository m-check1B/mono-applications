import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login with demo credentials
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@focus-kraliki.app');
    await page.fill('input[type="password"]', 'test123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
  });

  test('should display task dashboard', async ({ page }) => {
    await expect(page.locator('h1:has-text("Dashboard")')).toBeVisible();
    await expect(page.locator('text=Total Tasks')).toBeVisible();
    await expect(page.locator('text=Completed')).toBeVisible();
    await expect(page.locator('text=In Progress')).toBeVisible();
    await expect(page.locator('text=Overdue')).toBeVisible();
  });

  test('should create new task via quick add', async ({ page }) => {
    const taskTitle = `Test Task ${Date.now()}`;
    
    // Find quick add form
    await page.fill('input[placeholder*="task"]', taskTitle);
    await page.press('input[placeholder*="task"]', 'Enter');
    
    // Verify task appears in list
    await expect(page.locator(`text=${taskTitle}`)).toBeVisible({ timeout: 5000 });
  });

  test('should toggle task view modes', async ({ page }) => {
    // Click List View
    await page.click('button:has-text("List View")');
    await expect(page.locator('text=Your Tasks')).toBeVisible();
    
    // Click Kanban View
    await page.click('button:has-text("Kanban View")');
    await expect(page.locator('text=To Do')).toBeVisible();
    await expect(page.locator('text=In Progress')).toBeVisible();
    await expect(page.locator('text=Completed')).toBeVisible();
    
    // Click Calendar View
    await page.click('button:has-text("Calendar View")');
    await expect(page.locator('text=Calendar View')).toBeVisible();
  });

  test('should toggle task completion', async ({ page }) => {
    // Create a task first
    const taskTitle = `Toggle Task ${Date.now()}`;
    await page.fill('input[placeholder*="task"]', taskTitle);
    await page.press('input[placeholder*="task"]', 'Enter');
    
    // Find and toggle the task
    const task = page.locator(`text=${taskTitle}`).first();
    await task.locator('input[type="checkbox"]').click();
    
    // Verify task is marked as completed
    await expect(task).toHaveClass(/completed|line-through/, { timeout: 5000 });
  });

  test('should delete task', async ({ page }) => {
    // Create a task first
    const taskTitle = `Delete Task ${Date.now()}`;
    await page.fill('input[placeholder*="task"]', taskTitle);
    await page.press('input[placeholder*="task"]', 'Enter');
    
    // Find and delete the task
    const task = page.locator(`text=${taskTitle}`).first();
    await task.hover();
    await task.locator('button[aria-label*="delete"]').click();
    
    // Confirm deletion if needed
    const confirmButton = page.locator('button:has-text("Delete")');
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }
    
    // Verify task is removed
    await expect(page.locator(`text=${taskTitle}`)).not.toBeVisible({ timeout: 5000 });
  });
});
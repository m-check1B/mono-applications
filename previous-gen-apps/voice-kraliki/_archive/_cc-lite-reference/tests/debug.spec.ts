import { test, expect } from '@playwright/test';

test.describe('Debug Tests', () => {
  test('capture console errors and page content', async ({ page }) => {
    // Capture console messages
    const consoleMessages: string[] = [];
    const errors: string[] = [];
    
    page.on('console', msg => {
      consoleMessages.push(`${msg.type()}: ${msg.text()}`);
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', error => {
      errors.push(`Page error: ${error.message}`);
    });

    // Navigate to login page
    await page.goto('/login');
    
    // Wait a bit for any async errors
    await page.waitForTimeout(2000);
    
    // Log all console messages
    console.log('=== Console Messages ===');
    consoleMessages.forEach(msg => console.log(msg));
    
    // Log all errors
    console.log('=== Errors ===');
    errors.forEach(err => console.log(err));
    
    // Get page content
    const pageContent = await page.content();
    console.log('=== Page HTML (first 500 chars) ===');
    console.log(pageContent.substring(0, 500));
    
    // Check for React root
    const rootElement = await page.$('#root');
    const rootHTML = rootElement ? await rootElement.innerHTML() : 'No root element';
    console.log('=== React Root Content ===');
    console.log(rootHTML);
    
    // Try to get computed styles of body
    const bodyStyles = await page.evaluate(() => {
      const body = document.body;
      const styles = window.getComputedStyle(body);
      return {
        backgroundColor: styles.backgroundColor,
        color: styles.color,
        display: styles.display
      };
    });
    console.log('=== Body Styles ===');
    console.log(JSON.stringify(bodyStyles, null, 2));
    
    // Check for any visible text
    const visibleText = await page.textContent('body');
    console.log('=== Visible Text ===');
    console.log(visibleText?.trim() || 'No visible text');
    
    // Check network failures
    const failedRequests: string[] = [];
    page.on('requestfailed', request => {
      failedRequests.push(`${request.url()} - ${request.failure()?.errorText}`);
    });
    
    // Reload to capture network errors
    await page.reload();
    await page.waitForTimeout(2000);
    
    console.log('=== Failed Requests ===');
    failedRequests.forEach(req => console.log(req));
    
    // Assert page has content (will fail if blank)
    expect(errors.length).toBe(0);
  });
});
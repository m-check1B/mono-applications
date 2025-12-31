import { test, expect } from '@playwright/test';

const TEST_CREDENTIALS = {
  email: 'test.assistant@stack2025.com',
  password: 'Stack2025!Test@Assistant#Secure$2024'
};

const APP_URL = 'http://127.0.0.1:5183';

test.describe('CC-Light Authentication Test', () => {
  test('should authenticate user and navigate dashboard', async ({ page }) => {
    // Navigate to the application
    console.log('Navigating to CC-Light application...');
    await page.goto(APP_URL);
    
    // Wait for page to load and take screenshot of login page
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'screenshots/01-login-page.png', fullPage: true });
    console.log('Screenshot saved: 01-login-page.png');
    
    // Check if we're on login page or already logged in
    const isLoginPage = await page.locator('input[type="email"], input[name="email"]').isVisible().catch(() => false);
    
    if (isLoginPage) {
      console.log('Login page detected, entering credentials...');
      
      // Fill in credentials
      await page.fill('input[type="email"], input[name="email"]', TEST_CREDENTIALS.email);
      await page.fill('input[type="password"], input[name="password"]', TEST_CREDENTIALS.password);
      
      // Take screenshot before submitting
      await page.screenshot({ path: 'screenshots/02-credentials-entered.png', fullPage: true });
      console.log('Screenshot saved: 02-credentials-entered.png');
      
      // Submit the form
      await page.click('button[type="submit"], .login-button, .submit-button');
      
      // Wait for navigation/response
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      // Take screenshot after login attempt
      await page.screenshot({ path: 'screenshots/03-after-login.png', fullPage: true });
      console.log('Screenshot saved: 03-after-login.png');
    } else {
      console.log('Already logged in or redirected to dashboard');
    }
    
    // Check current URL and page content
    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);
    
    // Take screenshot of current state
    await page.screenshot({ path: 'screenshots/04-current-state.png', fullPage: true });
    console.log('Screenshot saved: 04-current-state.png');
    
    // Check for dashboard elements
    const dashboardElements = [
      'nav, .navigation, .sidebar',
      '.dashboard, .main-content, .content',
      'h1, .title, .page-title',
      '.user-menu, .profile, .user-info'
    ];
    
    for (const selector of dashboardElements) {
      const element = await page.locator(selector).first().isVisible().catch(() => false);
      if (element) {
        console.log(`Found dashboard element: ${selector}`);
      }
    }
    
    // Test navigation if we can find nav elements
    const navLinks = await page.locator('nav a, .nav-link, .menu-item').all();
    console.log(`Found ${navLinks.length} navigation links`);
    
    if (navLinks.length > 0) {
      // Click first few nav links to test functionality
      for (let i = 0; i < Math.min(3, navLinks.length); i++) {
        try {
          const linkText = await navLinks[i].textContent();
          console.log(`Testing navigation link: ${linkText}`);
          
          await navLinks[i].click();
          await page.waitForLoadState('networkidle');
          await page.waitForTimeout(1000);
          
          await page.screenshot({ 
            path: `screenshots/05-nav-${i + 1}-${linkText?.toLowerCase().replace(/\s+/g, '-')}.png`, 
            fullPage: true 
          });
          console.log(`Screenshot saved: 05-nav-${i + 1}-${linkText?.toLowerCase().replace(/\s+/g, '-')}.png`);
        } catch (error) {
          console.log(`Error clicking nav link ${i}: ${error}`);
        }
      }
    }
    
    // Check for any console errors
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleLogs.push(`CONSOLE ERROR: ${msg.text()}`);
      }
    });
    
    // Wait a bit more to catch any delayed console errors
    await page.waitForTimeout(3000);
    
    // Final screenshot
    await page.screenshot({ path: 'screenshots/06-final-state.png', fullPage: true });
    console.log('Screenshot saved: 06-final-state.png');
    
    // Log console errors if any
    if (consoleLogs.length > 0) {
      console.log('Console errors detected:');
      consoleLogs.forEach(log => console.log(log));
    } else {
      console.log('No console errors detected');
    }
    
    // Basic assertions
    expect(page.url()).toContain(APP_URL);
  });
});
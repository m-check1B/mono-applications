import { test, expect } from '@playwright/test';

test.describe('App Verification with Screenshots', () => {
  test('capture full application flow', async ({ page }) => {
    // 1. Visit homepage and capture
    await page.goto('/');
    await page.waitForTimeout(2000); // Allow time for React to mount
    await page.screenshot({ path: 'screenshots/01-homepage.png', fullPage: true });
    console.log('✅ Screenshot 1: Homepage captured');

    // 2. Check if login page loads
    const hasLoginForm = await page.locator('input[type="email"]').isVisible().catch(() => false);
    
    if (hasLoginForm) {
      console.log('✅ Login form detected');
      await page.screenshot({ path: 'screenshots/02-login-form.png', fullPage: true });
      
      // 3. Try to login with demo credentials
      await page.fill('input[type="email"]', 'test@focus-kraliki.app');
      await page.fill('input[type="password"]', 'test123');
      await page.screenshot({ path: 'screenshots/03-credentials-filled.png', fullPage: true });
      
      // 4. Submit login
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000); // Wait for login to process
      await page.screenshot({ path: 'screenshots/04-after-login.png', fullPage: true });
      
      // 5. Check if dashboard loads
      const hasDashboard = await page.locator('text=Dashboard').isVisible().catch(() => false);
      if (hasDashboard) {
        console.log('✅ Dashboard loaded successfully');
        await page.screenshot({ path: 'screenshots/05-dashboard.png', fullPage: true });
        
        // 6. Navigate to different sections
        const sections = [
          { name: 'AI Chat', file: '06-ai-chat.png' },
          { name: 'Shadow Work', file: '07-shadow-work.png' },
          { name: 'Cognitive', file: '08-cognitive.png' },
          { name: 'Types', file: '09-types.png' },
          { name: 'Settings', file: '10-settings.png' }
        ];
        
        for (const section of sections) {
          const sectionElement = await page.locator(`text=${section.name}`).first();
          if (await sectionElement.isVisible().catch(() => false)) {
            await sectionElement.click();
            await page.waitForTimeout(2000);
            await page.screenshot({ path: `screenshots/${section.file}`, fullPage: true });
            console.log(`✅ Screenshot: ${section.name} captured`);
          }
        }
      }
    } else {
      console.log('⚠️ App might be loading or has different structure');
      // Capture whatever is on the page
      await page.screenshot({ path: 'screenshots/app-state.png', fullPage: true });
      
      // Log page content for debugging
      const pageTitle = await page.title();
      const pageContent = await page.content();
      console.log('Page Title:', pageTitle);
      console.log('Page has content:', pageContent.length > 0);
      
      // Check for any React error boundaries
      const hasError = await page.locator('text=Error').isVisible().catch(() => false);
      if (hasError) {
        console.log('❌ Error detected on page');
        await page.screenshot({ path: 'screenshots/error-state.png', fullPage: true });
      }
    }

    // Final verification
    const finalTitle = await page.title();
    expect(finalTitle).toContain('Focus by Kraliki');
    console.log('✅ Page title verified:', finalTitle);
  });

  test('verify API connectivity', async ({ request }) => {
    // Test backend connectivity
    const api =
      process.env.FOCUS_KRALIKI_API_URL ||
      process.env.FOCUS_KRALIKI_API_URL || process.env.FOCUS_LITE_API_URL ||
      process.env.API_URL ||
      'https://focus-kraliki-api.verduona.dev';
    const response = await request.get(`${api}/trpc`);
    console.log('Backend response status:', response.status());
    expect([200, 404]).toContain(response.status()); // 404 is ok for GET on tRPC
    console.log('✅ Backend is reachable');
  });

  test('capture browser console logs', async ({ page }) => {
    const consoleLogs: string[] = [];
    const consoleErrors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      } else {
        consoleLogs.push(msg.text());
      }
    });
    
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    if (consoleErrors.length > 0) {
      console.log('❌ Console Errors:', consoleErrors);
    } else {
      console.log('✅ No console errors');
    }
    
    if (consoleLogs.length > 0) {
      console.log('📝 Console Logs:', consoleLogs.slice(0, 5)); // First 5 logs
    }
    
    // Capture final state
    await page.screenshot({ path: 'screenshots/final-state.png', fullPage: true });
  });
});

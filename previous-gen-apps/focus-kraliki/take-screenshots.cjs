const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Login page
    await page.goto('http://localhost:5173/login');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/tmp/screenshot-login-light.png', fullPage: false });
    console.log('✓ Login page (light mode) captured');

    // Toggle to dark mode
    const themeToggle = page.locator('button[title="Toggle Theme"]');
    if (await themeToggle.count() > 0) {
      await themeToggle.click();
      await page.waitForTimeout(500);
      // Click dark mode option
      await page.locator('text=Dark').click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: '/tmp/screenshot-login-dark.png', fullPage: false });
      console.log('✓ Login page (dark mode) captured');
    }

    // Register page
    await page.goto('http://localhost:5173/register');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/tmp/screenshot-register.png', fullPage: false });
    console.log('✓ Register page captured');

    // Try to get dashboard if we can (might need login)
    try {
      await page.goto('http://localhost:5173/dashboard');
      await page.waitForTimeout(2000);
      await page.screenshot({ path: '/tmp/screenshot-dashboard.png', fullPage: false });
      console.log('✓ Dashboard page captured');
    } catch (e) {
      console.log('⚠ Could not capture dashboard (login required)');
    }

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
})();

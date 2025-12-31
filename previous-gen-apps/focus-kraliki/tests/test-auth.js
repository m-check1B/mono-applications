const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Enable console logging
  page.on('console', msg => console.log('Browser console:', msg.text()));
  page.on('pageerror', err => console.error('Browser error:', err));
  page.on('response', response => {
    if (response.url().includes('/trpc/')) {
      console.log(`API Response: ${response.url()} - Status: ${response.status()}`);
    }
  });

  try {
    console.log('1. Navigating to login page...');
    await page.goto('https://focus.verduona.dev/login', { waitUntil: 'networkidle' });
    
    console.log('2. Taking screenshot of login page...');
    await page.screenshot({ path: 'login-page.png' });

    console.log('3. Filling in login form...');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpass123');

    console.log('4. Clicking login button...');
    await Promise.all([
      page.waitForResponse(response => 
        response.url().includes('/trpc/auth.login') && response.status() === 200,
        { timeout: 10000 }
      ).then(response => {
        console.log('Login response received:', response.status());
        return response.json().then(data => console.log('Response data:', JSON.stringify(data)));
      }).catch(err => console.error('Failed to get login response:', err)),
      page.click('button[type="submit"]')
    ]);

    console.log('5. Waiting for navigation...');
    await page.waitForTimeout(2000);

    console.log('6. Current URL:', page.url());
    
    console.log('7. Taking screenshot after login...');
    await page.screenshot({ path: 'after-login.png' });

    if (!page.url().includes('/login')) {
      console.log('✅ SUCCESS: Login worked! User is redirected from login page');
    } else {
      console.log('❌ FAILURE: Still on login page');
      // Check for error messages
      const errorElement = await page.$('[role="alert"], .error, .text-red-500');
      if (errorElement) {
        const errorText = await errorElement.textContent();
        console.log('Error message found:', errorText);
      }
    }

  } catch (error) {
    console.error('Test failed:', error);
    await page.screenshot({ path: 'error-state.png' });
  } finally {
    await browser.close();
  }
})();
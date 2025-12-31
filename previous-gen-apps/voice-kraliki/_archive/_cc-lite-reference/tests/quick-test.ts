import { chromium } from 'playwright';

async function quickTest() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('📸 Taking screenshot of login page...');
  await page.goto('http://localhost:3001');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: 'screenshots/login-page.png', fullPage: true });
  
  // Check what's on the page
  const content = await page.content();
  console.log('Page title:', await page.title());
  
  // Look for input fields
  const emailField = await page.locator('input[name="email"]').count();
  const passwordField = await page.locator('input[name="password"]').count();
  
  console.log('Email field found:', emailField > 0);
  console.log('Password field found:', passwordField > 0);
  
  // Try different selectors
  const emailPlaceholder = await page.locator('input[placeholder*="email" i]').count();
  const passwordPlaceholder = await page.locator('input[placeholder*="password" i]').count();
  
  console.log('Email placeholder found:', emailPlaceholder > 0);
  console.log('Password placeholder found:', passwordPlaceholder > 0);
  
  // Check for login button
  const loginButton = await page.locator('button:has-text("Sign In")').count();
  const loginButton2 = await page.locator('button:has-text("Login")').count();
  
  console.log('Sign In button found:', loginButton > 0);
  console.log('Login button found:', loginButton2 > 0);
  
  await browser.close();
  console.log('✅ Quick test complete. Check screenshots/login-page.png');
}

quickTest().catch(console.error);
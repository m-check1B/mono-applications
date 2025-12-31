const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function testFocusKralikiApp() {
  console.log('🚀 Starting Focus by Kraliki App Tests...\n');
  
  // Create screenshots directory
  const screenshotsDir = path.join(__dirname, 'test-screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir);
  }

  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1280, height: 720 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  
  try {
    console.log('📱 Testing Frontend Server...');
    
    // Test 1: Load the application
    console.log('1. Loading application at http://localhost:5176');
    await page.goto('http://localhost:5176', { waitUntil: 'networkidle0' });
    await page.screenshot({ path: path.join(screenshotsDir, '01-app-loaded.png'), fullPage: true });
    
    // Check if the page title is correct
    const title = await page.title();
    console.log(`   ✓ Page Title: ${title}`);
    
    // Test 2: Check for login page elements
    console.log('2. Checking login page elements...');
    
    // Wait for login form to be visible
    try {
      await page.waitForSelector('h1', { timeout: 5000 });
      const h1Text = await page.$eval('h1', el => el.textContent);
      console.log(`   ✓ H1 Text: ${h1Text}`);
      
      await page.waitForSelector('input[type="email"]', { timeout: 5000 });
      console.log('   ✓ Email input field found');
      
      await page.waitForSelector('input[type="password"]', { timeout: 5000 });
      console.log('   ✓ Password input field found');
      
      await page.waitForSelector('button[type="submit"]', { timeout: 5000 });
      console.log('   ✓ Submit button found');
      
    } catch (error) {
      console.log('   ❌ Login form elements not found, checking current state...');
      
      // Check what's actually on the page
      const bodyText = await page.evaluate(() => document.body.textContent);
      console.log(`   📝 Page content: ${bodyText.substring(0, 200)}...`);
      
      // Check for any error messages in console
      const consoleErrors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });
      
      if (consoleErrors.length > 0) {
        console.log('   🚨 Console errors:');
        consoleErrors.forEach(error => console.log(`     - ${error}`));
      }
    }
    
    await page.screenshot({ path: path.join(screenshotsDir, '02-login-page.png'), fullPage: true });
    
    // Test 3: Try demo login
    console.log('3. Testing demo login...');
    
    try {
      // Fill in demo credentials if form exists
      const emailInput = await page.$('input[type="email"]');
      const passwordInput = await page.$('input[type="password"]');
      
      if (emailInput && passwordInput) {
        await emailInput.type('test@focus-kraliki.app');
        await passwordInput.type('test123');
        
        await page.screenshot({ path: path.join(screenshotsDir, '03-credentials-filled.png'), fullPage: true });
        
        // Click submit
        await page.click('button[type="submit"]');
        
        // Wait for potential redirect or response
        await page.waitForTimeout(3000);
        await page.screenshot({ path: path.join(screenshotsDir, '04-after-login-attempt.png'), fullPage: true });
        
        console.log('   ✓ Login attempt completed');
        
        // Check if we're now on the dashboard
        const currentUrl = page.url();
        console.log(`   📍 Current URL: ${currentUrl}`);
        
        // Look for dashboard elements
        try {
          await page.waitForSelector('[data-testid="dashboard"], .dashboard, text=Dashboard', { timeout: 3000 });
          console.log('   ✓ Dashboard loaded successfully!');
          await page.screenshot({ path: path.join(screenshotsDir, '05-dashboard-loaded.png'), fullPage: true });
        } catch (dashboardError) {
          console.log('   ℹ️  Dashboard not detected, might still be on login page');
        }
        
      } else {
        console.log('   ❌ Login form inputs not found');
      }
      
    } catch (loginError) {
      console.log(`   ❌ Login test failed: ${loginError.message}`);
    }
    
    // Test 4: Check for key UI components
    console.log('4. Checking for key UI components...');
    
    // Look for common UI elements
    const selectors = [
      'button',
      'input',
      'nav',
      '.card, [class*="card"]',
      '.sidebar, [class*="sidebar"]',
      '.header, [class*="header"]'
    ];
    
    for (const selector of selectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          console.log(`   ✓ Found element: ${selector}`);
        } else {
          console.log(`   - No element found: ${selector}`);
        }
      } catch (error) {
        console.log(`   - Error checking ${selector}: ${error.message}`);
      }
    }
    
    await page.screenshot({ path: path.join(screenshotsDir, '06-final-state.png'), fullPage: true });
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ path: path.join(screenshotsDir, '99-error-state.png'), fullPage: true });
  } finally {
    await browser.close();
  }
  
  console.log('\n✅ Test completed! Screenshots saved to:', screenshotsDir);
  console.log('📊 Check the screenshots to verify app functionality.');
}

// Test backend connectivity
async function testBackend() {
  console.log('\n🔌 Testing Backend Connectivity...');
  
  try {
    const api =
      process.env.FOCUS_KRALIKI_API_URL ||
      process.env.FOCUS_KRALIKI_API_URL || process.env.FOCUS_LITE_API_URL ||
      'http://127.0.0.1:3804';
    const response = await fetch(`${api}/trpc`);
    console.log(`   ✓ Backend responding with status: ${response.status}`);
    
    if (response.status === 404) {
      console.log('   ℹ️  404 is expected for tRPC base path - backend is running');
    }
  } catch (error) {
    console.log(`   ❌ Backend connection failed: ${error.message}`);
  }
}

// Run tests
async function main() {
  await testBackend();
  await testFocusKralikiApp();
}

main().catch(console.error);

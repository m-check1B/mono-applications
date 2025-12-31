const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Listen for console messages
  page.on('console', msg => {
    console.log(`Console ${msg.type()}: ${msg.text()}`);
  });
  
  page.on('pageerror', error => {
    console.log(`Page error: ${error.message}`);
  });

  await page.goto('http://localhost:3006');
  await page.waitForTimeout(3000);
  
  // Check for bug report button
  const bugButton = await page.$('[data-testid="bug-report-button"], button:has-text("Report Bug"), .bug-report-floating-button');
  
  if (bugButton) {
    console.log('✅ Bug report button found!');
    await page.screenshot({ path: 'cc-light-with-bug-button.png' });
  } else {
    console.log('❌ Bug report button NOT found');
    // Try to see what's on the page
    const html = await page.content();
    console.log('Page HTML snippet:', html.substring(0, 500));
  }
  
  await browser.close();
})();
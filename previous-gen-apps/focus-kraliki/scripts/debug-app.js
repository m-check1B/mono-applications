const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capture console messages
  page.on('console', msg => {
    console.log(`[${msg.type()}]`, msg.text());
  });
  
  // Capture page errors
  page.on('pageerror', err => {
    console.error('Page Error:', err.message);
  });
  
  // Capture request failures
  page.on('requestfailed', request => {
    console.error('Request failed:', request.url(), request.failure().errorText);
  });
  
  console.log('Opening http://localhost:5176...');
  await page.goto('http://localhost:5176');
  
  // Wait for React to mount
  await page.waitForTimeout(3000);
  
  // Check if root element exists
  const rootElement = await page.$('#root');
  if (rootElement) {
    const innerHTML = await rootElement.innerHTML();
    console.log('Root element content length:', innerHTML.length);
    if (innerHTML.length < 50) {
      console.log('⚠️ Root element is empty or nearly empty');
      console.log('Root HTML:', innerHTML);
    }
  } else {
    console.log('❌ No root element found');
  }
  
  // Check for React DevTools
  const hasReact = await page.evaluate(() => {
    return window.React || window._react || document.querySelector('[data-reactroot]');
  });
  console.log('React detected:', !!hasReact);
  
  // Get all script tags
  const scripts = await page.$$eval('script', scripts => 
    scripts.map(s => ({ src: s.src, type: s.type }))
  );
  console.log('Scripts loaded:', scripts.length);
  
  // Check network activity
  const responses = [];
  page.on('response', response => {
    if (response.status() >= 400) {
      responses.push({ url: response.url(), status: response.status() });
    }
  });
  
  await page.reload();
  await page.waitForTimeout(2000);
  
  if (responses.length > 0) {
    console.log('Failed network requests:', responses);
  }
  
  // Try to get any error messages
  const errors = await page.$$eval('.error, [class*="error"], [class*="Error"]', elements => 
    elements.map(el => el.textContent)
  );
  if (errors.length > 0) {
    console.log('Error elements found:', errors);
  }
  
  console.log('\n📸 Taking screenshot...');
  await page.screenshot({ path: 'debug-screenshot.png' });
  console.log('Screenshot saved as debug-screenshot.png');
  
  console.log('\nKeeping browser open for manual inspection...');
  console.log('Press Ctrl+C to close');
  
  // Keep browser open
  await new Promise(() => {});
})();
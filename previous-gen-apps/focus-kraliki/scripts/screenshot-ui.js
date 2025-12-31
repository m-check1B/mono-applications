// Screenshot key UI states: login, AI Home, Type Manager overlay
// Usage: node apps/focus-kraliki/screenshot-ui.js
// Requires: playwright installed (pnpm -C apps/focus-kraliki dlx playwright install --with-deps)

const { chromium } = require('playwright');

async function ensureScreenshotsDir(fs, path) {
  const dir = path.join(__dirname, 'screenshots');
  try {
    await fs.promises.mkdir(dir, { recursive: true });
  } catch {}
  return dir;
}

(async () => {
  const fs = require('fs');
  const path = require('path');
  const outDir = await ensureScreenshotsDir(fs, path);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // Log some network info for debugging
  page.on('response', (response) => {
    const url = response.url();
    if (url.includes('/trpc/')) {
      console.log(`[tRPC] ${response.status()} ${url}`);
    }
  });

  try {
    // 1) Login page
    console.log('Navigating to login…');
    await page.goto('https://focus.verduona.dev/login', { waitUntil: 'networkidle', timeout: 30000 });
    await page.screenshot({ path: path.join(outDir, '01-login.png'), fullPage: true });

    // 2) Login
    console.log('Logging in…');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpass123');

    const loginResp = page.waitForResponse((r) => r.url().includes('/trpc/auth.login'));
    await page.click('button[type="submit"]');
    await loginResp.catch(() => null);

    // 3) Wait for AI workspace loaded (textarea placeholder)
    await page.waitForSelector('textarea[placeholder^="Describe your work"]', { timeout: 15000 });
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(outDir, '02-ai-home.png'), fullPage: true });

    // 4) Open Type Manager via Projects +
    console.log('Opening Type Manager overlay…');
    await page.click('button[title="Quick type manager"]', { timeout: 10000 });
    await page.waitForSelector('text=Type Configuration', { timeout: 10000 });
    await page.screenshot({ path: path.join(outDir, '03-type-manager.png'), fullPage: true });

    // 5) Close overlay
    await page.click('button[title="Close"]');
    await page.waitForSelector('text=Type Configuration', { state: 'detached', timeout: 10000 });

    // 6) Submit a sample input and capture output
    console.log('Submitting sample input…');
    await page.fill('textarea[placeholder^="Describe your work"]', 'Plan my afternoon: finish report and gym at 6pm');
    const chatResp = page.waitForResponse((r) => r.url().includes('/trpc/ai.chat'));
    const taskResp = page.waitForResponse((r) => r.url().includes('/trpc/task.create'));
    await page.keyboard.press('Enter');
    await Promise.race([
      Promise.allSettled([chatResp, taskResp]),
      page.waitForTimeout(5000),
    ]);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outDir, '04-ai-home-with-output.png'), fullPage: true });

    console.log('Screenshots saved to:', outDir);
  } catch (err) {
    console.error('Screenshot script failed:', err);
    await page.screenshot({ path: require('path').join(outDir, 'error.png'), fullPage: true }).catch(() => {});
  } finally {
    await browser.close();
  }
})();


import { Page, expect } from '@playwright/test';
import path from 'path';

export class TestUtils {
  private page: Page;
  private screenshotsDir: string;

  constructor(page: Page, screenshotsDir?: string) {
    this.page = page;
    this.screenshotsDir = screenshotsDir || path.join(process.cwd(), 'test-results', 'screenshots');
  }

  // Helper for taking screenshots with timestamps
  async takeScreenshot(name: string, description?: string) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}_${timestamp}.png`;
    const filepath = path.join(this.screenshotsDir, filename);

    await this.page.screenshot({
      path: filepath,
      fullPage: true
    });

    console.log(`📸 Screenshot saved: ${filename}`);
    if (description) {
      console.log(`   Description: ${description}`);
    }

    return filepath;
  }

  // Helper for waiting with retry logic
  async waitForSelector(selector: string, options: { timeout?: number; state?: string } = {}) {
    const { timeout = 10000, state = 'visible' } = options;

    try {
      await this.page.waitForSelector(selector, { timeout, state });
      return true;
    } catch (error) {
      console.log(`⚠️  Selector not found: ${selector}, retrying...`);
      // Wait a bit more and try again
      await this.page.waitForTimeout(2000);
      try {
        await this.page.waitForSelector(selector, { timeout: 5000, state });
        return true;
      } catch (retryError) {
        console.error(`❌ Selector failed after retry: ${selector}`);
        throw retryError;
      }
    }
  }

  // Helper for safe clicking with retry
  async safeClick(selector: string, options: { timeout?: number; force?: boolean } = {}) {
    const { timeout = 10000, force = false } = options;

    try {
      await this.page.click(selector, { timeout, force });
      return true;
    } catch (error) {
      console.log(`⚠️  Click failed: ${selector}, retrying...`);
      await this.page.waitForTimeout(1000);
      try {
        await this.page.click(selector, { timeout: 5000, force });
        return true;
      } catch (retryError) {
        console.error(`❌ Click failed after retry: ${selector}`);
        throw retryError;
      }
    }
  }

  // Helper for safe filling with retry
  async safeFill(selector: string, value: string, options: { timeout?: number } = {}) {
    const { timeout = 10000 } = options;

    try {
      await this.page.fill(selector, value, { timeout });
      return true;
    } catch (error) {
      console.log(`⚠️  Fill failed: ${selector}, retrying...`);
      await this.page.waitForTimeout(1000);
      try {
        await this.page.fill(selector, value, { timeout: 5000 });
        return true;
      } catch (retryError) {
        console.error(`❌ Fill failed after retry: ${selector}`);
        throw retryError;
      }
    }
  }

  // Helper for navigation with retry
  async safeNavigate(url: string, options: { timeout?: number; waitUntil?: string } = {}) {
    const { timeout = 30000, waitUntil = 'networkidle' } = options;

    try {
      await this.page.goto(url, { timeout, waitUntil });
      return true;
    } catch (error) {
      console.log(`⚠️  Navigation failed: ${url}, retrying...`);
      await this.page.waitForTimeout(2000);
      try {
        await this.page.goto(url, { timeout: 15000, waitUntil });
        return true;
      } catch (retryError) {
        console.error(`❌ Navigation failed after retry: ${url}`);
        throw retryError;
      }
    }
  }

  // Helper for checking element existence
  async elementExists(selector: string, timeout = 5000) {
    try {
      await this.page.waitForSelector(selector, { timeout, state: 'attached' });
      return true;
    } catch {
      return false;
    }
  }

  // Helper for getting element text
  async getText(selector: string, timeout = 5000) {
    try {
      const element = await this.page.waitForSelector(selector, { timeout });
      return await element.textContent();
    } catch {
      return null;
    }
  }

  // Helper for checking if element is visible
  async isVisible(selector: string, timeout = 5000) {
    try {
      const element = await this.page.waitForSelector(selector, { timeout, state: 'visible' });
      return await element.isVisible();
    } catch {
      return false;
    }
  }

  // Helper for waiting for network idle
  async waitForNetworkIdle(timeout = 10000) {
    try {
      await this.page.waitForLoadState('networkidle', { timeout });
      return true;
    } catch (error) {
      console.log('⚠️  Network idle timeout, continuing...');
      return false;
    }
  }

  // Helper for handling file uploads
  async uploadFile(selector: string, filePath: string) {
    const fileInput = await this.page.waitForSelector(selector);
    await fileInput.setInputFiles(filePath);
    console.log(`📁 File uploaded: ${filePath}`);
  }

  // Helper for handling alerts and dialogs
  async handleDialog(dialogType: 'accept' | 'dismiss' = 'accept') {
    this.page.on('dialog', async dialog => {
      if (dialogType === 'accept') {
        await dialog.accept();
      } else {
        await dialog.dismiss();
      }
    });
  }

  // Helper for getting test user data
  getTestData() {
    const fs = require('fs');
    const testDataPath = path.join(process.cwd(), 'test-results', 'test-user.json');

    if (fs.existsSync(testDataPath)) {
      return JSON.parse(fs.readFileSync(testDataPath, 'utf8'));
    }

    // Return default test data if file doesn't exist
    return {
      email: 'test@focus-kraliki.app',
      name: 'Test User',
      password: 'test123'
    };
  }

  // Helper for generating unique test data
  generateUniqueData(prefix = 'test') {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);

    return {
      email: `${prefix}-${timestamp}-${random}@focus-kraliki.test`,
      name: `${prefix.charAt(0).toUpperCase() + prefix.slice(1)} User ${timestamp}`,
      password: 'test123456',
      title: `${prefix.charAt(0).toUpperCase() + prefix.slice(1)} Task ${timestamp}`,
      description: `This is a test ${prefix} created at ${new Date().toISOString()}`
    };
  }

  // Helper for performance measurements
  async measurePerformance(name: string, action: () => Promise<void>) {
    const startTime = performance.now();
    console.log(`⏱️  Starting ${name}...`);

    await action();

    const endTime = performance.now();
    const duration = endTime - startTime;
    console.log(`⏱️  ${name} completed in ${duration.toFixed(2)}ms`);

    return duration;
  }
}

export default TestUtils;
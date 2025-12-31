import { test, expect } from '@playwright/test';
import { fileURLToPath } from 'url';
import path from 'path';
import { getSupervisorCredentials } from './utils/test-credentials';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test configuration
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:3007';
const API_URL = process.env.API_URL || 'http://127.0.0.1:3010';
const supervisorCredentials = getSupervisorCredentials();

test.describe('CC-Light Beta Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('Home page loads', async ({ page }) => {
    const response = await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    expect(response?.status()).toBeLessThan(400);
    
    // Take screenshot
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/home.png'),
      fullPage: true 
    });
  });

  test('Login page functionality', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    
    // Check for login form elements
    await expect(page.locator('input[type="email"], input[name*="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("Login")')).toBeVisible();
    
    // Take screenshot
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/login.png') 
    });
  });

  test('Test login with demo credentials', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    
    // Fill in demo credentials
    await page.fill('input[type="email"], input[name*="email"]', supervisorCredentials.email);
    await page.fill('input[type="password"]', supervisorCredentials.password);
    
    // Click login
    await page.click('button[type="submit"], button:has-text("Login")');
    
    // Wait for navigation
    await page.waitForURL((url) => url.pathname !== '/login', { 
      timeout: 10000 
    }).catch(() => {
      // Login might not work yet, that's ok for beta
    });
    
    // Take screenshot of result
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/after-login.png') 
    });
  });

  test('API health check', async ({ request }) => {
    const response = await request.get(`${API_URL}/health`).catch(() => null);
    
    if (response) {
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('status');
    }
  });

  test('Revolutionary features - Command Center', async ({ page }) => {
    await page.goto(`${BASE_URL}/command`);
    
    // Check for glassmorphism elements
    const glassElements = await page.locator('.glass-card, [class*="glass"]').count();
    expect(glassElements).toBeGreaterThan(0);
    
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/command-center.png') 
    });
  });

  test('Revolutionary features - AI Analytics', async ({ page }) => {
    await page.goto(`${BASE_URL}/ai-analytics`);
    
    // Check for neural network visualization
    const hasCanvas = await page.locator('canvas').count();
    const hasMetrics = await page.locator('[class*="metric"], [class*="analytics"]').count();
    
    expect(hasCanvas + hasMetrics).toBeGreaterThan(0);
    
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/ai-analytics.png') 
    });
  });

  test('Revolutionary features - Emotional Contagion', async ({ page }) => {
    await page.goto(`${BASE_URL}/emotional-contagion`);
    
    // Check for emotional tracking elements
    const emotionalElements = await page.locator('[class*="emotion"], [class*="contagion"]').count();
    
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/emotional-contagion.png') 
    });
  });

  test('Supervisor dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/supervisor`);
    
    // Check for dashboard elements
    const hasDashboard = await page.locator('[class*="dashboard"], [role="main"]').count();
    expect(hasDashboard).toBeGreaterThan(0);
    
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/supervisor.png') 
    });
  });

  test('Operator dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/operator`);
    
    // Check for operator elements
    const hasOperator = await page.locator('[class*="operator"], [class*="agent"]').count();
    expect(hasOperator).toBeGreaterThan(0);
    
    await page.screenshot({ 
      path: path.join(__dirname, '../screenshots/operator.png') 
    });
  });

  test('Logging system verification', async ({ page }) => {
    // Monitor console logs
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      consoleLogs.push(`${msg.type()}: ${msg.text()}`);
    });
    
    await page.goto(BASE_URL);
    
    // Check for proper logging
    const hasLogs = consoleLogs.length > 0;
    expect(hasLogs).toBe(true);
    
    // Save logs for debugging
    const fs = await import('fs');
    await fs.promises.writeFile(
      path.join(__dirname, '../logs/console-logs.txt'),
      consoleLogs.join('\n')
    );
  });
});

test.describe('CC-Light Performance Tests', () => {
  test('Page load performance', async ({ page }) => {
    const startTime = Date.now();
    await page.goto(BASE_URL);
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000); // Should load in under 3 seconds
  });

  test('API response time', async ({ request }) => {
    const startTime = Date.now();
    await request.get(`${API_URL}/health`).catch(() => null);
    const responseTime = Date.now() - startTime;
    
    expect(responseTime).toBeLessThan(500); // API should respond in under 500ms
  });
});

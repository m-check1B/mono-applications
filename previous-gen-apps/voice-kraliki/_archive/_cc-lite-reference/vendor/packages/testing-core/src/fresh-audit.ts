#!/usr/bin/env tsx

import { chromium } from 'playwright';
import chalk from 'chalk';
import fs from 'fs';
import path from 'path';

async function performFreshAudit() {
  console.log(chalk.cyan.bold('\n🔍 STACK 2025 FRESH AUDIT - NO ASSUMPTIONS\n'));
  console.log(chalk.gray('=' .repeat(60)));
  
  const auditResults = {
    frontend: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
    backend: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
    packages: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
    database: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
    authentication: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
    ui_components: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
    testing: { status: 'unknown', issues: [] as string[], successes: [] as string[] },
  };

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 1. FRONTEND AUDIT
  console.log(chalk.yellow('\n📱 FRONTEND AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  try {
    // Check if frontend responds
    const frontendResponse = await page.goto('http://localhost:5178/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    if (frontendResponse?.ok()) {
      auditResults.frontend.successes.push('Frontend server responds on port 5178');
      console.log(chalk.green('  ✓ Frontend server running'));
    } else {
      auditResults.frontend.issues.push('Frontend server not responding properly');
      console.log(chalk.red('  ✗ Frontend server issue'));
    }

    // Check for JavaScript errors
    const jsErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        jsErrors.push(msg.text());
      }
    });
    
    await page.reload();
    await page.waitForTimeout(2000);
    
    if (jsErrors.length > 0) {
      auditResults.frontend.issues.push(`${jsErrors.length} JavaScript errors found`);
      console.log(chalk.red(`  ✗ JavaScript errors: ${jsErrors.length}`));
      jsErrors.forEach(err => console.log(chalk.gray(`    - ${err.substring(0, 80)}`)));
    } else {
      auditResults.frontend.successes.push('No JavaScript errors');
      console.log(chalk.green('  ✓ No JavaScript errors'));
    }

    // Check if login form exists
    const emailInput = await page.locator('input[type="email"]').count();
    const passwordInput = await page.locator('input[type="password"]').count();
    
    if (emailInput > 0 && passwordInput > 0) {
      auditResults.frontend.successes.push('Login form present');
      console.log(chalk.green('  ✓ Login form found'));
    } else {
      auditResults.frontend.issues.push('Login form missing or incomplete');
      console.log(chalk.red('  ✗ Login form not found'));
    }

    // Check page title
    const title = await page.title();
    if (title && title.includes('ProductivityHub')) {
      auditResults.frontend.successes.push(`Page title set: ${title}`);
      console.log(chalk.green(`  ✓ Page title: ${title}`));
    } else {
      auditResults.frontend.issues.push('Page title missing or incorrect');
      console.log(chalk.red('  ✗ Page title issue'));
    }

    // Capture screenshot for evidence
    await page.screenshot({ path: 'audit-frontend.png' });
    console.log(chalk.blue('  📸 Screenshot saved: audit-frontend.png'));
    
    auditResults.frontend.status = auditResults.frontend.issues.length === 0 ? 'working' : 'issues';
    
  } catch (error) {
    auditResults.frontend.status = 'failed';
    auditResults.frontend.issues.push(`Frontend completely failed: ${error}`);
    console.log(chalk.red(`  ✗ Frontend failed: ${error}`));
  }

  // 2. BACKEND AUDIT
  console.log(chalk.yellow('\n🔌 BACKEND AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  try {
    // Health check
    const healthResponse = await page.request.get('http://localhost:3800/health');
    if (healthResponse.ok()) {
      const healthData = await healthResponse.json();
      auditResults.backend.successes.push('Health endpoint responding');
      console.log(chalk.green('  ✓ Health check passed'));
      console.log(chalk.gray(`    Status: ${JSON.stringify(healthData).substring(0, 50)}`));
    } else {
      auditResults.backend.issues.push('Health check failed');
      console.log(chalk.red('  ✗ Health check failed'));
    }

    // Check tRPC
    const trpcResponse = await page.request.post('http://localhost:3800/trpc/auth.login', {
      data: { email: 'test@test.com', password: 'test' },
      headers: { 'Content-Type': 'application/json' }
    });
    
    // We expect this to fail with auth error, not server error
    if (trpcResponse.status() === 400 || trpcResponse.status() === 401) {
      auditResults.backend.successes.push('tRPC endpoints responding correctly');
      console.log(chalk.green('  ✓ tRPC endpoints working'));
    } else if (trpcResponse.status() >= 500) {
      auditResults.backend.issues.push('tRPC server error');
      console.log(chalk.red('  ✗ tRPC server error'));
    }

    auditResults.backend.status = auditResults.backend.issues.length === 0 ? 'working' : 'issues';
    
  } catch (error) {
    auditResults.backend.status = 'failed';
    auditResults.backend.issues.push(`Backend failed: ${error}`);
    console.log(chalk.red(`  ✗ Backend failed: ${error}`));
  }

  // 3. PACKAGES AUDIT
  console.log(chalk.yellow('\n📦 STACK 2025 PACKAGES AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  const packagesDir = '/home/adminmatej/github/packages';
  const expectedPackages = [
    'auth-core', 'ui-core', 'database-core', 'shared-core', 
    'bug-report-core', 'ai-providers-core', 'testing-core'
  ];
  
  for (const pkg of expectedPackages) {
    const pkgPath = path.join(packagesDir, pkg);
    if (fs.existsSync(pkgPath)) {
      const packageJsonPath = path.join(pkgPath, 'package.json');
      if (fs.existsSync(packageJsonPath)) {
        auditResults.packages.successes.push(`${pkg} exists`);
        console.log(chalk.green(`  ✓ ${pkg} found`));
      } else {
        auditResults.packages.issues.push(`${pkg} missing package.json`);
        console.log(chalk.red(`  ✗ ${pkg} missing package.json`));
      }
    } else {
      auditResults.packages.issues.push(`${pkg} not found`);
      console.log(chalk.red(`  ✗ ${pkg} not found`));
    }
  }
  
  auditResults.packages.status = auditResults.packages.issues.length === 0 ? 'working' : 'issues';

  // 4. DATABASE AUDIT
  console.log(chalk.yellow('\n🗄️ DATABASE AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  // Check if .env file exists
  const envPath = '/home/adminmatej/github/apps/productivity-hub/.env';
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    if (envContent.includes('DATABASE_URL')) {
      auditResults.database.successes.push('Database URL configured');
      console.log(chalk.green('  ✓ Database URL configured'));
    } else {
      auditResults.database.issues.push('Database URL not configured');
      console.log(chalk.red('  ✗ Database URL missing'));
    }
  } else {
    auditResults.database.issues.push('.env file missing');
    console.log(chalk.red('  ✗ .env file not found'));
  }

  // 5. AUTHENTICATION AUDIT
  console.log(chalk.yellow('\n🔐 AUTHENTICATION AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  // Try to interact with login form
  try {
    await page.goto('http://localhost:5178/');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'testpassword');
    
    const signInButton = await page.locator('button:has-text("Sign")').count();
    if (signInButton > 0) {
      auditResults.authentication.successes.push('Login form interactive');
      console.log(chalk.green('  ✓ Login form accepts input'));
    } else {
      auditResults.authentication.issues.push('Sign in button not found');
      console.log(chalk.red('  ✗ Sign in button missing'));
    }
  } catch (error) {
    auditResults.authentication.issues.push(`Auth form error: ${error}`);
    console.log(chalk.red(`  ✗ Auth interaction failed`));
  }

  // 6. UI COMPONENTS AUDIT
  console.log(chalk.yellow('\n🎨 UI COMPONENTS AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  const uiComponentsPath = '/home/adminmatej/github/packages/ui-core/src/components/ui';
  if (fs.existsSync(uiComponentsPath)) {
    const components = fs.readdirSync(uiComponentsPath).filter(f => f.endsWith('.tsx'));
    auditResults.ui_components.successes.push(`${components.length} components found`);
    console.log(chalk.green(`  ✓ ${components.length} UI components found`));
    
    // Check if build works
    const uiPackagePath = '/home/adminmatej/github/packages/ui-core';
    const distPath = path.join(uiPackagePath, 'dist');
    if (fs.existsSync(distPath)) {
      auditResults.ui_components.successes.push('UI package built');
      console.log(chalk.green('  ✓ UI package has build output'));
    } else {
      auditResults.ui_components.issues.push('UI package not built');
      console.log(chalk.yellow('  ⚠ UI package needs building'));
    }
  } else {
    auditResults.ui_components.issues.push('UI components directory not found');
    console.log(chalk.red('  ✗ UI components missing'));
  }

  // 7. TESTING AUDIT
  console.log(chalk.yellow('\n🧪 TESTING AUDIT'));
  console.log(chalk.gray('-'.repeat(40)));
  
  const testingCorePath = '/home/adminmatej/github/packages/testing-core';
  if (fs.existsSync(testingCorePath)) {
    const testFiles = fs.readdirSync(path.join(testingCorePath, 'src')).filter(f => f.includes('test'));
    if (testFiles.length > 0) {
      auditResults.testing.successes.push(`${testFiles.length} test files found`);
      console.log(chalk.green(`  ✓ ${testFiles.length} test files found`));
    } else {
      auditResults.testing.issues.push('No test files found');
      console.log(chalk.red('  ✗ No test files'));
    }
  }

  await browser.close();

  // GENERATE SUMMARY
  console.log(chalk.cyan('\n' + '='.repeat(60)));
  console.log(chalk.cyan.bold('📊 AUDIT SUMMARY'));
  console.log(chalk.cyan('='.repeat(60)));

  let totalIssues = 0;
  let totalSuccesses = 0;

  for (const [category, results] of Object.entries(auditResults)) {
    const categoryName = category.replace(/_/g, ' ').toUpperCase();
    const icon = results.issues.length === 0 ? '✅' : results.issues.length > results.successes.length ? '❌' : '⚠️';
    
    console.log(`\n${icon} ${categoryName}`);
    console.log(`   Successes: ${results.successes.length} | Issues: ${results.issues.length}`);
    
    totalIssues += results.issues.length;
    totalSuccesses += results.successes.length;
    
    if (results.issues.length > 0) {
      console.log(chalk.red('   Issues:'));
      results.issues.slice(0, 3).forEach(issue => {
        console.log(chalk.red(`   - ${issue}`));
      });
    }
  }

  console.log(chalk.cyan('\n' + '='.repeat(60)));
  console.log(chalk.bold('\n📈 OVERALL METRICS:'));
  console.log(`   Total Successes: ${chalk.green(totalSuccesses)}`);
  console.log(`   Total Issues: ${chalk.red(totalIssues)}`);
  console.log(`   Success Rate: ${chalk.bold(((totalSuccesses / (totalSuccesses + totalIssues)) * 100).toFixed(1) + '%')}`);

  // VERDICT
  console.log(chalk.cyan('\n' + '='.repeat(60)));
  console.log(chalk.bold('🎯 VERDICT:'));
  
  if (totalIssues === 0) {
    console.log(chalk.green.bold('   ✅ SYSTEM FULLY FUNCTIONAL - NO ISSUES FOUND'));
  } else if (totalIssues < 5) {
    console.log(chalk.yellow.bold('   ⚠️ SYSTEM MOSTLY FUNCTIONAL - MINOR ISSUES'));
  } else if (totalIssues < 10) {
    console.log(chalk.yellow.bold('   ⚠️ SYSTEM PARTIALLY FUNCTIONAL - SEVERAL ISSUES'));
  } else {
    console.log(chalk.red.bold('   ❌ SYSTEM HAS SIGNIFICANT ISSUES - NEEDS ATTENTION'));
  }

  console.log(chalk.cyan('=' .repeat(60) + '\n'));

  // Save audit report
  const report = {
    timestamp: new Date().toISOString(),
    results: auditResults,
    metrics: {
      totalSuccesses,
      totalIssues,
      successRate: ((totalSuccesses / (totalSuccesses + totalIssues)) * 100).toFixed(1)
    }
  };
  
  fs.writeFileSync('audit-report.json', JSON.stringify(report, null, 2));
  console.log(chalk.blue('📄 Full report saved to audit-report.json\n'));
}

// Run audit
performFreshAudit().catch(console.error);
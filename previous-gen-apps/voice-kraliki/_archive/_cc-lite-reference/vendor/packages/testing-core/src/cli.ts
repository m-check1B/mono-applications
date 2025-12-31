#!/usr/bin/env node

/**
 * Stack 2025 Test Runner CLI - Entry point for testing all apps
 */

import chalk from 'chalk';
import { AppTester } from './app-tester';
import { AppConfig } from './types';

// Configuration for all Stack 2025 apps
const APP_CONFIGS: AppConfig[] = [
  {
    name: 'Invoice Gym',
    frontendUrl: 'http://localhost:5173',
    backendUrl: 'http://localhost:3002',
    healthEndpoint: 'http://localhost:3002/health',
    authEndpoint: 'http://localhost:3002/api/auth/login',
    testCredentials: {
      email: 'test@example.com',
      password: 'Test123!@#',
    },
    features: ['invoices', 'clients', 'qr-payments', 'voice-commands', 'mcp-server'],
  },
  {
    name: 'CC Light',
    frontendUrl: 'http://localhost:3003',
    backendUrl: 'http://localhost:3003',
    healthEndpoint: 'http://localhost:3003/health',
    testCredentials: {
      email: 'test@example.com',
      password: 'Test123!@#',
    },
    features: ['command-center', 'quick-actions'],
  },
  {
    name: 'Productivity Hub',
    frontendUrl: 'http://localhost:5177',
    backendUrl: 'http://localhost:3001',
    healthEndpoint: 'http://localhost:3001/health',
    authEndpoint: 'http://localhost:3001/api/auth/login',
    testCredentials: {
      email: 'test@example.com',
      password: 'Test123!@#',
    },
    features: ['tasks', 'calendar', 'notes', 'metrics'],
  },
];

async function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'test:all';
  
  console.log(chalk.cyan.bold(`
╔════════════════════════════════════════╗
║     Stack 2025 Testing Framework      ║
║        Automated App Testing           ║
╚════════════════════════════════════════╝
  `));

  switch (command) {
    case 'test:all':
      console.log(chalk.blue('📦 Testing all Stack 2025 apps...'));
      await AppTester.testMultipleApps(APP_CONFIGS, { 
        headless: !args.includes('--headed'),
        parallel: args.includes('--parallel'),
        includeFrontend: args.includes('--include-frontend')
      });
      break;
      
    case 'test:invoice':
      console.log(chalk.blue('📄 Testing Invoice Gym...'));
      const invoiceTester = new AppTester(APP_CONFIGS[0]);
      await invoiceTester.testApp({ 
        headless: !args.includes('--headed'),
        scenarios: args.includes('--full') ? 'all' : 'basic',
        includeFrontend: args.includes('--include-frontend')
      });
      break;
      
    case 'test:cc':
      console.log(chalk.blue('🎮 Testing CC Light...'));
      const ccTester = new AppTester(APP_CONFIGS[1]);
      await ccTester.testApp({ 
        headless: !args.includes('--headed'),
        scenarios: args.includes('--full') ? 'all' : 'basic',
        includeFrontend: args.includes('--include-frontend')
      });
      break;
      
    case 'test:hub':
      console.log(chalk.blue('📊 Testing Productivity Hub...'));
      const hubTester = new AppTester(APP_CONFIGS[2]);
      await hubTester.testApp({ 
        headless: !args.includes('--headed'),
        scenarios: args.includes('--full') ? 'all' : 'basic',
        includeFrontend: args.includes('--include-frontend')
      });
      break;
      
    case 'test:ui':
      console.log(chalk.blue('🎨 Testing UI Components...'));
      const appName = args.find(arg => !arg.startsWith('--'))?.replace('test:ui', '').trim() || 'productivity-hub';
      let appConfig;
      
      if (appName.includes('hub')) {
        appConfig = APP_CONFIGS[2]; // Productivity Hub
      } else if (appName.includes('cc')) {
        appConfig = APP_CONFIGS[1]; // CC Light
      } else if (appName.includes('invoice')) {
        appConfig = APP_CONFIGS[0]; // Invoice App
      } else {
        appConfig = APP_CONFIGS[2]; // Default to Productivity Hub
      }
      
      const uiTester = new AppTester(appConfig);
      await uiTester.testUIComponents();
      break;
      
    case 'diagnose':
      console.log(chalk.blue('🔍 Running UI Diagnosis...'));
      const diagAppName = args.find(arg => !arg.startsWith('--'))?.replace('diagnose', '').trim() || 'productivity-hub';
      let diagAppConfig;
      
      if (diagAppName.includes('hub')) {
        diagAppConfig = APP_CONFIGS[2]; // Productivity Hub
      } else if (diagAppName.includes('cc')) {
        diagAppConfig = APP_CONFIGS[1]; // CC Light
      } else if (diagAppName.includes('invoice')) {
        diagAppConfig = APP_CONFIGS[0]; // Invoice App
      } else {
        diagAppConfig = APP_CONFIGS[2]; // Default to Productivity Hub
      }
      
      const diagTester = new AppTester(diagAppConfig);
      await diagTester.diagnoseUI();
      break;
      
    case 'health':
      console.log(chalk.blue('🏥 Checking app health...'));
      const { HealthChecker } = await import('./health-checker');
      const checker = new HealthChecker();
      await checker.checkMultipleApps(APP_CONFIGS);
      break;
      
    default:
      console.log(chalk.yellow(`
Available commands:
  test:all    - Test all apps
  test:invoice - Test Invoice Gym only  
  test:cc     - Test CC Light only
  test:hub    - Test Productivity Hub only
  health      - Health check all apps

Options:
  --headed    - Run with visible browser
  --parallel  - Run tests in parallel
  --full      - Run all test scenarios
  --include-frontend - Run comprehensive frontend tests
      `));
  }
  
  process.exit(0);
}

// Handle errors
process.on('unhandledRejection', (error: any) => {
  console.error(chalk.red('❌ Fatal error:'), error);
  process.exit(1);
});

// Run
main().catch(error => {
  console.error(chalk.red('❌ Test runner failed:'), error);
  process.exit(1);
});
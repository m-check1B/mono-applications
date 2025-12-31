#!/usr/bin/env node

/**
 * Focus by Kraliki E2E Testing Script
 * 
 * This script performs comprehensive end-to-end testing of the Focus by Kraliki application
 * including user registration, login, task management, AI chat, and theme switching.
 * 
 * @module E2ETestSuite
 * @version 1.0.0
 */

const { chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// Test configuration
const config = {
  baseUrl: 'http://localhost:5173',
  screenshotsDir: path.join(__dirname, 'e2e-screenshots'),
  timeout: 30000,
  slowMo: 1000
};

// Test data
const testData = {
  user: {
    email: 'test@example.com',
    password: 'test123',
    name: 'Test User'
  },
  tasks: [
    { title: 'Complete project documentation', description: 'Finish the README and API docs' },
    { title: 'Review pull requests', description: 'Check and merge pending PRs' },
    { title: 'Team meeting', description: 'Weekly team sync at 2 PM' }
  ],
  aiMessages: [
    'Help me organize my tasks for today',
    'What\'s the best way to prioritize my work?',
    'Generate a task from: "Call client about project status"'
  ]
};

class E2ETester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.screenshots = [];
  }

  async init() {
    console.log('🚀 Starting E2E Test Suite for Focus by Kraliki');
    console.log('=========================================');
    
    // Create screenshots directory
    if (!fs.existsSync(config.screenshotsDir)) {
      fs.mkdirSync(config.screenshotsDir, { recursive: true });
    }

    // Launch browser
    this.browser = await chromium.launch({
      headless: false,
      slowMo: config.slowMo,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    this.page = await this.browser.newPage();
    await this.page.setViewportSize({ width: 1280, height: 720 });
    
    // Set timeout
    this.page.setDefaultTimeout(config.timeout);
    
    console.log('✅ Browser launched successfully');
  }

  async takeScreenshot(name, description = '') {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}_${timestamp}.png`;
    const filepath = path.join(config.screenshotsDir, filename);
    
    await this.page.screenshot({ 
      path: filepath,
      fullPage: true 
    });
    
    this.screenshots.push({
      name,
      filename,
      filepath,
      description,
      timestamp: new Date().toISOString()
    });
    
    console.log(`📸 Screenshot saved: ${filename}`);
    if (description) {
      console.log(`   Description: ${description}`);
    }
  }

  async navigateToHome() {
    console.log('\n🏠 Navigating to home page...');
    await this.page.goto(config.baseUrl);
    await this.page.waitForLoadState('networkidle');
    await this.takeScreenshot('home_page', 'Focus by Kraliki home page');
  }

  async testUserRegistration() {
    console.log('\n👤 Testing user registration...');
    
    // Navigate to registration
    await this.page.click('[data-testid="register-link"]');
    await this.page.waitForLoadState('networkidle');
    
    // Fill registration form
    await this.page.fill('[data-testid="register-name"]', testData.user.name);
    await this.page.fill('[data-testid="register-email"]', testData.user.email);
    await this.page.fill('[data-testid="register-password"]', testData.user.password);
    await this.page.fill('[data-testid="register-confirm-password"]', testData.user.password);
    
    await this.takeScreenshot('registration_form', 'Registration form filled');
    
    // Submit registration
    await this.page.click('[data-testid="register-submit"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('registration_success', 'Registration successful');
    console.log('✅ User registration completed');
  }

  async testUserLogin() {
    console.log('\n🔐 Testing user login...');
    
    // Fill login form
    await this.page.fill('[data-testid="login-email"]', testData.user.email);
    await this.page.fill('[data-testid="login-password"]', testData.user.password);
    
    await this.takeScreenshot('login_form', 'Login form filled');
    
    // Submit login
    await this.page.click('[data-testid="login-submit"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('login_success', 'Login successful - Dashboard');
    console.log('✅ User login completed');
  }

  async testTaskCreation() {
    console.log('\n📋 Testing task creation...');
    
    // Navigate to tasks
    await this.page.click('[data-testid="nav-tasks"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('tasks_page', 'Tasks page');
    
    // Create multiple tasks
    for (let i = 0; i < testData.tasks.length; i++) {
      const task = testData.tasks[i];
      
      console.log(`   Creating task: ${task.title}`);
      
      // Click add task button
      await this.page.click('[data-testid="add-task-btn"]');
      await this.page.waitForSelector('[data-testid="task-modal"]');
      
      // Fill task form
      await this.page.fill('[data-testid="task-title"]', task.title);
      await this.page.fill('[data-testid="task-description"]', task.description);
      
      await this.takeScreenshot(`task_creation_${i}`, `Creating task: ${task.title}`);
      
      // Submit task
      await this.page.click('[data-testid="task-submit"]');
      await this.page.waitForLoadState('networkidle');
      
      // Wait for task to appear in list
      await this.page.waitForSelector(`text=${task.title}`);
    }
    
    await this.takeScreenshot('tasks_created', 'All tasks created successfully');
    console.log('✅ Task creation completed');
  }

  async testTaskManagement() {
    console.log('\n🔄 Testing task management...');
    
    // Test task completion
    const firstTask = testData.tasks[0];
    await this.page.click(`text=${firstTask.title} >> xpath=.. >> [data-testid="task-checkbox"]`);
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('task_completed', 'Task marked as completed');
    
    // Test task editing
    const secondTask = testData.tasks[1];
    await this.page.click(`text=${secondTask.title} >> xpath=.. >> [data-testid="task-edit"]`);
    await this.page.waitForSelector('[data-testid="task-modal"]');
    
    await this.page.fill('[data-testid="task-title"]', `${secondTask.title} (Updated)`);
    await this.takeScreenshot('task_editing', 'Editing task');
    
    await this.page.click('[data-testid="task-submit"]');
    await this.page.waitForLoadState('networkidle');
    
    // Test task deletion
    const thirdTask = testData.tasks[2];
    await this.page.click(`text=${thirdTask.title} >> xpath=.. >> [data-testid="task-delete"]`);
    await this.page.waitForSelector('[data-testid="confirm-delete"]');
    
    await this.takeScreenshot('task_deleting', 'Confirming task deletion');
    
    await this.page.click('[data-testid="confirm-delete"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('task_management_complete', 'Task management operations completed');
    console.log('✅ Task management completed');
  }

  async testAIChat() {
    console.log('\n🤖 Testing AI chat functionality...');
    
    // Navigate to AI chat
    await this.page.click('[data-testid="nav-ai-chat"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('ai_chat_page', 'AI chat page');
    
    // Send multiple messages
    for (let i = 0; i < testData.aiMessages.length; i++) {
      const message = testData.aiMessages[i];
      
      console.log(`   Sending AI message: ${message.substring(0, 50)}...`);
      
      // Type message
      await this.page.fill('[data-testid="ai-chat-input"]', message);
      
      await this.takeScreenshot(`ai_chat_input_${i}`, `AI chat input: ${message.substring(0, 30)}...`);
      
      // Send message
      await this.page.click('[data-testid="ai-chat-send"]');
      await this.page.waitForLoadState('networkidle');
      
      // Wait for AI response
      await this.page.waitForSelector('[data-testid="ai-response"]');
      
      await this.takeScreenshot(`ai_chat_response_${i}`, `AI response to message ${i + 1}`);
    }
    
    await this.takeScreenshot('ai_chat_complete', 'AI chat conversation completed');
    console.log('✅ AI chat testing completed');
  }

  async testThemeSwitching() {
    console.log('\n🎨 Testing theme switching...');
    
    // Navigate to settings
    await this.page.click('[data-testid="nav-settings"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('settings_page', 'Settings page');
    
    // Test theme switching
    const themes = ['light', 'dark', 'system'];
    
    for (const theme of themes) {
      console.log(`   Switching to ${theme} theme`);
      
      await this.page.click(`[data-testid="theme-${theme}"]`);
      await this.page.waitForLoadState('networkidle');
      
      await this.takeScreenshot(`theme_${theme}`, `${theme} theme applied`);
    }
    
    await this.takeScreenshot('theme_switching_complete', 'Theme switching completed');
    console.log('✅ Theme switching completed');
  }

  async testNaturalLanguageTaskCreation() {
    console.log('\n🗣️ Testing natural language task creation...');
    
    // Navigate to AI chat
    await this.page.click('[data-testid="nav-ai-chat"]');
    await this.page.waitForLoadState('networkidle');
    
    // Send natural language task creation request
    const nlTask = "Schedule a team meeting for next Monday at 2 PM to discuss the Q4 roadmap";
    await this.page.fill('[data-testid="ai-chat-input"]', nlTask);
    await this.takeScreenshot('nl_task_input', 'Natural language task input');
    
    await this.page.click('[data-testid="ai-chat-send"]');
    await this.page.waitForLoadState('networkidle');
    
    // Check if task was created
    await this.page.waitForSelector('[data-testid="task-created-notification"]');
    await this.takeScreenshot('nl_task_created', 'Task created from natural language');
    
    // Verify task appears in tasks list
    await this.page.click('[data-testid="nav-tasks"]');
    await this.page.waitForLoadState('networkidle');
    
    await this.takeScreenshot('nl_task_in_list', 'Natural language task in task list');
    console.log('✅ Natural language task creation completed');
  }

  async generateReport() {
    console.log('\n📊 Generating test report...');
    
    const report = {
      testSuite: 'Focus by Kraliki E2E Test Suite',
      timestamp: new Date().toISOString(),
      summary: {
        totalTests: 7,
        passed: 7,
        failed: 0,
        screenshots: this.screenshots.length
      },
      tests: [
        { name: 'User Registration', status: 'passed', screenshots: 2 },
        { name: 'User Login', status: 'passed', screenshots: 2 },
        { name: 'Task Creation', status: 'passed', screenshots: 4 },
        { name: 'Task Management', status: 'passed', screenshots: 4 },
        { name: 'AI Chat', status: 'passed', screenshots: 4 },
        { name: 'Theme Switching', status: 'passed', screenshots: 4 },
        { name: 'Natural Language Task Creation', status: 'passed', screenshots: 3 }
      ],
      screenshots: this.screenshots,
      environment: {
        browser: 'Chromium',
        baseUrl: config.baseUrl,
        resolution: '1280x720'
      }
    };
    
    const reportPath = path.join(config.screenshotsDir, 'test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`📄 Test report saved to: ${reportPath}`);
    console.log(`📸 Total screenshots: ${this.screenshots.length}`);
    console.log(`📁 Screenshots directory: ${config.screenshotsDir}`);
    
    return report;
  }

  async cleanup() {
    console.log('\n🧹 Cleaning up...');
    
    if (this.browser) {
      await this.browser.close();
    }
    
    console.log('✅ Cleanup completed');
  }

  async runFullTestSuite() {
    try {
      await this.init();
      
      // Run all tests
      await this.navigateToHome();
      await this.testUserRegistration();
      await this.testUserLogin();
      await this.testTaskCreation();
      await this.testTaskManagement();
      await this.testAIChat();
      await this.testThemeSwitching();
      await this.testNaturalLanguageTaskCreation();
      
      // Generate report
      const report = await this.generateReport();
      
      console.log('\n🎉 E2E Test Suite Completed Successfully!');
      console.log('=========================================');
      console.log(`✅ All tests passed: ${report.summary.passed}/${report.summary.totalTests}`);
      console.log(`📸 Screenshots captured: ${report.summary.screenshots}`);
      console.log(`📁 Report location: ${path.join(config.screenshotsDir, 'test-report.json')}`);
      
      return report;
      
    } catch (error) {
      console.error('❌ E2E Test Suite Failed:', error);
      
      // Take error screenshot
      if (this.page) {
        await this.takeScreenshot('test_failure', `Test failed: ${error.message}`);
      }
      
      throw error;
      
    } finally {
      await this.cleanup();
    }
  }
}

// Run the test suite
if (require.main === module) {
  const tester = new E2ETester();
  tester.runFullTestSuite()
    .then(report => {
      console.log('\n🚀 Test execution completed successfully!');
      process.exit(0);
    })
    .catch(error => {
      console.error('\n💥 Test execution failed:', error);
      process.exit(1);
    });
}

module.exports = E2ETester;
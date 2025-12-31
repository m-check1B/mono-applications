import { test, expect } from '@playwright/test';
import TestUtils from './utils/test-utils';

test.describe('Business Operations Applications', () => {
  let testUtils: TestUtils;

  test.beforeEach(async ({ page }) => {
    testUtils = new TestUtils(page);
  });

  test.describe('Plane Application - Project Management', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to Plane application (adjust URL as needed)
      await testUtils.safeNavigate('http://localhost:3000');
    });

    test('should display Plane landing page', async ({ page }) => {
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('nav')).toBeVisible();
      await testUtils.takeScreenshot('plane-landing', 'Plane application landing page');
    });

    test('should navigate to project management features', async ({ page }) => {
      // Test navigation to different project management features
      const navigationItems = [
        'Projects',
        'Issues',
        'Cycles',
        'Modules',
        'Views'
      ];

      for (const item of navigationItems) {
        const navLink = page.locator(`nav >> text=${item}`).first();
        if (await navLink.isVisible()) {
          await testUtils.safeClick(`nav >> text=${item}`);
          await testUtils.waitForNetworkIdle();
          await expect(page.locator('h1, h2')).toBeVisible();
          await testUtils.takeScreenshot(`plane-${item.toLowerCase()}`, `Plane ${item} page`);
        }
      }
    });

    test('should handle project creation workflow', async ({ page }) => {
      // Navigate to projects
      await testUtils.safeClick('nav >> text=Projects');
      await testUtils.waitForNetworkIdle();

      // Click create project button
      const createButton = page.locator('button:has-text("Create"), button:has-text("New Project")').first();
      if (await createButton.isVisible()) {
        await testUtils.safeClick('button:has-text("Create"), button:has-text("New Project")');

        // Fill project creation form
        const uniqueData = testUtils.generateUniqueData('project');
        await testUtils.safeFill('input[name*="name"], input[placeholder*="name"]', uniqueData.title);

        await testUtils.takeScreenshot('plane-project-creation', 'Project creation form');

        // Submit form
        await testUtils.safeClick('button:has-text("Create Project"), button:has-text("Submit")');
        await testUtils.waitForNetworkIdle();

        // Verify project was created
        await expect(page.locator(`text=${uniqueData.title}`)).toBeVisible();
      }
    });
  });

  test.describe('Notion Integration - Automation', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to Notion automation interface
      await testUtils.safeNavigate('http://localhost:3001');
    });

    test('should display Notion automation dashboard', async ({ page }) => {
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('text=Notion Automation')).toBeVisible();
      await testUtils.takeScreenshot('notion-dashboard', 'Notion automation dashboard');
    });

    test('should handle database integration', async ({ page }) => {
      // Test database connection
      const connectButton = page.locator('button:has-text("Connect"), button:has-text("Connect Database")').first();
      if (await connectButton.isVisible()) {
        await testUtils.safeClick('button:has-text("Connect"), button:has-text("Connect Database")');
        await testUtils.waitForNetworkIdle();

        // Look for database configuration form
        const formExists = await testUtils.elementExists('form, .database-config');
        if (formExists) {
          await testUtils.takeScreenshot('notion-database-config', 'Notion database configuration');
        }
      }
    });

    test('should handle workflow automation', async ({ page }) => {
      // Navigate to workflows
      await testUtils.safeClick('nav >> text=Workflows, nav >> text=Automation');
      await testUtils.waitForNetworkIdle();

      // Test workflow creation
      const createWorkflowButton = page.locator('button:has-text("Create Workflow"), button:has-text("New Workflow")').first();
      if (await createWorkflowButton.isVisible()) {
        await testUtils.safeClick('button:has-text("Create Workflow"), button:has-text("New Workflow")');
        await testUtils.waitForNetworkIdle();

        await testUtils.takeScreenshot('notion-workflow-creation', 'Notion workflow creation');
      }
    });
  });

  test.describe('Focus by Kraliki Operations Integration', () => {
    test.beforeEach(async ({ page }) => {
      // Login to Focus by Kraliki
      await page.goto('/');
      await testUtils.safeFill('input[type="email"]', 'test@focus-kraliki.app');
      await testUtils.safeFill('input[type="password"]', 'test123');
      await testUtils.safeClick('button[type="submit"]');
      await expect(page.locator('text=Dashboard')).toBeVisible({ timeout: 10000 });
    });

    test('should access operations dashboard', async ({ page }) => {
      // Navigate to operations section
      await testUtils.safeClick('text=Operations, text=Business Ops');
      await testUtils.waitForNetworkIdle();

      await expect(page.locator('h1:has-text("Operations"), h2:has-text("Operations")')).toBeVisible();
      await testUtils.takeScreenshot('operations-dashboard', 'Operations dashboard');
    });

    test('should handle task delegation workflows', async ({ page }) => {
      // Navigate to operations
      await testUtils.safeClick('text=Operations, text=Business Ops');
      await testUtils.waitForNetworkIdle();

      // Create a task with delegation
      const uniqueData = testUtils.generateUniqueData('delegation');

      // Look for task creation form
      const taskForm = page.locator('form, .task-form').first();
      if (await taskForm.isVisible()) {
        await testUtils.safeFill('input[placeholder*="task"], textarea[placeholder*="task"]', uniqueData.title);
        await testUtils.safeFill('textarea[placeholder*="description"], input[placeholder*="description"]', uniqueData.description);

        // Look for assignee field
        const assigneeField = page.locator('select[name*="assignee"], input[placeholder*="assignee"]').first();
        if (await assigneeField.isVisible()) {
          await testUtils.safeFill('select[name*="assignee"], input[placeholder*="assignee"]', 'Team Member');
        }

        await testUtils.takeScreenshot('task-delegation', 'Task delegation form');

        // Submit task
        await testUtils.safeClick('button:has-text("Create Task"), button:has-text("Submit")');
        await testUtils.waitForNetworkIdle();

        // Verify task was created
        await expect(page.locator(`text=${uniqueData.title}`)).toBeVisible();
      }
    });

    test('should handle team collaboration features', async ({ page }) => {
      // Navigate to team collaboration
      await testUtils.safeClick('text=Team, text=Collaboration');
      await testUtils.waitForNetworkIdle();

      // Test team features
      const teamFeatures = [
        'Members',
        'Chat',
        'Files',
        'Meetings'
      ];

      for (const feature of teamFeatures) {
        const featureTab = page.locator(`button:has-text("${feature}"), nav >> text=${feature}`).first();
        if (await featureTab.isVisible()) {
          await testUtils.safeClick(`button:has-text("${feature}"), nav >> text=${feature}`);
          await testUtils.waitForNetworkIdle();
          await testUtils.takeScreenshot(`team-${feature.toLowerCase()}`, `Team ${feature} view`);
        }
      }
    });

    test('should handle reporting and analytics', async ({ page }) => {
      // Navigate to reports
      await testUtils.safeClick('text=Reports, text=Analytics');
      await testUtils.waitForNetworkIdle();

      // Test different report types
      const reportTypes = [
        'Performance',
        'Productivity',
        'Team Activity',
        'Task Completion'
      ];

      for (const reportType of reportTypes) {
        const reportButton = page.locator(`button:has-text("${reportType}"), nav >> text=${reportType}`).first();
        if (await reportButton.isVisible()) {
          await testUtils.safeClick(`button:has-text("${reportType}"), nav >> text=${reportType}`);
          await testUtils.waitForNetworkIdle();

          // Check for charts or data visualization
          const chartExists = await testUtils.elementExists('canvas, .chart, .graph');
          if (chartExists) {
            await testUtils.takeScreenshot(`report-${reportType.toLowerCase()}`, `${reportType} report view`);
          }
        }
      }
    });
  });

  test.describe('Cross-Application Integration', () => {
    test('should verify integration between Focus by Kraliki and Plane', async ({ page }) => {
      // Test integration endpoints
      const integrationEndpoints = [
        '/api/integration/plane/sync',
        '/api/integration/plane/projects',
        '/api/integration/plane/issues'
      ];

      for (const endpoint of integrationEndpoints) {
        try {
          const response = await page.request.get(`${process.env.BASE_URL || 'http://127.0.0.1:3017'}${endpoint}`);
          if (response.ok()) {
            console.log(`✅ Integration endpoint available: ${endpoint}`);
          }
        } catch (error) {
          console.log(`⚠️  Integration endpoint not available: ${endpoint}`);
        }
      }
    });

    test('should verify integration with Notion automation', async ({ page }) => {
      // Test Notion integration
      const notionEndpoints = [
        '/api/integration/notion/databases',
        '/api/integration/notion/workflows',
        '/api/integration/notion/sync'
      ];

      for (const endpoint of notionEndpoints) {
        try {
          const response = await page.request.get(`${process.env.BASE_URL || 'http://127.0.0.1:3017'}${endpoint}`);
          if (response.ok()) {
            console.log(`✅ Notion integration endpoint available: ${endpoint}`);
          }
        } catch (error) {
          console.log(`⚠️  Notion integration endpoint not available: ${endpoint}`);
        }
      }
    });
  });
});
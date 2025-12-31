/**
 * Common test scenarios for Stack 2025 apps
 */

import { TestScenario } from './types';

export const commonScenarios: TestScenario[] = [
  {
    name: 'Basic Navigation',
    description: 'User can navigate through main pages',
    actions: [
      { type: 'wait', value: 2000, description: 'Wait for page load' },
      { type: 'screenshot', value: 'home.png', description: 'Capture home page' },
    ],
    validations: [
      { 
        type: 'exists', 
        target: 'body', 
        expected: true, 
        description: 'Page body exists' 
      },
    ],
  },
  
  {
    name: 'Authentication Flow',
    description: 'User can login and logout',
    actions: [
      { type: 'click', target: 'a:has-text("Login"), a:has-text("Přihlásit")', description: 'Click login link' },
      { type: 'wait', value: 1000, description: 'Wait for form' },
    ],
    validations: [
      {
        type: 'exists',
        target: 'input[type="email"], input[name="email"]',
        expected: true,
        description: 'Email input exists',
      },
      {
        type: 'exists',
        target: 'input[type="password"]',
        expected: true,
        description: 'Password input exists',
      },
    ],
  },
];

export const invoiceAppScenarios: TestScenario[] = [
  {
    name: 'Create Invoice',
    description: 'User can create a new invoice',
    actions: [
      { type: 'click', target: 'a:has-text("Faktury")', description: 'Click invoices menu' },
      { type: 'wait', value: 1000, description: 'Wait for page' },
      { type: 'click', target: 'button:has-text("Nová faktura")', description: 'Click new invoice' },
      { type: 'wait', value: 1000, description: 'Wait for form' },
    ],
    validations: [
      {
        type: 'exists',
        target: 'form',
        expected: true,
        description: 'Invoice form exists',
      },
    ],
  },
  
  {
    name: 'View Dashboard',
    description: 'User can view dashboard with stats',
    actions: [
      { type: 'click', target: 'a:has-text("Přehled")', description: 'Click dashboard' },
      { type: 'wait', value: 2000, description: 'Wait for data load' },
    ],
    validations: [
      {
        type: 'exists',
        target: 'h1, h2',
        expected: true,
        description: 'Dashboard heading exists',
      },
    ],
  },
];

export const productivityHubScenarios: TestScenario[] = [
  {
    name: 'Create Task',
    description: 'User can create a new task',
    actions: [
      { type: 'click', target: 'button:has-text("New Task"), button:has-text("Add Task")', description: 'Click new task' },
      { type: 'wait', value: 1000, description: 'Wait for form' },
    ],
    validations: [
      {
        type: 'exists',
        target: 'input, textarea',
        expected: true,
        description: 'Task form exists',
      },
    ],
  },
];

export const ccLightScenarios: TestScenario[] = [
  {
    name: 'Command Center View',
    description: 'User can view command center',
    actions: [
      { type: 'wait', value: 2000, description: 'Wait for load' },
      { type: 'screenshot', value: 'cc-main.png', description: 'Capture main view' },
    ],
    validations: [
      {
        type: 'exists',
        target: 'body',
        expected: true,
        description: 'Command center loaded',
      },
    ],
  },
];

// Standard scenarios mapping for different apps
export const standardScenarios: Record<string, TestScenario[]> = {
  'productivity-hub': [...commonScenarios, ...productivityHubScenarios],
  'cc-light': [...commonScenarios, ...ccLightScenarios],
  'invoice-app': [...commonScenarios, ...invoiceAppScenarios],
  'productivity hub': [...commonScenarios, ...productivityHubScenarios],
  'cc light': [...commonScenarios, ...ccLightScenarios],
  'invoice app': [...commonScenarios, ...invoiceAppScenarios],
};
/**
 * Type definitions for Stack 2025 Testing Core
 */

export interface AppConfig {
  name: string;
  frontendUrl: string;
  backendUrl: string;
  healthEndpoint?: string;
  authEndpoint?: string;
  features?: string[];
  testCredentials?: {
    email: string;
    password: string;
  };
}

export interface TestResult {
  app: string;
  timestamp: Date;
  duration: number;
  status: 'passed' | 'failed' | 'skipped';
  tests: TestCase[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
  };
}

export interface TestCase {
  name: string;
  category: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
  screenshots?: string[];
  logs?: string[];
}

export interface UserAction {
  type: 'click' | 'fill' | 'navigate' | 'wait' | 'screenshot' | 'api';
  target?: string;
  value?: any;
  description: string;
}

export interface TestScenario {
  name: string;
  description: string;
  actions: UserAction[];
  validations: ValidationRule[];
}

export interface ValidationRule {
  type: 'exists' | 'contains' | 'equals' | 'status' | 'response';
  target: string;
  expected: any;
  description: string;
}
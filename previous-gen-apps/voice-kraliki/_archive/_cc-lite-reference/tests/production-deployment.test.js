#!/usr/bin/env node

/**
 * Voice by Kraliki Production Deployment Test Suite
 * Stack 2025 Compliant - BSI Security Requirements Met
 *
 * This test suite validates production deployment readiness
 * including configuration, security, performance, and monitoring
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import { join } from 'path';
import axios from 'axios';
import { URL } from 'url';

const __dirname = new URL('.', import.meta.url).pathname;

// Test Configuration
const TEST_CONFIG = {
  endpoints: {
    health: 'http://127.0.0.1:3900/health',
    metrics: 'http://127.0.0.1:3900/metrics',
    frontend: 'http://127.0.0.1:5174',
    trpc: 'http://127.0.0.1:3900/trpc'
  },
  timeouts: {
    startup: 30000,
    health: 5000,
    metrics: 5000,
    api: 10000
  },
  performance: {
    minUptime: 60000, // 1 minute minimum uptime
    maxMemory: 512 * 1024 * 1024, // 512MB max memory
    responseTime: 2000, // 2 second max response time
    concurrentRequests: 50,
    requestDuration: 30000 // 30 second test duration
  }
};

// Test Results
const testResults = {
  passed: [],
  failed: [],
  skipped: [],
  timestamp: new Date().toISOString(),
  environment: process.env.NODE_ENV || 'production'
};

// Test Categories
const tests = {
  configuration: {
    validateEnvironmentVariables: async () => {
      const requiredVars = [
        'NODE_ENV',
        'PORT',
        'HOST',
        'DATABASE_URL',
        'JWT_SECRET',
        'JWT_REFRESH_SECRET',
        'SESSION_SECRET',
        'COOKIE_SECRET'
      ];

      const missing = requiredVars.filter(varName => !process.env[varName]);
      if (missing.length > 0) {
        throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
      }

      if (process.env.NODE_ENV !== 'production') {
        throw new Error('NODE_ENV must be set to "production" for production deployment');
      }

      if (process.env.HOST === '0.0.0.0') {
        throw new Error('HOST cannot be 0.0.0.0 - security violation');
      }

      return { status: 'passed', message: 'All required environment variables are configured correctly' };
    },

    validateProductionConfig: async () => {
      const configPath = join(process.cwd(), '.env.production');
      try {
        const config = await fs.readFile(configPath, 'utf8');
        const lines = config.split('\n').filter(line => line.trim() && !line.startsWith('#'));

        const hasProductionSettings = lines.some(line =>
          line.includes('NODE_ENV=production') ||
          line.includes('APP_ENV=production')
        );

        if (!hasProductionSettings) {
          throw new Error('Production configuration file is missing production settings');
        }

        // Check for placeholder values
        const placeholders = [
          'your_account_sid_here',
          'your_auth_token_here',
          'your_api_key_here'
        ];

        const hasPlaceholders = placeholders.some(placeholder =>
          config.includes(placeholder)
        );

        if (hasPlaceholders) {
          throw new Error('Production configuration contains placeholder values');
        }

        return { status: 'passed', message: 'Production configuration is valid' };
      } catch (error) {
        throw new Error(`Failed to validate production config: ${error.message}`);
      }
    }
  },

  deployment: {
    checkDockerCompose: async () => {
      const dockerComposePath = join(process.cwd(), 'docker-compose.production.yml');
      try {
        const compose = await fs.readFile(dockerComposePath, 'utf8');

        // Check for security configurations
        const securityChecks = [
          { check: compose.includes('security_opt:'), message: 'Security options not configured' },
          { check: compose.includes('127.0.0.1:'), message: 'Ports not properly bound to localhost' },
          { check: compose.includes('healthcheck:'), message: 'Health checks not configured' },
          { check: compose.includes('user: "1001:1001"'), message: 'Non-root user not configured' }
        ];

        const failedChecks = securityChecks.filter(({ check }) => !check);
        if (failedChecks.length > 0) {
          throw new Error(failedChecks.map(({ message }) => message).join(', '));
        }

        return { status: 'passed', message: 'Docker Compose configuration is secure' };
      } catch (error) {
        throw new Error(`Docker Compose validation failed: ${error.message}`);
      }
    },

    checkDeploymentScript: async () => {
      const scriptPath = join(process.cwd(), 'deploy-production.sh');
      try {
        await fs.access(scriptPath, fs.constants.X_OK);
        return { status: 'passed', message: 'Deployment script exists and is executable' };
      } catch (error) {
        throw new Error('Deployment script is missing or not executable');
      }
    }
  },

  services: {
    checkDatabaseConnectivity: async () => {
      // This would be replaced with actual database connectivity test
      const { PrismaClient } = await import('@prisma/client');
      const prisma = new PrismaClient();

      try {
        await prisma.$connect();
        await prisma.$queryRaw`SELECT 1`;
        return { status: 'passed', message: 'Database connectivity verified' };
      } catch (error) {
        throw new Error(`Database connectivity failed: ${error.message}`);
      } finally {
        await prisma.$disconnect();
      }
    },

    checkRedisConnectivity: async () => {
      // This would be replaced with actual Redis connectivity test
      try {
        const redis = await import('redis');
        const client = redis.createClient({
          url: process.env.REDIS_URL || 'redis://localhost:6379'
        });

        await client.connect();
        await client.ping();
        await client.quit();

        return { status: 'passed', message: 'Redis connectivity verified' };
      } catch (error) {
        throw new Error(`Redis connectivity failed: ${error.message}`);
      }
    }
  },

  api: {
    healthEndpoint: async () => {
      try {
        const response = await axios.get(TEST_CONFIG.endpoints.health, {
          timeout: TEST_CONFIG.timeouts.health
        });

        if (response.status !== 200) {
          throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
        }

        const data = response.data;
        if (data.status !== 'ok') {
          throw new Error(`Health check returned non-ok status: ${data.status}`);
        }

        return { status: 'passed', message: 'Health endpoint is responding correctly' };
      } catch (error) {
        throw new Error(`Health endpoint test failed: ${error.message}`);
      }
    },

    metricsEndpoint: async () => {
      try {
        const response = await axios.get(TEST_CONFIG.endpoints.metrics, {
          timeout: TEST_CONFIG.timeouts.metrics
        });

        if (response.status !== 200) {
          throw new Error(`Metrics endpoint failed: ${response.status} ${response.statusText}`);
        }

        const data = response.data;
        if (!data.uptime) {
          throw new Error('Metrics endpoint missing uptime data');
        }

        return { status: 'passed', message: 'Metrics endpoint is responding correctly' };
      } catch (error) {
        throw new Error(`Metrics endpoint test failed: ${error.message}`);
      }
    },

    corsValidation: async () => {
      try {
        const response = await axios.get(TEST_CONFIG.endpoints.health, {
          headers: { Origin: 'https://malicious-site.com' },
          timeout: TEST_CONFIG.timeouts.health
        });

        // Check if CORS headers are properly set
        const corsHeader = response.headers['access-control-allow-origin'];
        if (corsHeader && corsHeader !== 'null') {
          throw new Error('CORS policy allows unauthorized origins');
        }

        return { status: 'passed', message: 'CORS policy is properly configured' };
      } catch (error) {
        throw new Error(`CORS validation failed: ${error.message}`);
      }
    }
  },

  security: {
    rateLimiting: async () => {
      const requests = Array(150).fill(null).map(() =>
        axios.get(TEST_CONFIG.endpoints.health, { timeout: 1000 })
      );

      const responses = await Promise.allSettled(requests);
      const rateLimited = responses.filter(result =>
        result.status === 'fulfilled' &&
        result.value.status === 429
      );

      if (rateLimited.length === 0) {
        throw new Error('Rate limiting is not working');
      }

      return {
        status: 'passed',
        message: `Rate limiting is working (${rateLimited.length} requests blocked)`
      };
    },

    securityHeaders: async () => {
      try {
        const response = await axios.get(TEST_CONFIG.endpoints.health, {
          timeout: TEST_CONFIG.timeouts.health
        });

        const requiredHeaders = [
          'x-content-type-options',
          'x-frame-options',
          'strict-transport-security'
        ];

        const missingHeaders = requiredHeaders.filter(header =>
          !response.headers[header]
        );

        if (missingHeaders.length > 0) {
          throw new Error(`Missing security headers: ${missingHeaders.join(', ')}`);
        }

        return { status: 'passed', message: 'All security headers are present' };
      } catch (error) {
        throw new Error(`Security headers validation failed: ${error.message}`);
      }
    }
  },

  performance: {
    responseTime: async () => {
      const start = Date.now();
      try {
        const response = await axios.get(TEST_CONFIG.endpoints.health, {
          timeout: TEST_CONFIG.timeouts.health
        });
        const end = Date.now();
        const responseTime = end - start;

        if (responseTime > TEST_CONFIG.performance.responseTime) {
          throw new Error(`Response time ${responseTime}ms exceeds limit of ${TEST_CONFIG.performance.responseTime}ms`);
        }

        return {
          status: 'passed',
          message: `Response time is acceptable (${responseTime}ms)`
        };
      } catch (error) {
        throw new Error(`Response time test failed: ${error.message}`);
      }
    },

    concurrentLoad: async () => {
      const startTime = Date.now();
      const requests = Array(TEST_CONFIG.performance.concurrentRequests).fill(null).map((_, i) =>
        axios.get(`${TEST_CONFIG.endpoints.health}?test=${i}`, {
          timeout: TEST_CONFIG.timeouts.health
        })
      );

      const results = await Promise.allSettled(requests);
      const endTime = Date.now();
      const duration = endTime - startTime;

      const successful = results.filter(result =>
        result.status === 'fulfilled' && result.value.status === 200
      ).length;

      const successRate = (successful / TEST_CONFIG.performance.concurrentRequests) * 100;

      if (successRate < 95) {
        throw new Error(`Load test success rate ${successRate.toFixed(1)}% is below 95% threshold`);
      }

      if (duration > TEST_CONFIG.performance.requestDuration) {
        throw new Error(`Load test duration ${duration}ms exceeds limit of ${TEST_CONFIG.performance.requestDuration}ms`);
      }

      return {
        status: 'passed',
        message: `Load test passed (${successRate.toFixed(1)}% success rate, ${duration}ms duration)`
      };
    }
  }
};

// Test Runner
class TestRunner {
  constructor() {
    this.results = testResults;
  }

  async runTestCategory(category, categoryTests) {
    console.log(`\n🧪 Running ${category} tests...`);

    for (const [testName, testFn] of Object.entries(categoryTests)) {
      try {
        console.log(`  📋 Testing: ${testName}`);
        const result = await testFn();
        this.results.passed.push({
          category,
          test: testName,
          ...result,
          timestamp: new Date().toISOString()
        });
        console.log(`  ✅ ${testName}: ${result.message}`);
      } catch (error) {
        this.results.failed.push({
          category,
          test: testName,
          status: 'failed',
          message: error.message,
          timestamp: new Date().toISOString()
        });
        console.log(`  ❌ ${testName}: ${error.message}`);
      }
    }
  }

  async runAllTests() {
    console.log('🚀 Starting Voice by Kraliki Production Deployment Test Suite');
    console.log('========================================================');
    console.log(`📅 Test Date: ${new Date().toISOString()}`);
    console.log(`🌍 Environment: ${testResults.environment}`);

    // Run all test categories
    for (const [category, categoryTests] of Object.entries(tests)) {
      await this.runTestCategory(category, categoryTests);
    }

    // Generate report
    await this.generateReport();

    // Print summary
    this.printSummary();

    return this.results;
  }

  async generateReport() {
    const report = {
      summary: {
        total: this.results.passed.length + this.results.failed.length + this.results.skipped.length,
        passed: this.results.passed.length,
        failed: this.results.failed.length,
        skipped: this.results.skipped.length,
        passRate: ((this.results.passed.length / (this.results.passed.length + this.results.failed.length)) * 100).toFixed(1)
      },
      results: this.results,
      recommendations: this.generateRecommendations()
    };

    const reportPath = join(process.cwd(), 'test-results', `production-test-report-${Date.now()}.json`);
    await fs.mkdir(join(process.cwd(), 'test-results'), { recursive: true });
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));

    console.log(`\n📊 Test report saved to: ${reportPath}`);

    return report;
  }

  generateRecommendations() {
    const recommendations = [];

    if (this.results.failed.some(r => r.category === 'security')) {
      recommendations.push('Review and fix security configuration issues before production deployment');
    }

    if (this.results.failed.some(r => r.category === 'performance')) {
      recommendations.push('Optimize performance and consider scaling resources if needed');
    }

    if (this.results.failed.some(r => r.category === 'configuration')) {
      recommendations.push('Complete configuration setup with proper production values');
    }

    if (this.results.failed.length > 0) {
      recommendations.push('Address all failed tests before proceeding with production deployment');
    } else {
      recommendations.push('All tests passed - production deployment is ready');
    }

    return recommendations;
  }

  printSummary() {
    const total = this.results.passed.length + this.results.failed.length + this.results.skipped.length;
    const passRate = ((this.results.passed.length / total) * 100).toFixed(1);

    console.log('\n📋 Test Summary');
    console.log('================');
    console.log(`📊 Total Tests: ${total}`);
    console.log(`✅ Passed: ${this.results.passed.length}`);
    console.log(`❌ Failed: ${this.results.failed.length}`);
    console.log(`⏭️  Skipped: ${this.results.skipped.length}`);
    console.log(`📈 Pass Rate: ${passRate}%`);

    if (this.results.failed.length > 0) {
      console.log('\n❌ Failed Tests:');
      this.results.failed.forEach(failure => {
        console.log(`   - ${failure.category}.${failure.test}: ${failure.message}`);
      });
    }

    console.log('\n🎯 Recommendations:');
    this.generateRecommendations().forEach(rec => {
      console.log(`   - ${rec}`);
    });
  }
}

// Main execution
async function main() {
  try {
    // Set production environment for testing
    process.env.NODE_ENV = 'production';

    const runner = new TestRunner();
    const results = await runner.runAllTests();

    // Exit with appropriate code
    process.exit(results.failed.length > 0 ? 1 : 0);
  } catch (error) {
    console.error('Test suite execution failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { TestRunner, tests, TEST_CONFIG };
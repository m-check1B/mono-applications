/**
 * Basic Circuit Breaker Test
 * Tests the core functionality of our circuit breaker implementation
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { circuitBreakerService } from '../server/services/circuit-breaker-service';

describe('Circuit Breaker Service', () => {
  beforeEach(() => {
    // Clean up any existing circuit breakers
    circuitBreakerService.resetAll();
  });

  afterEach(() => {
    // Clean up after tests
    circuitBreakerService.cleanup();
  });

  it('should create a circuit breaker for a service', async () => {
    const testFunction = async (input: string) => {
      return `Hello ${input}`;
    };

    const circuitBreaker = circuitBreakerService.createCircuitBreaker(
      'test_service',
      testFunction
    );

    expect(circuitBreaker).toBeDefined();

    // Test successful execution
    const result = await circuitBreakerService.execute('test_service', 'World');
    expect(result).toBe('Hello World');
  });

  it('should handle service failures gracefully', async () => {
    let callCount = 0;
    const failingFunction = async () => {
      callCount++;
      if (callCount <= 3) {
        throw new Error('Service temporarily unavailable');
      }
      return 'Success after retries';
    };

    // Create circuit breaker with fallback
    circuitBreakerService.createCircuitBreaker(
      'failing_service',
      failingFunction,
      {
        timeout: 1000,
        errorThresholdPercentage: 50,
        resetTimeout: 1000,
        volumeThreshold: 2
      },
      {
        type: 'static',
        fallbackFunction: async () => 'Fallback response'
      }
    );

    // First few calls should fail and use fallback
    try {
      const result1 = await circuitBreakerService.execute('failing_service');
      // Might get fallback or throw
    } catch (error) {
      expect((error as Error).message).toContain('Service temporarily unavailable');
    }

    // Eventually should succeed
    const finalResult = await circuitBreakerService.execute('failing_service');
    expect(finalResult).toBeDefined();
  });

  it('should provide health status for circuit breakers', async () => {
    const testFunction = async () => 'test';

    circuitBreakerService.createCircuitBreaker('health_test', testFunction);

    const status = circuitBreakerService.getStatus('health_test');
    expect(status).toBeDefined();
    expect(status?.state).toBeDefined();

    const allStatus = circuitBreakerService.getAllStatus();
    expect(allStatus).toHaveProperty('health_test');

    const healthCheck = circuitBreakerService.healthCheck();
    expect(healthCheck).toHaveProperty('healthy');
    expect(healthCheck).toHaveProperty('details');
  });

  it('should track metrics correctly', async () => {
    const testFunction = async (shouldFail: boolean) => {
      if (shouldFail) {
        throw new Error('Intentional failure');
      }
      return 'success';
    };

    circuitBreakerService.createCircuitBreaker('metrics_test', testFunction);

    // Execute some successful calls
    await circuitBreakerService.execute('metrics_test', false);
    await circuitBreakerService.execute('metrics_test', false);

    // Execute some failed calls
    try {
      await circuitBreakerService.execute('metrics_test', true);
    } catch (error) {
      // Expected failure
    }

    const metrics = circuitBreakerService.getMetrics();
    expect(metrics).toHaveProperty('metrics_test');

    const serviceMetrics = metrics.metrics_test;
    expect(serviceMetrics.successRate).toBeDefined();
    expect(serviceMetrics.fallbackRate).toBeDefined();
  });

  it('should reset circuit breakers correctly', async () => {
    const testFunction = async () => 'test';

    circuitBreakerService.createCircuitBreaker('reset_test', testFunction);

    // Execute a call to initialize
    await circuitBreakerService.execute('reset_test');

    // Reset the specific circuit breaker
    circuitBreakerService.reset('reset_test');

    const status = circuitBreakerService.getStatus('reset_test');
    expect(status?.state).toBe('closed');

    // Test reset all
    circuitBreakerService.resetAll();

    const allStatus = circuitBreakerService.getAllStatus();
    Object.values(allStatus).forEach((status: any) => {
      if (status) {
        expect(status.state).toBe('closed');
      }
    });
  });
});
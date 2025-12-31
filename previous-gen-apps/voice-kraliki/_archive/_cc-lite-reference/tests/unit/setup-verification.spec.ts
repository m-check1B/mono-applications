import { describe, test, expect, vi } from 'vitest';

/**
 * Basic sanity checks for the Vitest testing environment
 */

describe('Test Environment Setup', () => {
  test('Vitest globals are available', () => {
    expect(vi).toBeDefined();
    expect(typeof vi.fn).toBe('function');
  });

  test('Process environment is accessible', () => {
    expect(process.env).toBeDefined();
    expect(process.env.NODE_ENV).toBeDefined();
  });

  test('TypeScript transpilation works', () => {
    const testString: string = 'vitest';
    const testNumber: number = 123;

    expect(typeof testString).toBe('string');
    expect(typeof testNumber).toBe('number');
  });
});

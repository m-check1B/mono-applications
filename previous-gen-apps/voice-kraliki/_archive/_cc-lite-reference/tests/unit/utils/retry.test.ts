import { describe, it, expect, vi } from 'vitest';
import { calculateBackoff, withRetry } from '../../../server/utils/retry';

describe('retry utilities', () => {
  it('calculateBackoff returns value within expected jitter range', () => {
    const attempt = 2;
    const base = 100;
    const max = 10000;
    const value = calculateBackoff(attempt, base, max);
    const exp = Math.min(base * Math.pow(2, attempt - 1), max);
    const jitter = exp * 0.25;
    expect(value).toBeGreaterThanOrEqual(exp - jitter);
    expect(value).toBeLessThanOrEqual(exp + jitter);
  });

  it('withRetry retries and eventually succeeds', async () => {
    const fn = vi.fn()
      .mockRejectedValueOnce(new Error('fail 1'))
      .mockRejectedValueOnce(new Error('fail 2'))
      .mockResolvedValue('ok');

    const start = Date.now();
    const result = await withRetry(fn, { maxRetries: 3, initialDelay: 10, maxDelay: 20, factor: 1 });
    const elapsed = Date.now() - start;
    expect(result).toBe('ok');
    expect(fn).toHaveBeenCalledTimes(3);
    expect(elapsed).toBeGreaterThanOrEqual(20);
  }, 10_000);
});


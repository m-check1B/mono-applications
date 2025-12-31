import { describe, it, expect } from 'vitest';
import { AppErrorFactory, ErrorSeverity, ErrorCategory, convertTRPCError, isAppError, withErrorHandling } from '../../../server/utils/error-handler';
import { TRPCError } from '@trpc/server';

describe('error-handler basics', () => {
  it('creates AppError with defaults', () => {
    const err = AppErrorFactory.createError('SYSTEM_INTERNAL_ERROR');
    expect(isAppError(err)).toBe(true);
    expect(err.statusCode).toBeGreaterThan(0);
    expect(err.severity).toBeDefined();
    expect(err.category).toBeDefined();
  });

  it('converts TRPC UNAUTHORIZED to AUTH_INVALID_TOKEN', () => {
    const trpc = new TRPCError({ code: 'UNAUTHORIZED', message: 'nope' });
    const app = convertTRPCError(trpc);
    expect(isAppError(app)).toBe(true);
    expect(app.code).toContain('AUTH');
    expect(app.statusCode).toBe(401);
  });

  it('withErrorHandling returns fallback value', async () => {
    const value = await withErrorHandling(async () => { throw new Error('boom'); }, 'fallback');
    expect(value).toBe('fallback');
  });
});


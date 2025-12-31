import { describe, it, expect } from 'vitest';
import {
  formatDurationSeconds,
  transformCallRecord,
  transformCallRecordForUI
} from '../../src/utils/call-utils';

describe('formatDurationSeconds', () => {
  it('formats numeric seconds into mm:ss', () => {
    expect(formatDurationSeconds(65)).toBe('01:05');
  });

  it('pads seconds and minutes with leading zeros', () => {
    expect(formatDurationSeconds(5)).toBe('00:05');
    expect(formatDurationSeconds(65)).toBe('01:05');
  });

  it('accepts numeric strings and formatted strings', () => {
    expect(formatDurationSeconds('90')).toBe('01:30');
    expect(formatDurationSeconds('01:45')).toBe('01:45');
  });

  it('handles invalid input gracefully', () => {
    expect(formatDurationSeconds('invalid')).toBe('00:00');
    expect(formatDurationSeconds(undefined)).toBe('00:00');
    expect(formatDurationSeconds(null as unknown as number)).toBe('00:00');
  });

  it('normalizes fractional seconds by truncating decimals', () => {
    expect(formatDurationSeconds(59.8)).toBe('00:59');
    expect(formatDurationSeconds(125.4)).toBe('02:05');
  });
});

describe('call record transformation helpers', () => {
  it('uses fallback duration fields when transforming raw records', () => {
    const record = transformCallRecord({
      id: 'call-1',
      callDuration: '125',
      status: 'connected'
    });

    expect(record.duration).toBe(125);
  });

  it('formats duration for UI even when only fallback fields exist', () => {
    const call = transformCallRecordForUI({
      id: 'call-2',
      status: 'active',
      queue: 'Support',
      callDuration: 125
    });

    expect(call.duration).toBe('02:05');
  });
});

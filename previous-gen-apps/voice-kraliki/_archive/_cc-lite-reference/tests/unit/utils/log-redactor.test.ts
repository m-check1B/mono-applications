import { describe, it, expect } from 'vitest';
import { logRedactor } from '../../../server/utils/log-redactor';

describe('log-redactor', () => {
  it('redacts JWT tokens (partial masking)', () => {
    const token = 'eyJabc1234567890.abcDEF1234567890.XYZ9876543210';
    const input = `Authorization: ${token}`;
    const out = logRedactor.redactString(input);
    expect(out).toContain('Authorization:');
    expect(out).not.toContain(token); // original token not present
  });

  it('redacts URLs with tokens and passwords', () => {
    const input = 'https://user:pass@example.com/path?token=abcdef1234567890key&foo=bar';
    const out = logRedactor.redactUrl(input);
    // password redacted (may be URL-encoded)
    expect(out).toMatch(/https:\/\/user:(\[REDACTED\]|%5BREDACTED%5D)@/);
    expect(out).toContain('token=');
    expect(out).not.toContain('abcdef123456');
  });

  it('redacts sensitive headers', () => {
    const headers = {
      Authorization: 'Bearer supersecrettokenvalue',
      'X-Api-Key': 'abcd-efgh-ijkl',
      Accept: 'application/json'
    } as any;
    const out = logRedactor.redactHeaders(headers);
    expect(out.Authorization).toMatch(/^Bearer /);
    expect(out['X-Api-Key']).toBe('[REDACTED]');
    expect(out.Accept).toBe('application/json');
  });
});

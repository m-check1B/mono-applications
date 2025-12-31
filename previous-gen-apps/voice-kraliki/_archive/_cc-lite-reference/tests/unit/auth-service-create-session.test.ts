import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { webcrypto } from 'node:crypto';

vi.mock('@unified/auth-core', async () => {
  const actual = await vi.importActual<typeof import('@unified/auth-core')>('@unified/auth-core');
  return {
    ...actual,
    signToken: vi.fn().mockResolvedValue('signed-token')
  };
});

import * as authCore from '@unified/auth-core';
import { AuthService } from '../../server/services/auth-service';

(process as any).env.SKIP_DB_TEST_SETUP = 'true';
if (!('crypto' in globalThis)) {
  Object.defineProperty(globalThis, 'crypto', { value: webcrypto });
}

const prismaMock = {
  user: {
    update: vi.fn(),
    findUnique: vi.fn()
  },
  userSession: {
    create: vi.fn()
  }
} as const;

describe('AuthService.createSessionForUserId', () => {
  const baseUser = {
    id: 'user-1',
    email: 'agent@cc-light.local',
    username: 'agent',
    firstName: 'Test',
    lastName: 'Agent',
    role: 'ADMIN' as const,
    organizationId: 'org-1',
    phoneExtension: '1001',
    avatar: null,
    lastLoginAt: new Date('2024-01-01T00:00:00Z'),
    organization: {
      id: 'org-1',
      name: 'Demo Org'
    }
  };

  let authService: AuthService;
  let userUpdateMock: vi.Mock;
  let userFindMock: vi.Mock;
  let sessionCreateMock: vi.Mock;

  beforeEach(async () => {
    vi.clearAllMocks();

    userUpdateMock = prismaMock.user.update as unknown as vi.Mock;
    userFindMock = prismaMock.user.findUnique as unknown as vi.Mock;
    sessionCreateMock = prismaMock.userSession.create as unknown as vi.Mock;

    userUpdateMock.mockResolvedValue({
      ...baseUser,
      lastLoginAt: new Date('2025-01-01T00:00:00Z')
    });
    userFindMock.mockResolvedValue(baseUser);
    sessionCreateMock.mockResolvedValue({ id: 'session-1' });

    const { privateKeyPEM, publicKeyPEM } = await authCore.generateAuthKeys();
    authService = new AuthService({
      prisma: prismaMock as unknown as any,
      privateKey: privateKeyPEM,
      publicKey: publicKeyPEM
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('persists a session with hashed refresh token and updates lastLoginAt by default', async () => {
    const result = await authService.createSessionForUserId(baseUser.id);

    expect(result.user.id).toBe(baseUser.id);
    expect(result.token).toBe('signed-token');
    expect(typeof result.refreshToken).toBe('string');

    expect(sessionCreateMock).toHaveBeenCalledTimes(1);
    const sessionPayload = sessionCreateMock.mock.calls[0][0];
    expect(sessionPayload.data.userId).toBe(baseUser.id);
    expect(sessionPayload.data.refreshTokenHash).toBeTruthy();
    expect(sessionPayload.data.refreshTokenHash).not.toEqual(result.refreshToken);

    expect(userUpdateMock).toHaveBeenCalledTimes(1);
    const updateArgs = userUpdateMock.mock.calls[0][0];
    expect(updateArgs).toMatchObject({
      where: { id: baseUser.id },
      data: { lastLoginAt: expect.any(Date) }
    });
  });

  it('can reuse existing lastLoginAt when updateLastLogin is false', async () => {
    await authService.createSessionForUserId(baseUser.id, { updateLastLogin: false });

    expect(userUpdateMock).not.toHaveBeenCalled();
    expect(userFindMock).toHaveBeenCalledWith({
      where: { id: baseUser.id },
      include: { organization: true }
    });
  });
});

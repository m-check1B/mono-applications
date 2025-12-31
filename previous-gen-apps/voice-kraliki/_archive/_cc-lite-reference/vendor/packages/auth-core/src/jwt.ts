import { randomUUID } from 'node:crypto';
import { SignJWT, jwtVerify, generateKeyPair, exportSPKI, exportPKCS8, importSPKI, importPKCS8 } from 'jose';
import { z } from 'zod';
import type { SessionPayload, AccessTokenPayload, AuthResponse, TokenService } from './types';

export const SessionPayloadSchema = z.object({
  sub: z.string(),            // user id
  email: z.string().email(),
  roles: z.array(z.string()).default([]),
  iat: z.number().optional(),
  exp: z.number().optional(),
  metadata: z.record(z.any()).optional()
});

export const AccessTokenPayloadSchema = z.object({
  sub: z.string(),            // user id
  email: z.string().email(),
  roles: z.array(z.string()).optional().default([]),
  permissions: z.array(z.string()).optional().default([]),
  iat: z.number().optional(),
  exp: z.number().optional(),
  appId: z.string().optional()
});

let runtimeKeys: { publicKeyPEM: string; privateKeyPEM: string } | null = null;
const refreshStore = new Map<string, SessionPayload>();

async function ensureKeys() {
  if (process.env.AUTH_PRIVATE_KEY && process.env.AUTH_PUBLIC_KEY) {
    return {
      privateKeyPEM: process.env.AUTH_PRIVATE_KEY,
      publicKeyPEM: process.env.AUTH_PUBLIC_KEY
    };
  }

  if (!runtimeKeys) {
    runtimeKeys = await generateAuthKeys();
  }
  return runtimeKeys;
}

export async function signToken(payload: SessionPayload, privateKeyPEM?: string) {
  const pkPem = privateKeyPEM ?? (await ensureKeys()).privateKeyPEM;
  const pk = await importPKCS8(pkPem, 'EdDSA');
  return new SignJWT(payload as any)
    .setProtectedHeader({ alg: 'EdDSA', typ: 'JWT' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(pk);
}

export async function verifyToken(token: string, publicKeyPEM?: string): Promise<SessionPayload> {
  const pubPem = publicKeyPEM ?? (await ensureKeys()).publicKeyPEM;
  const pub = await importSPKI(pubPem, 'EdDSA');
  const { payload } = await jwtVerify(token, pub, { algorithms: ['EdDSA'] });
  return SessionPayloadSchema.parse(payload);
}

export async function signAccessToken(payload: AccessTokenPayload, privateKeyPEM: string): Promise<string> {
  const pk = await importPKCS8(privateKeyPEM, 'EdDSA');
  return new SignJWT(payload as any)
    .setProtectedHeader({ alg: 'EdDSA', typ: 'JWT' })
    .setIssuedAt()
    .setExpirationTime('24h')
    .sign(pk);
}

export async function verifyAccessToken(token: string, publicKeyPEM: string): Promise<AccessTokenPayload> {
  const pub = await importSPKI(publicKeyPEM, 'EdDSA');
  const { payload } = await jwtVerify(token, pub, { algorithms: ['EdDSA'] });
  return AccessTokenPayloadSchema.parse(payload);
}

// Synchronous version that catches errors
export function verifyAccessTokenSync(token: string, publicKeyPEM: string): AccessTokenPayload | null {
  try {
    // This is a simplified sync version - in practice you might want to cache the key
    // For now, we'll return null for sync verification to avoid async issues
    return null;
  } catch (error) {
    return null;
  }
}

// Generate Ed25519 keypair
export async function generateAuthKeys() {
  const { publicKey, privateKey } = await generateKeyPair('EdDSA');
  const publicKeyPEM = await exportSPKI(publicKey);
  const privateKeyPEM = await exportPKCS8(privateKey);
  
  return {
    publicKeyPEM,
    privateKeyPEM
  };
}

// Convert PEM to JWK for JWKS endpoint
export async function pemToJWK(publicKeyPEM: string) {
  const key = await importSPKI(publicKeyPEM, 'EdDSA');
  const jwk = await crypto.subtle.exportKey('jwk', key as any);
  return {
    ...jwk,
    alg: 'EdDSA',
    use: 'sig',
    kid: 'primary' // Key ID
  };
}

// Fastify preHandler middleware
export function fastifyAuth({ publicKeyPEM, cookieName = 'vd_session' }: {
  publicKeyPEM: string; 
  cookieName?: string;
}) {
  return async function(req: any, reply: any) {
    const raw = req.cookies?.[cookieName];
    if (!raw) return reply.code(401).send({ error: 'unauthenticated' });
    try {
      req.user = await verifyToken(raw, publicKeyPEM);
    } catch (err) {
      return reply.code(401).send({ error: 'invalid-session' });
    }
  };
}

// Express middleware (for websites/demos)
export function expressAuth({ publicKeyPEM, cookieName = 'vd_session' }: {
  publicKeyPEM: string;
  cookieName?: string;
}) {
  return async function(req: any, res: any, next: any) {
    const raw = req.cookies?.[cookieName];
    if (!raw) return res.status(401).json({ error: 'unauthenticated' });
    try {
      req.user = await verifyToken(raw, publicKeyPEM);
      next();
    } catch {
      return res.status(401).json({ error: 'invalid-session' });
    }
  };
}

// Helper to set secure cookie
export function setAuthCookie(reply: any, token: string, options: {
  cookieName?: string;
  domain?: string;
  secure?: boolean;
  sameSite?: 'lax' | 'strict' | 'none';
} = {}) {
  const {
    cookieName = 'vd_session',
    domain = '.verduona.com',
    secure = true,
    sameSite = 'lax'
  } = options;
  
  reply.setCookie(cookieName, token, {
    httpOnly: true,
    secure,
    sameSite,
    domain,
    path: '/',
    maxAge: 7 * 24 * 60 * 60 // 7 days
  });
}

// TokenService implementation
export class JWTTokenService implements TokenService {
  constructor(
    private privateKeyPEM: string,
    private publicKeyPEM: string
  ) {}

  async sign(payload: AccessTokenPayload): Promise<string> {
    return signAccessToken(payload, this.privateKeyPEM);
  }

  async verify(token: string): Promise<AccessTokenPayload> {
    return verifyAccessToken(token, this.publicKeyPEM);
  }

  verifyAccessToken(token: string): AccessTokenPayload | null {
    return verifyAccessTokenSync(token, this.publicKeyPEM);
  }

  async refresh(refreshToken: string): Promise<AuthResponse> {
    // This is a placeholder - in practice you'd:
    // 1. Verify refresh token
    // 2. Get user from database
    // 3. Generate new access token
    // 4. Return new tokens
    throw new Error('refresh method not implemented');
  }
}

// Factory function to create token service
export function createTokenService(privateKeyPEM: string, publicKeyPEM: string): TokenService {
  return new JWTTokenService(privateKeyPEM, publicKeyPEM);
}

interface CreateTokenOptions {
  userId: string;
  email: string;
  roles?: string[];
  metadata?: Record<string, any>;
  expiresIn?: string;
}

export async function createToken(options: CreateTokenOptions) {
  const { privateKeyPEM, publicKeyPEM } = await ensureKeys();
  const payload: SessionPayload = {
    sub: options.userId,
    email: options.email,
    roles: options.roles ?? (options.metadata?.role ? [options.metadata.role] : []),
    metadata: options.metadata,
  };

  const token = await signToken(payload, privateKeyPEM);
  const refreshToken = randomUUID();
  refreshStore.set(refreshToken, payload);

  const expiresInMs = options.expiresIn ? parseDuration(options.expiresIn) : 7 * 24 * 60 * 60 * 1000;

  return {
    token,
    refreshToken,
    expiresAt: new Date(Date.now() + expiresInMs).toISOString(),
    payload,
    publicKey: publicKeyPEM
  };
}

export async function refreshToken(refreshToken: string) {
  const payload = refreshStore.get(refreshToken);
  if (!payload) {
    throw new Error('invalid-refresh-token');
  }

  return createToken({
    userId: payload.sub,
    email: payload.email,
    roles: payload.roles,
    metadata: payload.metadata
  });
}

function parseDuration(input: string): number {
  const match = /^([0-9]+)(ms|s|m|h|d)$/.exec(input);
  if (!match) return 7 * 24 * 60 * 60 * 1000;
  const [, value, unit] = match;
  const amount = Number(value);
  switch (unit) {
    case 'ms':
      return amount;
    case 's':
      return amount * 1000;
    case 'm':
      return amount * 60 * 1000;
    case 'h':
      return amount * 60 * 60 * 1000;
    case 'd':
      return amount * 24 * 60 * 60 * 1000;
    default:
      return 7 * 24 * 60 * 60 * 1000;
  }
}

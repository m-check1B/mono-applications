import { env } from '$env/dynamic/private';
import { createRemoteJWKSet, jwtVerify, type JWTPayload } from 'jose';
import { logger } from '$lib/utils/logger';

// Zitadel OIDC configuration
const ZITADEL_DOMAIN = env.ZITADEL_DOMAIN || 'identity.verduona.dev';
const CLIENT_ID = env.ZITADEL_CLIENT_ID || '';
const CLIENT_SECRET = env.ZITADEL_CLIENT_SECRET || '';

// JWKS client for JWT verification (cached automatically by jose)
const JWKS = createRemoteJWKSet(new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/keys`));

export interface VerifiedTokenPayload extends JWTPayload {
  sub: string;
  name?: string;
  preferred_username?: string;
  email?: string;
}

export interface User {
  id: string;
  name: string;
  email?: string;
  isSSO: boolean;
}

function getRedirectUri(): string {
  if (env.SSO_REDIRECT_URI) {
    return env.SSO_REDIRECT_URI;
  }

  return env.ORIGIN ? `${env.ORIGIN}/auth/sso/callback` : 'http://localhost:5173/auth/sso/callback';
}

export function isAuthConfigured(): boolean {
  return !!(CLIENT_ID && CLIENT_SECRET);
}

export function createAuthorizationURL(state: string): URL | null {
  if (!CLIENT_ID) return null;

  const url = new URL(`https://${ZITADEL_DOMAIN}/oauth/v2/authorize`);
  url.searchParams.set('client_id', CLIENT_ID);
  url.searchParams.set('redirect_uri', getRedirectUri());
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('scope', 'openid profile email');
  url.searchParams.set('state', state);

  return url;
}

export async function validateAuthorizationCode(code: string): Promise<{
  accessToken: string;
  refreshToken?: string;
  idToken: string;
} | null> {
  if (!CLIENT_ID || !CLIENT_SECRET) return null;

  try {
    const response = await fetch(`https://${ZITADEL_DOMAIN}/oauth/v2/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + btoa(`${CLIENT_ID}:${CLIENT_SECRET}`)
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: getRedirectUri()
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      logger.error('Token exchange failed', new Error(errorText));
      return null;
    }

    const tokens = await response.json();
    return {
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
      idToken: tokens.id_token
    };
  } catch (error) {
    logger.error('Failed to validate authorization code', error);
    return null;
  }
}

/**
 * Verify ID token signature using Zitadel's JWKS.
 * This cryptographically validates the token wasn't tampered with.
 */
export async function verifyIdToken(idToken: string): Promise<VerifiedTokenPayload | null> {
  try {
    const { payload } = await jwtVerify(idToken, JWKS, {
      issuer: `https://${ZITADEL_DOMAIN}`,
    });

    if (!payload.sub) {
      logger.error('ID token missing sub claim');
      return null;
    }

    return payload as VerifiedTokenPayload;
  } catch (error) {
    logger.error('ID token verification failed', error);
    return null;
  }
}

/**
 * Parse session cookie and extract user info
 */
export function parseSessionCookie(cookie: string | undefined): User | null {
  if (!cookie) return null;

  try {
    const decoded = JSON.parse(atob(cookie));
    return {
      id: decoded.sub,
      name: decoded.name || decoded.preferred_username || 'User',
      email: decoded.email,
      isSSO: true
    };
  } catch {
    return null;
  }
}

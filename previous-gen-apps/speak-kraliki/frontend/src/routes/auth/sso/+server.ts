import { redirect, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { isAuthConfigured, createAuthorizationURL } from '$lib/server/auth';

export const GET: RequestHandler = async ({ cookies }) => {
  if (!isAuthConfigured()) {
    throw error(503, 'SSO is not configured. Please contact administrator.');
  }

  const state = crypto.randomUUID();
  cookies.set('oauth_state', state, {
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 60 * 10 // 10 minutes
  });

  const authUrl = createAuthorizationURL(state);
  if (!authUrl) {
    throw error(500, 'Failed to create authorization URL');
  }

  throw redirect(302, authUrl.toString());
};

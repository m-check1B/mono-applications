import { redirect, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { validateAuthorizationCode, verifyIdToken, shouldUseSecureCookies } from '$lib/server/auth';

export const GET: RequestHandler = async ({ url, cookies, request }) => {
	const code = url.searchParams.get('code');
	const state = url.searchParams.get('state');
	const storedState = cookies.get('oauth_state');

	// Clear the state cookie
	cookies.delete('oauth_state', { path: '/' });

	// Validate state
	if (!state || state !== storedState) {
		throw error(400, 'Invalid state parameter');
	}

	if (!code) {
		throw error(400, 'Missing authorization code');
	}

	// Exchange code for tokens
	const tokens = await validateAuthorizationCode(code);
	if (!tokens) {
		throw error(500, 'Failed to validate authorization code');
	}

	// Verify ID token signature with JWKS (cryptographic verification)
	const userData = await verifyIdToken(tokens.idToken);
	if (!userData) {
		throw error(500, 'Failed to verify ID token');
	}

	// Store the actual JWT (ID token) in session cookie
	// This allows us to verify it cryptographically on each request
	cookies.set('session', tokens.idToken, {
		path: '/',
		httpOnly: true,
		secure: shouldUseSecureCookies(url, request),
		sameSite: 'lax',
		maxAge: 60 * 60 * 24 * 7 // 1 week
	});

	throw redirect(302, '/');
};

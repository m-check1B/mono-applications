import type { LayoutServerLoad } from './$types';
import { isLocalRequest, getLocalUser, verifyIdToken } from '$lib/server/auth';
import { redirect } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ request, cookies, url }) => {
	// Always allow API routes without auth check here (they handle their own)
	if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/auth/')) {
		return { user: null };
	}

	// Localhost bypass for Kraliki agents and local development
	// This is required for agent swarm to access the dashboard
	if (isLocalRequest(request)) {
		return { user: getLocalUser() };
	}

	// Check session cookie
	const sessionToken = cookies.get('session');

	if (!sessionToken) {
		// Public requests without session must login
		throw redirect(302, '/auth/login');
	}

	// Try to parse as local auth session first (base64 JSON)
	try {
		const sessionData = JSON.parse(atob(sessionToken));
		if (sessionData.isLocal) {
			// Local auth session - bypass JWT validation
			return {
				user: {
					id: sessionData.sub || 'local-user',
					name: sessionData.name || 'Local User',
					email: sessionData.email,
					isLocal: true
				}
			};
		}
	} catch {
		// Not a local session, continue to JWT validation
	}

	// Verify session token (JWT) with Zitadel's JWKS
	// This cryptographically validates the token signature and expiration
	const userData = await verifyIdToken(sessionToken);

	if (!userData) {
		// Invalid or expired token - clear session and redirect to login
		cookies.delete('session', { path: '/' });
		throw redirect(302, '/auth/login');
	}

	return {
		user: {
			id: userData.sub,
			name: userData.name || userData.preferred_username || 'User',
			email: userData.email,
			isLocal: false
		}
	};
};

// @ts-nocheck
import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import {
	validateLocalCredentials,
	isAuthConfigured,
	isLocalAuthConfigured,
	createAuthorizationURL,
	isSsoDisabled,
	shouldUseSecureCookies
} from '$lib/server/auth';

export const load = () => {
	return {
		authConfigured: isAuthConfigured(),
		localAuthConfigured: isLocalAuthConfigured(),
		ssoDisabled: isSsoDisabled()
	};
};

export const actions = {
	default: async ({ request, cookies, url }: import('./$types').RequestEvent) => {
		const data = await request.formData();
		const email = data.get('email')?.toString() || '';
		const password = data.get('password')?.toString() || '';

		if (!email || !password) {
			return fail(400, { error: 'Email and password required' });
		}

		// Try local credentials first
		const user = validateLocalCredentials(email, password);
		if (user) {
			// For local auth, create a simple session token (not JWT, just base64)
			// This bypasses JWT validation since local users don't go through Zitadel
			const sessionData = btoa(JSON.stringify({
				sub: user.id,
				name: user.name,
				email: user.email,
				isLocal: true
			}));

			cookies.set('session', sessionData, {
				path: '/',
				httpOnly: true,
				secure: shouldUseSecureCookies(url, request),
				sameSite: 'lax',
				maxAge: 60 * 60 * 24 * 7 // 1 week
			});
			throw redirect(302, '/');
		}

		// If Zitadel is configured, redirect there
		if (isAuthConfigured()) {
			const state = crypto.randomUUID();
			cookies.set('oauth_state', state, {
				path: '/',
				httpOnly: true,
				secure: true,
				sameSite: 'lax',
				maxAge: 60 * 10
			});
			const authUrl = createAuthorizationURL(state);
			if (authUrl) {
				throw redirect(302, authUrl.toString());
			}
		}

		return fail(401, { error: 'Invalid credentials' });
	}
};
;null as any as PageServerLoad;;null as any as Actions;
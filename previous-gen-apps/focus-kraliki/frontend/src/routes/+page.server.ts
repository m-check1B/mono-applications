import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { logger } from '$lib/utils/logger';

const TOKEN_COOKIE = 'focus_token';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = cookies.get(TOKEN_COOKIE);

	if (!token) {
		throw redirect(307, '/login');
	}

	try {
		const response = await fetch('/api/auth/me', {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		if (response.ok) {
			throw redirect(307, '/dashboard');
		}
	} catch (error) {
		logger.error('Failed to validate auth token on server load', error);
	}

	cookies.delete(TOKEN_COOKIE, { path: '/' });
	throw redirect(307, '/login');
};

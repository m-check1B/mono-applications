// @ts-nocheck
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { createLocalUser, shouldUseSecureCookies } from '$lib/server/auth';

function getRequiredPin(): string {
	const directPin = (process.env.REGISTRATION_PIN || '').trim();
	if (directPin) return directPin;

	const env = (process.env.KRALIKI_ENV || '').trim().toUpperCase();
	if (!env) return '';

	const envPin = (process.env[`REGISTRATION_PIN_${env}`] || '').trim();
	return envPin;
}

export const actions = {
	default: async ({ request, cookies, url }: import('./$types').RequestEvent) => {
		const data = await request.formData();
		const name = data.get('name')?.toString().trim() || '';
		const email = data.get('email')?.toString().trim() || '';
		const password = data.get('password')?.toString() || '';
		const confirmPassword = data.get('confirmPassword')?.toString() || '';
		const registrationPin = data.get('registrationPin')?.toString().trim() || '';
		const requiredPin = getRequiredPin();

		if (!name || !email || !password) {
			return fail(400, {
				error: 'Name, email, and password are required',
				name,
				email,
				registrationPin
			});
		}

		if (password !== confirmPassword) {
			return fail(400, { error: 'Passwords do not match', name, email, registrationPin });
		}

		if (requiredPin && registrationPin !== requiredPin) {
			return fail(400, { error: 'Invalid registration PIN', name, email, registrationPin });
		}

		const result = createLocalUser(name, email, password);
		if (result.error || !result.user) {
			return fail(400, { error: result.error || 'Failed to create account', name, email });
		}

		const sessionData = btoa(
			JSON.stringify({
				sub: result.user.id,
				name: result.user.name,
				email: result.user.email,
				isLocal: true
			})
		);

		cookies.set('session', sessionData, {
			path: '/',
			httpOnly: true,
			secure: shouldUseSecureCookies(url, request),
			sameSite: 'lax',
			maxAge: 60 * 60 * 24 * 7 // 1 week
		});

		throw redirect(302, '/');
	}
};
;null as any as Actions;
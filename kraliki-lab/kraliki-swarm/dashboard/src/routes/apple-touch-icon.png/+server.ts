import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = () => {
	// Serve a reasonable default instead of 404s from mobile browsers.
	throw redirect(302, '/favicon.svg');
};

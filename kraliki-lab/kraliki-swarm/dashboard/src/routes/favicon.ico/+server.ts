import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = () => {
	// Redirect legacy favicon requests to the SVG asset.
	throw redirect(302, '/favicon.svg');
};

import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = () => {
	// Handle older iOS icon requests without a hard 404.
	throw redirect(302, '/favicon.svg');
};

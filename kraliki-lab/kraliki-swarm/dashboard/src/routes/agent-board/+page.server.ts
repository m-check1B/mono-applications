import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Redirect to agents page which has the agent management functionality
	throw redirect(302, '/agents');
};

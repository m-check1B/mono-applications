import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	// Redirect to comms page which has the blackboard functionality
	throw redirect(302, '/comms');
};

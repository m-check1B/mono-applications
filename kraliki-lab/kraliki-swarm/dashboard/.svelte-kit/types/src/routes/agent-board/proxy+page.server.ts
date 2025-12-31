// @ts-nocheck
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load = async () => {
	// Redirect to agents page which has the agent management functionality
	throw redirect(302, '/agents');
};
;null as any as PageServerLoad;
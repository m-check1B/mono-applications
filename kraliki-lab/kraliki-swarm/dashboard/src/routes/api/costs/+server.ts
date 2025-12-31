import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getCostAnalytics } from '$lib/server/data';

export const GET: RequestHandler = async () => {
	const costs = await getCostAnalytics();
	return json(costs);
};

import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getFullStatus } from '$lib/server/data';

export const GET: RequestHandler = async () => {
	const status = await getFullStatus();
	return json(status);
};

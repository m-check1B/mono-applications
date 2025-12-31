import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * Speak by Kraliki - Conversations API Proxy (legacy VoP)
 * Deprecated: use /api/speak instead.
 */
const legacyResponse = () =>
	json(
		{ error: 'Legacy Speak endpoint removed. Use /api/speak instead.' },
		{ status: 410 }
	);

export const GET: RequestHandler = async () => legacyResponse();

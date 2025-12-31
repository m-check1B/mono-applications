import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * Speak by Kraliki legacy VoP endpoint (removed).
 *
 * Deprecated: use /api/speak routes for new integrations.
 */
const legacyResponse = () =>
	json(
		{ error: 'Legacy Speak endpoint removed. Use /api/speak instead.' },
		{ status: 410 }
	);

export const GET: RequestHandler = async () => legacyResponse();
export const POST: RequestHandler = async () => legacyResponse();
export const PUT: RequestHandler = async () => legacyResponse();
export const PATCH: RequestHandler = async () => legacyResponse();
export const DELETE: RequestHandler = async () => legacyResponse();

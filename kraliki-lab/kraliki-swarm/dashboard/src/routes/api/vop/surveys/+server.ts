import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

/**
 * Speak by Kraliki - Surveys API Proxy (legacy VoP)
 * Deprecated: use /api/speak/surveys instead.
 */
const legacyResponse = () =>
	json(
		{ error: 'Legacy Speak endpoint removed. Use /api/speak/surveys instead.' },
		{ status: 410 }
	);

export const GET: RequestHandler = async () => legacyResponse();
export const POST: RequestHandler = async () => legacyResponse();
export const PATCH: RequestHandler = async () => legacyResponse();

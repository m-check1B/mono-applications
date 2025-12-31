import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const VOICE_URL = 'http://127.0.0.1:8000';

/**
 * Voice by Kraliki providers endpoint
 * GET /api/voice/providers - List AI and telephony providers
 */
export const GET: RequestHandler = async () => {
  try {
    const response = await fetch(`${VOICE_URL}/api/v1/providers`, {
      signal: AbortSignal.timeout(10000)
    });

    if (!response.ok) {
      return json({ error: 'Voice by Kraliki providers API error', status: response.status }, { status: response.status });
    }

    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: 'Voice by Kraliki providers service unavailable' }, { status: 503 });
  }
};

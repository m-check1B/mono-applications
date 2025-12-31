import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const VOICE_URL = 'http://127.0.0.1:8000';

/**
 * Voice by Kraliki health check endpoint
 * GET /api/voice/health
 */
export const GET: RequestHandler = async () => {
  try {
    const response = await fetch(`${VOICE_URL}/health`, {
      signal: AbortSignal.timeout(5000)
    });

    if (!response.ok) {
      return json({
        status: 'unhealthy',
        service: 'voice-kraliki',
        error: `HTTP ${response.status}`
      }, { status: 503 });
    }

    const data = await response.json();
    return json({
      ...data,
      proxy: 'kraliki-swarm-dashboard'
    });
  } catch {
    return json({
      status: 'unhealthy',
      service: 'voice-kraliki',
      error: 'Service unreachable'
    }, { status: 503 });
  }
};

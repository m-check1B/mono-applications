import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const VOICE_URL = 'http://127.0.0.1:8000';

interface KralikiUser {
  id: string;
  email: string;
  name: string;
}

function getUserFromCookie(cookies: import('@sveltejs/kit').Cookies): KralikiUser | null {
  const sessionToken = cookies.get('session');
  if (!sessionToken) return null;
  try {
    const userData = JSON.parse(atob(sessionToken));
    return {
      id: userData.sub || 'unknown',
      email: userData.email || `${userData.sub}@kraliki.local`,
      name: userData.name || 'Kraliki User'
    };
  } catch {
    return null;
  }
}

function getKralikiHeaders(cookies: import('@sveltejs/kit').Cookies): Record<string, string> {
  const user = getUserFromCookie(cookies);
  if (user) {
    return {
      'X-Kraliki-Session': 'kraliki-internal',
      'X-Kraliki-User-Id': user.id,
      'X-Kraliki-User-Email': user.email,
      'X-Kraliki-User-Name': user.name,
      'X-Kraliki-Tier': 'free',
      'Content-Type': 'application/json'
    };
  }
  return {
    'X-Kraliki-Session': 'kraliki-internal',
    'X-Kraliki-User-Id': 'local-agent',
    'X-Kraliki-User-Email': 'agent@kraliki.local',
    'X-Kraliki-User-Name': 'Local Agent',
    'X-Kraliki-Tier': 'free',
    'Content-Type': 'application/json'
  };
}

/**
 * Voice by Kraliki sessions endpoint
 * GET /api/voice/sessions - List sessions
 * POST /api/voice/sessions - Create session
 */
export const GET: RequestHandler = async ({ url, cookies }) => {
  const headers = getKralikiHeaders(cookies);
  const status = url.searchParams.get('status');

  let apiUrl = `${VOICE_URL}/api/v1/sessions`;
  if (status) {
    apiUrl += `?status=${status}`;
  }

  try {
    const response = await fetch(apiUrl, {
      headers,
      signal: AbortSignal.timeout(10000)
    });

    if (!response.ok) {
      return json({ error: 'Voice by Kraliki sessions API error', status: response.status }, { status: response.status });
    }

    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: 'Voice by Kraliki sessions service unavailable' }, { status: 503 });
  }
};

export const POST: RequestHandler = async ({ request, cookies }) => {
  const headers = getKralikiHeaders(cookies);

  try {
    const body = await request.json();
    const response = await fetch(`${VOICE_URL}/api/v1/sessions`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000)
    });

    if (!response.ok) {
      return json({ error: 'Voice by Kraliki sessions API error', status: response.status }, { status: response.status });
    }

    const data = await response.json();
    return json(data);
  } catch {
    return json({ error: 'Voice by Kraliki sessions service unavailable' }, { status: 503 });
  }
};

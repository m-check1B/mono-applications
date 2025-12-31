import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Agent-Board API proxy
const AGENT_BOARD_URL = process.env.AGENT_BOARD_URL || 'http://127.0.0.1:3021';

export const GET: RequestHandler = async ({ params, url }) => {
	const path = params.path || '';
	const queryString = url.search || '';
	const targetUrl = `${AGENT_BOARD_URL}/api/${path}${queryString}`;

	try {
		const res = await fetch(targetUrl, {
			signal: AbortSignal.timeout(10000)
		});

		if (!res.ok) {
			return json({ error: 'Agent-Board API error' }, { status: res.status });
		}

		const data = await res.json();
		return json(data);
	} catch (e) {
		return json({ error: 'Agent-Board service unavailable' }, { status: 503 });
	}
};

export const POST: RequestHandler = async ({ params, url, request }) => {
	const path = params.path || '';
	const queryString = url.search || '';
	const targetUrl = `${AGENT_BOARD_URL}/api/${path}${queryString}`;

	try {
		const body = await request.json();
		const res = await fetch(targetUrl, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body),
			signal: AbortSignal.timeout(10000)
		});

		if (!res.ok) {
			return json({ error: 'Agent-Board API error' }, { status: res.status });
		}

		const data = await res.json();
		return json(data);
	} catch (e) {
		return json({ error: 'Agent-Board service unavailable' }, { status: 503 });
	}
};

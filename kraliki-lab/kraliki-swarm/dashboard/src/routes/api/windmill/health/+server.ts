import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const WINDMILL_API_URL = 'http://127.0.0.1:8101';

export const GET: RequestHandler = async () => {
	try {
		const response = await fetch(`${WINDMILL_API_URL}/health`, {
			signal: AbortSignal.timeout(5000)
		});

		if (response.ok) {
			const data = await response.json();
			return json(data);
		} else {
			return json({
				status: 'unhealthy',
				error: `HTTP ${response.status}`
			}, { status: 503 });
		}
	} catch (error) {
		return json({
			status: 'unhealthy',
			error: 'Windmill API unreachable'
		}, { status: 503 });
	}
};

import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Focus by Kraliki backend - uses Docker container IP since DNS doesn't resolve outside Docker
const FOCUS_URL = process.env.FOCUS_URL || 'http://172.28.0.4:3017';

/**
 * Focus by Kraliki health check endpoint
 * Used by Kraliki dashboard to verify Focus availability
 */
export const GET: RequestHandler = async ({ url }) => {
	const appDomain = url.hostname.endsWith('verduona.dev') ? 'verduona.dev' : 'kraliki.com';
	const publicUrl = `https://focus.${appDomain}`;
	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 2000);

		const response = await fetch(`${FOCUS_URL}/health`, {
			signal: controller.signal
		});

		clearTimeout(timeoutId);

		if (response.ok) {
			return json({
				status: 'online',
				url: FOCUS_URL,
				publicUrl
			});
		} else {
			return json({
				status: 'offline',
				url: FOCUS_URL,
				publicUrl
			});
		}
	} catch {
		return json({
			status: 'offline',
			url: FOCUS_URL,
			publicUrl
		});
	}
};

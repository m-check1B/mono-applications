import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Voice by Kraliki backend - uses Docker container IP since DNS doesn't resolve outside Docker
const VOICE_URL = process.env.VOICE_URL || 'http://172.27.0.5:8000';

export const GET: RequestHandler = async ({ url }) => {
	const appDomain = url.hostname.endsWith('verduona.dev') ? 'verduona.dev' : 'kraliki.com';
	const publicUrl = `https://voice.${appDomain}`;
	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), 2000);

		const response = await fetch(`${VOICE_URL}/health`, {
			signal: controller.signal
		});

		clearTimeout(timeoutId);

		if (response.ok) {
			return json({
				status: 'online',
				url: VOICE_URL,
				publicUrl
			});
		} else {
			return json({
				status: 'offline',
				url: VOICE_URL,
				publicUrl
			});
		}
	} catch {
		return json({
			status: 'offline',
			url: VOICE_URL,
			publicUrl
		});
	}
};

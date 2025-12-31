import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			out: 'build'
		}),
		csrf: {
			// Allow known app origins until CSRF policy is tightened.
			trustedOrigins: [
				'http://localhost:5173',
				'http://127.0.0.1:5173',
				'http://beta.kraliki.com',
				'http://kraliki.com',
				'http://www.kraliki.com',
				'https://beta.kraliki.com',
				'https://kraliki.verduona.dev',
				'https://kraliki.com',
				'https://www.kraliki.com'
			]
		}
	}
};

export default config;

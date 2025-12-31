import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5177,
		host: '127.0.0.1',
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:3035',
				changeOrigin: true
			}
		}
	}
});


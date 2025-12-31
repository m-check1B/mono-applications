import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
        plugins: [sveltekit()],
        server: {
                port: 5000,
                host: '0.0.0.0',
                strictPort: true,
                allowedHosts: true,
                hmr: {
                        clientPort: 443
                },
                proxy: {
                        '/api': {
                                target: 'http://127.0.0.1:3017',
                                changeOrigin: true,
                                rewrite: (path) => path.replace(/^\/api/, '')
                        }
                }
        }
});

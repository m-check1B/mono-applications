import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 5176,
    allowedHosts: [
      'localhost',
      'learn.verduona.localhost',
      'learn.verduona.dev',
      'learn.kraliki.com'
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8030',
        changeOrigin: true
      }
    }
  }
});

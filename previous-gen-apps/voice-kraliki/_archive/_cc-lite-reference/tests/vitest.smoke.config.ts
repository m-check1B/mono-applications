import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, '..'),
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: [path.resolve(__dirname, 'setup.ts')],
    include: ['tests/smoke/**/*.test.ts'],
    exclude: [],
    coverage: {
      enabled: false,
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
      '@server': path.resolve(__dirname, '../server'),
      '@unified': path.resolve(__dirname, '../vendor/packages'),
      '@stack-2025': path.resolve(__dirname, '../vendor/packages'),
    },
  },
});

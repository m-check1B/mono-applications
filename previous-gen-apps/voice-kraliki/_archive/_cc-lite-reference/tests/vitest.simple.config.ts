import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, '..'),
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup-simple.ts'],
    // Use forks instead of threads to avoid process.listeners error
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: false,
        maxForks: 2,
        minForks: 1
      }
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/**',
        'dist/**',
        '*.config.*',
        'tests/**',
        '**/*.d.ts'
      ]
    },
    testTimeout: 10000
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
      '@server': path.resolve(__dirname, '../server')
    }
  }
});
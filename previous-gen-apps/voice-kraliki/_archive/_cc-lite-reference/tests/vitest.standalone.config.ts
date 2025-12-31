import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, '..'),
  plugins: [react()],
  test: {
    globals: true,
    environment: 'node',
    // No setup files to avoid database connection
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '*.config.ts',
        'tests/',
        'src/main.tsx',
        'src/vite-env.d.ts'
      ],
      thresholds: {
        branches: 60,
        functions: 60,
        lines: 60,
        statements: 60
      }
    },
    include: ['tests/**/*-standalone.test.ts'],
    testTimeout: 30000,
    maxConcurrency: 5,
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        maxThreads: 4,
        minThreads: 2
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
      '@server': path.resolve(__dirname, '../server'),
      '@unified': path.resolve(__dirname, '../vendor/packages'),
      '@stack-2025': path.resolve(__dirname, '../vendor/packages')
    }
  }
});
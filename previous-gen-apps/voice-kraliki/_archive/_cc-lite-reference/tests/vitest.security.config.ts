import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, '..'),
  plugins: [react()],
  test: {
    globals: true,
    environment: 'node', // Use node environment for security tests
    setupFiles: [path.resolve(__dirname, 'setup.ts')],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '*.config.ts',
        'tests/setup.ts',
        'src/main.tsx',
        'src/vite-env.d.ts'
      ],
      include: [
        'server/**/*.ts',
        'src/**/*.ts',
        'src/**/*.tsx'
      ],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    },
    include: [
      'tests/security/**/*.{test,spec}.{ts,tsx}',
      'tests/integration/**/*.{test,spec}.{ts,tsx}',
      'tests/unit/**/*.{test,spec}.{ts,tsx}'
    ],
    exclude: [
      'tests/e2e/**',
      'tests/browser-automation/**',
      'tests/visual/**',
      'tests/voice/**',
      'tests/performance/**',
      'tests/accessibility/**',
      'tests/mobile/**',
      'tests/**/*.spec.ts', // Exclude Playwright test files
      'node_modules/',
      'dist/'
    ],
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

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, '..'),
  plugins: [react()],
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup-simple.ts'], // Use simplified setup for unit tests
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '*.config.ts',
        'tests/',
        'src/main.tsx',
        'src/vite-env.d.ts'
      ],
      include: [
        'server/**/*.ts',
        'src/**/*.ts',
        'src/**/*.tsx'
      ],
      thresholds: {
        branches: 70,
        functions: 70,
        lines: 70,
        statements: 70
      }
    },
    include: [
      'tests/security/auth-service-security-simple.test.ts',
      'tests/security/cookie-security.test.ts',
      'tests/security/twilio-webhook-security.test.ts',
      'tests/security/trpc-router-security.test.ts',
      'tests/security/metrics-endpoint-security.test.ts'
    ],
    exclude: [
      'tests/e2e/**',
      'tests/browser-automation/**',
      'tests/visual/**',
      'tests/voice/**',
      'tests/performance/**',
      'tests/accessibility/**',
      'tests/mobile/**',
      'tests/integration/**', // Exclude integration tests that need DB
      'tests/**/*.spec.ts', // Exclude Playwright test files
      'node_modules/',
      'dist/'
    ],
    testTimeout: 15000,
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
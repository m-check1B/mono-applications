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
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'json-summary'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        '*.config.ts',
        'tests/',
        'src/main.tsx',
        'src/vite-env.d.ts',
        'server/index.ts',
        'server/trpc/index.ts',
        'prisma/',
        'scripts/',
        'public/',
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/mocks/',
        '**/fixtures/',
      ],
      include: [
        'src/**/*.{ts,tsx}',
        'server/**/*.{ts,tsx}',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
        // Service layer should have high coverage
        'server/services/': {
          branches: 85,
          functions: 90,
          lines: 85,
          statements: 85,
        },
        // tRPC routers should have high coverage
        'server/trpc/routers/': {
          branches: 80,
          functions: 85,
          lines: 80,
          statements: 80,
        },
        // Core components should have good coverage
        'src/components/': {
          branches: 75,
          functions: 80,
          lines: 75,
          statements: 75,
        },
        // Services should have high coverage
        'src/services/': {
          branches: 85,
          functions: 90,
          lines: 85,
          statements: 85,
        },
      },
      // Watermarks for visual indicators
      watermarks: {
        statements: [50, 80],
        functions: [50, 80],
        branches: [50, 80],
        lines: [50, 80],
      },
    },
    include: [
      'tests/unit/**/*.{test,spec}.{ts,tsx}',
      'tests/integration/**/*.{test,spec}.{ts,tsx}',
      'tests/security/**/*.{test,spec}.{ts,tsx}',
      'tests/performance/**/*.{test,spec}.{ts,tsx}',
    ],
    exclude: [
      'tests/e2e/**',
      'tests/browser-automation/**',
      'tests/visual/**',
      'tests/voice/**',
      'tests/accessibility/**',
      'tests/mobile/**',
      'tests/telephony/**',
      'tests/qa/**',
      'tests/fixtures/**',
      'tests/mocks/**',
    ],
    testTimeout: 30000,
    maxConcurrency: 4,
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        maxThreads: 4,
        minThreads: 2,
      },
    },
    // Coverage-specific reporting
    reporters: [
      'default',
      'json',
      'html',
      ['junit', { outputFile: './coverage/junit.xml' }],
    ],
    outputFile: {
      json: './coverage/results.json',
      html: './coverage/index.html',
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
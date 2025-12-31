import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'text-summary'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'build/',
        '*.config.ts',
        '*.config.js',
        'tests/',
        'test-*',
        'src/main.tsx',
        'src/vite-env.d.ts',
        '**/types/**',
        '**/*.d.ts',
        '**/coverage/**',
        '**/playwright-report/**',
        'public/**',
        'scripts/**',
        'docs/**',
        'examples/**',
        'archive/**',
        'tmp/**',
        '**/*{.,-}{test,spec}.{ts,tsx,js,jsx}',
        '**/test-{setup,helpers,fixtures}/**'
      ],
      include: [
        'src/**/*.{ts,tsx,js,jsx}',
        'server/**/*.{ts,tsx,js,jsx}'
      ],
      thresholds: {
        branches: 75,
        functions: 75,
        lines: 75,
        statements: 75,
        // Per-file thresholds for critical components
        'src/components/**/*.{ts,tsx}': {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        },
        'server/core/**/*.{ts,js}': {
          branches: 85,
          functions: 85,
          lines: 85,
          statements: 85
        },
        'server/trpc/**/*.{ts,js}': {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      },
      watermarks: {
        statements: [50, 80],
        functions: [50, 80],
        branches: [50, 80],
        lines: [50, 80]
      }
    },
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
    exclude: [
      'tests/e2e/**',
      'tests/browser-automation/**',
      'tests/visual/**',
      'tests/voice/**',
      'tests/performance/**',
      'tests/accessibility/**',
      'tests/mobile/**',
      'tests/telephony/**',
      'tests/qa/**'
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
      '@': path.resolve(__dirname, './src'),
      '@server': path.resolve(__dirname, './server'),
      '@unified': path.resolve(__dirname, './vendor/packages'),
      '@stack-2025': path.resolve(__dirname, './vendor/packages')
    }
  }
});

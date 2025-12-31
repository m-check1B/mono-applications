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
        branches: 30,
        functions: 30,
        lines: 30,
        statements: 30
      },
      watermarks: {
        statements: [30, 60],
        functions: [30, 60],
        branches: [30, 60],
        lines: [30, 60]
      }
    },
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: [
      'tests/e2e/**',
      'tests/browser-automation/**',
      'tests/visual/**',
      'tests/voice/**',
      'tests/performance/**',
      'tests/accessibility/**',
      'tests/mobile/**',
      'tests/telephony/**',
      'tests/qa/**',
      'tests/unit/**',
      'tests/integration/**'
    ],
    testTimeout: 10000,
    maxConcurrency: 2
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../src'),
      '@server': path.resolve(__dirname, '../server')
    }
  }
});
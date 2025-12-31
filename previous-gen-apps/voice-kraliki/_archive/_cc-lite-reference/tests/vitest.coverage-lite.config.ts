import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, '..'),
  test: {
    globals: true,
    environment: 'node',
    setupFiles: [],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'text-summary'],
      reportsDirectory: './coverage',
      include: [
        'server/**/*.{ts,tsx,js,jsx}',
      ],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        'tests/**',
        'scripts/**',
      ],
      thresholds: {
        branches: 0,
        functions: 0,
        lines: 0,
        statements: 0,
      },
    },
    include: [
      'tests/unit/utils/**/*.test.ts',
    ],
    testTimeout: 10000,
    maxConcurrency: 2,
  },
});


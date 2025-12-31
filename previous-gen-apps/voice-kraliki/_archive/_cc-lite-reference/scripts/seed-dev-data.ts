#!/usr/bin/env tsx
import { execSync } from 'node:child_process';

try {
  execSync('pnpm tsx scripts/seed-database.ts', { stdio: 'inherit' });
} catch (e) {
  console.error('Dev seed failed:', (e as any).message);
  process.exit(1);
}


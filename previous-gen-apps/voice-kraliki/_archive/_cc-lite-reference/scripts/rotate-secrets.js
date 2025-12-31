#!/usr/bin/env node
// Minimal bridge to generate secrets using tsx gen-keys script.
import { execSync } from 'node:child_process';

const args = process.argv.slice(2);
const outputEnv = args.includes('--output-env');

try {
  if (outputEnv) {
    console.log('# Run: pnpm tsx scripts/gen-keys.ts');
    console.log('# Then copy secrets into your .env.production or Docker secrets.');
  }
  execSync('pnpm tsx scripts/gen-keys.ts', { stdio: 'inherit' });
} catch (e) {
  console.error('Secret rotation helper failed:', e.message);
  process.exit(1);
}


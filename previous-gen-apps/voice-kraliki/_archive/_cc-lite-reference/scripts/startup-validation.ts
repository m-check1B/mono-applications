#!/usr/bin/env tsx
import { existsSync } from 'node:fs';
import { join } from 'node:path';

const args = new Set(process.argv.slice(2));
const skipExternal = args.has('--skip-external');

let ok = true;

// Basic file checks
if (!existsSync(join(process.cwd(), 'server/index.ts'))) {
  console.error('❌ Missing server entry: server/index.ts');
  ok = false;
}
if (!existsSync(join(process.cwd(), 'vite.config.ts'))) {
  console.error('❌ Missing frontend config: vite.config.ts');
  ok = false;
}

// Basic env checks
const required = ['PORT'];
for (const k of required) {
  if (!process.env[k]) {
    console.warn(`⚠️ ${k} not set, using default`);
  }
}

// External checks could be added here (db connectivity, etc.)
if (!skipExternal) {
  // Intentionally minimal to avoid network access in CI/sandbox
}

if (!ok) {
  process.exit(1);
}
console.log('✅ Startup validation passed');


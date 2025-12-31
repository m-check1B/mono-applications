#!/usr/bin/env tsx
import { execSync } from 'node:child_process';
import fs from 'node:fs';

function ensureSeedFile() {
  if (!fs.existsSync('prisma/seed.ts') && !fs.existsSync('prisma/seed.js') && !fs.existsSync('prisma/seed.cjs')) {
    // prisma/seed.cjs should exist from repo; fallback is to create minimal CJS seed
    const seed = `/* auto-generated */\nmodule.exports = require('./seed.cjs');`;
    fs.writeFileSync('prisma/seed.js', seed);
  }
}

try {
  ensureSeedFile();
  execSync('pnpm prisma db seed', { stdio: 'inherit' });
} catch (e) {
  console.error('Seeding failed:', (e as any).message);
  process.exit(1);
}


#!/usr/bin/env tsx
import fs from 'node:fs';
import path from 'node:path';
import dotenv from 'dotenv';

const args = new Set(process.argv.slice(2));
const strict = args.has('--strict');
const envName = (() => {
  for (const a of args) if (a.startsWith('--env=')) return a.split('=')[1];
  return 'development';
})();

const envFile = envName === 'production' ? '.env.production' : '.env';
const envPath = path.resolve(process.cwd(), envFile);

if (!fs.existsSync(envPath)) {
  console.error(`❌ Missing ${envFile}. Create it from .env.example`);
  process.exit(1);
}

dotenv.config({ path: envPath });

const required = ['DATABASE_URL'];
if (envName === 'production') required.push('JWT_SECRET', 'COOKIE_SECRET');

const missing = required.filter((k) => !process.env[k] || String(process.env[k]).trim() === '');
if (missing.length) {
  console.error(`❌ Missing required env vars in ${envFile}: ${missing.join(', ')}`);
  process.exit(1);
}

if (strict) {
  const recommended = ['PORT', 'HOST'];
  const missingRec = recommended.filter((k) => !process.env[k]);
  if (missingRec.length) {
    console.warn(`⚠️ Recommended env vars missing: ${missingRec.join(', ')}`);
  }
}

console.log(`✅ ${envFile} looks valid`);


#!/usr/bin/env tsx
import { glob } from 'glob';
import { readFileSync, writeFileSync } from 'node:fs';

async function main() {
  const files = await glob('dist/server/server/**/*.js');
  let changed = 0;
  for (const f of files) {
    let src = readFileSync(f, 'utf8');
    const updated = src.replace(/from\s+(["'])(\.\.?\/[\w\-\.\/]*)\1/g, (m, q, p) => {
      if (p.endsWith('.js') || p.endsWith('.mjs') || p.endsWith('.cjs')) return m;
      return `from ${q}${p}.js${q}`;
    });
    if (updated !== src) {
      writeFileSync(f, updated, 'utf8');
      changed++;
    }
  }
  console.log(`Patched ${changed} files with .js extensions in dist`);
}

main().catch((e) => { console.error(e); process.exit(1); });

#!/usr/bin/env tsx
import { glob } from 'glob';
import { readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { dirname, resolve as resolvePath } from 'node:path';

function needsExt(spec: string) {
  return !(/[.](js|mjs|cjs|ts|tsx|json)$/.test(spec));
}

function appendExt(spec: string, fileDir: string): string {
  // If spec points to a directory, append /index.js else .js
  try {
    const abs = resolvePath(fileDir, spec);
    if (existsSync(abs) && statSync(abs).isDirectory()) {
      return `${spec}${spec.endsWith('/') ? '' : '/'}index.js`;
    }
  } catch {}
  return `${spec}.js`;
}

function transform(content: string, filePath: string): string {
  const dir = dirname(filePath);
  // import ... from './x'
  content = content.replace(/(import\s+[^;]*?from\s+)(["'])(\.\.?\/[\w\-\.\/]*)\2/g, (m, pre, q, spec) => {
    if (!needsExt(spec)) return m;
    return `${pre}${q}${appendExt(spec, dir)}${q}`;
  });
  // export ... from './x'
  content = content.replace(/(export\s+[^;]*?from\s+)(["'])(\.\.?\/[\w\-\.\/]*)\2/g, (m, pre, q, spec) => {
    if (!needsExt(spec)) return m;
    return `${pre}${q}${appendExt(spec, dir)}${q}`;
  });
  // bare import './x'
  content = content.replace(/(^|\n)\s*import\s+(["'])(\.\.?\/[\w\-\.\/]*)\2\s*;?/g, (m, start, q, spec) => {
    if (!needsExt(spec)) return m;
    return `${start}import ${q}${appendExt(spec, dir)}${q};`;
  });
  // dynamic import('...')
  content = content.replace(/import\(\s*(["'])(\.\.?\/[\w\-\.\/]*)\1\s*\)/g, (m, q, spec) => {
    if (!needsExt(spec)) return m;
    return `import(${q}${appendExt(spec, dir)}${q})`;
  });
  return content;
}

async function main() {
  const files = await glob('server/**/*.ts', { ignore: ['server/**/*.d.ts'] });
  let changed = 0;
  for (const f of files) {
    const src = readFileSync(f, 'utf8');
    const out = transform(src, f);
    if (out !== src) {
      writeFileSync(f, out, 'utf8');
      changed++;
    }
  }
  console.log(`codemod: appended .js to ${changed} server import specifiers`);
}

main().catch((e) => { console.error(e); process.exit(1); });

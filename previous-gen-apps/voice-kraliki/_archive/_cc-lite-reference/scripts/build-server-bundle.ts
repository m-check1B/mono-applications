#!/usr/bin/env tsx
import { build } from 'esbuild';
import { rmSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

async function main() {
  const outFile = resolve('dist/server/server-bundle.mjs');
  try { rmSync(outFile); } catch {}
  mkdirSync(resolve('dist/server'), { recursive: true });

  await build({
    entryPoints: ['server/index.ts'],
    outfile: outFile,
    platform: 'node',
    format: 'esm',
    target: ['node20'],
    bundle: true,
    sourcemap: true,
    external: [
      // Avoid bundling native or heavy optional deps
      '@sentry/*',
      '@sentry-internal/*',
      'telnyx',
      'twilio',
      'pg-native',
      'canvas',
      'sharp'
    ],
    banner: {
      js: `import { createRequire as __createRequire } from 'module'; const require = __createRequire(import.meta.url);`
    },
  });
  console.log('✅ Server bundle created at', outFile);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

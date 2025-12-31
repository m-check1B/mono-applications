#!/usr/bin/env tsx
import { existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { join } from 'node:path';

function tryCountFiles(pattern: string) {
  try {
    const out = execSync(`bash -lc "rg --files -g '${pattern}' | wc -l"`, { stdio: 'pipe', encoding: 'utf8' });
    return parseInt(out.trim(), 10) || 0;
  } catch {
    return 0;
  }
}

function main() {
  const cwd = process.cwd();
  const flags = new Set(process.argv.slice(2));
  const status = {
    ok: true,
    cwd,
    node: process.version,
    hasServer: existsSync(join(cwd, 'server/index.ts')),
    hasFrontend: existsSync(join(cwd, 'src/main.tsx')) || existsSync(join(cwd, 'index.html')),
    hasPrisma: existsSync(join(cwd, 'prisma/schema.prisma')),
    hasDockerProd: existsSync(join(cwd, 'docker-compose.production.yml')),
    hasDevCompose: existsSync(join(cwd, 'docker-compose.dev.yml')),
    tests: {
      unit: tryCountFiles('tests/unit/**/*.{test,spec}.{ts,tsx,js,jsx}'),
      integration: tryCountFiles('tests/integration/**/*.{test,spec}.{ts,tsx,js,jsx}'),
      e2e: tryCountFiles('tests/e2e/**/*.{test,spec}.{ts,tsx,js,jsx}'),
      total: tryCountFiles('tests/**/*.{test,spec}.{ts,tsx,js,jsx}')
    }
  };

  if (flags.has('--json')) {
    console.log(JSON.stringify(status, null, 2));
  } else {
    console.log('📦 Voice by Kraliki Project Status');
    console.log('===========================');
    console.log('Node:', status.node);
    console.log('Server:', status.hasServer ? 'OK' : 'MISSING server/index.ts');
    console.log('Frontend:', status.hasFrontend ? 'OK' : 'MISSING src');
    console.log('Prisma:', status.hasPrisma ? 'OK' : 'MISSING prisma/schema.prisma');
    console.log('Docker (prod):', status.hasDockerProd ? 'OK' : 'MISSING docker-compose.production.yml');
    console.log('Docker (dev):', status.hasDevCompose ? 'OK' : 'MISSING docker-compose.dev.yml');
    console.log('Tests:', status.tests.total, '(unit:', status.tests.unit, 'integration:', status.tests.integration, 'e2e:', status.tests.e2e + ')');
  }
}

main();


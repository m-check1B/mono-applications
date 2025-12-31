import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rootDir = path.resolve(__dirname, '..');
const frontendDir = path.join(rootDir, 'frontend');
const backendDir = path.join(rootDir, 'backend');
const vendorDir = path.join(rootDir, 'vendor');

export const focusKralikiManifest = {
  id: 'focus-kraliki',
  displayName: 'Focus by Kraliki',
  version: '2.1.0',
  description: 'AI-first productivity planning module with Gemini 2.5 live voice.',
  stack: {
    frontend: {
      framework: 'sveltekit',
      devCommand: 'cd frontend && pnpm dev',
      buildCommand: 'cd frontend && pnpm build',
      outputDir: path.join(frontendDir, '.svelte-kit'),
    },
    backend: {
      framework: 'fastapi',
      module: 'ocelot_apps.focus_lite',
      factory: 'PlanningModule',
      asgiApp: 'app.main:app',
      port: 3017,
      startCommand: './scripts/start.sh',
    },
  },
  scripts: {
    setup: './scripts/setup.sh',
    start: './scripts/start.sh',
    build: './scripts/build.sh',
    test: './scripts/test.sh',
  },
  paths: {
    root: rootDir,
    frontend: frontendDir,
    backend: backendDir,
    module: __dirname,
    vendor: vendorDir,
  },
};

export function resolveFrontendEntrypoint(relativePath = 'src/routes/+page.svelte') {
  return path.join(frontendDir, relativePath);
}

export function ensureBackendReady() {
  const required = ['app', 'ocelot_apps'];
  for (const name of required) {
    const target = path.join(backendDir, name);
    if (!fs.existsSync(target)) {
      throw new Error(`Missing backend package directory: ${target}`);
    }
  }
  return true;
}

export default focusKralikiManifest;

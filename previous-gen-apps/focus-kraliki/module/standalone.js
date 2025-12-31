import { spawn } from 'node:child_process';
import { focusKralikiManifest } from './index.js';

export function startStandalone(options = {}) {
  const env = { ...process.env, ...options.env };
  const child = spawn('./scripts/start.sh', {
    cwd: focusKralikiManifest.paths.root,
    env,
    stdio: 'inherit',
    shell: true,
  });

  return child;
}

export default { startStandalone };

// @ts-nocheck
import type { PageServerLoad } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface Agent {
  name: string;
  status: 'online' | 'idle' | 'error';
  task?: string;
}

interface Project {
  name: string;
  path: string;
}

export const load = async () => {
  // Projects to visualize
  const projects: Project[] = [
    { name: 'kraliki-swarm', path: '/github/applications/kraliki-lab/kraliki-swarm' },
    { name: 'focus', path: '/github/applications/focus-kraliki' },
    { name: 'speak', path: '/github/applications/speak-kraliki' },
    { name: 'voice', path: '/github/applications/voice-kraliki' },
    { name: 'learn', path: '/github/applications/learn-kraliki' },
    { name: 'lab', path: '/github/applications/lab-kraliki' }
  ];

  // Get agent status from PM2
  let agents: Agent[] = [];
  try {
    const { stdout } = await execAsync('pm2 jlist 2>/dev/null || echo "[]"');
    const pm2List = JSON.parse(stdout);

    // Filter for kraliki-related processes
    agents = pm2List
      .filter((p: any) => p.name && (
        p.name.includes('kraliki') ||
        p.name.includes('watchdog') ||
        p.name.includes('orchestrator')
      ))
      .map((p: any) => ({
        name: p.name,
        status: p.pm2_env?.status === 'online' ? 'online' :
                p.pm2_env?.status === 'stopped' ? 'idle' : 'error',
        task: undefined
      }));

    // If no PM2 processes, provide defaults for visualization
    if (agents.length === 0) {
      agents = [
        { name: 'watchdog-claude', status: 'idle' },
        { name: 'watchdog-opencode', status: 'idle' },
        { name: 'watchdog-gemini', status: 'idle' },
        { name: 'watchdog-codex', status: 'idle' },
        { name: 'kraliki-swarm-dashboard', status: 'online' }
      ];
    }
  } catch {
    // Fallback agents for visualization
    agents = [
      { name: 'watchdog-claude', status: 'idle' },
      { name: 'watchdog-opencode', status: 'idle' },
      { name: 'watchdog-gemini', status: 'idle' },
      { name: 'watchdog-codex', status: 'idle' },
      { name: 'kraliki-swarm-dashboard', status: 'online' }
    ];
  }

  return { projects, agents };
};
;null as any as PageServerLoad;
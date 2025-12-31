import { exec } from "child_process";
import { promisify } from "util";
const execAsync = promisify(exec);
const load = async () => {
  const projects = [
    { name: "kraliki-swarm", path: "/github/applications/kraliki-lab/kraliki-swarm" },
    { name: "focus", path: "/github/applications/focus-kraliki" },
    { name: "speak", path: "/github/applications/speak-kraliki" },
    { name: "voice", path: "/github/applications/voice-kraliki" },
    { name: "learn", path: "/github/applications/learn-kraliki" },
    { name: "lab", path: "/github/applications/lab-kraliki" }
  ];
  let agents = [];
  try {
    const { stdout } = await execAsync('pm2 jlist 2>/dev/null || echo "[]"');
    const pm2List = JSON.parse(stdout);
    agents = pm2List.filter((p) => p.name && (p.name.includes("kraliki") || p.name.includes("watchdog") || p.name.includes("orchestrator"))).map((p) => ({
      name: p.name,
      status: p.pm2_env?.status === "online" ? "online" : p.pm2_env?.status === "stopped" ? "idle" : "error",
      task: void 0
    }));
    if (agents.length === 0) {
      agents = [
        { name: "watchdog-claude", status: "idle" },
        { name: "watchdog-opencode", status: "idle" },
        { name: "watchdog-gemini", status: "idle" },
        { name: "watchdog-codex", status: "idle" },
        { name: "kraliki-swarm-dashboard", status: "online" }
      ];
    }
  } catch {
    agents = [
      { name: "watchdog-claude", status: "idle" },
      { name: "watchdog-opencode", status: "idle" },
      { name: "watchdog-gemini", status: "idle" },
      { name: "watchdog-codex", status: "idle" },
      { name: "kraliki-swarm-dashboard", status: "online" }
    ];
  }
  return { projects, agents };
};
export {
  load
};

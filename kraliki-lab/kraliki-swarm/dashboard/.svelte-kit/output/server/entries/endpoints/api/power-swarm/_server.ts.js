import { json } from "@sveltejs/kit";
import { exec } from "child_process";
import { promisify } from "util";
const execAsync = promisify(exec);
const stopProcesses = [
  "kraliki-watchdog-claude",
  "kraliki-watchdog-opencode",
  "kraliki-watchdog-gemini",
  "kraliki-watchdog-codex",
  "kraliki-health",
  "kraliki-stats",
  "kraliki-n8n-api",
  "kraliki-comm",
  "kraliki-comm-zt",
  "kraliki-comm-ws",
  "kraliki-msg-poller",
  "kraliki-linear-sync",
  "kraliki-agent-board",
  "kraliki-recall",
  "kraliki-events-bridge",
  "kraliki-mcp"
];
const killPatterns = [
  "Kraliki agent",
  "claude.*--append-system-prompt",
  "codex.*--full-auto",
  "gemini.*-p",
  "opencode.*--agent"
];
async function stopSwarm() {
  for (const pattern of killPatterns) {
    try {
      await execAsync(`pkill -9 -f "${pattern}" 2>/dev/null || true`);
    } catch {
    }
  }
  for (const proc of stopProcesses) {
    try {
      await execAsync(`pm2 stop ${proc} 2>/dev/null || true`);
    } catch {
    }
  }
}
async function startSwarm() {
  for (const proc of stopProcesses) {
    try {
      await execAsync(`pm2 restart ${proc} 2>/dev/null || true`);
    } catch {
    }
  }
}
const POST = async ({ request }) => {
  try {
    const body = await request.json();
    const action = typeof body?.action === "string" ? body.action : "";
    if (action === "off") {
      await stopSwarm();
      return json({ success: true, message: "Swarm powered off (dashboard still online)" });
    }
    if (action === "on") {
      await startSwarm();
      return json({ success: true, message: "Swarm powered on" });
    }
    if (action === "restart") {
      await stopSwarm();
      await startSwarm();
      return json({ success: true, message: "Swarm restarted" });
    }
    return json({ success: false, message: 'Invalid action. Use "off", "on", or "restart".' }, { status: 400 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return json({ success: false, message: `Power action failed: ${message}` }, { status: 500 });
  }
};
export {
  POST
};

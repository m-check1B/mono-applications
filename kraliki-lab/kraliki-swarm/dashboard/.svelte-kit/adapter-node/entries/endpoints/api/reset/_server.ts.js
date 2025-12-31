import { json } from "@sveltejs/kit";
import { exec } from "child_process";
import { promisify } from "util";
const execAsync = promisify(exec);
const KRALIKI_BASE = process.env.KRALIKI_DIR || process.env.KRALIKI_DATA_PATH || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm";
const POST = async () => {
  const results = [];
  try {
    const killPatterns = [
      "Kraliki agent",
      "claude.*--append-system-prompt",
      "codex.*--full-auto",
      "gemini.*-p",
      "opencode.*--agent"
    ];
    for (const pattern of killPatterns) {
      try {
        await execAsync(`pkill -9 -f "${pattern}" 2>/dev/null || true`);
      } catch {
      }
    }
    results.push("Killed zombie agents");
    try {
      await execAsync(`rm -f ${KRALIKI_BASE}/control/orchestrators/*.json 2>/dev/null || true`);
      results.push("Cleared orchestrator state");
    } catch {
    }
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
      "kraliki-events-bridge"
    ];
    for (const proc of stopProcesses) {
      try {
        await execAsync(`pm2 stop ${proc} 2>/dev/null || true`);
      } catch {
      }
    }
    results.push("Stopped PM2 processes");
    for (const proc of stopProcesses) {
      try {
        await execAsync(`pm2 restart ${proc} 2>/dev/null || true`);
      } catch {
      }
    }
    results.push("Started PM2 processes");
    return json({
      success: true,
      message: "Kraliki swarm reset complete",
      details: results,
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return json({
      success: false,
      message: `Reset failed: ${message}`,
      details: results
    }, { status: 500 });
  }
};
export {
  POST
};

import { json } from "@sveltejs/kit";
import { readFile, writeFile } from "fs/promises";
import { existsSync } from "fs";
const POLICY_FILE = "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/config/cli_policy.json";
const DEFAULT_POLICY = {
  clis: {
    opencode: { enabled: true, reason: "Default", priority: 1 },
    gemini: { enabled: true, reason: "Default", priority: 2 },
    codex: { enabled: true, reason: "Default", priority: 3 },
    claude: { enabled: true, reason: "Default", priority: 4 }
  }
};
async function loadPolicy() {
  try {
    if (existsSync(POLICY_FILE)) {
      const content = await readFile(POLICY_FILE, "utf-8");
      return JSON.parse(content);
    }
  } catch (e) {
    console.error("Failed to load CLI policy:", e);
  }
  return DEFAULT_POLICY;
}
async function savePolicy(policy) {
  policy._updated = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
  await writeFile(POLICY_FILE, JSON.stringify(policy, null, 2));
}
const GET = async () => {
  const policy = await loadPolicy();
  const clis = ["opencode", "gemini", "codex", "claude"].map((name) => {
    const config = policy.clis[name] || { enabled: true };
    return {
      name,
      enabled: config.enabled ?? true,
      reason: config.reason || "Default",
      priority: config.priority || 99,
      disabled_until: config.disabled_until
    };
  });
  return json({
    clis,
    updated: policy._updated,
    notes: policy.notes
  });
};
const POST = async ({ request }) => {
  try {
    const { cli, enabled, reason } = await request.json();
    if (!cli || typeof enabled !== "boolean") {
      return json({ error: "Invalid request - need cli and enabled" }, { status: 400 });
    }
    const policy = await loadPolicy();
    if (!policy.clis[cli]) {
      policy.clis[cli] = { enabled, reason: reason || "Toggled via dashboard" };
    } else {
      policy.clis[cli].enabled = enabled;
      if (reason) {
        policy.clis[cli].reason = reason;
      }
      if (enabled && policy.clis[cli].disabled_until) {
        delete policy.clis[cli].disabled_until;
      }
    }
    await savePolicy(policy);
    const clis = ["opencode", "gemini", "codex", "claude"].map((name) => {
      const config = policy.clis[name] || { enabled: true };
      return {
        name,
        enabled: config.enabled ?? true,
        reason: config.reason || "Default",
        priority: config.priority || 99,
        disabled_until: config.disabled_until
      };
    });
    return json({
      success: true,
      clis,
      updated: policy._updated
    });
  } catch (e) {
    console.error("Failed to update CLI policy:", e);
    return json({ error: "Failed to update CLI policy" }, { status: 500 });
  }
};
export {
  GET,
  POST
};

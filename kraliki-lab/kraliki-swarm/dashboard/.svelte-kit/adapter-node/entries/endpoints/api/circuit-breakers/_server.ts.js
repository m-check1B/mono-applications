import { json } from "@sveltejs/kit";
import { writeFile, readFile } from "fs/promises";
import { existsSync } from "fs";
const KRALIKI_BASE = process.env.KRALIKI_DIR || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm";
const CIRCUIT_BREAKERS_FILE = `${KRALIKI_BASE}/control/circuit-breakers.json`;
async function readJsonFile(path, fallback) {
  try {
    if (!existsSync(path)) return fallback;
    const content = await readFile(path, "utf-8");
    return JSON.parse(content);
  } catch {
    return fallback;
  }
}
const GET = async () => {
  try {
    const data = await readJsonFile(CIRCUIT_BREAKERS_FILE, {});
    return json(data);
  } catch (e) {
    console.error("Failed to read circuit breakers:", e);
    return json({}, { status: 500 });
  }
};
const POST = async ({ request }) => {
  try {
    const { name, action } = await request.json();
    if (!name || !action) {
      return json({ error: "Missing name or action" }, { status: 400 });
    }
    if (action !== "reset" && action !== "close") {
      return json({ error: 'Invalid action. Use "reset" or "close"' }, { status: 400 });
    }
    const data = await readJsonFile(CIRCUIT_BREAKERS_FILE, {});
    if (!data[name]) {
      return json({ error: `Circuit breaker "${name}" not found` }, { status: 404 });
    }
    const now = (/* @__PURE__ */ new Date()).toISOString();
    if (action === "reset" || action === "close") {
      data[name] = {
        ...data[name],
        state: "closed",
        failure_count: 0,
        last_success_time: now,
        last_update: now,
        note: action === "reset" ? "Manually reset via dashboard" : data[name].note
      };
    }
    await writeFile(CIRCUIT_BREAKERS_FILE, JSON.stringify(data, null, 2));
    return json({ success: true, message: `Circuit breaker "${name}" has been ${action}` });
  } catch (e) {
    console.error("Failed to update circuit breaker:", e);
    return json({ error: "Failed to update circuit breaker" }, { status: 500 });
  }
};
export {
  GET,
  POST
};

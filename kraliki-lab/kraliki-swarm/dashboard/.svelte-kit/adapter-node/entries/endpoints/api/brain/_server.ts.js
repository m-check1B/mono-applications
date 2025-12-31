import { json } from "@sveltejs/kit";
import { readFile } from "fs/promises";
import { join } from "path";
import { g as getScopePath } from "../../../../chunks/scopes.js";
async function loadPlanFile(planningDir, filename) {
  try {
    const content = await readFile(join(planningDir, filename), "utf-8");
    return JSON.parse(content);
  } catch {
    return null;
  }
}
const GET = async () => {
  try {
    const brainPath = await getScopePath("brain");
    if (!brainPath) {
      return json({ error: "Brain scope not configured" }, { status: 500 });
    }
    const planningDir = join(brainPath, "ai-planning");
    const masterContent = await readFile(join(planningDir, "master.json"), "utf-8");
    const master = JSON.parse(masterContent);
    const streamDetails = {};
    for (const [streamName, streamConfig] of Object.entries(master.streams)) {
      streamDetails[streamName] = [];
      for (const planFile of streamConfig.plans) {
        const planPath = join(streamConfig.path, planFile);
        const plan = await loadPlanFile(planningDir, planPath);
        if (plan) {
          streamDetails[streamName].push({
            file: planFile,
            ...plan
          });
        }
      }
    }
    const [startStr, endStr] = master.period_dates.split(" to ");
    const me90Start = new Date(startStr);
    const me90End = new Date(endStr);
    const today = /* @__PURE__ */ new Date();
    const totalDays = Math.ceil((me90End.getTime() - me90Start.getTime()) / (1e3 * 60 * 60 * 24));
    const daysPassed = Math.ceil((today.getTime() - me90Start.getTime()) / (1e3 * 60 * 60 * 24));
    const daysRemaining = totalDays - daysPassed;
    const progress = Math.min(100, Math.max(0, daysPassed / totalDays * 100));
    return json({
      master,
      streamDetails,
      me90: {
        start: startStr,
        end: endStr,
        totalDays,
        daysPassed,
        daysRemaining,
        progress: progress.toFixed(1)
      },
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch (e) {
    console.error("Failed to load brain data:", e);
    return json({
      error: "Failed to load brain data",
      details: e instanceof Error ? e.message : "Unknown error"
    }, { status: 500 });
  }
};
export {
  GET
};

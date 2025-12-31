import { json } from "@sveltejs/kit";
import { readFile, writeFile } from "fs/promises";
import { join } from "path";
import { g as getScopePath } from "../../../../chunks/scopes.js";
function parseQueueStatus(content) {
  const blockers = [];
  const lines = content.split("\n");
  let currentPriority = "MEDIUM";
  let inTable = false;
  let inCompleted = false;
  for (const line of lines) {
    if (line.includes("Recently Completed") || line.includes("Archive")) {
      inCompleted = true;
      inTable = false;
      continue;
    }
    if (line.match(/^#{2,3}\s+CRITICAL/i)) {
      currentPriority = "CRITICAL";
      inTable = false;
      inCompleted = false;
    } else if (line.match(/^#{2,3}\s+HIGH/i)) {
      currentPriority = "HIGH";
      inTable = false;
      inCompleted = false;
    } else if (line.match(/^#{2,3}\s+MEDIUM/i)) {
      currentPriority = "MEDIUM";
      inTable = false;
      inCompleted = false;
    } else if (line.match(/^#{2,3}\s+LOW/i) || line.includes("Can Wait") || line.includes("Verification")) {
      currentPriority = "LOW";
      inTable = false;
      inCompleted = false;
    }
    if (line.startsWith("| ID") || line.startsWith("|----")) {
      inTable = true;
      continue;
    }
    if (!inCompleted && inTable && line.startsWith("|") && line.includes("HW-")) {
      const parts = line.split("|").map((p) => p.trim()).filter(Boolean);
      if (parts.length >= 2) {
        const id = parts[0].replace(/\*\*/g, "").trim();
        const task = parts[1].trim();
        let priority = currentPriority;
        if (parts[2] && ["CRITICAL", "HIGH", "MEDIUM", "LOW"].includes(parts[2].toUpperCase())) {
          priority = parts[2].toUpperCase();
        }
        const time = parts[3] || parts[2] || "";
        const notes = parts[4] || parts[3] || "";
        blockers.push({
          id,
          task,
          priority,
          time,
          notes
        });
      }
    }
  }
  return blockers;
}
const GET = async () => {
  try {
    const blockersPath = await getScopePath("blockers");
    if (!blockersPath) {
      return json({ error: "Blockers scope not configured", blockers: [], total: 0, critical: 0, high: 0 });
    }
    const queueFile = join(blockersPath, "QUEUE_STATUS.md");
    const content = await readFile(queueFile, "utf-8");
    const blockers = parseQueueStatus(content);
    const priorityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
    blockers.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    return json({
      blockers,
      total: blockers.length,
      critical: blockers.filter((b) => b.priority === "CRITICAL").length,
      high: blockers.filter((b) => b.priority === "HIGH").length,
      lastUpdated: (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch (e) {
    console.error("Failed to read human blockers:", e);
    return json({
      blockers: [],
      total: 0,
      critical: 0,
      high: 0,
      error: "Failed to read queue status"
    });
  }
};
const POST = async ({ request }) => {
  try {
    const { action, id } = await request.json();
    const blockersPath = await getScopePath("blockers");
    if (!blockersPath) {
      return json({ error: "Blockers scope not configured" }, { status: 500 });
    }
    const queueFile = join(blockersPath, "QUEUE_STATUS.md");
    if (action === "mark_done") {
      let content = await readFile(queueFile, "utf-8");
      const lines = content.split("\n");
      const newLines = lines.filter((line) => !line.includes(id));
      const resolvedSection = lines.findIndex((l) => l.includes("## RECENTLY RESOLVED"));
      if (resolvedSection !== -1) {
        let insertAt = resolvedSection + 4;
        newLines.splice(insertAt, 0, `| ${id} | Marked done via dashboard | Human | ${(/* @__PURE__ */ new Date()).toISOString().split("T")[0]} |`);
      }
      await writeFile(queueFile, newLines.join("\n"));
      return json({ success: true, message: `${id} marked as done` });
    }
    return json({ error: "Unknown action" }, { status: 400 });
  } catch (e) {
    console.error("Failed to update human blockers:", e);
    return json({ error: "Failed to update" }, { status: 500 });
  }
};
export {
  GET,
  POST
};

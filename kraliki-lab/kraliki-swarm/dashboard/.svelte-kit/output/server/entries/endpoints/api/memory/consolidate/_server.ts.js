import { json } from "@sveltejs/kit";
import { exec } from "child_process";
import { promisify } from "util";
import { readdir } from "fs/promises";
import { g as getScopePath } from "../../../../../chunks/scopes.js";
const execAsync = promisify(exec);
const EPHEMERAL_PATTERN = /^([A-Z]{2})-([a-z_]+)-\d{2}:\d{2}\.\d{2}\.\d{2}\.[A-Z]{2}$/;
async function getConsolidationPlan() {
  const kralikiPath = await getScopePath("kraliki");
  if (!kralikiPath) {
    return { ephemeral_files: 0, memories_to_move: 0, target_files: 0, consolidations: [] };
  }
  const memoriesPath = `${kralikiPath}/arena/data/memories`;
  let files;
  try {
    files = await readdir(memoriesPath);
  } catch {
    return { ephemeral_files: 0, memories_to_move: 0, target_files: 0, consolidations: [] };
  }
  const consolidations = {};
  let ephemeralFiles = 0;
  let memoriesToMove = 0;
  for (const file of files) {
    if (!file.endsWith(".jsonl")) continue;
    const agentName = file.replace(".jsonl", "");
    const match = EPHEMERAL_PATTERN.exec(agentName);
    if (!match) continue;
    ephemeralFiles++;
    const lab = match[1];
    const role = match[2];
    const targetName = `${lab}-${role}`;
    try {
      const filePath = `${memoriesPath}/${file}`;
      const { stdout } = await execAsync(`wc -l < "${filePath}"`, { timeout: 5e3 });
      const lineCount = parseInt(stdout.trim()) || 0;
      memoriesToMove += lineCount;
      if (!consolidations[targetName]) {
        consolidations[targetName] = { sources: 0, memories: 0 };
      }
      consolidations[targetName].sources++;
      consolidations[targetName].memories += lineCount;
    } catch {
    }
  }
  return {
    ephemeral_files: ephemeralFiles,
    memories_to_move: memoriesToMove,
    target_files: Object.keys(consolidations).length,
    consolidations: Object.entries(consolidations).map(([target, data]) => ({
      target: `${target}.jsonl`,
      sources: data.sources,
      memories: data.memories
    })).sort((a, b) => b.memories - a.memories)
  };
}
async function executeConsolidation() {
  const kralikiPath = await getScopePath("kraliki");
  if (!kralikiPath) {
    return { success: false, message: "Could not find Kraliki path" };
  }
  const memoryScript = `${kralikiPath}/arena/memory.py`;
  try {
    const { stdout, stderr } = await execAsync(
      `cd "${kralikiPath}" && python3 "${memoryScript}" consolidate --execute`,
      { timeout: 3e4 }
    );
    const mergedMatch = stdout.match(/Merged (\d+) memories/);
    const deletedMatch = stdout.match(/Deleted (\d+) ephemeral files/);
    const targetsMatch = stdout.match(/into (\d+) files/);
    const merged = mergedMatch ? parseInt(mergedMatch[1]) : 0;
    const deleted = deletedMatch ? parseInt(deletedMatch[1]) : 0;
    const targets = targetsMatch ? parseInt(targetsMatch[1]) : 0;
    if (merged > 0 || deleted > 0) {
      return {
        success: true,
        message: `Consolidated ${merged} memories into ${targets} files, deleted ${deleted} ephemeral files`,
        details: { merged, deleted, targets }
      };
    } else if (stdout.includes("No ephemeral memories to consolidate")) {
      return {
        success: true,
        message: "No ephemeral memories to consolidate",
        details: { merged: 0, deleted: 0, targets: 0 }
      };
    } else {
      return {
        success: false,
        message: stderr || "Unknown error during consolidation"
      };
    }
  } catch (e) {
    const error = e instanceof Error ? e.message : "Unknown error";
    return { success: false, message: `Consolidation failed: ${error}` };
  }
}
const GET = async () => {
  try {
    const plan = await getConsolidationPlan();
    return json({
      success: true,
      plan
    });
  } catch (e) {
    const error = e instanceof Error ? e.message : "Unknown error";
    return json({ success: false, error }, { status: 500 });
  }
};
const POST = async () => {
  try {
    const result = await executeConsolidation();
    return json(result);
  } catch (e) {
    const error = e instanceof Error ? e.message : "Unknown error";
    return json({ success: false, message: error }, { status: 500 });
  }
};
export {
  GET,
  POST
};

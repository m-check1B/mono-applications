import { json } from "@sveltejs/kit";
import { readdir, readFile } from "fs/promises";
import { g as getScopePath } from "../../../../chunks/scopes.js";
async function getKnownAgents() {
  try {
    const kralikiPath = await getScopePath("kraliki");
    if (!kralikiPath) return [];
    const genomesPath = `${kralikiPath}/genomes`;
    const files = await readdir(genomesPath);
    return files.filter((f) => f.endsWith(".md") && !f.endsWith(".disabled")).map((f) => f.replace(".md", "")).filter((f) => !f.includes("_prompt"));
  } catch {
    return [];
  }
}
async function getMemoriesFromFiles() {
  const entries = [];
  const byAgent = {};
  try {
    const kralikiPath = await getScopePath("kraliki");
    if (!kralikiPath) {
      return { entries: [], stats: { total_entries: 0, total_stores: 0, total_retrieves: 0, by_agent: {} } };
    }
    const memoriesPath = `${kralikiPath}/arena/data/memories`;
    let files;
    try {
      files = await readdir(memoriesPath);
    } catch {
      return { entries: [], stats: { total_entries: 0, total_stores: 0, total_retrieves: 0, by_agent: {} } };
    }
    for (const file of files) {
      if (!file.endsWith(".jsonl")) continue;
      const agent = file.replace(".jsonl", "");
      const filePath = `${memoriesPath}/${file}`;
      try {
        const content = await readFile(filePath, "utf-8");
        const lines = content.trim().split("\n").filter((l) => l.trim());
        if (!byAgent[agent]) {
          byAgent[agent] = { stores: 0, retrieves: 0 };
        }
        for (const line of lines) {
          try {
            const mem = JSON.parse(line);
            byAgent[agent].stores++;
            entries.push({
              id: `${agent}-${mem.metadata?.time || Date.now()}`,
              agent: mem.metadata?.agent || agent,
              action: "store",
              key: mem.metadata?.tags?.join(", ") || mem.text?.slice(0, 50) || "memory",
              timestamp: mem.metadata?.time || (/* @__PURE__ */ new Date()).toISOString(),
              size: line.length,
              text: mem.text
            });
          } catch {
          }
        }
      } catch {
      }
    }
    entries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    const totalStores = Object.values(byAgent).reduce((sum, a) => sum + a.stores, 0);
    return {
      entries: entries.slice(0, 50),
      // Return last 50 entries
      stats: {
        total_entries: totalStores,
        total_stores: totalStores,
        total_retrieves: 0,
        by_agent: byAgent
      }
    };
  } catch (e) {
    console.error("Error reading memories:", e);
    return { entries: [], stats: { total_entries: 0, total_stores: 0, total_retrieves: 0, by_agent: {} } };
  }
}
const GET = async () => {
  try {
    const knownAgents = await getKnownAgents();
    const { entries, stats } = await getMemoriesFromFiles();
    const activeAgents = new Set(Object.keys(stats.by_agent));
    const inactiveAgents = knownAgents.filter((agent) => !activeAgents.has(agent));
    return json({
      stats,
      entries,
      knownAgents,
      activeAgents: Array.from(activeAgents),
      inactiveAgents,
      inactiveCount: inactiveAgents.length
    });
  } catch (e) {
    const knownAgents = await getKnownAgents();
    return json({
      stats: null,
      entries: [],
      knownAgents,
      activeAgents: [],
      inactiveAgents: knownAgents,
      inactiveCount: knownAgents.length,
      error: "Memory service error"
    }, { status: 503 });
  }
};
export {
  GET
};

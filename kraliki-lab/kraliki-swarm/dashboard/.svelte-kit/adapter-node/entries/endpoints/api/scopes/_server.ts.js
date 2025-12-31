import { json } from "@sveltejs/kit";
import { readFile, writeFile, stat } from "fs/promises";
import { join } from "path";
import { l as loadScopes, c as clearScopesCache } from "../../../../chunks/scopes.js";
const WORKSPACE_DIR = process.env.KRALIKI_WORKSPACE || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/workspace";
const SCOPES_FILE = join(WORKSPACE_DIR, "scopes.json");
async function checkPathExists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}
const GET = async () => {
  try {
    const scopes = await loadScopes();
    const scopeStatuses = [];
    for (const [name, config] of Object.entries(scopes.scopes)) {
      const exists = await checkPathExists(config.path);
      const status = {
        name,
        path: config.path,
        description: config.description,
        exists,
        accessible: exists
      };
      if (config.subpaths) {
        status.subpaths = {};
        for (const [subName, subPath] of Object.entries(config.subpaths)) {
          const fullPath = join(config.path, subPath);
          status.subpaths[subName] = {
            path: fullPath,
            exists: await checkPathExists(fullPath)
          };
        }
      }
      scopeStatuses.push(status);
    }
    return json({
      config: scopes,
      statuses: scopeStatuses,
      workspaceDir: WORKSPACE_DIR,
      lastChecked: (/* @__PURE__ */ new Date()).toISOString()
    });
  } catch (e) {
    console.error("Failed to load scopes:", e);
    return json({
      error: "Failed to load scopes configuration",
      details: e instanceof Error ? e.message : "Unknown error"
    }, { status: 500 });
  }
};
const PUT = async ({ request }) => {
  try {
    const updates = await request.json();
    const currentContent = await readFile(SCOPES_FILE, "utf-8");
    const current = JSON.parse(currentContent);
    if (updates.scopes) {
      for (const [name, config] of Object.entries(updates.scopes)) {
        if (config === null) {
          delete current.scopes[name];
        } else {
          current.scopes[name] = config;
        }
      }
    }
    if (updates.name) current.name = updates.name;
    if (updates.description) current.description = updates.description;
    if (updates.version) current.version = updates.version;
    if (updates.storage) {
      if (updates.storage.type) current.storage.type = updates.storage.type;
      if (updates.storage.base) current.storage.base = updates.storage.base;
    }
    current.lastModified = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
    await writeFile(SCOPES_FILE, JSON.stringify(current, null, 2));
    clearScopesCache();
    return json({
      success: true,
      message: "Scopes configuration updated",
      config: current
    });
  } catch (e) {
    console.error("Failed to update scopes:", e);
    return json({
      error: "Failed to update scopes configuration",
      details: e instanceof Error ? e.message : "Unknown error"
    }, { status: 500 });
  }
};
export {
  GET,
  PUT
};

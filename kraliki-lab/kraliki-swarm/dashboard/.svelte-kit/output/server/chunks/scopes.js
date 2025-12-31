import { readFile } from "fs/promises";
import { join } from "path";
const WORKSPACE_DIR = process.env.KRALIKI_WORKSPACE || "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/workspace";
const SCOPES_FILE = join(WORKSPACE_DIR, "scopes.json");
let cachedScopes = null;
let cacheTime = 0;
const CACHE_TTL = 6e4;
async function loadScopes() {
  const now = Date.now();
  if (cachedScopes && now - cacheTime < CACHE_TTL) {
    return cachedScopes;
  }
  try {
    const content = await readFile(SCOPES_FILE, "utf-8");
    cachedScopes = JSON.parse(content);
    cacheTime = now;
    return cachedScopes;
  } catch (e) {
    console.error("Failed to load scopes config:", e);
    return getDefaultScopes();
  }
}
async function getScopePath(scopeName) {
  const scopes = await loadScopes();
  const scope = scopes.scopes[scopeName];
  return scope?.path || null;
}
function clearScopesCache() {
  cachedScopes = null;
  cacheTime = 0;
}
function getDefaultScopes() {
  return {
    version: "1.0",
    name: "Default",
    description: "Default scope configuration",
    scopes: {
      kraliki: {
        path: "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm",
        description: "Kraliki system"
      }
    },
    storage: {
      type: "local",
      base: "/home/adminmatej/github"
    }
  };
}
export {
  clearScopesCache as c,
  getScopePath as g,
  loadScopes as l
};

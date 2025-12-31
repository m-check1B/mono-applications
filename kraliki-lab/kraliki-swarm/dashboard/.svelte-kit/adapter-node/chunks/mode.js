import { d as derived, w as writable } from "./index.js";
function getInitialMode() {
  return "normal";
}
function createModeStore() {
  const { subscribe, set, update } = writable(getInitialMode());
  return {
    subscribe,
    set: (mode) => {
      set(mode);
    },
    update,
    // Utility to check URL override
    hasUrlOverride: () => {
      return false;
    }
  };
}
const workspaceMode = createModeStore();
derived(workspaceMode, ($mode) => $mode === "dev");
derived(workspaceMode, ($mode) => $mode === "dev");
derived(workspaceMode, ($mode) => $mode === "dev" || $mode === "normal");
derived(workspaceMode, ($mode) => $mode === "readonly");
derived(workspaceMode, ($mode) => $mode === "dev");
derived(workspaceMode, ($mode) => {
  switch ($mode) {
    case "dev":
      return {
        label: "DEV",
        description: "Full editing enabled",
        color: "warning"
      };
    case "readonly":
      return {
        label: "READ-ONLY",
        description: "Viewing only",
        color: "muted"
      };
    default:
      return {
        label: "NORMAL",
        description: "Standard access",
        color: "default"
      };
  }
});
export {
  workspaceMode as w
};

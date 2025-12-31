import { e as attr_class, f as stringify } from "../../../chunks/index2.js";
import { d as derived, w as writable, g as get } from "../../../chunks/index.js";
import "marked";
import "marked-highlight";
import "dompurify";
/* empty css                                                             */
import { e as escape_html } from "../../../chunks/escaping.js";
import { a as attr } from "../../../chunks/attributes.js";
const initialComposerState = {
  isRecording: false,
  isProcessing: false,
  provider: "gemini-native",
  mode: "ii-agent",
  model: "google/gemini-3-flash-preview",
  useOrchestrator: false
};
const initialIIAgentState = {
  isConnected: false,
  isInitialized: false,
  sessionUuid: null,
  agentToken: null,
  currentModel: null,
  isProcessing: false,
  error: null,
  eventLog: []
};
const initialState = {
  sessionId: null,
  messages: [],
  workflows: {},
  executionFeed: [],
  composerState: initialComposerState,
  iiAgentState: initialIIAgentState,
  currentAction: null,
  drawerState: {
    workflowDrawerOpen: false,
    executionDrawerOpen: false,
    selectedWorkflowId: null,
    selectedExecutionId: null
  }
};
function createAssistantStore() {
  const { subscribe, set, update } = writable(initialState);
  return {
    subscribe,
    // ========== Session Management ==========
    initSession: (sessionId) => {
      update((state) => ({
        ...state,
        sessionId: sessionId || crypto.randomUUID?.() || String(Date.now())
      }));
    },
    setCurrentAction: (action) => {
      update((state) => ({
        ...state,
        currentAction: action
      }));
    },
    clearSession: () => {
      set(initialState);
    },
    // ========== Message Management ==========
    addMessage: (message) => {
      const newMessage = {
        ...message,
        id: crypto.randomUUID?.() || String(Date.now()),
        timestamp: /* @__PURE__ */ new Date()
      };
      update((state) => ({
        ...state,
        messages: [...state.messages, newMessage]
      }));
      return newMessage;
    },
    updateMessage: (messageId, updates) => {
      update((state) => ({
        ...state,
        messages: state.messages.map(
          (msg) => msg.id === messageId ? { ...msg, ...updates } : msg
        )
      }));
    },
    deleteMessage: (messageId) => {
      update((state) => ({
        ...state,
        messages: state.messages.filter((msg) => msg.id !== messageId)
      }));
    },
    clearMessages: () => {
      update((state) => ({
        ...state,
        messages: []
      }));
    },
    // ========== Workflow Management ==========
    addWorkflow: (workflow) => {
      const newWorkflow = {
        ...workflow,
        id: workflow.telemetryId || crypto.randomUUID?.() || String(Date.now()),
        timestamp: /* @__PURE__ */ new Date()
      };
      update((state) => ({
        ...state,
        workflows: {
          ...state.workflows,
          [newWorkflow.id]: newWorkflow
        }
      }));
      return newWorkflow;
    },
    updateWorkflow: (workflowId, updates) => {
      update((state) => ({
        ...state,
        workflows: {
          ...state.workflows,
          [workflowId]: {
            ...state.workflows[workflowId],
            ...updates
          }
        }
      }));
    },
    deleteWorkflow: (workflowId) => {
      update((state) => {
        const { [workflowId]: _, ...rest } = state.workflows;
        return {
          ...state,
          workflows: rest
        };
      });
    },
    updateWorkflowDecision: (workflowId, status) => {
      update((state) => ({
        ...state,
        workflows: {
          ...state.workflows,
          [workflowId]: {
            ...state.workflows[workflowId],
            decisionStatus: status,
            decisionAt: (/* @__PURE__ */ new Date()).toISOString()
          }
        }
      }));
    },
    // ========== Execution Feed Management ==========
    addExecutionEntry: (entry) => {
      const newEntry = {
        ...entry,
        id: crypto.randomUUID?.() || String(Date.now()),
        timestamp: /* @__PURE__ */ new Date()
      };
      update((state) => ({
        ...state,
        executionFeed: [newEntry, ...state.executionFeed]
      }));
      return newEntry;
    },
    updateExecutionEntry: (entryId, updates) => {
      update((state) => ({
        ...state,
        executionFeed: state.executionFeed.map(
          (entry) => entry.id === entryId ? { ...entry, ...updates } : entry
        )
      }));
    },
    deleteExecutionEntry: (entryId) => {
      update((state) => ({
        ...state,
        executionFeed: state.executionFeed.filter((entry) => entry.id !== entryId)
      }));
    },
    setExecutionFeed: (entries) => {
      update((state) => ({
        ...state,
        executionFeed: entries
      }));
    },
    clearExecutionFeed: () => {
      update((state) => ({
        ...state,
        executionFeed: []
      }));
    },
    // ========== Composer State Management ==========
    setComposerState: (updates) => {
      update((state) => ({
        ...state,
        composerState: {
          ...state.composerState,
          ...updates
        }
      }));
    },
    setRecording: (isRecording) => {
      update((state) => ({
        ...state,
        composerState: {
          ...state.composerState,
          isRecording
        }
      }));
    },
    setProcessing: (isProcessing2) => {
      update((state) => ({
        ...state,
        composerState: {
          ...state.composerState,
          isProcessing: isProcessing2
        }
      }));
    },
    setMode: (mode) => {
      update((state) => ({
        ...state,
        composerState: {
          ...state.composerState,
          mode
        }
      }));
    },
    // ========== II-Agent State Management ==========
    setIIAgentConnection: (isConnected, sessionUuid, agentToken) => {
      update((state) => ({
        ...state,
        iiAgentState: {
          ...state.iiAgentState,
          isConnected,
          sessionUuid: sessionUuid || state.iiAgentState.sessionUuid,
          agentToken: agentToken || state.iiAgentState.agentToken,
          error: isConnected ? null : state.iiAgentState.error
        }
      }));
    },
    setIIAgentInitialized: (isInitialized, model) => {
      update((state) => ({
        ...state,
        iiAgentState: {
          ...state.iiAgentState,
          isInitialized,
          currentModel: model || state.iiAgentState.currentModel
        }
      }));
    },
    setIIAgentProcessing: (isProcessing2) => {
      update((state) => ({
        ...state,
        iiAgentState: {
          ...state.iiAgentState,
          isProcessing: isProcessing2
        }
      }));
    },
    setIIAgentError: (error) => {
      update((state) => ({
        ...state,
        iiAgentState: {
          ...state.iiAgentState,
          error
        }
      }));
    },
    addIIAgentEvent: (event) => {
      const newEvent = {
        id: crypto.randomUUID?.() || String(Date.now()),
        type: event.type,
        content: event.content,
        timestamp: /* @__PURE__ */ new Date(),
        formattedContent: formatIIAgentEvent(event)
      };
      update((state) => ({
        ...state,
        iiAgentState: {
          ...state.iiAgentState,
          eventLog: [...state.iiAgentState.eventLog, newEvent]
        }
      }));
      return newEvent;
    },
    clearIIAgentEvents: () => {
      update((state) => ({
        ...state,
        iiAgentState: {
          ...state.iiAgentState,
          eventLog: []
        }
      }));
    },
    // ========== Drawer State Management ==========
    openWorkflowDrawer: (workflowId) => {
      update((state) => ({
        ...state,
        drawerState: {
          ...state.drawerState,
          workflowDrawerOpen: true,
          selectedWorkflowId: workflowId
        }
      }));
    },
    closeWorkflowDrawer: () => {
      update((state) => ({
        ...state,
        drawerState: {
          ...state.drawerState,
          workflowDrawerOpen: false,
          selectedWorkflowId: null
        }
      }));
    },
    openExecutionDrawer: (executionId) => {
      update((state) => ({
        ...state,
        drawerState: {
          ...state.drawerState,
          executionDrawerOpen: true,
          selectedExecutionId: executionId
        }
      }));
    },
    closeExecutionDrawer: () => {
      update((state) => ({
        ...state,
        drawerState: {
          ...state.drawerState,
          executionDrawerOpen: false,
          selectedExecutionId: null
        }
      }));
    },
    // ========== Utility Methods ==========
    getState: () => {
      return get({ subscribe });
    }
  };
}
function formatIIAgentEvent(event) {
  switch (event.type) {
    case "agent_response":
      return event.content.text || "";
    case "agent_thinking":
      return `Thinking: ${event.content.thinking || "..."}`;
    case "tool_call":
      return `Tool: ${event.content.tool_name || "unknown"}`;
    case "tool_result":
      return `Result: ${JSON.stringify(event.content.result || {}).substring(0, 100)}...`;
    case "error":
      return `Error: ${event.content.error || event.content.message || "Unknown error"}`;
    case "system":
      return event.content.message || event.content.text || "System event";
    default:
      return JSON.stringify(event.content);
  }
}
const assistantStore = createAssistantStore();
derived(
  assistantStore,
  ($state) => {
    if (!$state.drawerState.selectedWorkflowId) return null;
    return $state.workflows[$state.drawerState.selectedWorkflowId] || null;
  }
);
derived(
  assistantStore,
  ($state) => {
    if (!$state.drawerState.selectedExecutionId) return null;
    return $state.executionFeed.find((e) => e.id === $state.drawerState.selectedExecutionId) || null;
  }
);
derived(
  assistantStore,
  ($state) => {
    const workflows = Object.values($state.workflows);
    if (workflows.length === 0) return null;
    return workflows.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())[0];
  }
);
derived(
  assistantStore,
  ($state) => $state.messages.slice(-20)
);
derived(
  assistantStore,
  ($state) => $state.iiAgentState.isConnected && $state.iiAgentState.isInitialized
);
derived(
  assistantStore,
  ($state) => $state.composerState.isProcessing || $state.iiAgentState.isProcessing
);
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let focusStatus = "checking";
    let authStatus = "unknown";
    let focusUrl = "https://focus.verduona.dev";
    let projects = [];
    let tasks = [];
    let selectedProjectId = null;
    let activeTab = "overview";
    const projectStats = (() => {
      const stats = /* @__PURE__ */ new Map();
      for (const project of projects) {
        stats.set(project.id, {
          total: project.task_count || 0,
          completed: project.completed_count || 0
        });
      }
      {
        for (const [projectId] of stats) {
          stats.set(projectId, { total: 0, completed: 0 });
        }
        for (const task of tasks) {
          if (!task.project_id) continue;
          const current = stats.get(task.project_id) || { total: 0, completed: 0 };
          current.total += 1;
          if (task.status === "done") {
            current.completed += 1;
          }
          stats.set(task.project_id, current);
        }
      }
      return stats;
    })();
    const projectsWithStats = projects.map((project) => {
      const stats = projectStats.get(project.id);
      return {
        ...project,
        task_count: stats?.total ?? project.task_count ?? 0,
        completed_count: stats?.completed ?? project.completed_count ?? 0
      };
    });
    projectsWithStats.find((p) => p.id === selectedProjectId);
    projectsWithStats.length;
    const activeProjects = projectsWithStats.filter((p) => p.status === "active").length;
    tasks.length;
    tasks.filter((t) => t.status === "done").length;
    tasks.filter((t) => t.status === "in_progress").length;
    tasks.filter((t) => t.linear_id).length;
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      $$renderer3.push(`<div class="page svelte-x1i5gj"><div class="page-header svelte-x1i5gj"><h2 class="glitch">Focus by Kraliki // Strategy to Execution</h2> <div class="header-badges svelte-x1i5gj"><span class="status-badge svelte-x1i5gj">${escape_html(activeProjects)} PROJECTS</span> <span${attr_class(`focus-badge ${stringify(focusStatus)}`, "svelte-x1i5gj")}>`);
      {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`FOCUS: CHECKING...`);
      }
      $$renderer3.push(`<!--]--></span></div></div> <div${attr_class("integration-banner svelte-x1i5gj", void 0, {
        "online": focusStatus === "online",
        "demo": authStatus === "unauthenticated"
      })}><div class="banner-content svelte-x1i5gj"><span class="banner-icon svelte-x1i5gj">⏱</span> <div class="banner-text svelte-x1i5gj"><strong class="svelte-x1i5gj">Focus by Kraliki: AI Brain Organizer</strong> `);
      {
        $$renderer3.push("<!--[!-->");
        $$renderer3.push(`<span class="svelte-x1i5gj">Capture anything, turn it into projects, sync to swarm execution.</span>`);
      }
      $$renderer3.push(`<!--]--></div> <div class="banner-actions svelte-x1i5gj"><a${attr("href", focusUrl)} target="_blank" class="brutal-btn small svelte-x1i5gj">OPEN FOCUS</a> `);
      {
        $$renderer3.push("<!--[!-->");
      }
      $$renderer3.push(`<!--]--></div></div></div> <div class="focus-tabs svelte-x1i5gj"><button${attr_class("focus-tab svelte-x1i5gj", void 0, { "active": activeTab === "overview" })}>COMMAND</button> <button${attr_class("focus-tab svelte-x1i5gj", void 0, { "active": activeTab === "projects" })}>PROJECTS</button> <button${attr_class("focus-tab svelte-x1i5gj", void 0, { "active": activeTab === "tasks" })}>TASKS</button> <button${attr_class("focus-tab svelte-x1i5gj", void 0, { "active": activeTab === "sync" })}>LINEAR SYNC</button> <button${attr_class("focus-tab brain-tab svelte-x1i5gj", void 0, { "active": activeTab === "brain" })}>AI BRAIN</button></div> `);
      {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<div class="loading-state svelte-x1i5gj"><div class="loader svelte-x1i5gj"></div> <span>Loading Focus by Kraliki data...</span></div>`);
      }
      $$renderer3.push(`<!--]--></div>`);
    }
    do {
      $$settled = true;
      $$inner_renderer = $$renderer2.copy();
      $$render_inner($$inner_renderer);
    } while (!$$settled);
    $$renderer2.subsume($$inner_renderer);
  });
}
export {
  _page as default
};

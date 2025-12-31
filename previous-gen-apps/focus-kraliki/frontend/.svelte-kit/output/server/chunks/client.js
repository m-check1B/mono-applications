class ApiClient {
  baseURL;
  token = null;
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  setToken(token) {
    this.token = token;
  }
  getToken() {
    return this.token;
  }
  getHeaders() {
    const headers = {
      "Content-Type": "application/json"
    };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers
      }
    });
    if (!response.ok) {
      let errorDetail = "Request failed";
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorData.message || JSON.stringify(errorData);
      } catch {
        errorDetail = await response.text();
      }
      const error = {
        detail: errorDetail,
        status: response.status
      };
      throw error;
    }
    return response.json();
  }
  async get(endpoint) {
    return this.request(endpoint, { method: "GET" });
  }
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : void 0
    });
  }
  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: "PATCH",
      body: JSON.stringify(data)
    });
  }
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(data)
    });
  }
  async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }
  // Auth endpoints
  auth = {
    register: (data) => this.post("/auth/register", data),
    login: (data) => this.post("/auth/login", data),
    me: () => this.get("/auth/me"),
    logout: () => this.post("/auth/logout")
  };
  // Google OAuth endpoints (FastAPI mounts them at /auth/google/*)
  google = {
    getAuthUrl: (data) => this.post("/auth/google/url", data),
    login: (data) => this.post("/auth/google/login", data),
    link: (data) => this.post("/auth/google/link", data),
    unlink: () => this.post("/auth/google/unlink")
  };
  // User endpoints
  users = {
    getProfile: () => this.get("/users/profile"),
    updateProfile: (data) => this.patch("/users/profile", data),
    getPreferences: () => this.get("/users/preferences"),
    updatePreferences: (data) => this.post("/users/preferences", data)
  };
  // Task endpoints
  tasks = {
    list: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/tasks${query}`);
    },
    create: (data) => this.post("/tasks", data),
    get: (taskId) => this.get(`/tasks/${taskId}`),
    update: (taskId, data) => this.patch(`/tasks/${taskId}`, data),
    delete: (taskId) => this.delete(`/tasks/${taskId}`),
    toggle: (taskId) => this.post(`/tasks/${taskId}/toggle`),
    stats: () => this.get("/tasks/stats/summary"),
    search: (query) => this.get(`/tasks/search?q=${encodeURIComponent(query)}`)
  };
  // Project endpoints
  projects = {
    list: () => this.get("/projects"),
    create: (data) => this.post("/projects", data),
    get: (projectId) => this.get(`/projects/${projectId}`),
    update: (projectId, data) => this.patch(`/projects/${projectId}`, data),
    delete: (projectId) => this.delete(`/projects/${projectId}`),
    // Templates
    listTemplates: () => this.get("/projects/templates/list"),
    createFromTemplate: (templateId, customName) => {
      const query = customName ? `?custom_name=${encodeURIComponent(customName)}` : "";
      return this.post(`/projects/templates/${templateId}/create${query}`);
    },
    // Progress
    getProgress: (projectId) => this.get(`/projects/${projectId}/progress`)
  };
  // Events endpoints
  events = {
    list: (params) => {
      const query = new URLSearchParams({
        start_date: params.startDate,
        end_date: params.endDate
      }).toString();
      return this.get(`/events?${query}`);
    },
    create: (data) => this.post("/events", data),
    syncGoogle: () => this.post("/events/sync/google")
  };
  integration = {
    calendarStatus: () => this.get("/integration/calendar/status"),
    createCalendarEvent: (data) => this.post("/integration/calendar/events", data)
  };
  // Time entry endpoints
  timeEntries = {
    list: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/time-entries${query}`);
    },
    stats: () => this.get("/time-entries/stats/summary"),
    active: () => this.get("/time-entries/active"),
    create: (data) => this.post("/time-entries", data),
    stop: (entryId, data) => this.post(`/time-entries/${entryId}/stop`, data || {}),
    delete: (entryId) => this.delete(`/time-entries/${entryId}`)
  };
  // AI endpoints
  ai = {
    chat: (data) => this.post("/ai/chat", data),
    parseTask: (data) => this.post("/ai/parse-task", data),
    enhanceInput: (data) => this.post("/ai/enhance-input", data),
    analyzeTask: (data) => this.post("/ai/analyze-task", data),
    orchestrateTask: (data) => this.post("/ai/orchestrate-task", data),
    highReasoning: (data) => this.post("/ai/high-reasoning", data),
    generateInsights: () => this.post("/ai/insights"),
    getTaskRecommendations: () => this.post("/ai/task-recommendations"),
    saveNote: (data) => this.post("/ai/notes", data),
    getNotes: () => this.get("/ai/notes"),
    saveMemory: (data) => this.post("/ai/memory/save", data),
    recallMemory: (data) => this.post("/ai/memory/recall", data),
    analyzeCognitiveState: () => this.post("/ai/cognitive-state"),
    markTelemetryRoute: (telemetryId, data) => this.post(`/ai/telemetry/${telemetryId}/route`, data),
    recordWorkflowDecision: (telemetryId, data) => this.post(`/ai/telemetry/${telemetryId}/decision`, data),
    telemetrySummary: () => this.get("/ai/telemetry/summary")
  };
  // Shadow Work endpoints
  shadow = {
    analyze: (data) => this.post("/shadow/analyze", data),
    getInsights: () => this.get("/shadow/insights"),
    acknowledgeInsight: (insightId) => this.post(`/shadow/insights/${insightId}/acknowledge`),
    getUnlockStatus: () => this.get("/shadow/unlock-status")
  };
  // Voice/Assistant endpoints
  assistant = {
    // Voice transcription - upload audio file
    transcribeAudio: async (audioBlob, language = "en", provider) => {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("language", language);
      if (provider) formData.append("provider", provider);
      const response = await fetch(`${this.baseURL}/voice/transcribe`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.getToken()}`
        },
        body: formData
      });
      if (!response.ok) throw new Error(await response.text());
      return response.json();
    },
    // Voice processing - analyze transcript with AI
    processVoice: (data) => this.post("/voice/process", data),
    // Voice to task - convert voice input to task
    voiceToTask: (data) => this.post("/voice/to-task", data),
    // Get available voice providers
    getProviders: () => this.get("/voice/providers"),
    // Get voice recordings
    getRecordings: (limit, offset) => {
      const params = new URLSearchParams();
      if (limit) params.append("limit", String(limit));
      if (offset) params.append("offset", String(offset));
      return this.get(`/voice/recordings?${params.toString()}`);
    },
    // Legacy methods (kept for compatibility)
    textToSpeech: (data) => this.post("/assistant/tts", data),
    chat: (data) => this.post("/assistant/chat", data)
  };
  // Pricing endpoints
  pricing = {
    listModels: () => this.get("/pricing/models")
  };
  // Billing endpoints
  billing = {
    getPlans: () => this.get("/billing/plans"),
    createCheckoutSession: (data) => this.post("/billing/checkout-session", data),
    createSubscription: (data) => this.post("/billing/create-subscription", data),
    cancelSubscription: () => this.post("/billing/cancel-subscription"),
    reactivateSubscription: () => this.post("/billing/reactivate-subscription"),
    portalSession: () => this.get("/billing/portal-session"),
    subscriptionStatus: () => this.get("/billing/subscription-status")
  };
  // Workflow endpoints
  workflow = {
    createTemplate: (data) => this.post("/workflow/templates", data),
    listTemplates: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/workflow/templates${query}`);
    },
    getTemplate: (templateId) => this.get(`/workflow/templates/${templateId}`),
    updateTemplate: (templateId, data) => this.put(`/workflow/templates/${templateId}`, data),
    deleteTemplate: (templateId) => this.delete(`/workflow/templates/${templateId}`),
    execute: (data) => this.post("/workflow/execute", data),
    generate: (data) => this.post("/workflow/generate", data),
    getCategories: () => this.get("/workflow/categories")
  };
  // Exports endpoints
  exports = {
    generateInvoice: (data) => this.post("/exports/invoices/generate", data),
    getBillableSummary: (params) => {
      const query = new URLSearchParams(params).toString();
      return this.get(`/exports/billable/summary?${query}`);
    },
    getWeeklyBillable: (weeks = 4) => this.get(`/exports/billable/weekly?weeks=${weeks}`)
  };
  // Swarm tools endpoints
  swarm = {
    createTaskFromNL: (data) => this.post("/swarm-tools/tasks/create-from-nl", data),
    getTaskWithContext: (data) => this.post("/swarm-tools/tasks/get-with-context", data),
    createSubtasks: (data) => this.post("/swarm-tools/tasks/create-subtasks", data),
    getRecommendations: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/swarm-tools/tasks/recommendations${query}`);
    },
    updateCognitiveState: (data) => this.post("/swarm-tools/cognitive/update-state", data),
    getLatestCognitive: () => this.get("/swarm-tools/cognitive/latest"),
    getCognitiveTrends: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/swarm-tools/cognitive/trends${query}`);
    }
  };
  // Knowledge endpoints
  knowledge = {
    // Item Types
    listItemTypes: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/knowledge/item-types${query}`);
    },
    createItemType: (data) => this.post("/knowledge/item-types", data),
    getItemType: (typeId) => this.get(`/knowledge/item-types/${typeId}`),
    updateItemType: (typeId, data) => this.patch(`/knowledge/item-types/${typeId}`, data),
    deleteItemType: (typeId) => this.delete(`/knowledge/item-types/${typeId}`),
    // Knowledge Items
    listKnowledgeItems: (params) => {
      const query = params ? `?${new URLSearchParams(params).toString()}` : "";
      return this.get(`/knowledge/items${query}`);
    },
    createKnowledgeItem: (data) => this.post("/knowledge/items", data),
    getKnowledgeItem: (itemId) => this.get(`/knowledge/items/${itemId}`),
    updateKnowledgeItem: (itemId, data) => this.patch(`/knowledge/items/${itemId}`, data),
    deleteKnowledgeItem: (itemId) => this.delete(`/knowledge/items/${itemId}`),
    toggleKnowledgeItem: (itemId) => this.post(`/knowledge/items/${itemId}/toggle`),
    searchKnowledgeItems: (query, typeId) => {
      const params = new URLSearchParams({ query });
      if (typeId) params.append("typeId", typeId);
      return this.get(`/knowledge/search?${params.toString()}`);
    }
  };
  // Agent endpoints (II-Agent integration)
  agent = {
    createSession: (data) => this.post("/agent/sessions", data || {})
  };
  // Settings endpoints
  settings = {
    saveOpenRouterKey: (data) => this.post("/settings/openrouter-key", data),
    deleteOpenRouterKey: () => this.delete("/settings/openrouter-key"),
    testOpenRouterKey: (data) => this.post("/settings/test-openrouter-key", data),
    getUsageStats: () => this.get("/settings/usage-stats")
  };
  // Push Notifications endpoints
  notifications = {
    getVapidKey: () => this.get("/notifications/vapid-key"),
    subscribe: (data) => this.post("/notifications/subscribe", data),
    unsubscribe: () => this.delete("/notifications/subscribe"),
    getPreferences: () => this.get("/notifications/preferences"),
    updatePreferences: (data) => this.patch("/notifications/preferences", data),
    test: () => this.post("/notifications/test", {})
  };
  // Analytics endpoints
  analytics = {
    overview: (params) => {
      const query = params?.workspaceId ? `?workspaceId=${params.workspaceId}` : "";
      return this.get(`/analytics/overview${query}`);
    },
    bottlenecks: (params) => {
      const query = params?.workspaceId ? `?workspaceId=${params.workspaceId}` : "";
      return this.get(`/analytics/bottlenecks${query}`);
    }
  };
  // Workspace endpoints
  workspaces = {
    list: () => this.get("/workspaces"),
    create: (data) => this.post("/workspaces", data),
    get: (workspaceId) => this.get(`/workspaces/${workspaceId}`),
    switch: (workspaceId) => this.post("/workspaces/switch", { workspaceId }),
    members: (workspaceId) => this.get(`/workspaces/${workspaceId}/members`),
    inviteMember: (workspaceId, data) => this.post(`/workspaces/${workspaceId}/members`, data),
    updateMember: (workspaceId, memberId, data) => this.patch(`/workspaces/${workspaceId}/members/${memberId}`, data),
    removeMember: (workspaceId, memberId) => this.delete(`/workspaces/${workspaceId}/members/${memberId}`)
  };
  // Onboarding endpoints (Track 5)
  onboarding = {
    getStatus: () => this.get("/onboarding/status"),
    listPersonas: () => this.get("/onboarding/personas"),
    getPersona: (personaId) => this.get(`/onboarding/personas/${personaId}`),
    selectPersona: (data) => this.post("/onboarding/select-persona", data),
    updatePrivacyPreferences: (data) => this.post("/onboarding/privacy-preferences", data),
    updateFeatureToggles: (data) => this.post("/onboarding/feature-toggles", data),
    complete: (data) => this.post("/onboarding/complete", data),
    skip: () => this.post("/onboarding/skip", {})
  };
  // Brain endpoints - AI Brain Organizer
  brain = {
    // AI-First Capture: Say anything, Brain organizes it
    capture: (data) => this.post("/brain/capture", data),
    // Get summary of all captured items by type
    summary: () => this.get("/brain/summary"),
    // Parse natural language goal into project + tasks
    understandGoal: (data) => this.post("/brain/understand-goal", data),
    // Get daily plan: "Good morning! Here's your day..."
    dailyPlan: () => this.get("/brain/daily-plan"),
    // Ask the Brain anything about your work
    ask: (data) => this.post("/brain/ask", data),
    // What should you do RIGHT NOW?
    nextAction: () => this.get("/brain/next-action"),
    // Check Brain health
    health: () => this.get("/brain/health")
  };
}
const api = new ApiClient("/api");
export {
  api as a
};

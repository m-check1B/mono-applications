import { g as sanitize_props, j as spread_props, s as slot, e as ensure_array_like, d as attr_class, c as attr } from "./index2.js";
import { I as Icon } from "./Icon.js";
import { e as escape_html } from "./escaping.js";
import { w as writable, g as get } from "./index.js";
import { W as WS_URL } from "./env.js";
import { b as authStore } from "./auth2.js";
import { e as endSession, b as bootstrapSession } from "./sessions.js";
function Check($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "M20 6 9 17l-5-5" }]];
  Icon($$renderer, spread_props([
    { name: "check" },
    $$sanitized_props,
    {
      /**
       * @component @name Check
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjAgNiA5IDE3bC01LTUiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/check
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function Zap($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "zap" },
    $$sanitized_props,
    {
      /**
       * @component @name Zap
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNCAxNGExIDEgMCAwIDEtLjc4LTEuNjNsOS45LTEwLjJhLjUuNSAwIDAgMSAuODYuNDZsLTEuOTIgNi4wMkExIDEgMCAwIDAgMTMgMTBoN2ExIDEgMCAwIDEgLjc4IDEuNjNsLTkuOSAxMC4yYS41LjUgMCAwIDEtLjg2LS40NmwxLjkyLTYuMDJBMSAxIDAgMCAwIDExIDE0eiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/zap
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function ProviderSwitcher($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      providers = [],
      currentProvider = null,
      isLive = false,
      onSwitch
    } = $$props;
    let isSwitching = false;
    function getStatusColor(status) {
      switch (status) {
        case "active":
          return "border-primary bg-primary/10";
        case "available":
          return "border-divider bg-secondary/50 hover:border-primary/50 hover:bg-primary/5";
        case "unavailable":
          return "border-divider bg-secondary/20 opacity-50 cursor-not-allowed";
        default:
          return "border-divider bg-secondary/50";
      }
    }
    function getProviderIcon(providerId) {
      if (providerId.includes("gemini")) return "🤖";
      if (providerId.includes("openai")) return "🔷";
      if (providerId.includes("deepgram")) return "🎙️";
      return "⚡";
    }
    $$renderer2.push(`<article class="card"><div class="card-header"><div class="flex items-center gap-2">`);
    Zap($$renderer2, { class: "size-5 text-text-primary" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold text-text-primary">Voice Provider</h2></div> <span class="text-xs text-text-muted">`);
    if (isLive) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="inline-flex items-center gap-1.5 text-primary"><span class="size-1.5 animate-pulse rounded-full bg-primary"></span> Switch enabled</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`Not in call`);
    }
    $$renderer2.push(`<!--]--></span></div> <div class="space-y-2">`);
    if (providers.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-sm text-text-muted">No providers configured</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array = ensure_array_like(providers);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let provider = each_array[$$index];
        $$renderer2.push(`<button type="button"${attr_class(`w-full rounded-xl border-2 p-4 text-left transition-all ${getStatusColor(provider.status)}`)}${attr("disabled", provider.status === "unavailable" || isSwitching, true)}><div class="flex items-center justify-between"><div class="flex items-center gap-3"><span class="text-2xl" role="img"${attr("aria-label", provider.name)}>${escape_html(getProviderIcon(provider.id))}</span> <div><p class="text-sm font-semibold text-text-primary">${escape_html(provider.name)}</p> `);
        if (provider.capabilities) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="mt-1 flex gap-2 text-xs text-text-muted">`);
          if (provider.capabilities.realtime) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span>Realtime</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (provider.capabilities.multimodal) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span>• Multimodal</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (provider.capabilities.functionCalling) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span>• Functions</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div></div> <div>`);
        if (provider.status === "active") {
          $$renderer2.push("<!--[-->");
          Check($$renderer2, { class: "size-5 text-primary" });
        } else {
          $$renderer2.push("<!--[!-->");
          {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]--></div></div></button>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> `);
    if (isLive && !isSwitching) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="mt-3 text-xs text-text-muted">💡 You can switch providers during an active call for seamless comparison</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></article>`);
  });
}
class RealtimeClient {
  socket = null;
  reconnectAttempts = 0;
  options;
  messageHandlers = /* @__PURE__ */ new Set();
  openHandlers = /* @__PURE__ */ new Set();
  closeHandlers = /* @__PURE__ */ new Set();
  errorHandlers = /* @__PURE__ */ new Set();
  shouldReconnect;
  constructor(options = {}) {
    this.options = {
      path: options.path ?? "",
      query: options.query ?? {},
      protocols: options.protocols ?? [],
      reconnect: options.reconnect ?? true,
      reconnectDelayMs: options.reconnectDelayMs ?? 2e3,
      maxReconnectAttempts: options.maxReconnectAttempts ?? 10,
      token: options.token
    };
    this.shouldReconnect = this.options.reconnect;
  }
  connect() {
    return;
  }
  disconnect() {
    this.shouldReconnect = false;
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
  setToken(token) {
    this.options = { ...this.options, token };
  }
  setQuery(query) {
    this.options = { ...this.options, query: { ...query } };
  }
  updateQuery(query) {
    this.options = { ...this.options, query: { ...this.options.query, ...query } };
  }
  setPath(path) {
    this.options = { ...this.options, path };
  }
  send(data) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(data);
    } else {
      console.warn("WebSocket not connected. Message not sent.");
    }
  }
  onMessage(handler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }
  onOpen(handler) {
    this.openHandlers.add(handler);
    return () => this.openHandlers.delete(handler);
  }
  onClose(handler) {
    this.closeHandlers.add(handler);
    return () => this.closeHandlers.delete(handler);
  }
  onError(handler) {
    this.errorHandlers.add(handler);
    return () => this.errorHandlers.delete(handler);
  }
  scheduleReconnect() {
    if (!this.shouldReconnect || !this.options.reconnect) return;
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) return;
    this.reconnectAttempts += 1;
    setTimeout(() => this.connect(), this.options.reconnectDelayMs);
  }
  buildUrl() {
    const { path, query, token } = this.options;
    const normalizedPath = path?.startsWith("/") ? path : `/${path ?? ""}`;
    const base = `${WS_URL}${normalizedPath}`;
    const params = new URLSearchParams();
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value === null || value === void 0) continue;
        params.set(key, String(value));
      }
    }
    const resolvedToken = typeof token === "function" ? token() : token;
    if (resolvedToken) {
      params.set("token", resolvedToken);
    }
    const queryString = params.toString();
    return queryString.length > 0 ? `${base}?${queryString}` : base;
  }
}
function createProviderSession(config = {}) {
  const initialProvider = config.provider || "gemini";
  const initialState = {
    status: "idle",
    provider: initialProvider
  };
  const state = writable(initialState);
  let client = null;
  let currentProvider = initialProvider;
  let sessionId = void 0;
  let websocketPath = void 0;
  let bootstrapTask = null;
  let lastBootstrap = null;
  function getAccessToken() {
    const snapshot = authStore.getSnapshot();
    return snapshot.tokens?.accessToken;
  }
  async function ensureBootstrap(provider) {
    if (sessionId && websocketPath && currentProvider === provider && lastBootstrap) {
      return lastBootstrap;
    }
    if (!bootstrapTask) {
      bootstrapTask = bootstrapSession({
        provider_type: provider,
        provider
      });
    }
    let response;
    try {
      response = await bootstrapTask;
    } finally {
      bootstrapTask = null;
    }
    const parsedUrl = (() => {
      try {
        return new URL(response.websocket_url);
      } catch {
        return null;
      }
    })();
    sessionId = response.session_id;
    websocketPath = parsedUrl ? `${parsedUrl.pathname}${parsedUrl.search}` : `/ws/sessions/${sessionId}`;
    lastBootstrap = response;
    state.update((prev) => ({
      ...prev,
      provider,
      sessionId,
      metadata: response.metadata,
      websocketPath
    }));
    return response;
  }
  function ensureClient() {
    if (client) return client;
    if (!websocketPath) {
      throw new Error("Session not initialized");
    }
    client = new RealtimeClient({
      path: websocketPath,
      token: () => getAccessToken(),
      reconnect: config.reconnect ?? false
    });
    client.onOpen(() => {
      state.update((prev) => ({ ...prev, status: "connected", error: void 0 }));
    });
    client.onMessage((event) => {
      let payload = event.data;
      try {
        if (typeof event.data === "string") {
          payload = JSON.parse(event.data);
        }
      } catch (error) {
        console.warn("Failed to parse realtime payload", error);
      }
      state.update((prev) => ({
        ...prev,
        lastEvent: payload,
        lastEventAt: Date.now()
      }));
    });
    client.onError((event) => {
      const message = event instanceof ErrorEvent ? event.message : "WebSocket error";
      state.update((prev) => ({ ...prev, status: "error", error: message }));
    });
    client.onClose((event) => {
      state.update((prev) => ({
        ...prev,
        status: "disconnected",
        error: event.wasClean ? void 0 : `Connection closed (${event.code})`
      }));
    });
    return client;
  }
  async function switchProvider(newProvider) {
    if (newProvider === currentProvider) return;
    if (client) {
      client.disconnect();
      client = null;
    }
    sessionId = void 0;
    websocketPath = void 0;
    bootstrapTask = null;
    lastBootstrap = null;
    currentProvider = newProvider;
    state.update((prev) => ({ ...prev, provider: newProvider, status: "idle", sessionId: void 0 }));
    const currentState = get(state);
    if (currentState.status === "connected" || currentState.status === "connecting") {
      state.update((prev) => ({ ...prev, status: "connecting" }));
      void ensureBootstrap(newProvider).then(() => ensureClient().connect()).catch((error) => {
        console.error("Failed to bootstrap session on provider switch", error);
        state.update((prev) => ({ ...prev, status: "error", error: String(error) }));
      });
    }
  }
  return {
    subscribe: state.subscribe,
    connect() {
      return;
    },
    disconnect() {
      if (sessionId) {
        void endSession(sessionId).catch((error) => {
          console.error("Failed to end session", error);
        });
      }
      client?.disconnect();
      client = null;
      sessionId = void 0;
      websocketPath = void 0;
      bootstrapTask = null;
      lastBootstrap = null;
      state.update((prev) => ({ ...prev, status: "disconnected", sessionId: void 0 }));
    },
    send(data) {
      client?.send(data);
    },
    reset() {
      client?.disconnect();
      client = null;
      sessionId = void 0;
      websocketPath = void 0;
      bootstrapTask = null;
      lastBootstrap = null;
      state.set({ ...initialState, provider: currentProvider });
    },
    getState() {
      return get(state);
    },
    async switchProvider(newProvider) {
      await switchProvider(newProvider);
    }
  };
}
export {
  ProviderSwitcher as P,
  createProviderSession as c
};

import { w as writable, g as get } from "./index.js";
import { B as BACKEND_URL } from "./env.js";
const JSON_CONTENT_TYPES = ["application/json", "application/ld+json"];
function resolveUrl(path) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${BACKEND_URL}${normalizedPath}`;
}
function toHeaders(input) {
  if (!input) return new Headers();
  if (input instanceof Headers) return new Headers(input);
  return new Headers(input);
}
function getRetryDelay(attempt, baseDelay = 1e3) {
  const exponentialDelay = Math.min(baseDelay * Math.pow(2, attempt), 3e4);
  const jitter = Math.random() * 0.3 * exponentialDelay;
  return exponentialDelay + jitter;
}
function isRetryableError(status) {
  return status === 429 || status >= 500 && status < 600;
}
async function tryRefreshTokens() {
  try {
    return await authStore.refreshTokens();
  } catch (error) {
    console.error("Failed to refresh tokens", error);
    return false;
  }
}
async function apiFetch(input, init = {}) {
  const {
    retryOnAuthError = true,
    autoJson = true,
    maxRetries = 3,
    retryDelay = 1e3,
    headers,
    ...rest
  } = init;
  const url = resolveUrl(input);
  const headerBag = toHeaders(headers);
  const { tokens } = authStore.getSnapshot();
  if (rest.body && !headerBag.has("Content-Type")) {
    headerBag.set("Content-Type", "application/json");
  }
  if (tokens?.accessToken) {
    headerBag.set("Authorization", `Bearer ${tokens.accessToken}`);
  }
  let lastError = null;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        ...rest,
        headers: headerBag
      });
      if (response.status === 401 && retryOnAuthError) {
        const refreshed = await tryRefreshTokens();
        if (refreshed) {
          return apiFetch(input, { ...init, retryOnAuthError: false });
        }
      }
      if (!response.ok) {
        let payload;
        if (autoJson) {
          try {
            payload = await response.clone().json();
          } catch {
            payload = await response.text();
          }
        }
        const error = Object.assign(new Error(response.statusText), {
          status: response.status,
          payload
        });
        if (isRetryableError(response.status) && attempt < maxRetries) {
          lastError = error;
          const delay = getRetryDelay(attempt, retryDelay);
          console.warn(`Request failed with status ${response.status}, retrying in ${delay}ms...`);
          await new Promise((resolve) => setTimeout(resolve, delay));
          continue;
        }
        throw error;
      }
      if (!autoJson) {
        return response;
      }
      const contentType = response.headers.get("Content-Type") ?? "";
      const shouldParseJson = JSON_CONTENT_TYPES.some((type) => contentType.includes(type));
      return shouldParseJson ? response.json() : response.text();
    } catch (error) {
      if (attempt < maxRetries) {
        lastError = error;
        const delay = getRetryDelay(attempt, retryDelay);
        console.warn(`Network error, retrying in ${delay}ms...`, error);
        await new Promise((resolve) => setTimeout(resolve, delay));
        continue;
      }
      throw error;
    }
  }
  throw lastError || new Error("Request failed after all retries");
}
async function apiGet(path, options) {
  return apiFetch(path, { ...options, method: "GET" });
}
async function apiPost(path, body, options = {}) {
  const { body: overrideBody, ...rest } = options;
  return apiFetch(path, {
    ...rest,
    method: "POST",
    body: overrideBody ?? JSON.stringify(body)
  });
}
function login(credentials) {
  return apiPost("/api/v1/auth/login", credentials);
}
function register(payload) {
  return apiPost("/api/v1/auth/register", payload);
}
function logout() {
  return apiPost("/api/v1/auth/logout", {});
}
class CrossTabSyncService {
  channel = null;
  listeners = /* @__PURE__ */ new Map();
  tabId;
  isSupported;
  constructor() {
    this.tabId = this.generateTabId();
    this.isSupported = typeof BroadcastChannel !== "undefined";
    if (this.isSupported) {
      this.channel = new BroadcastChannel("voice-kraliki-sync");
      this.setupMessageHandler();
    }
  }
  generateTabId() {
    return `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  setupMessageHandler() {
    if (!this.channel) return;
    this.channel.onmessage = (event) => {
      const message = event.data;
      if (message.tabId === this.tabId) return;
      const listeners = this.listeners.get(message.type);
      if (listeners) {
        listeners.forEach((listener) => listener(message));
      }
    };
  }
  broadcast(type, payload) {
    if (!this.channel) {
      console.warn("BroadcastChannel not supported");
      return;
    }
    const message = {
      type,
      payload,
      timestamp: Date.now(),
      tabId: this.tabId
    };
    this.channel.postMessage(message);
  }
  subscribe(type, listener) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, /* @__PURE__ */ new Set());
    }
    this.listeners.get(type).add(listener);
    return () => {
      this.listeners.get(type)?.delete(listener);
    };
  }
  close() {
    if (this.channel) {
      this.channel.close();
      this.channel = null;
    }
    this.listeners.clear();
  }
  isAvailable() {
    return this.isSupported && this.channel !== null;
  }
}
const crossTabSync = new CrossTabSyncService();
if (typeof window !== "undefined") {
  window.addEventListener("beforeunload", () => {
    crossTabSync.close();
  });
}
const initialState = {
  status: "unauthenticated",
  user: null,
  tokens: null,
  error: null
};
function persistState(state) {
  return;
}
function restoreState() {
  return { tokens: null, user: null };
}
async function requestTokenRefresh(refreshToken) {
  try {
    const response = await fetch(`${BACKEND_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (!response.ok) {
      throw new Error(`Failed to refresh token: ${response.statusText}`);
    }
    const payload = await response.json();
    return payload;
  } catch (error) {
    console.error("Token refresh failed", error);
    throw error;
  }
}
function broadcastAuthUpdate(tokens, user) {
}
function createAuthStore() {
  const restored = restoreState();
  const store = writable({
    ...initialState,
    ...restored,
    status: restored.tokens ? "authenticated" : "unauthenticated"
  });
  return {
    subscribe: store.subscribe,
    getSnapshot: () => get(store),
    setAuthenticating() {
      store.update((prev) => ({ ...prev, status: "authenticating", error: null }));
    },
    setAuthenticated(data) {
      store.update(() => {
        const next = {
          status: "authenticated",
          tokens: data.tokens,
          user: data.user,
          error: null
        };
        return next;
      });
    },
    setError(error) {
      store.update((prev) => ({ ...prev, error, status: "unauthenticated" }));
    },
    clear() {
      store.set(initialState);
    },
    async login(credentials) {
      this.setAuthenticating();
      try {
        const response = await login(credentials);
        const tokens = {
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
          expiresAt: response.expires_at
        };
        const user = response.user ?? null;
        store.update(() => {
          const next = {
            status: "authenticated",
            tokens,
            user,
            error: null
          };
          persistState(next);
          return next;
        });
        broadcastAuthUpdate(tokens, user);
        return { success: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to sign in";
        store.set({ ...initialState, error: message });
        return { success: false, error: message };
      }
    },
    async register(payload) {
      this.setAuthenticating();
      try {
        const response = await register(payload);
        const tokens = {
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
          expiresAt: response.expires_at
        };
        const user = response.user ?? null;
        store.update(() => {
          const next = {
            status: "authenticated",
            tokens,
            user,
            error: null
          };
          persistState(next);
          return next;
        });
        broadcastAuthUpdate(tokens, user);
        return { success: true };
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to register";
        store.set({ ...initialState, error: message });
        return { success: false, error: message };
      }
    },
    async logout() {
      try {
        await logout();
      } catch (error) {
        console.warn("Logout request failed", error);
      } finally {
        this.clear();
      }
    },
    async refreshTokens() {
      const current = get(store);
      const refreshToken = current.tokens?.refreshToken;
      if (!refreshToken) return false;
      store.update((prev) => ({ ...prev, status: "refreshing" }));
      try {
        const response = await requestTokenRefresh(refreshToken);
        const nextTokens = {
          accessToken: response.access_token,
          refreshToken: response.refresh_token ?? refreshToken,
          expiresAt: response.expires_at
        };
        const user = response.user ?? current.user;
        store.update((prev) => {
          const next = {
            status: "authenticated",
            tokens: nextTokens,
            user,
            error: null
          };
          persistState(next);
          return next;
        });
        broadcastAuthUpdate(nextTokens, user);
        return true;
      } catch (error) {
        store.set({ ...initialState, error: "Session expired" });
        return false;
      }
    }
  };
}
const authStore = createAuthStore();
export {
  apiGet as a,
  authStore as b,
  crossTabSync as c,
  apiPost as d
};

import { s as store_get, h as head, e as ensure_array_like, a as attr_class, b as stringify, u as unsubscribe_stores } from "../../../../chunks/index2.js";
import { p as page } from "../../../../chunks/stores.js";
import { d as derived, w as writable } from "../../../../chunks/index.js";
import { X as ssr_context, V as escape_html } from "../../../../chunks/context.js";
import "clsx";
function onDestroy(fn) {
  /** @type {SSRContext} */
  ssr_context.r.on_destroy(fn);
}
const API_BASE = "/api";
class ApiError extends Error {
  constructor(status, message, data) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = "ApiError";
  }
}
async function request(endpoint, options = {}) {
  const { method = "GET", body, token } = options;
  const headers = {
    "Content-Type": "application/json"
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : void 0,
    credentials: "include"
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(response.status, data.detail || "Request failed", data);
  }
  return response.json();
}
const voice = {
  start: (magicToken, mode = "voice") => request(`/vop/voice/start?token=${magicToken}&mode=${mode}`, { method: "POST" }),
  fallbackToText: (magicToken, reason = "user_requested") => request(`/vop/voice/fallback-text?token=${magicToken}&reason=${reason}`, { method: "POST" }),
  complete: (magicToken, transcript, durationSeconds) => request(`/vop/voice/complete?token=${magicToken}`, {
    method: "POST",
    body: {
      transcript,
      duration_seconds: durationSeconds
    }
  })
};
const initialState = {
  status: "idle",
  mode: "voice",
  transcript: [],
  currentMessage: "",
  isRecording: false,
  isProcessing: false,
  error: null,
  wsConnection: null,
  conversationId: null,
  reachMode: false,
  reachSessionId: null,
  startedAt: null,
  magicToken: null
};
function createVoiceStore() {
  const { subscribe, set, update } = writable(initialState);
  const resolveWebsocketUrl = (rawUrl) => {
    if (rawUrl.startsWith("ws://") || rawUrl.startsWith("wss://")) {
      return rawUrl;
    }
    if (rawUrl.startsWith("http://") || rawUrl.startsWith("https://")) {
      const wsScheme = rawUrl.startsWith("https://") ? "wss" : "ws";
      return rawUrl.replace(/^https?:\/\//, `${wsScheme}://`);
    }
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    return `${protocol}://${window.location.host}${rawUrl}`;
  };
  return {
    subscribe,
    connect: async (token) => {
      update((state) => ({
        ...state,
        status: "connecting",
        magicToken: token
      }));
      try {
        const startResponse = await voice.start(token, initialState.mode);
        const reachMode = startResponse.reach === true;
        const wsUrl = resolveWebsocketUrl(startResponse.websocket_url);
        const ws = new WebSocket(wsUrl);
        ws.onopen = () => {
          update((state) => ({
            ...state,
            status: "active",
            wsConnection: ws,
            reachMode,
            conversationId: startResponse.conversation_id,
            reachSessionId: startResponse.reach_session_id || null,
            startedAt: Date.now()
          }));
        };
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === "error") {
            update((state) => ({
              ...state,
              status: "error",
              error: data.message || data.error || data.data?.error || "Connection error"
            }));
            return;
          }
          if (!reachMode && data.type === "ai_message") {
            update((state) => ({
              ...state,
              transcript: [
                ...state.transcript,
                {
                  role: "ai",
                  content: data.content,
                  timestamp: (/* @__PURE__ */ new Date()).toISOString()
                }
              ],
              isProcessing: false
            }));
          }
          if (reachMode && data.type === "text.output") {
            update((state) => ({
              ...state,
              transcript: [
                ...state.transcript,
                {
                  role: "ai",
                  content: data.data?.text || "",
                  timestamp: (/* @__PURE__ */ new Date()).toISOString()
                }
              ],
              isProcessing: false
            }));
          }
          if (!reachMode && data.type === "completed") {
            update((state) => ({
              ...state,
              status: "completed"
            }));
          }
          if (!reachMode && data.type === "mode_changed") {
            update((state) => ({
              ...state,
              mode: data.mode
            }));
          }
        };
        ws.onerror = () => {
          update((state) => ({
            ...state,
            status: "error",
            error: "Connection error"
          }));
        };
        ws.onclose = () => {
          update((state) => ({
            ...state,
            wsConnection: null
          }));
        };
        update((state) => ({
          ...state,
          wsConnection: ws
        }));
      } catch (err) {
        update((state) => ({
          ...state,
          status: "error",
          error: err?.message || "Failed to start voice session"
        }));
      }
    },
    sendMessage: (content, type = "text") => {
      update((state) => {
        if (state.wsConnection?.readyState === WebSocket.OPEN) {
          state.wsConnection.send(JSON.stringify({ type, content }));
          return {
            ...state,
            transcript: [
              ...state.transcript,
              {
                role: "user",
                content,
                timestamp: (/* @__PURE__ */ new Date()).toISOString()
              }
            ],
            currentMessage: "",
            isProcessing: true
          };
        }
        return state;
      });
    },
    endConversation: async () => {
      let snapshot;
      update((state) => {
        snapshot = state;
        if (state.wsConnection?.readyState === WebSocket.OPEN) {
          if (!state.reachMode) {
            state.wsConnection.send(JSON.stringify({ type: "end" }));
          }
          state.wsConnection.close();
        }
        return state;
      });
      if (snapshot && snapshot.reachMode && snapshot.magicToken) {
        const durationSeconds = snapshot.startedAt ? Math.max(0, Math.floor((Date.now() - snapshot.startedAt) / 1e3)) : void 0;
        try {
          await voice.complete(snapshot.magicToken, snapshot.transcript, durationSeconds);
        } catch {
        }
      }
      update((state) => ({ ...state, status: "completed" }));
    },
    switchToText: (reason = "user_requested") => {
      update((state) => {
        if (!state.reachMode && state.wsConnection?.readyState === WebSocket.OPEN) {
          state.wsConnection.send(
            JSON.stringify({ type: "fallback", reason })
          );
        }
        return { ...state, mode: "text" };
      });
    },
    setRecording: (isRecording) => {
      update((state) => ({ ...state, isRecording }));
    },
    setCurrentMessage: (message) => {
      update((state) => ({ ...state, currentMessage: message }));
    },
    setConsent: () => {
      update((state) => ({ ...state, status: "consent" }));
    },
    reset: () => {
      update((state) => {
        state.wsConnection?.close();
        return initialState;
      });
    }
  };
}
const voiceStore = createVoiceStore();
derived(
  voiceStore,
  ($voice) => $voice.status === "active"
);
derived(
  voiceStore,
  ($voice) => $voice.transcript
);
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    store_get($$store_subs ??= {}, "$page", page).params.token;
    let publicActions = [];
    onDestroy(() => {
      voiceStore.reset();
    });
    function getStatusLabel(status) {
      const labels = {
        new: "Novy",
        heard: "Slysime vas",
        in_progress: "Resime",
        resolved: "Vyreseno"
      };
      return labels[status] || status;
    }
    function getStatusColor(status) {
      const colors = {
        new: "text-cyan-data",
        heard: "text-terminal-green",
        in_progress: "text-yellow-400",
        resolved: "text-gray-500"
      };
      return colors[status] || "";
    }
    head("weknjb", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Speak by Kraliki - Check-in</title>`);
      });
    });
    $$renderer2.push(`<div class="min-h-screen flex items-center justify-center p-4 bg-void relative overflow-hidden">`);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="brutal-card max-w-lg w-full p-8 relative z-20"><div class="text-center mb-6"><div class="text-terminal-green text-3xl mb-2 font-display">///</div> <h1 class="text-2xl font-display">SPEAK BY KRALIKI</h1></div> <p class="mb-6 text-center font-mono">Ahoj! Toto je tvůj měsíční prostor pro zpětnou vazbu.</p> <div class="border-2 border-terminal-green p-4 mb-6 bg-void brutal-shadow-sm"><div class="flex items-center gap-2 mb-2 font-mono text-sm"><span class="text-terminal-green">[OK]</span> <span>Rozhovor je 100% ANONYMNÍ</span></div> <div class="flex items-center gap-2 mb-2 font-mono text-sm"><span class="text-terminal-green">[OK]</span> <span>Tvůj nadřízený NEUVIDÍ co jsi řekl/a</span></div> <div class="flex items-center gap-2 mb-2 font-mono text-sm"><span class="text-terminal-green">[OK]</span> <span>Vedení vidí pouze agregované trendy</span></div> <div class="flex items-center gap-2 mb-2 font-mono text-sm"><span class="text-terminal-green">[OK]</span> <span>Po rozhovoru si můžeš přečíst a upravit přepis</span></div> <div class="flex items-center gap-2 font-mono text-sm"><span class="text-terminal-green">[OK]</span> <span>Můžeš kdykoliv požádat o smazání svých dat</span></div></div> <p class="text-sm text-muted-foreground mb-6 text-center font-mono">Rozhovor trvá cca 5 minut.</p> <button class="brutal-btn brutal-btn-primary w-full mb-4">ROZUMÍM, POJĎME NA TO</button> <div class="text-center"><button type="button" class="text-sm text-muted-foreground hover:text-foreground bg-transparent border-none cursor-pointer font-mono uppercase">Nechci odpovídat: Přeskočit tento měsíc</button></div> `);
        if (publicActions.length > 0) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="mt-8 pt-6 border-t-2 border-foreground"><h3 class="text-sm font-bold mb-4 uppercase font-display">Co děláme s vaší zpětnou vazbou</h3> <div class="space-y-3"><!--[-->`);
          const each_array = ensure_array_like(publicActions.slice(0, 3));
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let action = each_array[$$index];
            $$renderer2.push(`<div class="p-3 border-2 border-foreground bg-card brutal-shadow-sm text-sm"><div class="flex items-center gap-2 mb-1"><span${attr_class(`${stringify(getStatusColor(action.status))} font-bold font-mono`)}>[${escape_html(getStatusLabel(action.status))}]</span></div> <span class="font-mono">${escape_html(action.public_message || action.topic)}</span></div>`);
          }
          $$renderer2.push(`<!--]--></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

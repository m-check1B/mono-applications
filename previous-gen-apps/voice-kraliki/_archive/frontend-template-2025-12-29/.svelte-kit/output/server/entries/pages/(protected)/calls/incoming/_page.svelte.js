import { g as sanitize_props, j as spread_props, s as slot, c as attr, d as attr_class } from "../../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../../chunks/index-server.js";
import { u as useAppConfig } from "../../../../../chunks/useAppConfig.js";
import { w as writable, g as get } from "../../../../../chunks/index.js";
import "../../../../../chunks/env.js";
import { a as apiGet } from "../../../../../chunks/auth2.js";
import { c as createAudioManager, P as Phone_off } from "../../../../../chunks/audioManager.js";
import { R as Refresh_ccw, A as AIInsightsPanel } from "../../../../../chunks/AIInsightsPanel.js";
import { P as Phone_incoming } from "../../../../../chunks/phone-incoming.js";
import { P as Phone_call } from "../../../../../chunks/phone-call.js";
import { I as Icon } from "../../../../../chunks/Icon.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
function Radio($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M4.9 19.1C1 15.2 1 8.8 4.9 4.9" }],
    ["path", { "d": "M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5" }],
    ["circle", { "cx": "12", "cy": "12", "r": "2" }],
    ["path", { "d": "M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5" }],
    ["path", { "d": "M19.1 4.9C23 8.8 23 15.1 19.1 19" }]
  ];
  Icon($$renderer, spread_props([
    { name: "radio" },
    $$sanitized_props,
    {
      /**
       * @component @name Radio
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNC45IDE5LjFDMSAxNS4yIDEgOC44IDQuOSA0LjkiIC8+CiAgPHBhdGggZD0iTTcuOCAxNi4yYy0yLjMtMi4zLTIuMy02LjEgMC04LjUiIC8+CiAgPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMiIgLz4KICA8cGF0aCBkPSJNMTYuMiA3LjhjMi4zIDIuMyAyLjMgNi4xIDAgOC41IiAvPgogIDxwYXRoIGQ9Ik0xOS4xIDQuOUMyMyA4LjggMjMgMTUuMSAxOS4xIDE5IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/radio
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
function uint8ToBase64(bytes) {
  let binary = "";
  const len = bytes.byteLength;
  for (let i = 0; i < len; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
function int16ToBase64(int16) {
  return uint8ToBase64(new Uint8Array(int16.buffer));
}
function createGeminiSession(path = "/test-outbound") {
  const initialState = {
    status: "idle"
  };
  const state = writable(initialState);
  let client = null;
  return {
    subscribe: state.subscribe,
    connect() {
      return;
    },
    disconnect() {
      client?.disconnect();
      client = null;
      state.set({ status: "disconnected" });
    },
    send(data) {
      client?.send(data);
    },
    reset() {
      client?.disconnect();
      client = null;
      state.set(initialState);
    },
    getState() {
      return get(state);
    }
  };
}
function createIncomingSession(path = "/test-inbound") {
  const gemini = createGeminiSession(path);
  const audioManager = createAudioManager();
  const state = writable({
    status: "idle",
    session: gemini.getState(),
    audioStatus: audioManager.getState().status
  });
  let lastProcessedEventAt = null;
  gemini.subscribe((session) => {
    state.update((prev) => ({
      ...prev,
      session,
      status: session.status === "error" ? "error" : session.status === "connected" ? "connected" : session.status === "connecting" ? "connecting" : prev.status
    }));
  });
  audioManager.subscribe((audio) => {
    state.update((prev) => ({ ...prev, audioStatus: audio.status }));
  });
  audioManager.sendCapturedFrame((buffer) => {
    const base64 = int16ToBase64(buffer);
    try {
      gemini.send(
        JSON.stringify({ type: "audio-data", audioData: base64 })
      );
    } catch (error) {
      console.error("Failed to send inbound audio frame", error);
    }
  });
  function updateFromEvent(event) {
    switch (event.type) {
      case "call-offer":
        state.update((prev) => ({
          ...prev,
          activeCall: {
            from: typeof event.from === "string" ? event.from : void 0,
            metadata: event
          },
          lastEvent: event
        }));
        break;
      case "call-ended":
        state.update((prev) => ({
          ...prev,
          activeCall: void 0,
          lastEvent: event
        }));
        break;
      case "audio":
        if (typeof event.audio === "string") {
          audioManager.playBase64Audio(event.audio, typeof event.mimeType === "string" ? event.mimeType : void 0).catch((error) => {
            console.error("Failed to play inbound audio chunk", error);
          });
        }
        break;
      default:
        state.update((prev) => ({ ...prev, lastEvent: event }));
    }
  }
  gemini.subscribe((session) => {
    if (!session.lastEventAt || session.lastEventAt === lastProcessedEventAt) return;
    lastProcessedEventAt = session.lastEventAt;
    const payload = session.lastEvent;
    if (payload && typeof payload === "object" && "type" in payload) {
      updateFromEvent(payload);
    }
  });
  return {
    subscribe: state.subscribe,
    connect() {
      state.update((prev) => ({ ...prev, status: "connecting", error: void 0 }));
      gemini.connect();
    },
    disconnect() {
      gemini.disconnect();
      audioManager.stop();
      state.update((prev) => ({
        ...prev,
        status: "idle",
        activeCall: void 0
      }));
    },
    async accept() {
      const result = await audioManager.startMicrophone();
      if (!result.success) {
        state.update((prev) => ({ ...prev, error: result.error ?? "Microphone access failed." }));
        return;
      }
      gemini.send(JSON.stringify({ type: "accept-call" }));
    },
    decline() {
      gemini.send(JSON.stringify({ type: "decline-call" }));
      state.update((prev) => ({ ...prev, activeCall: void 0 }));
    },
    getState() {
      return get(state);
    }
  };
}
function createProviderHealthStore(refreshMs = 15e3) {
  const state = writable(null);
  let timer = null;
  async function refresh() {
    try {
      const data = await apiGet("/api/provider-health");
      state.set(data);
    } catch (error) {
      console.error("Failed to fetch provider health", error);
    }
  }
  function start() {
    refresh();
    if (timer) clearInterval(timer);
    timer = setInterval(refresh, refreshMs);
  }
  function stop() {
    if (timer) clearInterval(timer);
    timer = null;
  }
  return {
    subscribe: state.subscribe,
    start,
    stop,
    refresh
  };
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const config = useAppConfig();
    const incomingSession = createIncomingSession("/test-inbound");
    let incoming = incomingSession.getState();
    const unsubscribeSession = incomingSession.subscribe((value) => {
      incoming = value;
    });
    const healthStore = createProviderHealthStore();
    let health = null;
    const unsubscribeHealth = healthStore.subscribe((value) => {
      health = value;
    });
    let transcriptMessages = [];
    let currentIntent = null;
    let currentSentiment = null;
    let suggestions = [];
    let enabled = false;
    let autoAccept = true;
    const hasActiveCall = Boolean(incoming.activeCall);
    function handleSuggestionAction(suggestionId, action) {
      suggestions = suggestions.map((s) => s.id === suggestionId ? { ...s, status: action === "accept" ? "accepted" : "rejected" } : s);
      if (action === "accept") {
        const suggestion = suggestions.find((s) => s.id === suggestionId);
        if (suggestion) {
          console.log("Accepted suggestion:", suggestion);
        }
      }
    }
    function formatStatus(status) {
      switch (status) {
        case "connecting":
          return "Connecting…";
        case "connected":
          return "Connected";
        case "error":
          return "Error";
        default:
          return "Idle";
      }
    }
    healthStore.start();
    onDestroy(() => {
      incomingSession.disconnect();
      unsubscribeSession();
      healthStore.stop();
      unsubscribeHealth();
    });
    $$renderer2.push(`<section class="space-y-6"><header class="space-y-1"><h1 class="text-2xl font-semibold text-text-primary">Incoming Call Control</h1> <p class="text-sm text-text-muted">Connect WebSocket listeners, monitor provider health, and auto-route callers using Stack 2026 ergonomics.</p></header> <div class="grid gap-4 lg:grid-cols-[2fr_3fr]"><article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Provider Connection</h2> <button class="btn btn-ghost">`);
    Refresh_ccw($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Reset</button></div> <div class="space-y-4"><div class="rounded-2xl border border-divider bg-secondary p-4 text-sm text-text-secondary"><p class="font-medium text-text-primary">WebSocket Endpoint</p> <p class="mt-1 text-xs text-text-muted">${escape_html(config.wsUrl)}/test-inbound</p> <p class="mt-1 text-xs text-text-muted">Session: ${escape_html(formatStatus(incoming.session.status))}</p></div> <div class="flex items-center justify-between rounded-2xl border border-divider bg-secondary/70 px-4 py-3"><div><p class="text-sm font-medium text-text-primary">Auto-Accept Calls</p> <p class="text-xs text-text-muted">Automatically answer inbound callers using the active campaign script.</p></div> <label class="relative inline-flex cursor-pointer items-center"><input type="checkbox" class="peer sr-only"${attr("checked", autoAccept, true)}/> <span class="peer h-6 w-11 rounded-full bg-divider transition peer-checked:bg-primary-soft"></span> <span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-text-muted transition peer-checked:translate-x-5 peer-checked:bg-primary"></span></label></div> <div class="flex gap-2"><button${attr_class(`btn ${"btn-primary"}`)}>`);
    {
      $$renderer2.push("<!--[!-->");
      Phone_incoming($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----> Start Listening`);
    }
    $$renderer2.push(`<!--]--></button> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    if (hasActiveCall) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="rounded-xl border border-primary-soft bg-primary-soft/20 px-4 py-3 text-sm text-text-secondary"><p class="font-semibold text-text-primary">Incoming call from ${escape_html(incoming.activeCall?.from ?? "Unknown")}</p> <div class="mt-2 flex gap-2"><button class="btn btn-primary">`);
      Phone_call($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----> Accept</button> <button class="btn btn-ghost">`);
      Phone_off($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----> Decline</button></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (incoming.error) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">${escape_html(incoming.error)}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></article> `);
    AIInsightsPanel($$renderer2, {
      messages: transcriptMessages,
      isLive: enabled,
      intent: currentIntent,
      sentiment: currentSentiment,
      suggestions,
      onSuggestionAction: handleSuggestionAction
    });
    $$renderer2.push(`<!----> <article class="card"><div class="card-header"><div class="flex items-center gap-2 text-text-primary">`);
    Radio($$renderer2, { class: "size-5" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold">Realtime Events</h2></div></div> <div class="space-y-3 text-sm text-text-secondary"><p class="rounded-2xl border border-divider bg-secondary px-4 py-3">${escape_html(incoming.lastEvent ? JSON.stringify(incoming.lastEvent) : "No inbound events yet.")}</p> <p class="text-xs text-text-muted">Audio status: ${escape_html(incoming.audioStatus)}. When connected, microphone audio streams to Gemini and responses play through the browser.</p></div></article></div> <article class="card"><div class="card-header"><h2 class="text-lg font-semibold text-text-primary">Provider Health</h2> <button class="btn btn-ghost btn-sm">`);
    Refresh_ccw($$renderer2, { class: "size-4" });
    $$renderer2.push(`<!----> Refresh</button></div> <div class="space-y-2 text-sm text-text-secondary">`);
    if (health) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p>Status: ${escape_html(health.providerHealth?.gemini?.status ?? "unknown")}</p> <p>Active connections: ${escape_html(health.activeConnections ?? 0)}</p> <p class="text-xs text-text-muted">Last updated: ${escape_html(new Date(health.timestamp ?? Date.now()).toLocaleTimeString())}</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<p class="text-xs text-text-muted">Health data not available yet.</p>`);
    }
    $$renderer2.push(`<!--]--></div></article></section>`);
  });
}
export {
  _page as default
};

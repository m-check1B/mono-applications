import { x as head, z as attr_class } from "../../../../chunks/index2.js";
import { w as ws, o as onDestroy } from "../../../../chunks/websocket.svelte.js";
import { t as trpc } from "../../../../chunks/client.js";
import { a as auth } from "../../../../chunks/auth.svelte.js";
import "clsx";
import "lightweight-charts";
import { B as Button } from "../../../../chunks/Button.js";
import { B as Badge } from "../../../../chunks/Badge.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
class CallsStore {
  activeCalls = [];
  queuedCalls = [];
  constructor() {
    ws.onMessage((message) => {
      if (message.type === "call:created") {
        this.addCall(message.call);
      } else if (message.type === "call:updated") {
        this.updateCall(message.call);
      } else if (message.type === "call:ended") {
        this.removeCall(message.callId);
      }
    });
  }
  addCall(call) {
    if (call.status === "QUEUED") {
      this.queuedCalls = [...this.queuedCalls, call];
    } else if (call.status === "IN_PROGRESS" || call.status === "RINGING") {
      this.activeCalls = [...this.activeCalls, call];
    }
  }
  updateCall(call) {
    this.activeCalls = this.activeCalls.filter((c) => c.id !== call.id);
    this.queuedCalls = this.queuedCalls.filter((c) => c.id !== call.id);
    this.addCall(call);
  }
  removeCall(callId) {
    this.activeCalls = this.activeCalls.filter((c) => c.id !== callId);
    this.queuedCalls = this.queuedCalls.filter((c) => c.id !== callId);
  }
  setActiveCalls(calls2) {
    this.activeCalls = calls2.filter((c) => c.status === "IN_PROGRESS" || c.status === "RINGING");
  }
  setQueuedCalls(calls2) {
    this.queuedCalls = calls2.filter((c) => c.status === "QUEUED");
  }
}
new CallsStore();
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let agentStatus = "OFFLINE";
    const generateSparklineData = (baseValue, points = 20) => {
      return Array.from({ length: points }, (_, i) => ({
        time: Date.now() / 1e3 - (points - i) * 3600,
        value: baseValue + Math.random() * 10 - 5
      }));
    };
    generateSparklineData(20);
    generateSparklineData(180);
    generateSparklineData(2);
    generateSparklineData(92);
    async function updateAgentStatus(newStatus) {
      try {
        await trpc.agent.updateStatus.mutate({ status: newStatus });
      } catch {
      }
      agentStatus = newStatus;
    }
    function getStatusVariant(status) {
      switch (status) {
        case "AVAILABLE":
          return "success";
        case "BUSY":
          return "warning";
        case "BREAK":
          return "primary";
        case "WRAP_UP":
          return "secondary";
        default:
          return "gray";
      }
    }
    onDestroy(() => ws.disconnect());
    let $$settled = true;
    let $$inner_renderer;
    function $$render_inner($$renderer3) {
      head($$renderer3, ($$renderer4) => {
        $$renderer4.title(($$renderer5) => {
          $$renderer5.push(`<title>Operator Dashboard - Voice by Kraliki</title>`);
        });
      });
      $$renderer3.push(`<div class="fixed inset-0 -z-10 overflow-hidden pointer-events-none"><div class="absolute -top-40 left-1/2 h-[480px] w-[720px] -translate-x-1/2 rounded-full bg-gradient-radial from-primary-500/25 via-primary-600/10 to-transparent blur-3xl svelte-sqzup4"></div> <div class="absolute bottom-[-200px] right-[-120px] h-[520px] w-[520px] rounded-full bg-gradient-radial from-purple-500/25 via-purple-600/10 to-transparent blur-3xl svelte-sqzup4"></div></div> <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"><header class="sticky top-0 z-50 border-b border-white/10 bg-black/40 backdrop-blur-xl"><div class="mx-auto max-w-7xl px-4 h-16 flex items-center justify-between"><div class="flex items-center gap-3"><div class="p-2 bg-primary-500/20 rounded-lg"><svg class="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg></div> <div><h1 class="text-lg font-bold text-white">Operator Console</h1> <p class="text-xs text-gray-400">Welcome, ${escape_html(auth.user?.firstName || "Agent")}</p></div></div> <div class="flex items-center gap-4"><div${attr_class(
        `flex items-center gap-2 px-3 py-1.5 rounded-full text-sm backdrop-blur-sm ${ws.connected ? "bg-green-500/20 text-green-400 border border-green-500/30" : "bg-red-500/20 text-red-400 border border-red-500/30"}`,
        "svelte-sqzup4"
      )}><div${attr_class(`w-2 h-2 rounded-full ${ws.connected ? "bg-green-400 animate-pulse" : "bg-red-400"}`, "svelte-sqzup4")}></div> ${escape_html(ws.connected ? "Connected" : "Disconnected")}</div> `);
      Badge($$renderer3, {
        variant: getStatusVariant(agentStatus),
        class: "px-4 py-1.5",
        children: ($$renderer4) => {
          $$renderer4.push(`<!---->${escape_html(agentStatus)}`);
        }
      });
      $$renderer3.push(`<!----> <div class="flex gap-2">`);
      Button($$renderer3, {
        size: "sm",
        variant: agentStatus === "AVAILABLE" ? "success" : "secondary",
        onclick: () => updateAgentStatus("AVAILABLE"),
        children: ($$renderer4) => {
          $$renderer4.push(`<!---->Available`);
        }
      });
      $$renderer3.push(`<!----> `);
      Button($$renderer3, {
        size: "sm",
        variant: agentStatus === "BREAK" ? "primary" : "secondary",
        onclick: () => updateAgentStatus("BREAK"),
        children: ($$renderer4) => {
          $$renderer4.push(`<!---->Break`);
        }
      });
      $$renderer3.push(`<!----></div></div></div></header> `);
      {
        $$renderer3.push("<!--[-->");
        $$renderer3.push(`<div class="flex justify-center items-center py-24"><div class="relative"><div class="w-16 h-16 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div> <div class="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-purple-500 rounded-full animate-spin" style="animation-delay: -0.3s;"></div></div></div>`);
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

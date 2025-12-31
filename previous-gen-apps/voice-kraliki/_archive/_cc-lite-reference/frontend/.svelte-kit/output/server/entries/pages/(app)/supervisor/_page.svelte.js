import { x as head } from "../../../../chunks/index2.js";
import { o as onDestroy, w as ws } from "../../../../chunks/websocket.svelte.js";
import "../../../../chunks/client.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import "lightweight-charts";
import { B as Badge } from "../../../../chunks/Badge.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let liveCalls = [];
    let agents = [
      {
        id: "AGT001",
        name: "John Doe",
        email: "john.doe@company.com",
        status: "on-call",
        currentCall: { customerName: "Alice Johnson", duration: 187 },
        stats: { callsToday: 18, avgDuration: 245, satisfaction: 96 }
      },
      {
        id: "AGT002",
        name: "Sarah Smith",
        email: "sarah.smith@company.com",
        status: "on-call",
        currentCall: { customerName: "Bob Williams", duration: 95 },
        stats: { callsToday: 22, avgDuration: 198, satisfaction: 94 }
      },
      {
        id: "AGT003",
        name: "Mike Chen",
        email: "mike.chen@company.com",
        status: "on-call",
        currentCall: { customerName: "Carol Martinez", duration: 240 },
        stats: { callsToday: 15, avgDuration: 312, satisfaction: 89 }
      },
      {
        id: "AGT004",
        name: "Emma Davis",
        email: "emma.davis@company.com",
        status: "available",
        stats: { callsToday: 20, avgDuration: 220, satisfaction: 97 }
      },
      {
        id: "AGT005",
        name: "David Wilson",
        email: "david.wilson@company.com",
        status: "break",
        stats: { callsToday: 17, avgDuration: 265, satisfaction: 92 }
      }
    ];
    onDestroy(() => {
      ws.disconnect();
    });
    head($$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Supervisor Dashboard - Voice by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="space-y-6"><div class="flex justify-between items-center"><div><h1 class="text-2xl font-bold text-gray-900 dark:text-white">Supervisor Cockpit</h1> <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">Real-time monitoring and team management</p></div> <div class="flex items-center gap-3">`);
    Badge($$renderer2, {
      variant: "success",
      class: "text-sm",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->🟢 ${escape_html(agents.filter((a) => a.status === "available").length)} Available`);
      }
    });
    $$renderer2.push(`<!----> `);
    Badge($$renderer2, {
      variant: "primary",
      class: "text-sm",
      children: ($$renderer3) => {
        $$renderer3.push(`<!---->📞 ${escape_html(liveCalls.length)} Active Calls`);
      }
    });
    $$renderer2.push(`<!----></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex justify-center py-12"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

import { g as sanitize_props, j as spread_props, s as slot, e as ensure_array_like, d as attr_class, f as stringify } from "../../../../chunks/index2.js";
import { u as useAppConfig } from "../../../../chunks/useAppConfig.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { c as createQuery, e as fetchCompanies, d as fetchCampaigns, g as fetchTelephonyStats } from "../../../../chunks/calls.js";
import { a as apiGet } from "../../../../chunks/auth2.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { A as Activity } from "../../../../chunks/activity.js";
import { P as Phone_incoming } from "../../../../chunks/phone-incoming.js";
import { U as Users } from "../../../../chunks/users.js";
import { P as Phone_call } from "../../../../chunks/phone-call.js";
import { C as Circle_check_big } from "../../../../chunks/circle-check-big.js";
function Circle_alert($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "10" }],
    ["line", { "x1": "12", "x2": "12", "y1": "8", "y2": "12" }],
    [
      "line",
      { "x1": "12", "x2": "12.01", "y1": "16", "y2": "16" }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "circle-alert" },
    $$sanitized_props,
    {
      /**
       * @component @name CircleAlert
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KICA8bGluZSB4MT0iMTIiIHgyPSIxMiIgeTE9IjgiIHkyPSIxMiIgLz4KICA8bGluZSB4MT0iMTIiIHgyPSIxMi4wMSIgeTE9IjE2IiB5Mj0iMTYiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/circle-alert
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
function Clock($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "10" }],
    ["polyline", { "points": "12 6 12 12 16 14" }]
  ];
  Icon($$renderer, spread_props([
    { name: "clock" },
    $$sanitized_props,
    {
      /**
       * @component @name Clock
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KICA8cG9seWxpbmUgcG9pbnRzPSIxMiA2IDEyIDEyIDE2IDE0IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/clock
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
function Target($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "10" }],
    ["circle", { "cx": "12", "cy": "12", "r": "6" }],
    ["circle", { "cx": "12", "cy": "12", "r": "2" }]
  ];
  Icon($$renderer, spread_props([
    { name: "target" },
    $$sanitized_props,
    {
      /**
       * @component @name Target
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSI2IiAvPgogIDxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjIiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/target
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
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const config = useAppConfig();
    createQuery({
      queryKey: ["companies-count"],
      queryFn: fetchCompanies,
      staleTime: 3e4
    });
    createQuery({
      queryKey: ["campaigns-count"],
      queryFn: fetchCampaigns,
      staleTime: 3e4
    });
    createQuery({
      queryKey: ["health"],
      queryFn: () => apiGet("/health"),
      staleTime: 1e4
    });
    createQuery({
      queryKey: ["telephony-stats"],
      queryFn: fetchTelephonyStats,
      staleTime: 15e3
    });
    let totalCompanies = 0;
    let totalCampaigns = 0;
    let systemStatus = "checking...";
    let callsToday = 0;
    let successRate = 0;
    const overviewTiles = [
      {
        label: "Total Companies",
        value: totalCompanies,
        icon: Users,
        color: "text-cyan-data"
      },
      {
        label: "Active Campaigns",
        value: totalCampaigns,
        icon: Target,
        color: "text-terminal-green"
      },
      {
        label: "Calls Today",
        value: callsToday,
        icon: Phone_call,
        color: "text-accent"
      },
      {
        label: "Success Rate",
        value: `${successRate}%`,
        icon: Circle_check_big,
        color: "text-terminal-green"
      }
    ];
    const systemInfo = [
      {
        label: "System Status",
        value: systemStatus,
        icon: Circle_alert,
        color: "text-system-red"
      },
      {
        label: "Backend",
        value: config.backendUrl,
        icon: Activity,
        color: "text-muted-foreground"
      },
      {
        label: "WebSocket",
        value: config.wsUrl,
        icon: Phone_incoming,
        color: "text-muted-foreground"
      },
      {
        label: "Last Updated",
        value: (/* @__PURE__ */ new Date()).toLocaleTimeString(),
        icon: Clock,
        color: "text-muted-foreground"
      }
    ];
    $$renderer2.push(`<section class="space-y-12"><header class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between border-b-2 border-foreground pb-8"><div class="space-y-2"><h1 class="text-5xl font-display text-foreground tracking-tighter uppercase">Operator Console <span class="text-terminal-green">Overview</span></h1> <p class="text-[11px] font-bold uppercase tracking-[0.3em] text-muted-foreground">SYSTEM_STATUS: ${escape_html(systemStatus)} // ENVIROMENT: PRODUCTION // VERSION: 1.0.4-LITE</p></div> <div class="flex items-center gap-4"><button class="brutal-btn bg-terminal-green text-void">Start Outbound Session</button> <button class="brutal-btn bg-void text-terminal-green border-terminal-green">Manage Incoming</button></div></header> <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-4"><!--[-->`);
    const each_array = ensure_array_like(overviewTiles);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let tile = each_array[$$index];
      const Icon2 = tile.icon;
      $$renderer2.push(`<article class="brutal-card p-6 hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all group hover:border-terminal-green hover:shadow-[8px_8px_0px_0px_rgba(51,255,0,1)]"><div class="flex items-start justify-between"><div class="space-y-3"><p class="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2"><span class="w-2 h-2 bg-foreground/20 group-hover:bg-terminal-green"></span> ${escape_html(tile.label)}</p> <p class="text-4xl font-display text-foreground">${escape_html(tile.value)}</p></div> <div${attr_class(`flex size-12 items-center justify-center border-2 border-foreground group-hover:border-terminal-green group-hover:text-terminal-green ${stringify(tile.color)}`)}><!---->`);
      Icon2($$renderer2, { class: "size-6" });
      $$renderer2.push(`<!----></div></div></article>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-4"><!--[-->`);
    const each_array_1 = ensure_array_like(systemInfo);
    for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
      let info = each_array_1[$$index_1];
      const Icon2 = info.icon;
      $$renderer2.push(`<article class="brutal-card p-4 border-muted/30 shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)] hover:shadow-brutal hover:border-foreground transition-all"><div class="flex items-center justify-between"><div class="space-y-1"><p class="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">${escape_html(info.label)}</p> <p class="text-[11px] font-mono font-bold text-foreground break-all">${escape_html(info.value)}</p></div> <div${attr_class(`flex size-8 items-center justify-center border border-muted/30 ${stringify(info.color)}`)}><!---->`);
      Icon2($$renderer2, { class: "size-4" });
      $$renderer2.push(`<!----></div></div></article>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="grid grid-cols-1 lg:grid-cols-12 gap-8"><article class="brutal-card lg:col-span-8 p-8 relative overflow-hidden"><div class="absolute top-0 right-0 p-4 opacity-5">`);
    Activity($$renderer2, { class: "size-32" });
    $$renderer2.push(`<!----></div> <div class="relative z-10"><div class="flex items-center gap-3 mb-6"><div class="w-4 h-4 bg-terminal-green"></div> <h2 class="text-3xl font-display uppercase">Next Operations</h2></div> <div class="grid grid-cols-1 md:grid-cols-2 gap-8"><div class="space-y-4"><p class="text-sm font-mono text-muted-foreground leading-relaxed italic border-l-2 border-terminal-green pl-4">"Continue migration by wiring data sources and testing real-time flows. System integrity is priority #1."</p> <ul class="space-y-4 text-[11px] font-bold uppercase tracking-widest text-foreground"><li class="flex items-center gap-3"><span class="text-terminal-green font-mono">[01]</span> <span>Configure outbound models</span></li> <li class="flex items-center gap-3"><span class="text-terminal-green font-mono">[02]</span> <span>Validate WebSocket events</span></li> <li class="flex items-center gap-3"><span class="text-terminal-green font-mono">[03]</span> <span>Integrate provider health</span></li></ul></div> <div class="bg-muted/5 border-2 border-muted/20 p-6 font-mono text-[10px] text-muted-foreground space-y-2"><p class="text-terminal-green font-bold">>> SYSTEM_LOG_EXTRACT</p> <p>[23:13:22] GE-designer-23:13.22.12.AA: Applying Style 2026...</p> <p>[23:13:24] Dashboard UI refactored to Brutalism.</p> <p>[23:13:25] All shadows offset 4px solid.</p> <p>[23:13:26] Scanning for non-compliant elements...</p> <div class="flex gap-1 mt-4"><div class="w-1 h-3 bg-terminal-green animate-pulse"></div> <div class="w-1 h-3 bg-terminal-green animate-pulse delay-75"></div> <div class="w-1 h-3 bg-terminal-green animate-pulse delay-150"></div></div></div></div></div></article> <aside class="lg:col-span-4 space-y-6"><div class="brutal-card p-6 bg-void text-terminal-green border-terminal-green shadow-[6px_6px_0px_0px_rgba(51,255,0,0.3)]"><h3 class="font-display text-xl mb-4 uppercase tracking-tighter">Terminal Feed</h3> <div class="font-mono text-[10px] space-y-3"><div class="flex justify-between border-b border-terminal-green/20 pb-1"><span>OUTBOUND_ENGINE</span> <span class="text-cyan-data">ACTIVE</span></div> <div class="flex justify-between border-b border-terminal-green/20 pb-1"><span>TRANSCRIPTION_V2</span> <span class="text-terminal-green">READY</span></div> <div class="flex justify-between border-b border-terminal-green/20 pb-1"><span>IVR_ROUTING</span> <span class="text-system-red">ERROR_404</span></div></div> <button class="mt-6 w-full py-2 border border-terminal-green text-[9px] font-bold uppercase hover:bg-terminal-green hover:text-void transition-colors">Access Low-Level Logs</button></div></aside></div></section>`);
  });
}
export {
  _page as default
};

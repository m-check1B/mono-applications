import { g as sanitize_props, j as spread_props, s as slot, e as ensure_array_like, d as attr_class, c as attr, f as stringify } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { M as Mic } from "../../../../chunks/mic.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { P as Plus } from "../../../../chunks/plus.js";
import { S as Search } from "../../../../chunks/search.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function Sparkles($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"
      }
    ],
    ["path", { "d": "M20 3v4" }],
    ["path", { "d": "M22 5h-4" }],
    ["path", { "d": "M4 17v2" }],
    ["path", { "d": "M5 18H3" }]
  ];
  Icon($$renderer, spread_props([
    { name: "sparkles" },
    $$sanitized_props,
    {
      /**
       * @component @name Sparkles
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNOS45MzcgMTUuNUEyIDIgMCAwIDAgOC41IDE0LjA2M2wtNi4xMzUtMS41ODJhLjUuNSAwIDAgMSAwLS45NjJMOC41IDkuOTM2QTIgMiAwIDAgMCA5LjkzNyA4LjVsMS41ODItNi4xMzVhLjUuNSAwIDAgMSAuOTYzIDBMMTQuMDYzIDguNUEyIDIgMCAwIDAgMTUuNSA5LjkzN2w2LjEzNSAxLjU4MWEuNS41IDAgMCAxIDAgLjk2NEwxNS41IDE0LjA2M2EyIDIgMCAwIDAtMS40MzcgMS40MzdsLTEuNTgyIDYuMTM1YS41LjUgMCAwIDEtLjk2MyAweiIgLz4KICA8cGF0aCBkPSJNMjAgM3Y0IiAvPgogIDxwYXRoIGQ9Ik0yMiA1aC00IiAvPgogIDxwYXRoIGQ9Ik00IDE3djIiIC8+CiAgPHBhdGggZD0iTTUgMThIMyIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/sparkles
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
    let scenarios = [];
    let searchQuery = "";
    let selectedCategory = "All";
    const categories = [
      "All",
      "Customer Service",
      "Sales",
      "Technical Support",
      "Compliance"
    ];
    scenarios.filter((s) => {
      const matchesSearch = s.name.toLowerCase().includes(searchQuery.toLowerCase()) || s.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === "All";
      return matchesSearch && matchesCategory;
    });
    $$renderer2.push(`<div class="p-6 max-w-7xl mx-auto min-h-screen space-y-8"><header class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-4 border-foreground pb-6"><div class="space-y-2"><h1 class="text-5xl font-display text-foreground tracking-tighter uppercase">Scenario <span class="text-terminal-green">Matrix</span></h1> <p class="text-[11px] font-bold uppercase tracking-[0.3em] text-muted-foreground">TRAINING_MODULES // TOTAL_COUNT: ${escape_html(scenarios.length)} // STATUS: ONLINE</p></div> <div class="flex gap-3"><button class="brutal-btn bg-primary text-primary-foreground hover:translate-x-[-2px] hover:translate-y-[-2px]">`);
    Mic($$renderer2, { class: "w-5 h-5 inline mr-2" });
    $$renderer2.push(`<!----> Voice Arena</button> <button class="brutal-btn bg-accent text-accent-foreground hover:translate-x-[-2px] hover:translate-y-[-2px]">`);
    Sparkles($$renderer2, { class: "w-5 h-5 inline mr-2" });
    $$renderer2.push(`<!----> Quick Start</button> <button class="brutal-btn bg-terminal-green text-void hover:translate-x-[-2px] hover:translate-y-[-2px]">`);
    Plus($$renderer2, { class: "w-5 h-5 inline mr-2" });
    $$renderer2.push(`<!----> New Simulation</button></div></header> <div class="flex flex-col md:flex-row gap-4 items-center justify-between"><div class="flex items-center gap-2 w-full md:w-auto"><!--[-->`);
    const each_array = ensure_array_like(categories);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let cat = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-3 py-1 text-[10px] font-bold uppercase border-2 transition-all ${stringify(selectedCategory === cat ? "bg-foreground text-background border-foreground" : "border-transparent text-muted-foreground hover:border-muted")}`)}>${escape_html(cat)}</button>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="relative w-full md:w-64">`);
    Search($$renderer2, {
      class: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground"
    });
    $$renderer2.push(`<!----> <input type="text"${attr("value", searchQuery)} placeholder="SEARCH_INDEX..." class="w-full pl-9 pr-4 py-2 bg-card border-2 border-border font-mono text-sm focus:outline-none focus:border-terminal-green focus:shadow-[4px_4px_0px_0px_rgba(51,255,0,1)] transition-all placeholder:text-muted-foreground/50 uppercase"/></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"><!--[-->`);
      const each_array_1 = ensure_array_like(Array(6));
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        each_array_1[$$index_1];
        $$renderer2.push(`<div class="h-48 brutal-card animate-pulse bg-muted/10 border-muted"></div>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _page as default
};

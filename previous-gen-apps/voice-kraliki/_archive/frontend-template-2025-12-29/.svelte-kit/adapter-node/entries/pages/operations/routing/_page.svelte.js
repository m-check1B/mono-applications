import { g as sanitize_props, j as spread_props, s as slot, c as attr, e as ensure_array_like } from "../../../../chunks/index2.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { P as Play } from "../../../../chunks/play.js";
import { S as Search } from "../../../../chunks/search.js";
import { P as Plus } from "../../../../chunks/plus.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function Arrow_up_down($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "m21 16-4 4-4-4" }],
    ["path", { "d": "M17 20V4" }],
    ["path", { "d": "m3 8 4-4 4 4" }],
    ["path", { "d": "M7 4v16" }]
  ];
  Icon($$renderer, spread_props([
    { name: "arrow-up-down" },
    $$sanitized_props,
    {
      /**
       * @component @name ArrowUpDown
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMjEgMTYtNCA0LTQtNCIgLz4KICA8cGF0aCBkPSJNMTcgMjBWNCIgLz4KICA8cGF0aCBkPSJtMyA4IDQtNCA0IDQiIC8+CiAgPHBhdGggZD0iTTcgNHYxNiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/arrow-up-down
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
function Git_branch($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["line", { "x1": "6", "x2": "6", "y1": "3", "y2": "15" }],
    ["circle", { "cx": "18", "cy": "6", "r": "3" }],
    ["circle", { "cx": "6", "cy": "18", "r": "3" }],
    ["path", { "d": "M18 9a9 9 0 0 1-9 9" }]
  ];
  Icon($$renderer, spread_props([
    { name: "git-branch" },
    $$sanitized_props,
    {
      /**
       * @component @name GitBranch
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8bGluZSB4MT0iNiIgeDI9IjYiIHkxPSIzIiB5Mj0iMTUiIC8+CiAgPGNpcmNsZSBjeD0iMTgiIGN5PSI2IiByPSIzIiAvPgogIDxjaXJjbGUgY3g9IjYiIGN5PSIxOCIgcj0iMyIgLz4KICA8cGF0aCBkPSJNMTggOWE5IDkgMCAwIDEtOSA5IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/git-branch
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
    let rules = [];
    let searchQuery = "";
    let statusFilter = "all";
    let strategyFilter = "all";
    let stats = {
      total_rules: 0,
      active_rules: 0,
      inactive_rules: 0,
      avg_priority: 0
    };
    const strategyLabels = {
      skill_based: "Skill-Based",
      least_busy: "Least Busy",
      longest_idle: "Longest Idle",
      round_robin: "Round Robin",
      priority: "Priority",
      language: "Language",
      vip: "VIP",
      custom: "Custom"
    };
    rules.filter((rule) => {
      const matchesStrategy = strategyFilter === "all";
      return matchesStrategy;
    }).sort((a, b) => a.priority - b.priority);
    $$renderer2.push(`<div class="p-6 max-w-7xl mx-auto"><div class="mb-6"><h1 class="text-3xl font-bold text-gray-900 mb-2">Call Routing Rules</h1> <p class="text-gray-600">Configure intelligent call routing strategies to connect callers with the right agents</p></div> <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"><div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Total Rules</p> <p class="text-2xl font-bold text-gray-900">${escape_html(stats.total_rules)}</p></div> `);
    Git_branch($$renderer2, { class: "w-8 h-8 text-blue-500" });
    $$renderer2.push(`<!----></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Active Rules</p> <p class="text-2xl font-bold text-green-600">${escape_html(stats.active_rules)}</p></div> `);
    Play($$renderer2, { class: "w-8 h-8 text-green-500" });
    $$renderer2.push(`<!----></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Inactive Rules</p> <p class="text-2xl font-bold text-gray-600">${escape_html(stats.inactive_rules)}</p></div> `);
    Git_branch($$renderer2, { class: "w-8 h-8 text-gray-400" });
    $$renderer2.push(`<!----></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Avg Priority</p> <p class="text-2xl font-bold text-blue-600">${escape_html(stats.avg_priority)}</p></div> `);
    Arrow_up_down($$renderer2, { class: "w-8 h-8 text-blue-400" });
    $$renderer2.push(`<!----></div></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4 mb-4"><div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4"><div class="flex flex-col md:flex-row gap-4 flex-1"><div class="relative flex-1">`);
    Search($$renderer2, {
      class: "absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
    });
    $$renderer2.push(`<!----> <input type="text" placeholder="Search rules..."${attr("value", searchQuery)} class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> `);
    $$renderer2.select(
      {
        value: statusFilter,
        class: "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "all" }, ($$renderer4) => {
          $$renderer4.push(`All Status`);
        });
        $$renderer3.option({ value: "active" }, ($$renderer4) => {
          $$renderer4.push(`Active`);
        });
        $$renderer3.option({ value: "inactive" }, ($$renderer4) => {
          $$renderer4.push(`Inactive`);
        });
      }
    );
    $$renderer2.push(` `);
    $$renderer2.select(
      {
        value: strategyFilter,
        class: "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "all" }, ($$renderer4) => {
          $$renderer4.push(`All Strategies`);
        });
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(Object.entries(strategyLabels));
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let [value, label] = each_array[$$index];
          $$renderer3.option({ value }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(label)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</div> <a href="/operations/routing/builder" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">`);
    Plus($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Create Rule</a></div></div> <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="p-8 text-center"><div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div> <p class="mt-2 text-gray-600">Loading routing rules...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
export {
  _page as default
};

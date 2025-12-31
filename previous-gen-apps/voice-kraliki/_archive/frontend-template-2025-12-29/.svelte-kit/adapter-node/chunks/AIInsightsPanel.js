import { g as sanitize_props, j as spread_props, s as slot, d as attr_class, c as attr, e as ensure_array_like, f as stringify } from "./index2.js";
import { I as Icon } from "./Icon.js";
import { M as Message_circle, U as User, B as Bot } from "./user.js";
import { e as escape_html } from "./escaping.js";
function Brain($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"
      }
    ],
    [
      "path",
      {
        "d": "M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"
      }
    ],
    [
      "path",
      { "d": "M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4" }
    ],
    ["path", { "d": "M17.599 6.5a3 3 0 0 0 .399-1.375" }],
    ["path", { "d": "M6.003 5.125A3 3 0 0 0 6.401 6.5" }],
    ["path", { "d": "M3.477 10.896a4 4 0 0 1 .585-.396" }],
    ["path", { "d": "M19.938 10.5a4 4 0 0 1 .585.396" }],
    ["path", { "d": "M6 18a4 4 0 0 1-1.967-.516" }],
    ["path", { "d": "M19.967 17.484A4 4 0 0 1 18 18" }]
  ];
  Icon($$renderer, spread_props([
    { name: "brain" },
    $$sanitized_props,
    {
      /**
       * @component @name Brain
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgNWEzIDMgMCAxIDAtNS45OTcuMTI1IDQgNCAwIDAgMC0yLjUyNiA1Ljc3IDQgNCAwIDAgMCAuNTU2IDYuNTg4QTQgNCAwIDEgMCAxMiAxOFoiIC8+CiAgPHBhdGggZD0iTTEyIDVhMyAzIDAgMSAxIDUuOTk3LjEyNSA0IDQgMCAwIDEgMi41MjYgNS43NyA0IDQgMCAwIDEtLjU1NiA2LjU4OEE0IDQgMCAxIDEgMTIgMThaIiAvPgogIDxwYXRoIGQ9Ik0xNSAxM2E0LjUgNC41IDAgMCAxLTMtNCA0LjUgNC41IDAgMCAxLTMgNCIgLz4KICA8cGF0aCBkPSJNMTcuNTk5IDYuNWEzIDMgMCAwIDAgLjM5OS0xLjM3NSIgLz4KICA8cGF0aCBkPSJNNi4wMDMgNS4xMjVBMyAzIDAgMCAwIDYuNDAxIDYuNSIgLz4KICA8cGF0aCBkPSJNMy40NzcgMTAuODk2YTQgNCAwIDAgMSAuNTg1LS4zOTYiIC8+CiAgPHBhdGggZD0iTTE5LjkzOCAxMC41YTQgNCAwIDAgMSAuNTg1LjM5NiIgLz4KICA8cGF0aCBkPSJNNiAxOGE0IDQgMCAwIDEtMS45NjctLjUxNiIgLz4KICA8cGF0aCBkPSJNMTkuOTY3IDE3LjQ4NEE0IDQgMCAwIDEgMTggMTgiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/brain
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
function Refresh_ccw($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      { "d": "M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" }
    ],
    ["path", { "d": "M3 3v5h5" }],
    [
      "path",
      { "d": "M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" }
    ],
    ["path", { "d": "M16 16h5v5" }]
  ];
  Icon($$renderer, spread_props([
    { name: "refresh-ccw" },
    $$sanitized_props,
    {
      /**
       * @component @name RefreshCcw
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjEgMTJhOSA5IDAgMCAwLTktOSA5Ljc1IDkuNzUgMCAwIDAtNi43NCAyLjc0TDMgOCIgLz4KICA8cGF0aCBkPSJNMyAzdjVoNSIgLz4KICA8cGF0aCBkPSJNMyAxMmE5IDkgMCAwIDAgOSA5IDkuNzUgOS43NSAwIDAgMCA2Ljc0LTIuNzRMMjEgMTYiIC8+CiAgPHBhdGggZD0iTTE2IDE2aDV2NSIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/refresh-ccw
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
function AIInsightsPanel($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      messages = [],
      isLive = false,
      intent = null,
      sentiment = null,
      suggestions = [],
      onSuggestionAction
    } = $$props;
    function formatTime(date) {
      return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    }
    function getRoleLabel(role) {
      return role === "user" ? "Customer" : "AI Agent";
    }
    function getRoleIcon(role) {
      return role === "user" ? User : Bot;
    }
    function getRoleColor(role) {
      return role === "user" ? "text-blue-500" : "text-primary";
    }
    let hasInsights = intent || sentiment;
    let hasSuggestions = suggestions && suggestions.length > 0;
    $$renderer2.push(`<article class="card h-full"><div class="card-header"><div class="flex items-center gap-2">`);
    Brain($$renderer2, { class: "size-5 text-text-primary" });
    $$renderer2.push(`<!----> <h2 class="text-lg font-semibold text-text-primary">AI Insights</h2> `);
    if (isLive) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<span class="inline-flex items-center gap-1.5 rounded-full bg-primary/20 px-2 py-0.5 text-xs font-medium text-primary"><span class="size-1.5 animate-pulse rounded-full bg-primary"></span> Live</span>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="flex gap-1 rounded-lg bg-secondary p-1"><button${attr_class(`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${stringify(
      "bg-background text-text-primary shadow-sm"
    )}`)}>Transcript (${escape_html(messages.length)})</button> <button${attr_class(`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${stringify("text-text-muted hover:text-text-primary")}`)}${attr("disabled", !hasInsights, true)}>Insights ${escape_html(hasInsights ? "✓" : "")}</button> <button${attr_class(`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${stringify("text-text-muted hover:text-text-primary")}`)}${attr("disabled", !hasSuggestions, true)}>Suggestions (${escape_html(suggestions.length)})</button></div></div> <div class="max-h-[600px] overflow-y-auto">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="space-y-3 p-4">`);
      if (messages.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="flex flex-col items-center justify-center py-12 text-center">`);
        Message_circle($$renderer2, { class: "size-12 text-text-muted opacity-30" });
        $$renderer2.push(`<!----> <p class="mt-3 text-sm text-text-muted">No conversation yet. Start a call to see real-time transcription.</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<!--[-->`);
        const each_array = ensure_array_like(messages);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let message = each_array[$$index];
          $$renderer2.push(`<div class="rounded-xl border border-divider bg-secondary/50 p-4"><div class="flex items-start gap-3"><div${attr_class(`rounded-full p-2 ${message.role === "user" ? "bg-blue-500/10" : "bg-primary/10"}`)}><!---->`);
          getRoleIcon(message.role)?.($$renderer2, { class: `size-4 ${getRoleColor(message.role)}` });
          $$renderer2.push(`<!----></div> <div class="flex-1 space-y-1"><div class="flex items-center justify-between"><span${attr_class(`text-sm font-medium ${getRoleColor(message.role)}`)}>${escape_html(getRoleLabel(message.role))}</span> <span class="text-xs text-text-muted">${escape_html(formatTime(message.timestamp))}</span></div> <p class="text-sm leading-relaxed text-text-secondary">${escape_html(message.content)}</p></div></div></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></article>`);
  });
}
export {
  AIInsightsPanel as A,
  Refresh_ccw as R
};

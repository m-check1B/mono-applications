import { s as sanitize_props, a as spread_props, c as slot, d as store_get, u as unsubscribe_stores, e as attr_class, f as stringify, g as ensure_array_like, j as attr_style, b as bind_props } from "../../../chunks/index2.js";
import { o as onDestroy } from "../../../chunks/index-server.js";
import { a as authStore } from "../../../chunks/auth2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import { w as writable } from "../../../chunks/index.js";
import { c as contextPanelStore } from "../../../chunks/contextPanel.js";
import { l as logger } from "../../../chunks/logger.js";
import { c as derivedMode, n as notificationsStore } from "../../../chunks/notifications.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { S as Sparkles } from "../../../chunks/sparkles.js";
import { C as Calendar, T as Trash_2, k as knowledgeStore, X, P as Plus } from "../../../chunks/knowledge.js";
import { C as Chart_column } from "../../../chunks/chart-column.js";
import { S as Settings } from "../../../chunks/settings.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { a as attr } from "../../../chunks/attributes.js";
import { w as workspacesStore } from "../../../chunks/workspaces.js";
import { L as Loader_circle } from "../../../chunks/loader-circle.js";
import { C as Check } from "../../../chunks/check.js";
import { U as User, S as Send } from "../../../chunks/user.js";
import { a as api } from "../../../chunks/client.js";
import { i as isOnline, o as offlineProjects, q as queueOperation, c as clearOfflineStore, O as OFFLINE_STORES, a as offlineTimeEntries } from "../../../chunks/offlineStorage.js";
import { B as Brain } from "../../../chunks/brain.js";
import { B as Briefcase } from "../../../chunks/briefcase.js";
import "marked";
import "marked-highlight";
import "dompurify";
/* empty css                                                             */
import { T as Terminal, C as Circle_alert } from "../../../chunks/terminal.js";
function Activity($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "activity" },
    $$sanitized_props,
    {
      /**
       * @component @name Activity
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjIgMTJoLTIuNDhhMiAyIDAgMCAwLTEuOTMgMS40NmwtMi4zNSA4LjM2YS4yNS4yNSAwIDAgMS0uNDggMEw5LjI0IDIuMThhLjI1LjI1IDAgMCAwLS40OCAwbC0yLjM1IDguMzZBMiAyIDAgMCAxIDQuNDkgMTJIMiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/activity
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
function Arrow_right($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M5 12h14" }],
    ["path", { "d": "m12 5 7 7-7 7" }]
  ];
  Icon($$renderer, spread_props([
    { name: "arrow-right" },
    $$sanitized_props,
    {
      /**
       * @component @name ArrowRight
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNSAxMmgxNCIgLz4KICA8cGF0aCBkPSJtMTIgNSA3IDctNyA3IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/arrow-right
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
function Arrow_up_right($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M7 7h10v10" }],
    ["path", { "d": "M7 17 17 7" }]
  ];
  Icon($$renderer, spread_props([
    { name: "arrow-up-right" },
    $$sanitized_props,
    {
      /**
       * @component @name ArrowUpRight
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNyA3aDEwdjEwIiAvPgogIDxwYXRoIGQ9Ik03IDE3IDE3IDciIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/arrow-up-right
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
function Bell_off($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M10.268 21a2 2 0 0 0 3.464 0" }],
    [
      "path",
      {
        "d": "M17 17H4a1 1 0 0 1-.74-1.673C4.59 13.956 6 12.499 6 8a6 6 0 0 1 .258-1.742"
      }
    ],
    ["path", { "d": "m2 2 20 20" }],
    [
      "path",
      {
        "d": "M8.668 3.01A6 6 0 0 1 18 8c0 2.687.77 4.653 1.707 6.05"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "bell-off" },
    $$sanitized_props,
    {
      /**
       * @component @name BellOff
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTAuMjY4IDIxYTIgMiAwIDAgMCAzLjQ2NCAwIiAvPgogIDxwYXRoIGQ9Ik0xNyAxN0g0YTEgMSAwIDAgMS0uNzQtMS42NzNDNC41OSAxMy45NTYgNiAxMi40OTkgNiA4YTYgNiAwIDAgMSAuMjU4LTEuNzQyIiAvPgogIDxwYXRoIGQ9Im0yIDIgMjAgMjAiIC8+CiAgPHBhdGggZD0iTTguNjY4IDMuMDFBNiA2IDAgMCAxIDE4IDhjMCAyLjY4Ny43NyA0LjY1MyAxLjcwNyA2LjA1IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/bell-off
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
function Bell($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M10.268 21a2 2 0 0 0 3.464 0" }],
    [
      "path",
      {
        "d": "M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "bell" },
    $$sanitized_props,
    {
      /**
       * @component @name Bell
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTAuMjY4IDIxYTIgMiAwIDAgMCAzLjQ2NCAwIiAvPgogIDxwYXRoIGQ9Ik0zLjI2MiAxNS4zMjZBMSAxIDAgMCAwIDQgMTdoMTZhMSAxIDAgMCAwIC43NC0xLjY3M0MxOS40MSAxMy45NTYgMTggMTIuNDk5IDE4IDhBNiA2IDAgMCAwIDYgOGMwIDQuNDk5LTEuNDExIDUuOTU2LTIuNzM4IDcuMzI2IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/bell
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
function Book($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "book" },
    $$sanitized_props,
    {
      /**
       * @component @name Book
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNCAxOS41di0xNUEyLjUgMi41IDAgMCAxIDYuNSAySDE5YTEgMSAwIDAgMSAxIDF2MThhMSAxIDAgMCAxLTEgMUg2LjVhMSAxIDAgMCAxIDAtNUgyMCIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/book
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
function Chevron_left($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "m15 18-6-6 6-6" }]];
  Icon($$renderer, spread_props([
    { name: "chevron-left" },
    $$sanitized_props,
    {
      /**
       * @component @name ChevronLeft
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMTUgMTgtNi02IDYtNiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/chevron-left
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
function Chevron_right($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "m9 18 6-6-6-6" }]];
  Icon($$renderer, spread_props([
    { name: "chevron-right" },
    $$sanitized_props,
    {
      /**
       * @component @name ChevronRight
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtOSAxOCA2LTYtNi02IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/chevron-right
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
function Circle_check($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "10" }],
    ["path", { "d": "m9 12 2 2 4-4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "circle-check" },
    $$sanitized_props,
    {
      /**
       * @component @name CircleCheck
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KICA8cGF0aCBkPSJtOSAxMiAyIDIgNC00IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/circle-check
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
function Circle($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["circle", { "cx": "12", "cy": "12", "r": "10" }]];
  Icon($$renderer, spread_props([
    { name: "circle" },
    $$sanitized_props,
    {
      /**
       * @component @name Circle
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/circle
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
function Clipboard_list($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "rect",
      {
        "width": "8",
        "height": "4",
        "x": "8",
        "y": "2",
        "rx": "1",
        "ry": "1"
      }
    ],
    [
      "path",
      {
        "d": "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"
      }
    ],
    ["path", { "d": "M12 11h4" }],
    ["path", { "d": "M12 16h4" }],
    ["path", { "d": "M8 11h.01" }],
    ["path", { "d": "M8 16h.01" }]
  ];
  Icon($$renderer, spread_props([
    { name: "clipboard-list" },
    $$sanitized_props,
    {
      /**
       * @component @name ClipboardList
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI0IiB4PSI4IiB5PSIyIiByeD0iMSIgcnk9IjEiIC8+CiAgPHBhdGggZD0iTTE2IDRoMmEyIDIgMCAwIDEgMiAydjE0YTIgMiAwIDAgMS0yIDJINmEyIDIgMCAwIDEtMi0yVjZhMiAyIDAgMCAxIDItMmgyIiAvPgogIDxwYXRoIGQ9Ik0xMiAxMWg0IiAvPgogIDxwYXRoIGQ9Ik0xMiAxNmg0IiAvPgogIDxwYXRoIGQ9Ik04IDExaC4wMSIgLz4KICA8cGF0aCBkPSJNOCAxNmguMDEiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/clipboard-list
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
function Database($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["ellipse", { "cx": "12", "cy": "5", "rx": "9", "ry": "3" }],
    ["path", { "d": "M3 5V19A9 3 0 0 0 21 19V5" }],
    ["path", { "d": "M3 12A9 3 0 0 0 21 12" }]
  ];
  Icon($$renderer, spread_props([
    { name: "database" },
    $$sanitized_props,
    {
      /**
       * @component @name Database
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8ZWxsaXBzZSBjeD0iMTIiIGN5PSI1IiByeD0iOSIgcnk9IjMiIC8+CiAgPHBhdGggZD0iTTMgNVYxOUE5IDMgMCAwIDAgMjEgMTlWNSIgLz4KICA8cGF0aCBkPSJNMyAxMkE5IDMgMCAwIDAgMjEgMTIiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/database
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
function Dollar_sign($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["line", { "x1": "12", "x2": "12", "y1": "2", "y2": "22" }],
    [
      "path",
      { "d": "M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "dollar-sign" },
    $$sanitized_props,
    {
      /**
       * @component @name DollarSign
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8bGluZSB4MT0iMTIiIHgyPSIxMiIgeTE9IjIiIHkyPSIyMiIgLz4KICA8cGF0aCBkPSJNMTcgNUg5LjVhMy41IDMuNSAwIDAgMCAwIDdoNWEzLjUgMy41IDAgMCAxIDAgN0g2IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/dollar-sign
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
function Ellipsis_vertical($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "1" }],
    ["circle", { "cx": "12", "cy": "5", "r": "1" }],
    ["circle", { "cx": "12", "cy": "19", "r": "1" }]
  ];
  Icon($$renderer, spread_props([
    { name: "ellipsis-vertical" },
    $$sanitized_props,
    {
      /**
       * @component @name EllipsisVertical
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxIiAvPgogIDxjaXJjbGUgY3g9IjEyIiBjeT0iNSIgcj0iMSIgLz4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjE5IiByPSIxIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/ellipsis-vertical
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
function External_link($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M15 3h6v6" }],
    ["path", { "d": "M10 14 21 3" }],
    [
      "path",
      {
        "d": "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "external-link" },
    $$sanitized_props,
    {
      /**
       * @component @name ExternalLink
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTUgM2g2djYiIC8+CiAgPHBhdGggZD0iTTEwIDE0IDIxIDMiIC8+CiAgPHBhdGggZD0iTTE4IDEzdjZhMiAyIDAgMCAxLTIgMkg1YTIgMiAwIDAgMS0yLTJWOGEyIDIgMCAwIDEgMi0yaDYiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/external-link
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
function File_text($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"
      }
    ],
    ["path", { "d": "M14 2v4a2 2 0 0 0 2 2h4" }],
    ["path", { "d": "M10 9H8" }],
    ["path", { "d": "M16 13H8" }],
    ["path", { "d": "M16 17H8" }]
  ];
  Icon($$renderer, spread_props([
    { name: "file-text" },
    $$sanitized_props,
    {
      /**
       * @component @name FileText
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTUgMkg2YTIgMiAwIDAgMC0yIDJ2MTZhMiAyIDAgMCAwIDIgMmgxMmEyIDIgMCAwIDAgMi0yVjdaIiAvPgogIDxwYXRoIGQ9Ik0xNCAydjRhMiAyIDAgMCAwIDIgMmg0IiAvPgogIDxwYXRoIGQ9Ik0xMCA5SDgiIC8+CiAgPHBhdGggZD0iTTE2IDEzSDgiIC8+CiAgPHBhdGggZD0iTTE2IDE3SDgiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/file-text
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
function Folder_kanban($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"
      }
    ],
    ["path", { "d": "M8 10v4" }],
    ["path", { "d": "M12 10v2" }],
    ["path", { "d": "M16 10v6" }]
  ];
  Icon($$renderer, spread_props([
    { name: "folder-kanban" },
    $$sanitized_props,
    {
      /**
       * @component @name FolderKanban
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNNCAyMGgxNmEyIDIgMCAwIDAgMi0yVjhhMiAyIDAgMCAwLTItMmgtNy45M2EyIDIgMCAwIDEtMS42Ni0uOWwtLjgyLTEuMkEyIDIgMCAwIDAgNy45MyAzSDRhMiAyIDAgMCAwLTIgMnYxM2MwIDEuMS45IDIgMiAyWiIgLz4KICA8cGF0aCBkPSJNOCAxMHY0IiAvPgogIDxwYXRoIGQ9Ik0xMiAxMHYyIiAvPgogIDxwYXRoIGQ9Ik0xNiAxMHY2IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/folder-kanban
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
function Folder($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "folder" },
    $$sanitized_props,
    {
      /**
       * @component @name Folder
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjAgMjBhMiAyIDAgMCAwIDItMlY4YTIgMiAwIDAgMC0yLTJoLTcuOWEyIDIgMCAwIDEtMS42OS0uOUw5LjYgMy45QTIgMiAwIDAgMCA3LjkzIDNINGEyIDIgMCAwIDAtMiAydjEzYTIgMiAwIDAgMCAyIDJaIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/folder
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
function Funnel($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "funnel" },
    $$sanitized_props,
    {
      /**
       * @component @name Funnel
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTAgMjBhMSAxIDAgMCAwIC41NTMuODk1bDIgMUExIDEgMCAwIDAgMTQgMjF2LTdhMiAyIDAgMCAxIC41MTctMS4zNDFMMjEuNzQgNC42N0ExIDEgMCAwIDAgMjEgM0gzYTEgMSAwIDAgMC0uNzQyIDEuNjdsNy4yMjUgNy45ODlBMiAyIDAgMCAxIDEwIDE0eiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/funnel
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
function Ghost($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M9 10h.01" }],
    ["path", { "d": "M15 10h.01" }],
    [
      "path",
      {
        "d": "M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "ghost" },
    $$sanitized_props,
    {
      /**
       * @component @name Ghost
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNOSAxMGguMDEiIC8+CiAgPHBhdGggZD0iTTE1IDEwaC4wMSIgLz4KICA8cGF0aCBkPSJNMTIgMmE4IDggMCAwIDAtOCA4djEybDMtMyAyLjUgMi41TDEyIDE5bDIuNSAyLjVMMTcgMTlsMyAzVjEwYTggOCAwIDAgMC04LTh6IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/ghost
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
function Grip_vertical($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "9", "cy": "12", "r": "1" }],
    ["circle", { "cx": "9", "cy": "5", "r": "1" }],
    ["circle", { "cx": "9", "cy": "19", "r": "1" }],
    ["circle", { "cx": "15", "cy": "12", "r": "1" }],
    ["circle", { "cx": "15", "cy": "5", "r": "1" }],
    ["circle", { "cx": "15", "cy": "19", "r": "1" }]
  ];
  Icon($$renderer, spread_props([
    { name: "grip-vertical" },
    $$sanitized_props,
    {
      /**
       * @component @name GripVertical
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSI5IiBjeT0iMTIiIHI9IjEiIC8+CiAgPGNpcmNsZSBjeD0iOSIgY3k9IjUiIHI9IjEiIC8+CiAgPGNpcmNsZSBjeD0iOSIgY3k9IjE5IiByPSIxIiAvPgogIDxjaXJjbGUgY3g9IjE1IiBjeT0iMTIiIHI9IjEiIC8+CiAgPGNpcmNsZSBjeD0iMTUiIGN5PSI1IiByPSIxIiAvPgogIDxjaXJjbGUgY3g9IjE1IiBjeT0iMTkiIHI9IjEiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/grip-vertical
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
function Key($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"
      }
    ],
    ["path", { "d": "m21 2-9.6 9.6" }],
    ["circle", { "cx": "7.5", "cy": "15.5", "r": "5.5" }]
  ];
  Icon($$renderer, spread_props([
    { name: "key" },
    $$sanitized_props,
    {
      /**
       * @component @name Key
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMTUuNSA3LjUgMi4zIDIuM2ExIDEgMCAwIDAgMS40IDBsMi4xLTIuMWExIDEgMCAwIDAgMC0xLjRMMTkgNCIgLz4KICA8cGF0aCBkPSJtMjEgMi05LjYgOS42IiAvPgogIDxjaXJjbGUgY3g9IjcuNSIgY3k9IjE1LjUiIHI9IjUuNSIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/key
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
function Link($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"
      }
    ],
    [
      "path",
      {
        "d": "M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "link" },
    $$sanitized_props,
    {
      /**
       * @component @name Link
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTAgMTNhNSA1IDAgMCAwIDcuNTQuNTRsMy0zYTUgNSAwIDAgMC03LjA3LTcuMDdsLTEuNzIgMS43MSIgLz4KICA8cGF0aCBkPSJNMTQgMTFhNSA1IDAgMCAwLTcuNTQtLjU0bC0zIDNhNSA1IDAgMCAwIDcuMDcgNy4wN2wxLjcxLTEuNzEiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/link
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
function Lock($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "rect",
      {
        "width": "18",
        "height": "11",
        "x": "3",
        "y": "11",
        "rx": "2",
        "ry": "2"
      }
    ],
    ["path", { "d": "M7 11V7a5 5 0 0 1 10 0v4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "lock" },
    $$sanitized_props,
    {
      /**
       * @component @name Lock
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB3aWR0aD0iMTgiIGhlaWdodD0iMTEiIHg9IjMiIHk9IjExIiByeD0iMiIgcnk9IjIiIC8+CiAgPHBhdGggZD0iTTcgMTFWN2E1IDUgMCAwIDEgMTAgMHY0IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/lock
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
function Monitor($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "rect",
      { "width": "20", "height": "14", "x": "2", "y": "3", "rx": "2" }
    ],
    ["line", { "x1": "8", "x2": "16", "y1": "21", "y2": "21" }],
    ["line", { "x1": "12", "x2": "12", "y1": "17", "y2": "21" }]
  ];
  Icon($$renderer, spread_props([
    { name: "monitor" },
    $$sanitized_props,
    {
      /**
       * @component @name Monitor
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB3aWR0aD0iMjAiIGhlaWdodD0iMTQiIHg9IjIiIHk9IjMiIHJ4PSIyIiAvPgogIDxsaW5lIHgxPSI4IiB4Mj0iMTYiIHkxPSIyMSIgeTI9IjIxIiAvPgogIDxsaW5lIHgxPSIxMiIgeDI9IjEyIiB5MT0iMTciIHkyPSIyMSIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/monitor
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
function Moon($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" }]];
  Icon($$renderer, spread_props([
    { name: "moon" },
    $$sanitized_props,
    {
      /**
       * @component @name Moon
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgM2E2IDYgMCAwIDAgOSA5IDkgOSAwIDEgMS05LTlaIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/moon
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
function Octagon_alert($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M12 16h.01" }],
    ["path", { "d": "M12 8v4" }],
    [
      "path",
      {
        "d": "M15.312 2a2 2 0 0 1 1.414.586l4.688 4.688A2 2 0 0 1 22 8.688v6.624a2 2 0 0 1-.586 1.414l-4.688 4.688a2 2 0 0 1-1.414.586H8.688a2 2 0 0 1-1.414-.586l-4.688-4.688A2 2 0 0 1 2 15.312V8.688a2 2 0 0 1 .586-1.414l4.688-4.688A2 2 0 0 1 8.688 2z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "octagon-alert" },
    $$sanitized_props,
    {
      /**
       * @component @name OctagonAlert
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgMTZoLjAxIiAvPgogIDxwYXRoIGQ9Ik0xMiA4djQiIC8+CiAgPHBhdGggZD0iTTE1LjMxMiAyYTIgMiAwIDAgMSAxLjQxNC41ODZsNC42ODggNC42ODhBMiAyIDAgMCAxIDIyIDguNjg4djYuNjI0YTIgMiAwIDAgMS0uNTg2IDEuNDE0bC00LjY4OCA0LjY4OGEyIDIgMCAwIDEtMS40MTQuNTg2SDguNjg4YTIgMiAwIDAgMS0xLjQxNC0uNTg2bC00LjY4OC00LjY4OEEyIDIgMCAwIDEgMiAxNS4zMTJWOC42ODhhMiAyIDAgMCAxIC41ODYtMS40MTRsNC42ODgtNC42ODhBMiAyIDAgMCAxIDguNjg4IDJ6IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/octagon-alert
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
function Paperclip($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M13.234 20.252 21 12.3" }],
    [
      "path",
      {
        "d": "m16 6-8.414 8.586a2 2 0 0 0 0 2.828 2 2 0 0 0 2.828 0l8.414-8.586a4 4 0 0 0 0-5.656 4 4 0 0 0-5.656 0l-8.415 8.585a6 6 0 1 0 8.486 8.486"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "paperclip" },
    $$sanitized_props,
    {
      /**
       * @component @name Paperclip
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTMuMjM0IDIwLjI1MiAyMSAxMi4zIiAvPgogIDxwYXRoIGQ9Im0xNiA2LTguNDE0IDguNTg2YTIgMiAwIDAgMCAwIDIuODI4IDIgMiAwIDAgMCAyLjgyOCAwbDguNDE0LTguNTg2YTQgNCAwIDAgMCAwLTUuNjU2IDQgNCAwIDAgMC01LjY1NiAwbC04LjQxNSA4LjU4NWE2IDYgMCAxIDAgOC40ODYgOC40ODYiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/paperclip
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
function Play($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["polygon", { "points": "6 3 20 12 6 21 6 3" }]];
  Icon($$renderer, spread_props([
    { name: "play" },
    $$sanitized_props,
    {
      /**
       * @component @name Play
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cG9seWdvbiBwb2ludHM9IjYgMyAyMCAxMiA2IDIxIDYgMyIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/play
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
function Refresh_cw($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      { "d": "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" }
    ],
    ["path", { "d": "M21 3v5h-5" }],
    [
      "path",
      { "d": "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" }
    ],
    ["path", { "d": "M8 16H3v5" }]
  ];
  Icon($$renderer, spread_props([
    { name: "refresh-cw" },
    $$sanitized_props,
    {
      /**
       * @component @name RefreshCw
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMyAxMmE5IDkgMCAwIDEgOS05IDkuNzUgOS43NSAwIDAgMSA2Ljc0IDIuNzRMMjEgOCIgLz4KICA8cGF0aCBkPSJNMjEgM3Y1aC01IiAvPgogIDxwYXRoIGQ9Ik0yMSAxMmE5IDkgMCAwIDEtOSA5IDkuNzUgOS43NSAwIDAgMS02Ljc0LTIuNzRMMyAxNiIgLz4KICA8cGF0aCBkPSJNOCAxNkgzdjUiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/refresh-cw
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
function Save($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"
      }
    ],
    ["path", { "d": "M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7" }],
    ["path", { "d": "M7 3v4a1 1 0 0 0 1 1h7" }]
  ];
  Icon($$renderer, spread_props([
    { name: "save" },
    $$sanitized_props,
    {
      /**
       * @component @name Save
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTUuMiAzYTIgMiAwIDAgMSAxLjQuNmwzLjggMy44YTIgMiAwIDAgMSAuNiAxLjRWMTlhMiAyIDAgMCAxLTIgMkg1YTIgMiAwIDAgMS0yLTJWNWEyIDIgMCAwIDEgMi0yeiIgLz4KICA8cGF0aCBkPSJNMTcgMjF2LTdhMSAxIDAgMCAwLTEtMUg4YTEgMSAwIDAgMC0xIDF2NyIgLz4KICA8cGF0aCBkPSJNNyAzdjRhMSAxIDAgMCAwIDEgMWg3IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/save
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
function Search($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "11", "cy": "11", "r": "8" }],
    ["path", { "d": "m21 21-4.3-4.3" }]
  ];
  Icon($$renderer, spread_props([
    { name: "search" },
    $$sanitized_props,
    {
      /**
       * @component @name Search
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMSIgY3k9IjExIiByPSI4IiAvPgogIDxwYXRoIGQ9Im0yMSAyMS00LjMtNC4zIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/search
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
function Server($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "rect",
      {
        "width": "20",
        "height": "8",
        "x": "2",
        "y": "2",
        "rx": "2",
        "ry": "2"
      }
    ],
    [
      "rect",
      {
        "width": "20",
        "height": "8",
        "x": "2",
        "y": "14",
        "rx": "2",
        "ry": "2"
      }
    ],
    ["line", { "x1": "6", "x2": "6.01", "y1": "6", "y2": "6" }],
    ["line", { "x1": "6", "x2": "6.01", "y1": "18", "y2": "18" }]
  ];
  Icon($$renderer, spread_props([
    { name: "server" },
    $$sanitized_props,
    {
      /**
       * @component @name Server
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB3aWR0aD0iMjAiIGhlaWdodD0iOCIgeD0iMiIgeT0iMiIgcng9IjIiIHJ5PSIyIiAvPgogIDxyZWN0IHdpZHRoPSIyMCIgaGVpZ2h0PSI4IiB4PSIyIiB5PSIxNCIgcng9IjIiIHJ5PSIyIiAvPgogIDxsaW5lIHgxPSI2IiB4Mj0iNi4wMSIgeTE9IjYiIHkyPSI2IiAvPgogIDxsaW5lIHgxPSI2IiB4Mj0iNi4wMSIgeTE9IjE4IiB5Mj0iMTgiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/server
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
function Square($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "rect",
      { "width": "18", "height": "18", "x": "3", "y": "3", "rx": "2" }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "square" },
    $$sanitized_props,
    {
      /**
       * @component @name Square
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cmVjdCB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHg9IjMiIHk9IjMiIHJ4PSIyIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/square
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
function Sun($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["circle", { "cx": "12", "cy": "12", "r": "4" }],
    ["path", { "d": "M12 2v2" }],
    ["path", { "d": "M12 20v2" }],
    ["path", { "d": "m4.93 4.93 1.41 1.41" }],
    ["path", { "d": "m17.66 17.66 1.41 1.41" }],
    ["path", { "d": "M2 12h2" }],
    ["path", { "d": "M20 12h2" }],
    ["path", { "d": "m6.34 17.66-1.41 1.41" }],
    ["path", { "d": "m19.07 4.93-1.41 1.41" }]
  ];
  Icon($$renderer, spread_props([
    { name: "sun" },
    $$sanitized_props,
    {
      /**
       * @component @name Sun
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSI0IiAvPgogIDxwYXRoIGQ9Ik0xMiAydjIiIC8+CiAgPHBhdGggZD0iTTEyIDIwdjIiIC8+CiAgPHBhdGggZD0ibTQuOTMgNC45MyAxLjQxIDEuNDEiIC8+CiAgPHBhdGggZD0ibTE3LjY2IDE3LjY2IDEuNDEgMS40MSIgLz4KICA8cGF0aCBkPSJNMiAxMmgyIiAvPgogIDxwYXRoIGQ9Ik0yMCAxMmgyIiAvPgogIDxwYXRoIGQ9Im02LjM0IDE3LjY2LTEuNDEgMS40MSIgLz4KICA8cGF0aCBkPSJtMTkuMDcgNC45My0xLjQxIDEuNDEiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/sun
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
function Tag($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"
      }
    ],
    [
      "circle",
      { "cx": "7.5", "cy": "7.5", "r": ".5", "fill": "currentColor" }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "tag" },
    $$sanitized_props,
    {
      /**
       * @component @name Tag
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIuNTg2IDIuNTg2QTIgMiAwIDAgMCAxMS4xNzIgMkg0YTIgMiAwIDAgMC0yIDJ2Ny4xNzJhMiAyIDAgMCAwIC41ODYgMS40MTRsOC43MDQgOC43MDRhMi40MjYgMi40MjYgMCAwIDAgMy40MiAwbDYuNTgtNi41OGEyLjQyNiAyLjQyNiAwIDAgMCAwLTMuNDJ6IiAvPgogIDxjaXJjbGUgY3g9IjcuNSIgY3k9IjcuNSIgcj0iLjUiIGZpbGw9ImN1cnJlbnRDb2xvciIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/tag
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
function Trending_up($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["polyline", { "points": "22 7 13.5 15.5 8.5 10.5 2 17" }],
    ["polyline", { "points": "16 7 22 7 22 13" }]
  ];
  Icon($$renderer, spread_props([
    { name: "trending-up" },
    $$sanitized_props,
    {
      /**
       * @component @name TrendingUp
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cG9seWxpbmUgcG9pbnRzPSIyMiA3IDEzLjUgMTUuNSA4LjUgMTAuNSAyIDE3IiAvPgogIDxwb2x5bGluZSBwb2ludHM9IjE2IDcgMjIgNyAyMiAxMyIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/trending-up
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
function Triangle_alert($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"
      }
    ],
    ["path", { "d": "M12 9v4" }],
    ["path", { "d": "M12 17h.01" }]
  ];
  Icon($$renderer, spread_props([
    { name: "triangle-alert" },
    $$sanitized_props,
    {
      /**
       * @component @name TriangleAlert
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMjEuNzMgMTgtOC0xNGEyIDIgMCAwIDAtMy40OCAwbC04IDE0QTIgMiAwIDAgMCA0IDIxaDE2YTIgMiAwIDAgMCAxLjczLTMiIC8+CiAgPHBhdGggZD0iTTEyIDl2NCIgLz4KICA8cGF0aCBkPSJNMTIgMTdoLjAxIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/triangle-alert
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
function Wand_sparkles($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72"
      }
    ],
    ["path", { "d": "m14 7 3 3" }],
    ["path", { "d": "M5 6v4" }],
    ["path", { "d": "M19 14v4" }],
    ["path", { "d": "M10 2v2" }],
    ["path", { "d": "M7 8H3" }],
    ["path", { "d": "M21 16h-4" }],
    ["path", { "d": "M11 3H9" }]
  ];
  Icon($$renderer, spread_props([
    { name: "wand-sparkles" },
    $$sanitized_props,
    {
      /**
       * @component @name WandSparkles
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMjEuNjQgMy42NC0xLjI4LTEuMjhhMS4yMSAxLjIxIDAgMCAwLTEuNzIgMEwyLjM2IDE4LjY0YTEuMjEgMS4yMSAwIDAgMCAwIDEuNzJsMS4yOCAxLjI4YTEuMiAxLjIgMCAwIDAgMS43MiAwTDIxLjY0IDUuMzZhMS4yIDEuMiAwIDAgMCAwLTEuNzIiIC8+CiAgPHBhdGggZD0ibTE0IDcgMyAzIiAvPgogIDxwYXRoIGQ9Ik01IDZ2NCIgLz4KICA8cGF0aCBkPSJNMTkgMTR2NCIgLz4KICA8cGF0aCBkPSJNMTAgMnYyIiAvPgogIDxwYXRoIGQ9Ik03IDhIMyIgLz4KICA8cGF0aCBkPSJNMjEgMTZoLTQiIC8+CiAgPHBhdGggZD0iTTExIDNIOSIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/wand-sparkles
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
function createToastStore() {
  const { subscribe, update } = writable([]);
  function push(message, type = "info", timeout = 4e3, action) {
    const id = crypto.randomUUID?.() || String(Date.now());
    const toast2 = { id, type, message, timeout, action };
    update((list) => [...list, toast2]);
    if (timeout > 0) {
      setTimeout(() => dismiss(id), timeout);
    }
  }
  function dismiss(id) {
    update((list) => list.filter((t) => t.id !== id));
  }
  return {
    subscribe,
    push,
    success: (message, timeout, action) => push(message, "success", timeout, action),
    info: (message, timeout, action) => push(message, "info", timeout, action),
    warning: (message, timeout, action) => push(message, "warning", timeout, action),
    error: (message, timeout, action) => push(message, "error", timeout, action),
    dismiss,
    // ✨ Gap #12: Convenience methods for common patterns
    successWithUndo: (message, onUndo, timeout = 6e3) => {
      push(message, "success", timeout, {
        label: "Undo",
        onClick: onUndo
      });
    },
    errorWithRetry: (message, onRetry, timeout = 8e3) => {
      push(message, "error", timeout, {
        label: "Retry",
        onClick: onRetry
      });
    }
  };
}
const toast = createToastStore();
function ThemeToggle($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    $$renderer2.push(`<div class="relative"><button class="p-2 hover:bg-accent border-2 border-transparent hover:border-black dark:hover:border-white flex items-center justify-center" title="Toggle Theme">`);
    if (store_get($$store_subs ??= {}, "$mode", derivedMode) === "light") {
      $$renderer2.push("<!--[-->");
      Sun($$renderer2, { class: "w-5 h-5" });
    } else {
      $$renderer2.push("<!--[!-->");
      if (store_get($$store_subs ??= {}, "$mode", derivedMode) === "dark") {
        $$renderer2.push("<!--[-->");
        Moon($$renderer2, { class: "w-5 h-5" });
      } else {
        $$renderer2.push("<!--[!-->");
        Monitor($$renderer2, { class: "w-5 h-5" });
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></button> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function AssistantShell($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { user = null, children } = $$props;
    const quickActions = [
      {
        icon: Folder_kanban,
        label: "Projects",
        action: () => contextPanelStore.open("projects")
      },
      {
        icon: Calendar,
        label: "Calendar",
        action: () => contextPanelStore.open("calendar")
      },
      {
        icon: Chart_column,
        label: "Analytics",
        action: () => contextPanelStore.open("analytics")
      },
      {
        icon: Settings,
        label: "Settings",
        action: () => contextPanelStore.open("settings")
      }
    ];
    $$renderer2.push(`<div class="min-h-screen bg-neutral-100 dark:bg-neutral-900 flex items-center justify-center p-0 md:p-4 lg:p-8"><div class="w-full h-screen md:h-[calc(100vh-4rem)] lg:h-[calc(100vh-8rem)] max-w-[1920px] bg-background text-foreground relative flex flex-col md:border-2 md:border-black md:dark:border-white md:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] md:dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] overflow-hidden"><header class="flex-shrink-0 flex items-center justify-between p-4 border-b-2 border-black dark:border-white bg-card z-10"><div class="flex items-center gap-3"><div class="w-8 h-8 border-2 border-black dark:border-white bg-primary text-primary-foreground flex items-center justify-center font-black text-sm">${escape_html(user?.full_name?.charAt(0).toUpperCase() || "F")}</div> <div class="font-black text-xl uppercase tracking-tighter">Focus <span class="text-muted-foreground text-sm font-normal normal-case">by Kraliki</span></div> `);
    if (!user?.isPremium) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<a href="/dashboard/settings?tab=billing"${attr_class(`hidden md:flex items-center gap-1.5 px-3 py-1 ${stringify(user?.academyStatus === "WAITLIST" ? "bg-secondary text-muted-foreground" : "bg-terminal-green text-black")} text-[10px] font-black uppercase tracking-widest border-2 border-black ${stringify(user?.academyStatus === "WAITLIST" ? "" : "animate-pulse hover:animate-none")} transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[1px] active:translate-y-[1px]`)}>`);
      Sparkles($$renderer2, { class: "w-3 h-3" });
      $$renderer2.push(`<!----> ${escape_html(user?.academyStatus === "WAITLIST" ? "Waitlisted" : "Join Academy (Jan 1)")}</a>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="flex items-center gap-1"><!--[-->`);
    const each_array = ensure_array_like(quickActions);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let { icon: IconComponent, label, action } = each_array[$$index];
      $$renderer2.push(`<button type="button" class="p-2 hover:bg-accent border-2 border-transparent hover:border-black dark:hover:border-white"${attr("title", label)}><!---->`);
      IconComponent($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></button>`);
    }
    $$renderer2.push(`<!--]--> <div class="w-px h-6 bg-border mx-1"></div> `);
    ThemeToggle($$renderer2);
    $$renderer2.push(`<!----> <button type="button" class="p-2 hover:bg-accent border-2 border-transparent hover:border-black dark:hover:border-white" title="Log out"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-log-out"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" x2="9" y1="12" y2="12"></line></svg></button></div></header> <main class="flex-1 overflow-hidden bg-background relative">`);
    children($$renderer2);
    $$renderer2.push(`<!----></main></div></div>`);
  });
}
function _defineProperty(obj, key, value) {
  if (key in obj) {
    Object.defineProperty(obj, key, {
      value,
      enumerable: true,
      configurable: true,
      writable: true
    });
  } else {
    obj[key] = value;
  }
  return obj;
}
var FEATURE_FLAG_NAMES = Object.freeze({
  // This flag exists as a workaround for issue 454 (basically a browser bug) - seems like these rect values take time to update when in grid layout. Setting it to true can cause strange behaviour in the REPL for non-grid zones, see issue 470
  USE_COMPUTED_STYLE_INSTEAD_OF_BOUNDING_RECT: "USE_COMPUTED_STYLE_INSTEAD_OF_BOUNDING_RECT"
});
_defineProperty({}, FEATURE_FLAG_NAMES.USE_COMPUTED_STYLE_INSTEAD_OF_BOUNDING_RECT, false);
var _ID_TO_INSTRUCTION;
var INSTRUCTION_IDs$1 = {
  DND_ZONE_ACTIVE: "dnd-zone-active",
  DND_ZONE_DRAG_DISABLED: "dnd-zone-drag-disabled"
};
_ID_TO_INSTRUCTION = {}, _defineProperty(_ID_TO_INSTRUCTION, INSTRUCTION_IDs$1.DND_ZONE_ACTIVE, "Tab to one the items and press space-bar or enter to start dragging it"), _defineProperty(_ID_TO_INSTRUCTION, INSTRUCTION_IDs$1.DND_ZONE_DRAG_DISABLED, "This is a disabled drag and drop list"), _ID_TO_INSTRUCTION;
function TasksView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let searchQuery = "";
    let filterStatus = "ALL";
    let filterPriority = "ALL";
    let displayedTasks = [];
    let items = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).items;
    store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    let isLoading = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).isLoading;
    let workspaceState = store_get($$store_subs ??= {}, "$workspacesStore", workspacesStore);
    workspaceState.members;
    let tasks = items.filter((item) => {
      item.item_metadata || {};
      return true;
    });
    function getPriorityColor(priority) {
      switch (priority) {
        case "HIGH":
          return "bg-destructive text-destructive-foreground";
        case "MEDIUM":
          return "bg-accent text-accent-foreground";
        default:
          return "bg-muted text-muted-foreground";
      }
    }
    function formatDueDate(dateStr) {
      if (!dateStr) return "";
      return new Date(dateStr).toLocaleDateString();
    }
    $$renderer2.push(`<div class="h-full flex flex-col relative overflow-hidden bg-background"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex flex-col gap-4 bg-background z-10"><div class="flex items-center gap-3"><div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">`);
    Clipboard_list($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></div> <div><h2 class="text-2xl font-black uppercase tracking-tighter">Tasks</h2> <p class="text-sm font-bold text-muted-foreground">Create via AI · Manage via gestures</p></div></div> <div class="flex flex-wrap gap-3"><div class="flex-1 min-w-[200px] relative">`);
    Search($$renderer2, {
      class: "absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground z-10"
    });
    $$renderer2.push(`<!----> <input type="text"${attr("value", searchQuery)} placeholder="Search tasks..." class="brutal-input pl-10"/></div> `);
    $$renderer2.select(
      {
        value: filterStatus,
        class: "brutal-input w-auto min-w-[140px] appearance-none cursor-pointer"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "ALL" }, ($$renderer4) => {
          $$renderer4.push(`All Status`);
        });
        $$renderer3.option({ value: "PENDING" }, ($$renderer4) => {
          $$renderer4.push(`Pending`);
        });
        $$renderer3.option({ value: "IN_PROGRESS" }, ($$renderer4) => {
          $$renderer4.push(`In Progress`);
        });
        $$renderer3.option({ value: "COMPLETED" }, ($$renderer4) => {
          $$renderer4.push(`Completed`);
        });
      }
    );
    $$renderer2.push(` `);
    $$renderer2.select(
      {
        value: filterPriority,
        class: "brutal-input w-auto min-w-[140px] appearance-none cursor-pointer"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: "ALL" }, ($$renderer4) => {
          $$renderer4.push(`All Priority`);
        });
        $$renderer3.option({ value: "HIGH" }, ($$renderer4) => {
          $$renderer4.push(`High`);
        });
        $$renderer3.option({ value: "MEDIUM" }, ($$renderer4) => {
          $$renderer4.push(`Medium`);
        });
        $$renderer3.option({ value: "LOW" }, ($$renderer4) => {
          $$renderer4.push(`Low`);
        });
      }
    );
    $$renderer2.push(`</div></div> <div class="flex-1 overflow-y-auto p-6 bg-grid-pattern">`);
    if (isLoading && tasks.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="h-full flex items-center justify-center"><div class="flex flex-col items-center gap-4">`);
      Loader_circle($$renderer2, { class: "w-12 h-12 animate-spin text-primary" });
      $$renderer2.push(`<!----> <p class="font-black uppercase tracking-widest text-sm">Synchronizing...</p></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (displayedTasks.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="h-full flex flex-col items-center justify-center text-center p-8"><div class="brutal-card p-12 max-w-md bg-background flex flex-col items-center gap-6"><div class="p-4 bg-secondary border-2 border-border">`);
        Clipboard_list($$renderer2, { class: "w-16 h-16 text-muted-foreground" });
        $$renderer2.push(`<!----></div> <div class="space-y-2"><h3 class="text-3xl font-black uppercase tracking-tighter">Void Detected</h3> <p class="text-sm font-bold uppercase text-muted-foreground tracking-wide">No tasks match your current configuration or the queue is empty.</p></div> `);
        {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="p-3 bg-red-100 dark:bg-red-900/30 border-2 border-red-500 text-red-500 text-xs font-bold uppercase">CRITICAL: "Tasks" item type not found in database.</div>`);
        }
        $$renderer2.push(`<!--]--></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="space-y-4"><!--[-->`);
        const each_array = ensure_array_like(displayedTasks);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let task = each_array[$$index];
          $$renderer2.push(`<div role="button" tabindex="0" class="brutal-card p-4 flex gap-4 group hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all outline-none focus:ring-2 focus:ring-terminal-green active:translate-x-[4px] active:translate-y-[4px] active:shadow-none"><div class="hidden md:flex items-center justify-center cursor-grab active:cursor-grabbing text-muted-foreground hover:text-foreground border-r-2 border-border/10 pr-2">`);
          Grip_vertical($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></div> <button${attr_class(`mt-1 w-7 h-7 flex-shrink-0 border-2 border-black dark:border-white flex items-center justify-center hover:bg-terminal-green transition-colors ${stringify(task.completed ? "bg-terminal-green text-black" : "bg-card")}`)} tabindex="-1">`);
          if (task.completed) {
            $$renderer2.push("<!--[-->");
            Check($$renderer2, { class: "w-5 h-5 stroke-[3]" });
          } else {
            $$renderer2.push("<!--[!-->");
            if (task.item_metadata?.status === "IN_PROGRESS") {
              $$renderer2.push("<!--[-->");
              $$renderer2.push(`<div class="w-3 h-3 bg-primary animate-pulse"></div>`);
            } else {
              $$renderer2.push("<!--[!-->");
            }
            $$renderer2.push(`<!--]-->`);
          }
          $$renderer2.push(`<!--]--></button> <div class="flex-1 min-w-0 space-y-3 select-none"><div class="flex items-start justify-between gap-4"><h3${attr_class(`text-xl font-black uppercase leading-tight tracking-tight ${stringify(task.completed ? "line-through opacity-40" : "")}`)}>${escape_html(task.title)}</h3> <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity"><button class="p-2 brutal-btn bg-white dark:bg-black !shadow-none hover:!shadow-brutal-sm scale-90" title="Ask Assistant" tabindex="-1">`);
          Sparkles($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button> <button class="p-2 brutal-btn bg-white dark:bg-black hover:bg-destructive hover:text-white !shadow-none hover:!shadow-brutal-sm scale-90" title="Delete" tabindex="-1">`);
          Trash_2($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div></div> `);
          if (task.content) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<p class="text-sm font-medium text-muted-foreground line-clamp-2 leading-relaxed">${escape_html(task.content)}</p>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <div class="flex flex-wrap items-center gap-3 text-[10px] font-black uppercase tracking-widest"><span${attr_class(`px-2 py-0.5 border-2 border-border ${stringify(getPriorityColor(task.item_metadata?.priority))}`)}>${escape_html(task.item_metadata?.priority || "MEDIUM")}</span> `);
          if (task.item_metadata?.dueDate) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="flex items-center gap-1.5 px-2 py-0.5 border-2 border-border bg-secondary">`);
            Calendar($$renderer2, { class: "w-3.5 h-3.5" });
            $$renderer2.push(`<!----> ${escape_html(formatDueDate(task.item_metadata.dueDate))}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (task.item_metadata?.assignedUserId) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="flex items-center gap-1.5 px-2 py-0.5 border-2 border-border bg-secondary">`);
            User($$renderer2, { class: "w-3.5 h-3.5" });
            $$renderer2.push(`<!----> Assigned</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState$6 = {
  projects: [],
  templates: [],
  isLoading: false,
  error: null,
  currentProject: null,
  currentProjectProgress: null
};
function createProjectsStore() {
  const { subscribe, set, update } = writable(initialState$6);
  return {
    subscribe,
    async loadProjects() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        if (!isOnline()) {
          const projects2 = await offlineProjects.getAll();
          update((state) => ({
            ...state,
            projects: projects2,
            isLoading: false
          }));
          return { success: true, projects: projects2 };
        }
        const response = await api.projects.list();
        const projects = response.projects || [];
        await clearOfflineStore(OFFLINE_STORES.PROJECTS);
        for (const project of projects) {
          await offlineProjects.save(project);
        }
        update((state) => ({
          ...state,
          projects,
          isLoading: false
        }));
        return { success: true, projects };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load projects";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async createProject(projectData) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          const offlineProject = {
            id: crypto.randomUUID?.() || `offline-${Date.now()}`,
            name: projectData.name,
            description: projectData.description,
            color: projectData.color,
            icon: projectData.icon,
            userId: "offline",
            createdAt: now,
            updatedAt: now
          };
          await offlineProjects.save(offlineProject);
          await queueOperation({
            type: "create",
            entity: "project",
            data: projectData,
            endpoint: "/projects"
          });
          update((state) => ({
            ...state,
            projects: [offlineProject, ...state.projects],
            isLoading: false
          }));
          return { success: true, project: offlineProject };
        }
        const newProject = await api.projects.create(projectData);
        await offlineProjects.save(newProject);
        update((state) => ({
          ...state,
          projects: [newProject, ...state.projects],
          isLoading: false
        }));
        return { success: true, project: newProject };
      } catch (error) {
        const errorMessage = error.detail || "Failed to create project";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async loadTemplates() {
      try {
        if (!isOnline()) {
          return { success: false, error: "Offline mode: templates unavailable." };
        }
        const response = await api.projects.listTemplates();
        const templates = response.templates || [];
        update((state) => ({
          ...state,
          templates
        }));
        return { success: true, templates };
      } catch (error) {
        logger.error("Failed to load templates", error);
        return { success: false, error: error.detail };
      }
    },
    async createFromTemplate(templateId, customName) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        if (!isOnline()) {
          return { success: false, error: "Offline mode: cannot create from template." };
        }
        const newProject = await api.projects.createFromTemplate(templateId, customName);
        await offlineProjects.save(newProject);
        update((state) => ({
          ...state,
          projects: [newProject, ...state.projects],
          isLoading: false
        }));
        return { success: true, project: newProject };
      } catch (error) {
        const errorMessage = error.detail || "Failed to create project from template";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async getProjectProgress(projectId) {
      try {
        if (!isOnline()) {
          return { success: false, error: "Offline mode: project progress unavailable." };
        }
        const progress = await api.projects.getProgress(projectId);
        update((state) => ({
          ...state,
          currentProjectProgress: progress
        }));
        return { success: true, progress };
      } catch (error) {
        logger.error("Failed to load project progress", error);
        return { success: false, error: error.detail };
      }
    },
    async deleteProject(projectId) {
      try {
        if (!isOnline()) {
          await offlineProjects.delete(projectId);
          await queueOperation({
            type: "delete",
            entity: "project",
            data: {},
            endpoint: `/projects/${projectId}`
          });
          update((state) => ({
            ...state,
            projects: state.projects.filter((p) => p.id !== projectId)
          }));
          return { success: true };
        }
        await api.projects.delete(projectId);
        update((state) => ({
          ...state,
          projects: state.projects.filter((p) => p.id !== projectId)
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to delete project";
        return { success: false, error: errorMessage };
      }
    }
  };
}
const projectsStore = createProjectsStore();
function ProjectDetailDrawer($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { isOpen = false, project = null } = $$props;
    let progress = store_get($$store_subs ??= {}, "$projectsStore", projectsStore).currentProjectProgress;
    if (isOpen && project) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="absolute inset-y-0 right-0 w-full md:w-[600px] bg-background border-l-2 border-black dark:border-white shadow-[-8px_0px_0px_0px_rgba(0,0,0,1)] dark:shadow-[-8px_0px_0px_0px_rgba(255,255,255,1)] z-40 flex flex-col"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white bg-secondary flex items-start justify-between"><div class="space-y-2"><div class="flex items-center gap-2"><span class="text-xs font-bold uppercase bg-primary text-primary-foreground px-2 py-0.5 border border-black dark:border-white">${escape_html(project.status || "Active")}</span> <span class="text-xs font-bold uppercase text-muted-foreground">Created ${escape_html(new Date(project.createdAt || Date.now()).toLocaleDateString())}</span></div> <h2 class="text-2xl font-black uppercase tracking-tighter">${escape_html(project.name)}</h2></div> <div class="flex items-center gap-2"><button class="p-2 hover:bg-red-500 hover:text-white border border-transparent hover:border-black dark:hover:border-white transition-all" title="Delete Project">`);
      Trash_2($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></button> <button class="p-2 hover:bg-black/10 dark:hover:bg-white/10 border border-transparent hover:border-black dark:hover:border-white transition-all">`);
      X($$renderer2, { class: "w-6 h-6" });
      $$renderer2.push(`<!----></button></div></div> <div class="flex-1 overflow-y-auto p-6 space-y-8"><div class="brutal-card p-6 bg-white dark:bg-zinc-900"><h3 class="text-sm font-black uppercase text-muted-foreground mb-2">Description</h3> <p class="text-lg font-medium leading-relaxed">${escape_html(project.description || "No description provided for this project.")}</p></div> <div><h3 class="text-lg font-black uppercase tracking-tight mb-4 flex items-center gap-2">`);
      Trending_up($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----> Progress Overview</h3> `);
      {
        $$renderer2.push("<!--[!-->");
        if (progress) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="grid grid-cols-2 gap-4 mb-6"><div class="brutal-card p-4 flex flex-col items-center justify-center text-center"><span class="text-3xl font-black">${escape_html(progress.total_tasks || 0)}</span> <span class="text-xs font-bold uppercase text-muted-foreground">Total Tasks</span></div> <div class="brutal-card p-4 flex flex-col items-center justify-center text-center bg-green-100 dark:bg-green-900/20"><span class="text-3xl font-black text-green-600 dark:text-green-400">${escape_html(progress.completed_tasks || 0)}</span> <span class="text-xs font-bold uppercase text-muted-foreground">Completed</span></div> <div class="brutal-card p-4 flex flex-col items-center justify-center text-center bg-blue-100 dark:bg-blue-900/20"><span class="text-3xl font-black text-blue-600 dark:text-blue-400">${escape_html(progress.in_progress_tasks || 0)}</span> <span class="text-xs font-bold uppercase text-muted-foreground">In Progress</span></div> <div class="brutal-card p-4 flex flex-col items-center justify-center text-center bg-orange-100 dark:bg-orange-900/20"><span class="text-3xl font-black text-orange-600 dark:text-orange-400">${escape_html(progress.overdue_tasks || 0)}</span> <span class="text-xs font-bold uppercase text-muted-foreground">Overdue</span></div></div> <div class="space-y-2"><div class="flex justify-between text-sm font-bold uppercase"><span>Completion</span> <span>${escape_html(Math.round(progress.completion_percentage || 0))}%</span></div> <div class="h-4 w-full border-2 border-black dark:border-white bg-secondary p-0.5"><div class="h-full bg-primary transition-all duration-500"${attr_style(`width: ${stringify(progress.completion_percentage || 0)}%`)}></div></div></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="p-6 border-2 border-black dark:border-white border-dashed text-center"><p class="font-bold uppercase text-muted-foreground">No progress data available</p></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div> <div><h3 class="text-lg font-black uppercase tracking-tight mb-4 flex items-center gap-2">`);
      Clock($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----> Recent Activity</h3> <div class="space-y-3">`);
      if (progress && progress.recent_tasks && progress.recent_tasks.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<!--[-->`);
        const each_array = ensure_array_like(progress.recent_tasks);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let task = each_array[$$index];
          $$renderer2.push(`<div class="flex items-center justify-between p-3 border-2 border-black dark:border-white bg-white dark:bg-zinc-900"><span class="font-bold truncate flex-1 mr-4">${escape_html(task.title)}</span> <span class="text-xs font-bold uppercase px-2 py-1 bg-secondary border border-black dark:border-white">${escape_html(task.status)}</span></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="p-4 border-2 border-black dark:border-white border-dashed text-center text-sm font-bold text-muted-foreground">No recent activity</div>`);
      }
      $$renderer2.push(`<!--]--></div></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ProjectsView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let showDetailDrawer = false;
    let selectedProject = null;
    let projects = store_get($$store_subs ??= {}, "$projectsStore", projectsStore).projects;
    let isLoading = store_get($$store_subs ??= {}, "$projectsStore", projectsStore).isLoading;
    $$renderer2.push(`<div class="h-full flex flex-col relative overflow-hidden"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white bg-background z-10"><div class="flex items-center gap-3"><div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">`);
    Folder($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></div> <div><h2 class="text-2xl font-black uppercase tracking-tighter">Projects</h2> <p class="text-sm font-bold text-muted-foreground">Create via AI · Manage via gestures</p></div></div></div> <div class="flex-1 overflow-y-auto p-6">`);
    if (isLoading && projects.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="h-full flex items-center justify-center">`);
      Loader_circle($$renderer2, { class: "w-8 h-8 animate-spin" });
      $$renderer2.push(`<!----></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (projects.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-60">`);
        Folder($$renderer2, { class: "w-16 h-16 text-muted-foreground" });
        $$renderer2.push(`<!----> <p class="text-lg font-bold uppercase text-muted-foreground">No projects yet</p> <p class="text-sm text-muted-foreground">Ask the AI to create a project</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"><!--[-->`);
        const each_array = ensure_array_like(projects);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let project = each_array[$$index];
          $$renderer2.push(`<button class="brutal-card p-0 flex flex-col h-full hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none transition-all cursor-pointer group text-left w-full"><div class="p-5 flex-1 space-y-4 w-full"><div class="flex items-start justify-between w-full"><div class="space-y-1"><h3 class="text-lg font-black uppercase tracking-tight group-hover:underline decoration-2">${escape_html(project.name)}</h3> <span class="inline-block px-2 py-0.5 text-xs font-bold uppercase border border-black dark:border-white bg-secondary">${escape_html(project.status || "Active")}</span></div> <div class="p-1 hover:bg-accent border border-transparent hover:border-black dark:hover:border-white transition-colors">`);
          Ellipsis_vertical($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></div></div> <p class="text-sm font-medium text-muted-foreground line-clamp-2">${escape_html(project.description || "No description provided.")}</p></div> <div class="p-4 border-t-2 border-black dark:border-white bg-secondary/10 flex items-center justify-between text-xs font-bold uppercase text-muted-foreground w-full"><div class="flex items-center gap-2">`);
          Calendar($$renderer2, { class: "w-3.5 h-3.5" });
          $$renderer2.push(`<!----> <span>${escape_html(new Date(project.createdAt || Date.now()).toLocaleDateString())}</span></div> <div class="flex items-center gap-2">`);
          Circle_check($$renderer2, { class: "w-3.5 h-3.5" });
          $$renderer2.push(`<!----> <span>${escape_html(project.taskCount || 0)} Tasks</span></div></div></button>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> `);
    ProjectDetailDrawer($$renderer2, {
      isOpen: showDetailDrawer,
      project: selectedProject
    });
    $$renderer2.push(`<!----></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ItemTypeManager($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { isOpen = false } = $$props;
    let newTypeName = "";
    let isSubmitting = false;
    let itemTypes = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).isLoading;
    if (isOpen) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"><div class="w-full max-w-md bg-background border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] flex flex-col max-h-[80vh]"><div class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white bg-secondary"><div class="flex items-center gap-3">`);
      Tag($$renderer2, { class: "w-6 h-6" });
      $$renderer2.push(`<!----> <h2 class="text-xl font-black uppercase tracking-tighter">Manage Types</h2></div> <button class="p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">`);
      X($$renderer2, { class: "w-6 h-6" });
      $$renderer2.push(`<!----></button></div> <div class="flex-1 overflow-y-auto p-6 space-y-6"><div class="space-y-4 p-4 border-2 border-black dark:border-white bg-secondary/10"><h3 class="text-sm font-black uppercase">Create New Type</h3> <div class="flex gap-2"><input type="text"${attr("value", newTypeName)} placeholder="Type Name (e.g. Article)" class="flex-1 border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold"/> <button class="brutal-btn bg-primary text-primary-foreground p-2"${attr("disabled", !newTypeName.trim() || isSubmitting, true)}>`);
      {
        $$renderer2.push("<!--[!-->");
        Plus($$renderer2, { class: "w-4 h-4" });
      }
      $$renderer2.push(`<!--]--></button></div></div> <div class="space-y-2"><h3 class="text-sm font-black uppercase text-muted-foreground">Existing Types</h3> `);
      if (itemTypes.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<p class="text-sm italic text-muted-foreground">No types defined.</p>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<!--[-->`);
        const each_array = ensure_array_like(itemTypes);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let type = each_array[$$index];
          $$renderer2.push(`<div class="flex items-center justify-between p-3 border-2 border-black dark:border-white bg-white dark:bg-zinc-900"><div class="flex items-center gap-3"><div class="w-3 h-3 border border-black dark:border-white"${attr_style(`background-color: ${stringify(type.color || "#000")}`)}></div> <span class="font-bold uppercase">${escape_html(type.name)}</span></div> <button class="p-1.5 hover:bg-red-500 hover:text-white border border-transparent hover:border-black dark:hover:border-white transition-all">`);
          Trash_2($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function KnowledgeItemModal($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { isOpen = false, item = null } = $$props;
    let title = "";
    let content = "";
    let typeId = "";
    let isSubmitting = false;
    let isAiGenerating = false;
    let itemTypes = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    if (isOpen) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"><div class="w-full max-w-2xl bg-background border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] flex flex-col max-h-[90vh]"><div class="flex items-center justify-between p-6 border-b-2 border-black dark:border-white bg-secondary"><div class="flex items-center gap-3"><h2 class="text-xl font-black uppercase tracking-tighter">${escape_html(item ? "Edit Item" : "New Knowledge Item")}</h2></div> <button class="p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">`);
      X($$renderer2, { class: "w-6 h-6" });
      $$renderer2.push(`<!----></button></div> <div class="flex-1 overflow-y-auto p-6 space-y-6"><div class="space-y-2"><div class="flex items-center justify-between"><label for="title" class="text-xs font-black uppercase">Title</label> <button type="button"${attr("disabled", !title.trim(), true)} class="text-[10px] uppercase font-bold tracking-wide px-2 py-1 border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1" title="Ask AI to improve title">`);
      Sparkles($$renderer2, { class: "w-3 h-3" });
      $$renderer2.push(`<!----> AI Improve</button></div> <input id="title" type="text"${attr("value", title)} placeholder="Item Title" class="w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold"/></div> <div class="space-y-2"><label for="type" class="text-xs font-black uppercase">Type</label> `);
      $$renderer2.select(
        {
          id: "type",
          value: typeId,
          class: "w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-bold bg-background"
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array = ensure_array_like(itemTypes);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let type = each_array[$$index];
            $$renderer3.option({ value: type.id }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(type.name)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</div> <div class="space-y-2"><div class="flex items-center justify-between"><label for="content" class="text-xs font-black uppercase">Content</label> <div class="flex gap-2"><button type="button"${attr("disabled", !title.trim() || isAiGenerating, true)} class="text-[10px] uppercase font-bold tracking-wide px-2 py-1 border-2 border-accent text-accent-foreground bg-accent hover:bg-accent/80 transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1" title="Ask AI to generate content">`);
      Wand_sparkles($$renderer2, { class: "w-3 h-3" });
      $$renderer2.push(`<!----> ${escape_html("AI Generate")}</button> `);
      if (content.trim()) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button type="button" class="text-[10px] uppercase font-bold tracking-wide px-2 py-1 border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground transition-colors flex items-center gap-1" title="Ask AI to expand content">`);
        Sparkles($$renderer2, { class: "w-3 h-3" });
        $$renderer2.push(`<!----> AI Expand</button>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div> <textarea id="content" rows="10" placeholder="Markdown content..." class="w-full border-2 border-black dark:border-white px-3 py-2 text-sm focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] transition-all font-mono">`);
      const $$body = escape_html(content);
      if ($$body) {
        $$renderer2.push(`${$$body}`);
      }
      $$renderer2.push(`</textarea> <p class="text-[10px] text-muted-foreground uppercase font-bold tracking-wide">✨ AI responses appear in the main conversation - copy &amp; paste them here</p></div></div> <div class="p-6 border-t-2 border-black dark:border-white bg-secondary/10 flex justify-end gap-3"><button class="brutal-btn bg-white text-black"${attr("disabled", isSubmitting, true)}>Cancel</button> <button class="brutal-btn bg-primary text-primary-foreground flex items-center gap-2"${attr("disabled", !title.trim() || !content.trim() || !typeId, true)}>`);
      {
        $$renderer2.push("<!--[!-->");
        Save($$renderer2, { class: "w-4 h-4" });
        $$renderer2.push(`<!----> Save Item`);
      }
      $$renderer2.push(`<!--]--></button></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function TypePicker($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let {
      label = "Choose type",
      selectedId = null
    } = $$props;
    let itemTypes = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    $$renderer2.push(`<div class="space-y-2"><p class="text-xs font-bold uppercase text-muted-foreground">${escape_html(label)}</p> <div class="flex flex-wrap gap-2"><!--[-->`);
    const each_array = ensure_array_like(itemTypes);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let type = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-3 py-1 border-2 border-black dark:border-white text-xs font-bold uppercase transition-colors ${stringify(selectedId === type.id ? "bg-black text-white dark:bg-white dark:text-black" : "bg-background hover:bg-secondary")}`)}>${escape_html(type.name)}</button>`);
    }
    $$renderer2.push(`<!--]--></div> `);
    if (itemTypes.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-xs text-muted-foreground">Loading types…</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function KnowledgeView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let searchQuery = "";
    let showTypeManager = false;
    let showItemModal = false;
    let selectedItem = null;
    let items = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).items;
    let itemTypes = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).itemTypes;
    let isLoading = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).isLoading;
    let selectedTypeId = store_get($$store_subs ??= {}, "$knowledgeStore", knowledgeStore).selectedTypeId;
    function getItemType(typeId) {
      return itemTypes.find((t) => t.id === typeId);
    }
    $$renderer2.push(`<div class="h-full flex flex-col relative overflow-hidden"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10"><div class="flex items-center gap-3"><div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">`);
    Book($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></div> <div><h2 class="text-2xl font-black uppercase tracking-tighter">Knowledge Base</h2> <p class="text-sm font-bold text-muted-foreground">Create via AI · Manage via gestures</p></div></div> <button class="brutal-btn bg-white text-black flex items-center gap-2">`);
    Settings($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Types</button></div> <div class="p-6 pb-0 space-y-4"><div class="relative">`);
    Search($$renderer2, {
      class: "absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground z-10"
    });
    $$renderer2.push(`<!----> <input type="text"${attr("value", searchQuery)} placeholder="Search knowledge..." class="brutal-input pl-12 py-4 text-base"/></div> <div class="flex flex-wrap gap-2"><button${attr_class(`px-4 py-1.5 text-xs font-black uppercase border-2 transition-all ${stringify(selectedTypeId === null ? "bg-primary text-primary-foreground border-border shadow-brutal-sm" : "bg-card border-border hover:bg-secondary")}`)}>All</button> <!--[-->`);
    const each_array = ensure_array_like(itemTypes);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let type = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-4 py-1.5 text-xs font-black uppercase border-2 transition-all flex items-center gap-2 ${stringify(selectedTypeId === type.id ? "bg-primary text-primary-foreground border-border shadow-brutal-sm" : "bg-card border-border hover:bg-secondary")}`)}><div class="w-2.5 h-2.5"${attr_style(`background-color: ${stringify(type.color)}; border: 1px solid currentColor;`)}></div> ${escape_html(type.name)}</button>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="mt-4">`);
    TypePicker($$renderer2, {
      label: "Share these type IDs with the assistant when creating items",
      selectedId: selectedTypeId
    });
    $$renderer2.push(`<!----></div></div> <div class="flex-1 overflow-y-auto p-6 bg-grid-pattern">`);
    if (isLoading && items.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="h-full flex items-center justify-center"><div class="flex flex-col items-center gap-4">`);
      Loader_circle($$renderer2, { class: "w-12 h-12 animate-spin text-primary" });
      $$renderer2.push(`<!----> <p class="font-black uppercase tracking-widest text-sm">Accessing Archive...</p></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (items.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="h-full flex flex-col items-center justify-center text-center p-8"><div class="brutal-card p-12 max-w-md bg-background flex flex-col items-center gap-6"><div class="p-4 bg-secondary border-2 border-border">`);
        Book($$renderer2, { class: "w-16 h-16 text-muted-foreground" });
        $$renderer2.push(`<!----></div> <div class="space-y-2"><h3 class="text-3xl font-black uppercase tracking-tighter">Library Empty</h3> <p class="text-sm font-bold uppercase text-muted-foreground tracking-wide">Ask the AI to document knowledge, ideas, or notes.</p></div> <button class="brutal-btn bg-terminal-green text-black">Start Conversation</button></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"><!--[-->`);
        const each_array_1 = ensure_array_like(items);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let item = each_array_1[$$index_1];
          $$renderer2.push(`<div class="brutal-card p-5 flex flex-col gap-4 hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle active:translate-x-[4px] active:translate-y-[4px] active:shadow-none transition-all cursor-pointer group text-left relative" role="button" tabindex="0"><div class="flex items-start justify-between gap-4"><div class="p-2.5 border-2 border-border bg-secondary text-secondary-foreground flex-shrink-0">`);
          if (item.item_metadata?.type === "link") {
            $$renderer2.push("<!--[-->");
            Link($$renderer2, { class: "w-6 h-6" });
          } else {
            $$renderer2.push("<!--[!-->");
            File_text($$renderer2, { class: "w-6 h-6" });
          }
          $$renderer2.push(`<!--]--></div> <button class="p-2 brutal-btn bg-white dark:bg-black hover:bg-destructive hover:text-white !shadow-none hover:!shadow-brutal-sm scale-90 opacity-0 group-hover:opacity-100 transition-all">`);
          Trash_2($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div> <div class="flex-1 min-w-0 space-y-2"><h3 class="text-xl font-black uppercase tracking-tight leading-tight group-hover:text-primary transition-colors">${escape_html(item.title)}</h3> <div class="flex flex-wrap items-center gap-2 mt-auto">`);
          if (getItemType(item.typeId)) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="text-[10px] font-black uppercase px-2 py-0.5 border-2 border-border bg-accent text-accent-foreground shadow-brutal-sm">${escape_html(getItemType(item.typeId)?.name)}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <span class="text-[10px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-1">`);
          Tag($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----> ${escape_html(new Date(item.updatedAt || Date.now()).toLocaleDateString())}</span></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> `);
    ItemTypeManager($$renderer2, {
      isOpen: showTypeManager
    });
    $$renderer2.push(`<!----> `);
    KnowledgeItemModal($$renderer2, {
      isOpen: showItemModal,
      item: selectedItem
    });
    $$renderer2.push(`<!----></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState$5 = {
  events: [],
  isLoading: false,
  error: null,
  syncStatus: null
};
function createCalendarStore() {
  const { subscribe, set, update } = writable(initialState$5);
  return {
    subscribe,
    async loadEvents(startDate, endDate) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.events.list({ startDate, endDate });
        const events = response.events || [];
        update((state) => ({
          ...state,
          events,
          isLoading: false
        }));
        return { success: true, events };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load events";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async checkSyncStatus() {
      try {
        const status = await api.integration.calendarStatus();
        update((state) => ({
          ...state,
          syncStatus: status
        }));
        return { success: true, status };
      } catch (error) {
        logger.error("Failed to check sync status", error);
        return { success: false, error: error.detail };
      }
    },
    async syncGoogleCalendar() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        await api.events.syncGoogle();
        update((state) => ({ ...state, isLoading: false }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to sync calendar";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async createEvent(eventData) {
      try {
        const newEvent = await api.events.create(eventData);
        update((state) => ({
          ...state,
          events: [...state.events, newEvent]
        }));
        return { success: true, event: newEvent };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to create event" };
      }
    }
  };
}
const calendarStore = createCalendarStore();
function CalendarView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let currentDate = /* @__PURE__ */ new Date();
    let startDate = getStartDate(currentDate);
    getEndDate(currentDate);
    function getStartDate(date, v) {
      const d = new Date(date);
      {
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1);
        d.setDate(diff);
      }
      d.setHours(0, 0, 0, 0);
      return d;
    }
    function getEndDate(date, v) {
      const d = new Date(date);
      {
        const start = getStartDate(date);
        d.setDate(start.getDate() + 6);
      }
      d.setHours(23, 59, 59, 999);
      return d;
    }
    function formatTime(dateStr) {
      return new Date(dateStr).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    function isSameDay(d1, d2) {
      return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
    }
    function getDays() {
      const days = [];
      const start = new Date(startDate);
      const current = new Date(start);
      const count = 7;
      for (let i = 0; i < count; i++) {
        days.push(new Date(current));
        current.setDate(current.getDate() + 1);
      }
      return days;
    }
    $$renderer2.push(`<div class="space-y-6 h-full flex flex-col"><div class="flex flex-col md:flex-row md:items-center justify-between gap-4"><div class="flex items-center gap-4"><h2 class="text-3xl font-black uppercase tracking-tighter">Calendar</h2> <div class="flex items-center border-2 border-black dark:border-white"><button class="p-2 hover:bg-secondary transition-colors border-r-2 border-black dark:border-white">`);
    Chevron_left($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></button> <span class="px-4 py-2 font-mono font-bold min-w-[140px] text-center">${escape_html(currentDate.toLocaleDateString(void 0, { month: "long", year: "numeric" }))}</span> <button class="p-2 hover:bg-secondary transition-colors border-l-2 border-black dark:border-white">`);
    Chevron_right($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></button></div></div> <div class="flex items-center gap-3"><div class="flex border-2 border-black dark:border-white"><button${attr_class(`px-4 py-2 text-sm font-bold uppercase transition-colors ${stringify(
      "bg-black text-white dark:bg-white dark:text-black"
    )}`)}>Week</button> <button${attr_class(`px-4 py-2 text-sm font-bold uppercase transition-colors border-l-2 border-black dark:border-white ${stringify("bg-white text-black dark:bg-black dark:text-white hover:bg-secondary")}`)}>Month</button></div> <button class="brutal-btn bg-white text-black flex items-center gap-2"${attr("disabled", store_get($$store_subs ??= {}, "$calendarStore", calendarStore).isLoading, true)}>`);
    Refresh_cw($$renderer2, {
      class: `w-4 h-4 ${stringify(store_get($$store_subs ??= {}, "$calendarStore", calendarStore).isLoading ? "animate-spin" : "")}`
    });
    $$renderer2.push(`<!----> Sync</button></div></div> <div class="flex-1 border-2 border-black dark:border-white bg-white dark:bg-black flex flex-col overflow-hidden"><div class="grid grid-cols-7 border-b-2 border-black dark:border-white bg-secondary"><!--[-->`);
    const each_array = ensure_array_like(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let day = each_array[$$index];
      $$renderer2.push(`<div class="p-2 text-center font-black uppercase text-sm border-r-2 border-black dark:border-white last:border-r-0">${escape_html(day)}</div>`);
    }
    $$renderer2.push(`<!--]--></div> <div${attr_class(`flex-1 grid grid-cols-7 ${stringify("grid-rows-1")}`)}><!--[-->`);
    const each_array_1 = ensure_array_like(getDays());
    for (let $$index_2 = 0, $$length = each_array_1.length; $$index_2 < $$length; $$index_2++) {
      let day = each_array_1[$$index_2];
      const isToday = isSameDay(day, /* @__PURE__ */ new Date());
      day.getMonth() === currentDate.getMonth();
      const dayEvents = store_get($$store_subs ??= {}, "$calendarStore", calendarStore).events.filter((e) => isSameDay(new Date(e.startTime), day));
      $$renderer2.push(`<div${attr_class(`border-r-2 border-b-2 border-black dark:border-white last:border-r-0 p-2 min-h-[100px] relative group hover:bg-secondary/10 transition-colors ${stringify("")} ${stringify(isToday ? "bg-primary/5" : "")}`)}><span${attr_class(`absolute top-2 right-2 text-sm font-mono font-bold ${stringify(isToday ? "text-primary" : "")}`)}>${escape_html(day.getDate())}</span> <div class="mt-6 space-y-1"><!--[-->`);
      const each_array_2 = ensure_array_like(dayEvents);
      for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
        let event = each_array_2[$$index_1];
        $$renderer2.push(`<div class="text-xs p-1 border border-black dark:border-white bg-white dark:bg-black truncate cursor-pointer hover:bg-secondary transition-colors">`);
        if (!event.isAllDay) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<span class="font-mono text-[10px] opacity-70">${escape_html(formatTime(event.startTime))}</span>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> <span class="font-bold">${escape_html(event.title)}</span></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState$4 = {
  overview: null,
  bottlenecks: [],
  isLoading: false,
  error: null
};
function createAnalyticsStore() {
  const { subscribe, set, update } = writable(initialState$4);
  return {
    subscribe,
    async loadOverview(workspaceId) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.analytics.overview({ workspaceId });
        update((state) => ({
          ...state,
          overview: response,
          isLoading: false
        }));
        return { success: true, overview: response };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load analytics overview";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async loadBottlenecks(workspaceId) {
      try {
        const response = await api.analytics.bottlenecks({ workspaceId });
        const bottlenecks = response.bottlenecks || [];
        update((state) => ({
          ...state,
          bottlenecks
        }));
        return { success: true, bottlenecks };
      } catch (error) {
        logger.error("Failed to load bottlenecks", error);
        return { success: false, error: error.detail };
      }
    },
    async loadAll(workspaceId) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const [overviewRes, bottlenecksRes] = await Promise.all([
          api.analytics.overview({ workspaceId }),
          api.analytics.bottlenecks({ workspaceId })
        ]);
        update((state) => ({
          ...state,
          overview: overviewRes,
          bottlenecks: bottlenecksRes.bottlenecks || [],
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load analytics data";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    }
  };
}
const analyticsStore = createAnalyticsStore();
function AnalyticsView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let overview = store_get($$store_subs ??= {}, "$analyticsStore", analyticsStore).overview;
    let bottlenecks = store_get($$store_subs ??= {}, "$analyticsStore", analyticsStore).bottlenecks;
    let isLoading = store_get($$store_subs ??= {}, "$analyticsStore", analyticsStore).isLoading;
    function getSeverityColor(severity) {
      switch (severity) {
        case "high":
          return "text-red-600 dark:text-red-400";
        case "medium":
          return "text-orange-600 dark:text-orange-400";
        case "low":
          return "text-yellow-600 dark:text-yellow-400";
        default:
          return "text-muted-foreground";
      }
    }
    function getSeverityBg(severity) {
      switch (severity) {
        case "high":
          return "bg-red-100 dark:bg-red-900/20";
        case "medium":
          return "bg-orange-100 dark:bg-orange-900/20";
        case "low":
          return "bg-yellow-100 dark:bg-yellow-900/20";
        default:
          return "bg-secondary";
      }
    }
    $$renderer2.push(`<div class="h-full flex flex-col"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10"><div class="flex items-center gap-3"><div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">`);
    Chart_column($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></div> <div><h2 class="text-2xl font-black uppercase tracking-tighter">Insights</h2> <p class="text-sm font-bold text-muted-foreground">Productivity Analytics</p></div></div> <div class="flex items-center gap-2"><span class="text-xs font-bold uppercase px-2 py-1 border border-black dark:border-white bg-white dark:bg-black">${escape_html((/* @__PURE__ */ new Date()).toLocaleDateString())}</span></div></div> <div class="flex-1 overflow-y-auto p-6 space-y-8 bg-grid-pattern">`);
    if (isLoading && !overview) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="h-full flex items-center justify-center"><div class="flex flex-col items-center gap-4">`);
      Loader_circle($$renderer2, { class: "w-12 h-12 animate-spin text-primary" });
      $$renderer2.push(`<!----> <p class="font-black uppercase tracking-widest text-sm">Aggregating Data...</p></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"><div class="brutal-card p-6 space-y-3 bg-card hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all"><div class="flex items-center justify-between text-muted-foreground"><span class="text-xs font-black uppercase tracking-widest">Avg Completion</span> `);
      Clock($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></div> <div class="flex items-end gap-2"><span class="text-4xl font-black tracking-tighter tabular-nums">${escape_html(overview?.avg_completion_time?.toFixed(1) || "0")}h</span> <span class="text-[10px] font-black uppercase text-muted-foreground mb-1.5">/ task</span></div></div> <div class="brutal-card p-6 space-y-3 bg-card hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all"><div class="flex items-center justify-between text-muted-foreground"><span class="text-xs font-black uppercase tracking-widest">Velocity</span> `);
      Trending_up($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></div> <div class="flex items-end gap-2"><span class="text-4xl font-black tracking-tighter tabular-nums">${escape_html(overview?.velocity || "0")}</span> <span class="text-[10px] font-black uppercase text-green-500 mb-1.5">tasks/wk</span></div></div> <div class="brutal-card p-6 space-y-3 bg-card hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-brutal-subtle transition-all"><div class="flex items-center justify-between text-muted-foreground"><span class="text-xs font-black uppercase tracking-widest">Comp. Rate</span> `);
      Circle_check($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></div> <div class="flex items-end gap-2"><span class="text-4xl font-black tracking-tighter tabular-nums">${escape_html(Math.round((overview?.completion_rate || 0) * 100))}%</span></div></div> <div class="brutal-card p-6 space-y-3 bg-primary text-primary-foreground shadow-card"><div class="flex items-center justify-between opacity-80"><span class="text-xs font-black uppercase tracking-widest">Total Tasks</span> `);
      Chart_column($$renderer2, { class: "w-5 h-5" });
      $$renderer2.push(`<!----></div> <div class="flex items-end gap-2"><span class="text-4xl font-black tracking-tighter tabular-nums">${escape_html(overview?.total_tasks || "0")}</span> <span class="text-[10px] font-black uppercase opacity-80 mb-1.5">Total</span></div></div></div> <div class="grid grid-cols-1 lg:grid-cols-2 gap-8"><div class="brutal-card p-0 overflow-hidden flex flex-col bg-card shadow-card"><div class="p-5 border-b-2 border-border bg-secondary flex items-center justify-between"><h3 class="text-xl font-black uppercase tracking-tighter flex items-center gap-2">`);
      Octagon_alert($$renderer2, { class: "w-6 h-6" });
      $$renderer2.push(`<!----> Critical Bottlenecks</h3> `);
      if (bottlenecks.length > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="bg-destructive text-destructive-foreground text-[10px] font-black uppercase px-2 py-0.5 border-2 border-border animate-pulse">${escape_html(bottlenecks.length)} Active</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="divide-y-2 divide-border flex-1">`);
      if (bottlenecks.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="p-12 text-center text-muted-foreground bg-grid-pattern bg-[size:16px_16px]"><div class="inline-block p-4 border-2 border-border bg-secondary mb-4">`);
        Circle_check($$renderer2, { class: "w-12 h-12 opacity-40" });
        $$renderer2.push(`<!----></div> <p class="font-black uppercase tracking-widest mb-1">Zero Blockers</p> <p class="text-[10px] font-bold uppercase tracking-widest opacity-60">Optimized throughput detected.</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<!--[-->`);
        const each_array = ensure_array_like(bottlenecks);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let bottleneck = each_array[$$index];
          $$renderer2.push(`<div class="p-5 hover:bg-secondary transition-colors group"><div class="flex items-start justify-between mb-3"><span${attr_class(`text-[10px] font-black uppercase px-2 py-1 border-2 border-border shadow-brutal-sm ${stringify(getSeverityBg(bottleneck.severity))} ${stringify(getSeverityColor(bottleneck.severity))}`)}>${escape_html(bottleneck.type.replace("_", " "))}</span> <span class="text-[10px] font-black uppercase text-muted-foreground bg-card px-1.5 border border-border">${escape_html(bottleneck.affected_items.length)} ITEMS</span></div> <p class="font-bold text-base mb-3 leading-tight uppercase tracking-tight">${escape_html(bottleneck.description)}</p> `);
          if (bottleneck.suggestion) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="flex items-start gap-3 text-xs font-bold uppercase tracking-wide text-muted-foreground bg-background p-3 border-2 border-border border-dashed">`);
            Arrow_up_right($$renderer2, { class: "w-4 h-4 mt-0.5 flex-shrink-0 text-primary" });
            $$renderer2.push(`<!----> <span>RECO: ${escape_html(bottleneck.suggestion)}</span></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="brutal-card p-6 space-y-8 bg-card shadow-card"><div class="flex items-center justify-between border-b-2 border-border pb-4"><h3 class="text-xl font-black uppercase tracking-tighter">Task Priority Dist.</h3> <div class="flex gap-1"><div class="w-2 h-2 bg-red-500"></div> <div class="w-2 h-2 bg-orange-500"></div> <div class="w-2 h-2 bg-blue-500"></div></div></div> `);
      if (overview?.tasks_by_priority) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="space-y-6"><!--[-->`);
        const each_array_1 = ensure_array_like(Object.entries(overview.tasks_by_priority));
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let [priority, count] = each_array_1[$$index_1];
          $$renderer2.push(`<div class="space-y-2"><div class="flex justify-between text-[10px] font-black uppercase tracking-widest"><span class="flex items-center gap-2"><div${attr_class(`w-2 h-2 ${stringify(priority === "high" ? "bg-red-500" : priority === "medium" ? "bg-orange-500" : "bg-blue-500")}`)}></div> ${escape_html(priority)}</span> <span class="tabular-nums">${escape_html(count)} UNITS</span></div> <div class="h-10 w-full border-2 border-border bg-secondary p-1 relative"><div${attr_class(`h-full transition-all duration-1000 ease-out ${stringify(priority === "high" ? "bg-red-500" : priority === "medium" ? "bg-orange-500" : "bg-blue-500")}`)}${attr_style(`width: ${stringify(count / (overview.total_tasks || 1) * 100)}%`)}></div> <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.05)_1px,transparent_1px)] bg-[size:10%_100%] pointer-events-none"></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="h-40 flex items-center justify-center text-muted-foreground font-black uppercase tracking-widest border-2 border-dashed border-border">Data Unavailable</div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState$3 = {
  openRouterKey: null,
  usageStats: null,
  isKeyValid: false,
  isLoading: false,
  error: null
};
function createSettingsStore() {
  const { subscribe, set, update } = writable(initialState$3);
  return {
    subscribe,
    async loadSettings() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const stats = await api.settings.getUsageStats();
        update((state) => ({
          ...state,
          usageStats: stats,
          isKeyValid: true,
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        update((state) => ({
          ...state,
          isLoading: false,
          isKeyValid: false,
          usageStats: null
        }));
        return { success: false, error: error.detail || "Failed to load settings" };
      }
    },
    async saveOpenRouterKey(key) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        await api.settings.saveOpenRouterKey({ apiKey: key });
        update((state) => ({
          ...state,
          isKeyValid: true,
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to save API key";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage,
          isKeyValid: false
        }));
        return { success: false, error: errorMessage };
      }
    },
    async deleteOpenRouterKey() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        await api.settings.deleteOpenRouterKey();
        update((state) => ({
          ...state,
          isKeyValid: false,
          isLoading: false,
          openRouterKey: null
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to delete API key";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    }
  };
}
const settingsStore = createSettingsStore();
function NotificationSettings($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let testSending = false;
    $$renderer2.push(`<div class="brutal-card p-6"><div class="flex items-start gap-4 mb-6"><div class="p-3 bg-yellow-400 border-2 border-black dark:border-white">`);
    if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isSubscribed) {
      $$renderer2.push("<!--[-->");
      Bell($$renderer2, { class: "w-6 h-6 text-black" });
    } else {
      $$renderer2.push("<!--[!-->");
      Bell_off($$renderer2, { class: "w-6 h-6 text-black" });
    }
    $$renderer2.push(`<!--]--></div> <div><h3 class="text-xl font-black uppercase">Push Notifications</h3> <p class="text-sm text-muted-foreground mt-1">Get reminded about tasks, deadlines, and focus sessions.</p></div></div> `);
    if (!store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isSupported) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="p-4 bg-amber-100 dark:bg-amber-900/30 border-2 border-black dark:border-white text-sm"><div class="flex items-center gap-2 font-bold">`);
      Triangle_alert($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> Push notifications are not supported in this browser.</div> <p class="mt-1 text-muted-foreground">Try using Chrome, Firefox, or Edge for push notification support.</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="space-y-6"><div class="flex items-center justify-between p-4 border-2 border-black dark:border-white bg-secondary/20"><div><p class="font-bold uppercase text-sm">Enable Notifications</p> <p class="text-xs text-muted-foreground mt-1">`);
      if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).permission === "denied") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`Permission blocked. Enable in browser settings.`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isSubscribed) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`You'll receive push notifications.`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`Receive alerts even when Focus is closed.`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></p></div> <button${attr_class(`brutal-btn ${stringify(store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isSubscribed ? "bg-black text-white dark:bg-white dark:text-black" : "bg-white text-black")} flex items-center gap-2`)}${attr("disabled", store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isLoading || store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).permission === "denied", true)}>`);
      if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isLoading) {
        $$renderer2.push("<!--[-->");
        Loader_circle($$renderer2, { class: "w-4 h-4 animate-spin" });
      } else {
        $$renderer2.push("<!--[!-->");
        if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isSubscribed) {
          $$renderer2.push("<!--[-->");
          Check($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----> Enabled`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`Enable`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></button></div> `);
      if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).error) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="p-3 bg-destructive border-2 border-black dark:border-white text-destructive-foreground text-sm font-bold flex items-center gap-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] uppercase">`);
        Triangle_alert($$renderer2, { class: "w-4 h-4" });
        $$renderer2.push(`<!----> ${escape_html(store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).error)}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).isSubscribed) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="space-y-3"><h4 class="font-bold uppercase text-xs text-muted-foreground">Notification Types</h4> <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors"><div><p class="font-bold text-sm">Task Reminders</p> <p class="text-xs text-muted-foreground">Due dates and scheduled tasks</p></div> <input type="checkbox"${attr("checked", store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).preferences.taskReminders, true)} class="w-5 h-5 accent-primary"/></label> <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors"><div><p class="font-bold text-sm">Daily Digest</p> <p class="text-xs text-muted-foreground">Morning summary of your day</p></div> <input type="checkbox"${attr("checked", store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).preferences.dailyDigest, true)} class="w-5 h-5 accent-primary"/></label> <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors"><div><p class="font-bold text-sm">Pomodoro Alerts</p> <p class="text-xs text-muted-foreground">Break and session reminders</p></div> <input type="checkbox"${attr("checked", store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).preferences.pomodoroAlerts, true)} class="w-5 h-5 accent-primary"/></label> <label class="flex items-center justify-between p-3 border-2 border-black dark:border-white hover:bg-secondary/20 cursor-pointer transition-colors"><div><p class="font-bold text-sm">Project Updates</p> <p class="text-xs text-muted-foreground">Progress and milestone alerts</p></div> <input type="checkbox"${attr("checked", store_get($$store_subs ??= {}, "$notificationsStore", notificationsStore).preferences.projectUpdates, true)} class="w-5 h-5 accent-primary"/></label></div> <div class="pt-4 border-t-2 border-black dark:border-white"><div class="flex items-center gap-4"><button class="brutal-btn bg-secondary text-foreground flex items-center gap-2"${attr("disabled", testSending, true)}>`);
        {
          $$renderer2.push("<!--[!-->");
          Send($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----> Test Notification`);
        }
        $$renderer2.push(`<!--]--></button> `);
        {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function SettingsView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let apiKey = "";
    (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
    (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
    $$renderer2.push(`<div class="space-y-6"><div class="flex flex-col md:flex-row md:items-center justify-between gap-4"><div><h2 class="text-3xl font-black uppercase tracking-tighter">Settings</h2> <p class="text-muted-foreground font-mono text-sm mt-1">Manage your preferences and account.</p></div></div> <div class="flex border-b-2 border-black dark:border-white overflow-x-auto"><button${attr_class(`px-6 py-3 font-bold uppercase text-sm border-r-2 border-black dark:border-white transition-colors whitespace-nowrap ${stringify(
      "bg-black text-white dark:bg-white dark:text-black"
    )}`)}>General</button> <button${attr_class(`px-6 py-3 font-bold uppercase text-sm border-r-2 border-black dark:border-white transition-colors whitespace-nowrap ${stringify("hover:bg-secondary")}`)}>Billing</button> <button${attr_class(`px-6 py-3 font-bold uppercase text-sm transition-colors whitespace-nowrap ${stringify("hover:bg-secondary")}`)}>Exports</button></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="brutal-card p-6"><div class="flex items-start gap-4 mb-6"><div class="p-3 bg-primary border-2 border-black dark:border-white">`);
      Key($$renderer2, { class: "w-6 h-6 text-primary-foreground" });
      $$renderer2.push(`<!----></div> <div><h3 class="text-xl font-black uppercase">OpenRouter API Key</h3> <p class="text-sm text-muted-foreground mt-1">Required for AI features. Your key is stored locally and
                        encrypted.</p></div></div> <div class="space-y-4"><div class="space-y-2"><label for="apiKey" class="text-xs font-bold uppercase">API Key</label> <input id="apiKey" type="password"${attr("value", apiKey)} placeholder="sk-or-..." class="w-full p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"/></div> <div class="flex gap-3"><button class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2"${attr("disabled", store_get($$store_subs ??= {}, "$settingsStore", settingsStore).isLoading, true)}>`);
      if (store_get($$store_subs ??= {}, "$settingsStore", settingsStore).isLoading) {
        $$renderer2.push("<!--[-->");
        Loader_circle($$renderer2, { class: "w-4 h-4 animate-spin" });
      } else {
        $$renderer2.push("<!--[!-->");
        Save($$renderer2, { class: "w-4 h-4" });
      }
      $$renderer2.push(`<!--]--> Save Key</button> `);
      if (store_get($$store_subs ??= {}, "$settingsStore", settingsStore).openRouterKey) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button class="brutal-btn bg-red-500 text-white border-black flex items-center gap-2"${attr("disabled", store_get($$store_subs ??= {}, "$settingsStore", settingsStore).isLoading, true)}>`);
        Trash_2($$renderer2, { class: "w-4 h-4" });
        $$renderer2.push(`<!----> Delete</button>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> `);
      if (store_get($$store_subs ??= {}, "$settingsStore", settingsStore).error) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="p-3 bg-destructive border-2 border-black dark:border-white text-destructive-foreground text-sm font-bold flex items-center gap-2 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] uppercase">`);
        Triangle_alert($$renderer2, { class: "w-4 h-4" });
        $$renderer2.push(`<!----> Error: ${escape_html(store_get($$store_subs ??= {}, "$settingsStore", settingsStore).error)}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      if (store_get($$store_subs ??= {}, "$settingsStore", settingsStore).isKeyValid === true) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="p-3 bg-primary border-2 border-black dark:border-white text-primary-foreground text-sm font-bold shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)] uppercase">API Key is valid and active.</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div> `);
      if (store_get($$store_subs ??= {}, "$settingsStore", settingsStore).usageStats) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="brutal-card p-6"><div class="flex items-start gap-4 mb-6"><div class="p-3 bg-secondary border-2 border-black dark:border-white">`);
        Activity($$renderer2, { class: "w-6 h-6" });
        $$renderer2.push(`<!----></div> <div><h3 class="text-xl font-black uppercase">Usage Statistics</h3> <p class="text-sm text-muted-foreground mt-1">Monitor your AI token consumption.</p></div></div> <div class="grid grid-cols-1 md:grid-cols-3 gap-4"><div class="p-4 border-2 border-black dark:border-white bg-secondary/20"><p class="text-xs font-bold uppercase text-muted-foreground">Total Requests</p> <p class="text-2xl font-black font-mono mt-1">${escape_html(store_get($$store_subs ??= {}, "$settingsStore", settingsStore).usageStats.total_requests)}</p></div> <div class="p-4 border-2 border-black dark:border-white bg-secondary/20"><p class="text-xs font-bold uppercase text-muted-foreground">Tokens Used</p> <p class="text-2xl font-black font-mono mt-1">${escape_html(store_get($$store_subs ??= {}, "$settingsStore", settingsStore).usageStats.total_tokens?.toLocaleString() || 0)}</p></div> <div class="p-4 border-2 border-black dark:border-white bg-secondary/20"><p class="text-xs font-bold uppercase text-muted-foreground">Est. Cost</p> <p class="text-2xl font-black font-mono mt-1">$${escape_html(store_get($$store_subs ??= {}, "$settingsStore", settingsStore).usageStats.cost_estimate?.toFixed(4) || "0.0000")}</p></div></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> `);
      NotificationSettings($$renderer2);
      $$renderer2.push(`<!---->`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState$2 = {
  templates: [],
  categories: [],
  isLoading: false,
  error: null
};
function createWorkflowStore() {
  const { subscribe, set, update } = writable(initialState$2);
  return {
    subscribe,
    async loadTemplates(params) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const response = await api.workflow.listTemplates(params);
        const templates = response.templates || [];
        update((state) => ({
          ...state,
          templates,
          isLoading: false
        }));
        return { success: true, templates };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load templates";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async loadCategories() {
      try {
        const response = await api.workflow.getCategories();
        const categories = response.categories || [];
        update((state) => ({
          ...state,
          categories
        }));
        return { success: true, categories };
      } catch (error) {
        logger.error("Failed to load categories", error);
        return { success: false, error: error.detail };
      }
    },
    async createTemplate(templateData) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const newTemplate = await api.workflow.createTemplate(templateData);
        update((state) => ({
          ...state,
          templates: [newTemplate, ...state.templates],
          isLoading: false
        }));
        return { success: true, template: newTemplate };
      } catch (error) {
        const errorMessage = error.detail || "Failed to create template";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async generateTemplate(description, category) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const newTemplate = await api.workflow.generate({ description, category });
        update((state) => ({
          ...state,
          templates: [newTemplate, ...state.templates],
          isLoading: false
        }));
        return { success: true, template: newTemplate };
      } catch (error) {
        const errorMessage = error.detail || "Failed to generate template";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async executeWorkflow(templateId, options) {
      try {
        const response = await api.workflow.execute({
          templateId,
          startDate: options.startDate,
          priority: options.priority,
          customTitle: options.customTitle
        });
        return { success: true, ...response };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to execute workflow" };
      }
    },
    async deleteTemplate(templateId) {
      try {
        await api.workflow.deleteTemplate(templateId);
        update((state) => ({
          ...state,
          templates: state.templates.filter((t) => t.id !== templateId)
        }));
        return { success: true };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to delete template" };
      }
    }
  };
}
const workflowStore = createWorkflowStore();
function WorkflowTemplatesView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let searchQuery = "";
    let selectedCategory = "all";
    let filteredTemplates = store_get($$store_subs ??= {}, "$workflowStore", workflowStore).templates.filter((t) => {
      const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase()) || t.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === "all";
      return matchesSearch && matchesCategory;
    });
    $$renderer2.push(`<div class="space-y-6"><div class="flex flex-col md:flex-row md:items-center justify-between gap-4"><div><h2 class="text-3xl font-black uppercase tracking-tighter">Workflow Templates</h2> <p class="text-muted-foreground font-mono text-sm mt-1">Automate your processes with AI-generated workflows.</p></div> <button class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2">`);
    Sparkles($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Generate New</button></div> <div class="flex flex-col md:flex-row gap-4"><div class="relative flex-1">`);
    Search($$renderer2, {
      class: "absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground"
    });
    $$renderer2.push(`<!----> <input type="text"${attr("value", searchQuery)} placeholder="Search templates..." class="w-full pl-9 pr-4 py-2 bg-white dark:bg-black border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-0"/></div> <div class="flex gap-2 overflow-x-auto pb-2 md:pb-0"><button${attr_class(`px-4 py-2 border-2 border-black dark:border-white text-sm font-bold uppercase whitespace-nowrap transition-all ${stringify(
      "bg-black text-white dark:bg-white dark:text-black"
    )}`)}>All</button> <!--[-->`);
    const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$workflowStore", workflowStore).categories);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let category = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-4 py-2 border-2 border-black dark:border-white text-sm font-bold uppercase whitespace-nowrap transition-all ${stringify(selectedCategory === category ? "bg-black text-white dark:bg-white dark:text-black" : "bg-white text-black dark:bg-black dark:text-white hover:bg-secondary")}`)}>${escape_html(category)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    if (store_get($$store_subs ??= {}, "$workflowStore", workflowStore).isLoading) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex items-center justify-center py-12"><div class="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full"></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (filteredTemplates.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-center py-12 border-2 border-dashed border-black/20 dark:border-white/20"><p class="text-muted-foreground font-mono">No templates found.</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"><!--[-->`);
        const each_array_1 = ensure_array_like(filteredTemplates);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let template = each_array_1[$$index_1];
          $$renderer2.push(`<div class="brutal-card group flex flex-col h-full bg-white dark:bg-black p-6 transition-all hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:hover:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]"><div class="flex items-start justify-between mb-4"><div class="px-2 py-1 bg-secondary border border-black dark:border-white text-xs font-bold uppercase">${escape_html(template.category)}</div> `);
          if (!template.isSystem) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="text-muted-foreground hover:text-red-500 transition-colors">`);
            Trash_2($$renderer2, { class: "w-4 h-4" });
            $$renderer2.push(`<!----></button>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div> <h3 class="text-xl font-black uppercase leading-tight mb-2">${escape_html(template.name)}</h3> <p class="text-sm text-muted-foreground line-clamp-3 mb-4 flex-1">${escape_html(template.description)}</p> <div class="space-y-4"><div class="flex items-center gap-4 text-xs font-mono border-t border-black/10 dark:border-white/10 pt-4"><div class="flex items-center gap-1">`);
          Clock($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----> ${escape_html(template.totalEstimatedMinutes)}m</div> <div class="flex items-center gap-1">`);
          Arrow_right($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----> ${escape_html(template.steps.length)} steps</div></div> <button class="w-full brutal-btn bg-primary text-primary-foreground flex items-center justify-center gap-2 py-2">`);
          Play($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----> Start Workflow</button></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState$1 = {
  profile: null,
  insights: [],
  unlockStatus: null,
  isLoading: false,
  error: null
};
function createShadowStore() {
  const { subscribe, set, update } = writable(initialState$1);
  return {
    subscribe,
    async loadAll() {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        const [insightsRes, unlockRes] = await Promise.all([
          api.shadow.getInsights(),
          api.shadow.getUnlockStatus()
        ]);
        const profile = {
          archetypes: {
            primary: "The Creator",
            secondary: "The Ruler",
            shadow: "The Perfectionist"
          },
          traits: ["High Standards", "Control", "Visionary"],
          integration_level: 45,
          last_analysis: (/* @__PURE__ */ new Date()).toISOString()
        };
        update((state) => ({
          ...state,
          profile,
          insights: insightsRes.insights || [],
          unlockStatus: unlockRes || { isUnlocked: false, progress: 0, requirements: [] },
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load shadow work data";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async analyze() {
      update((state) => ({ ...state, isLoading: true }));
      try {
        const result = await api.shadow.analyze({});
        update((state) => ({
          ...state,
          insights: [...result.new_insights || [], ...state.insights],
          isLoading: false
        }));
        return { success: true, result };
      } catch (error) {
        const errorMessage = error.detail || "Analysis failed";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async acknowledgeInsight(insightId) {
      try {
        await api.shadow.acknowledgeInsight(insightId);
        update((state) => ({
          ...state,
          insights: state.insights.map(
            (i) => i.id === insightId ? { ...i, acknowledged: true } : i
          )
        }));
        return { success: true };
      } catch (error) {
        return { success: false, error: error.detail };
      }
    }
  };
}
const shadowStore = createShadowStore();
function ShadowView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let profile = store_get($$store_subs ??= {}, "$shadowStore", shadowStore).profile;
    let insights = store_get($$store_subs ??= {}, "$shadowStore", shadowStore).insights;
    let unlockStatus = store_get($$store_subs ??= {}, "$shadowStore", shadowStore).unlockStatus;
    let isLoading = store_get($$store_subs ??= {}, "$shadowStore", shadowStore).isLoading;
    $$renderer2.push(`<div class="h-full flex flex-col"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10"><div class="flex items-center gap-3"><div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">`);
    Ghost($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></div> <div><h2 class="text-2xl font-black uppercase tracking-tighter">Shadow Work</h2> <p class="text-sm font-bold text-muted-foreground">Archetype Analysis &amp; Integration</p></div></div> <button class="brutal-btn bg-black text-white dark:bg-white dark:text-black flex items-center gap-2"${attr("disabled", isLoading, true)}>`);
    if (isLoading) {
      $$renderer2.push("<!--[-->");
      Loader_circle($$renderer2, { class: "w-4 h-4 animate-spin" });
      $$renderer2.push(`<!----> Analyzing...`);
    } else {
      $$renderer2.push("<!--[!-->");
      Sparkles($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> New Analysis`);
    }
    $$renderer2.push(`<!--]--></button></div> <div class="flex-1 overflow-y-auto p-6 space-y-8">`);
    if (isLoading && !profile) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="h-full flex items-center justify-center">`);
      Loader_circle($$renderer2, { class: "w-8 h-8 animate-spin" });
      $$renderer2.push(`<!----></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (unlockStatus && !unlockStatus.isUnlocked) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="brutal-card p-8 bg-zinc-900 text-white relative overflow-hidden"><div class="absolute top-0 right-0 p-8 opacity-10">`);
        Lock($$renderer2, { class: "w-32 h-32" });
        $$renderer2.push(`<!----></div> <div class="relative z-10 max-w-2xl"><h3 class="text-2xl font-black uppercase tracking-tighter mb-4 flex items-center gap-3">`);
        Lock($$renderer2, { class: "w-6 h-6" });
        $$renderer2.push(`<!----> Shadow Mode Locked</h3> <p class="text-lg font-medium mb-6 opacity-90">Complete more tasks and maintain focus to unlock deep psychological insights.</p> <div class="space-y-4"><div class="flex justify-between text-sm font-bold uppercase"><span>Progress to Unlock</span> <span>${escape_html(Math.round(unlockStatus.progress * 100))}%</span></div> <div class="h-6 w-full border-2 border-white bg-black p-0.5"><div class="h-full bg-white transition-all duration-500"${attr_style(`width: ${stringify(unlockStatus.progress * 100)}%`)}></div></div> <div class="flex flex-wrap gap-2 mt-4"><!--[-->`);
        const each_array = ensure_array_like(unlockStatus.requirements);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let req = each_array[$$index];
          $$renderer2.push(`<span class="text-xs font-bold uppercase px-2 py-1 border border-white/50 bg-white/10">${escape_html(req)}</span>`);
        }
        $$renderer2.push(`<!--]--></div></div></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (profile) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="grid grid-cols-1 lg:grid-cols-3 gap-6"><div class="brutal-card p-6 bg-primary text-primary-foreground flex flex-col justify-between min-h-[200px]"><div><span class="text-xs font-black uppercase opacity-70">Primary Archetype</span> <h3 class="text-3xl font-black uppercase tracking-tighter mt-1">${escape_html(profile.archetypes.primary)}</h3></div> <div class="mt-4">`);
          Brain($$renderer2, { class: "w-12 h-12 opacity-80" });
          $$renderer2.push(`<!----></div></div> <div class="brutal-card p-6 bg-black text-white dark:bg-white dark:text-black flex flex-col justify-between min-h-[200px]"><div><span class="text-xs font-black uppercase opacity-70">Shadow Archetype</span> <h3 class="text-3xl font-black uppercase tracking-tighter mt-1">${escape_html(profile.archetypes.shadow)}</h3></div> <div class="mt-4">`);
          Ghost($$renderer2, { class: "w-12 h-12 opacity-80" });
          $$renderer2.push(`<!----></div></div> <div class="brutal-card p-6 flex flex-col justify-between min-h-[200px]"><div><span class="text-xs font-black uppercase text-muted-foreground">Integration Level</span> <div class="flex items-end gap-2 mt-1"><h3 class="text-5xl font-black tracking-tighter">${escape_html(profile.integration_level)}%</h3></div></div> <div class="w-full bg-secondary h-4 border-2 border-black dark:border-white mt-4"><div class="h-full bg-green-500"${attr_style(`width: ${stringify(profile.integration_level)}%`)}></div></div></div></div> <div class="space-y-4"><h3 class="text-xl font-black uppercase tracking-tight flex items-center gap-2">`);
          Sparkles($$renderer2, { class: "w-5 h-5" });
          $$renderer2.push(`<!----> Daily Insights</h3> `);
          if (insights.length === 0) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="p-8 border-2 border-black dark:border-white border-dashed text-center opacity-60"><p class="font-bold uppercase">No insights generated yet.</p> <button class="text-sm underline mt-2">Run analysis</button></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 gap-4"><!--[-->`);
            const each_array_1 = ensure_array_like(insights);
            for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
              let insight = each_array_1[$$index_1];
              $$renderer2.push(`<div${attr_class(`brutal-card p-6 flex flex-col gap-4 ${stringify(insight.acknowledged ? "opacity-60 bg-secondary/20" : "bg-background")}`)}><div class="flex items-start justify-between"><span class="text-xs font-black uppercase px-2 py-0.5 border border-black dark:border-white bg-secondary">${escape_html(insight.type)}</span> <span class="text-xs font-bold text-muted-foreground">${escape_html(new Date(insight.created_at).toLocaleDateString())}</span></div> <div><h4 class="text-lg font-black uppercase tracking-tight mb-2">${escape_html(insight.title)}</h4> <p class="text-sm font-medium leading-relaxed text-muted-foreground">${escape_html(insight.description)}</p></div> `);
              if (!insight.acknowledged) {
                $$renderer2.push("<!--[-->");
                $$renderer2.push(`<button class="mt-auto self-start brutal-btn bg-white text-black text-xs py-2">Acknowledge</button>`);
              } else {
                $$renderer2.push("<!--[!-->");
                $$renderer2.push(`<div class="mt-auto flex items-center gap-2 text-xs font-bold text-green-600 uppercase">`);
                Refresh_cw($$renderer2, { class: "w-3 h-3" });
                $$renderer2.push(`<!----> Integrated</div>`);
              }
              $$renderer2.push(`<!--]--></div>`);
            }
            $$renderer2.push(`<!--]--></div>`);
          }
          $$renderer2.push(`<!--]--></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
const initialState = {
  entries: [],
  activeEntry: null,
  stats: null,
  isLoading: false,
  error: null
};
function createTimeStore() {
  const { subscribe, set, update } = writable(initialState);
  return {
    subscribe,
    async loadEntries(limit = 50) {
      update((state) => ({ ...state, isLoading: true, error: null }));
      try {
        if (!isOnline()) {
          const entries2 = await offlineTimeEntries.getAll();
          update((state) => ({
            ...state,
            entries: entries2,
            isLoading: false
          }));
          return { success: true, entries: entries2 };
        }
        const response = await api.timeEntries.list({ limit });
        const entries = response.entries || [];
        await clearOfflineStore(OFFLINE_STORES.TIME_ENTRIES);
        for (const entry of entries) {
          await offlineTimeEntries.save(entry);
        }
        update((state) => ({
          ...state,
          entries,
          isLoading: false
        }));
        return { success: true, entries };
      } catch (error) {
        const errorMessage = error.detail || "Failed to load time entries";
        update((state) => ({
          ...state,
          isLoading: false,
          error: errorMessage
        }));
        return { success: false, error: errorMessage };
      }
    },
    async loadActiveEntry() {
      try {
        if (!isOnline()) {
          const entries = await offlineTimeEntries.getAll();
          const entry2 = entries.find((item) => !item.endTime) || null;
          update((state) => ({
            ...state,
            activeEntry: entry2
          }));
          return { success: true, entry: entry2 };
        }
        const entry = await api.timeEntries.active();
        update((state) => ({
          ...state,
          activeEntry: entry
        }));
        return { success: true, entry };
      } catch (error) {
        if (error.status !== 404) {
          logger.error("Failed to load active entry", error);
        }
        update((state) => ({ ...state, activeEntry: null }));
        return { success: false, error: error.detail };
      }
    },
    async startTimer(data) {
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          const offlineEntry = {
            id: crypto.randomUUID?.() || `offline-${Date.now()}`,
            userId: "offline",
            taskId: data.taskId,
            projectId: data.projectId,
            description: data.description,
            startTime: now,
            billable: data.billable ?? false
          };
          await offlineTimeEntries.save(offlineEntry);
          await queueOperation({
            type: "create",
            entity: "timeEntry",
            data,
            endpoint: "/time-entries"
          });
          update((state) => ({
            ...state,
            activeEntry: offlineEntry,
            entries: [offlineEntry, ...state.entries]
          }));
          return { success: true, entry: offlineEntry };
        }
        const newEntry = await api.timeEntries.create(data);
        await offlineTimeEntries.save(newEntry);
        update((state) => ({
          ...state,
          activeEntry: newEntry,
          entries: [newEntry, ...state.entries]
        }));
        return { success: true, entry: newEntry };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to start timer" };
      }
    },
    async stopTimer(entryId) {
      try {
        if (!isOnline()) {
          const now = (/* @__PURE__ */ new Date()).toISOString();
          let updatedEntry2 = null;
          update((state) => {
            const entries = state.entries.map((entry) => {
              if (entry.id !== entryId) return entry;
              updatedEntry2 = {
                ...entry,
                endTime: now,
                durationSeconds: entry.startTime ? Math.max(0, Math.floor((Date.parse(now) - Date.parse(entry.startTime)) / 1e3)) : entry.durationSeconds
              };
              return updatedEntry2;
            });
            return {
              ...state,
              activeEntry: null,
              entries
            };
          });
          if (updatedEntry2) {
            await offlineTimeEntries.save(updatedEntry2);
          }
          await queueOperation({
            type: "create",
            entity: "timeEntry",
            data: {},
            endpoint: `/time-entries/${entryId}/stop`
          });
          return { success: true, entry: updatedEntry2 };
        }
        const updatedEntry = await api.timeEntries.stop(entryId);
        await offlineTimeEntries.save(updatedEntry);
        update((state) => ({
          ...state,
          activeEntry: null,
          entries: state.entries.map((e) => e.id === entryId ? updatedEntry : e)
        }));
        return { success: true, entry: updatedEntry };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to stop timer" };
      }
    },
    async deleteEntry(entryId) {
      try {
        if (!isOnline()) {
          await offlineTimeEntries.delete(entryId);
          await queueOperation({
            type: "delete",
            entity: "timeEntry",
            data: {},
            endpoint: `/time-entries/${entryId}`
          });
          update((state) => ({
            ...state,
            entries: state.entries.filter((e) => e.id !== entryId),
            activeEntry: state.activeEntry?.id === entryId ? null : state.activeEntry
          }));
          return { success: true };
        }
        await api.timeEntries.delete(entryId);
        update((state) => ({
          ...state,
          entries: state.entries.filter((e) => e.id !== entryId),
          activeEntry: state.activeEntry?.id === entryId ? null : state.activeEntry
        }));
        return { success: true };
      } catch (error) {
        return { success: false, error: error.detail || "Failed to delete entry" };
      }
    }
  };
}
const timeStore = createTimeStore();
function TimeTrackingView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let description = "";
    let selectedProjectId = "";
    let isBillable = false;
    let elapsedTime = "00:00:00";
    let activeEntry = store_get($$store_subs ??= {}, "$timeStore", timeStore).activeEntry;
    onDestroy(() => {
    });
    function formatDuration(seconds) {
      if (!seconds) return "00:00:00";
      const h = Math.floor(seconds / 3600).toString().padStart(2, "0");
      const m = Math.floor(seconds % 3600 / 60).toString().padStart(2, "0");
      const s = (seconds % 60).toString().padStart(2, "0");
      return `${h}:${m}:${s}`;
    }
    function formatTime(dateStr) {
      return new Date(dateStr).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }
    $$renderer2.push(`<div class="space-y-6"><div class="flex flex-col md:flex-row md:items-center justify-between gap-4"><div><h2 class="text-3xl font-black uppercase tracking-tighter">Time Tracking</h2> <p class="text-muted-foreground font-mono text-sm mt-1">Track your work hours and billable time.</p></div></div> <div class="brutal-card bg-white dark:bg-black p-6 border-2 border-black dark:border-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] dark:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)]">`);
    if (activeEntry) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex flex-col md:flex-row items-center justify-between gap-6"><div class="flex-1 text-center md:text-left"><p class="text-sm font-bold uppercase text-muted-foreground mb-1">Current Task</p> <h3 class="text-xl font-black uppercase">${escape_html(activeEntry.description || "No description")}</h3> `);
      if (activeEntry.projectId) {
        $$renderer2.push("<!--[-->");
        const project = store_get($$store_subs ??= {}, "$projectsStore", projectsStore).projects.find((p) => p.id === activeEntry.projectId);
        $$renderer2.push(`<div class="inline-block mt-2 px-2 py-1 bg-secondary border border-black dark:border-white text-xs font-bold uppercase">${escape_html(project?.name || "Unknown Project")}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="text-4xl font-mono font-black tracking-widest">${escape_html(elapsedTime)}</div> <button class="brutal-btn bg-red-500 text-white border-black w-full md:w-auto flex items-center justify-center gap-2 py-3 px-6">`);
      Square($$renderer2, { class: "w-5 h-5 fill-current" });
      $$renderer2.push(`<!----> Stop Timer</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="flex flex-col md:flex-row gap-4 items-end"><div class="flex-1 w-full space-y-2"><label for="timeDescription" class="text-xs font-bold uppercase">Description</label> <input id="timeDescription" type="text"${attr("value", description)} placeholder="What are you working on?" class="w-full p-3 bg-secondary border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"/></div> <div class="w-full md:w-64 space-y-2"><label for="timeProject" class="text-xs font-bold uppercase">Project</label> `);
      $$renderer2.select(
        {
          id: "timeProject",
          value: selectedProjectId,
          class: "w-full p-3 bg-white dark:bg-black border-2 border-black dark:border-white font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary appearance-none"
        },
        ($$renderer3) => {
          $$renderer3.option({ value: "" }, ($$renderer4) => {
            $$renderer4.push(`No Project`);
          });
          $$renderer3.push(`<!--[-->`);
          const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$projectsStore", projectsStore).projects);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let project = each_array[$$index];
            $$renderer3.option({ value: project.id }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(project.name)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</div> <div class="flex items-center gap-2 pb-3"><input type="checkbox" id="billable"${attr("checked", isBillable, true)} class="w-5 h-5 border-2 border-black dark:border-white rounded-none focus:ring-0 checked:bg-black dark:checked:bg-white"/> <label for="billable" class="text-sm font-bold uppercase cursor-pointer select-none">Billable</label></div> <button class="brutal-btn bg-primary text-primary-foreground border-black w-full md:w-auto flex items-center justify-center gap-2 py-3 px-6"${attr("disabled", !description, true)}>`);
      Play($$renderer2, { class: "w-5 h-5 fill-current" });
      $$renderer2.push(`<!----> Start</button></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="space-y-4"><h3 class="text-xl font-black uppercase tracking-tight border-b-2 border-black dark:border-white pb-2">Recent Entries</h3> `);
    if (store_get($$store_subs ??= {}, "$timeStore", timeStore).isLoading && store_get($$store_subs ??= {}, "$timeStore", timeStore).entries.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex justify-center py-8"><div class="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full"></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (store_get($$store_subs ??= {}, "$timeStore", timeStore).entries.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-center py-8 text-muted-foreground font-mono">No time entries found.</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="space-y-3"><!--[-->`);
        const each_array_1 = ensure_array_like(store_get($$store_subs ??= {}, "$timeStore", timeStore).entries);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let entry = each_array_1[$$index_1];
          $$renderer2.push(`<div class="brutal-card p-4 bg-white dark:bg-black flex flex-col md:flex-row md:items-center justify-between gap-4 hover:translate-x-[2px] hover:translate-y-[2px] transition-transform"><div class="flex-1"><div class="flex items-center gap-2 mb-1"><span class="font-bold uppercase">${escape_html(entry.description || "No description")}</span> `);
          if (entry.billable) {
            $$renderer2.push("<!--[-->");
            Dollar_sign($$renderer2, { class: "w-3 h-3 text-green-600" });
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div> <div class="flex items-center gap-3 text-xs text-muted-foreground font-mono">`);
          if (entry.projectId) {
            $$renderer2.push("<!--[-->");
            const project = store_get($$store_subs ??= {}, "$projectsStore", projectsStore).projects.find((p) => p.id === entry.projectId);
            $$renderer2.push(`<span class="flex items-center gap-1">`);
            Briefcase($$renderer2, { class: "w-3 h-3" });
            $$renderer2.push(`<!----> ${escape_html(project?.name || "Unknown")}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <span class="flex items-center gap-1">`);
          Clock($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----> ${escape_html(formatTime(entry.startTime))} - ${escape_html(entry.endTime ? formatTime(entry.endTime) : "Now")}</span></div></div> <div class="flex items-center justify-between md:justify-end gap-4"><span class="font-mono font-black text-lg">${escape_html(formatDuration(entry.durationSeconds))}</span> <button class="p-2 hover:text-red-500 transition-colors">`);
          Trash_2($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ToastStack($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let toasts = store_get($$store_subs ??= {}, "$toast", toast);
    function getBg(type) {
      switch (type) {
        case "success":
          return "bg-green-500 text-white";
        case "warning":
          return "bg-amber-500 text-black";
        case "error":
          return "bg-red-600 text-white";
        default:
          return "bg-black text-white";
      }
    }
    $$renderer2.push(`<div class="fixed right-4 top-4 z-[200] flex flex-col gap-3 max-w-sm"><!--[-->`);
    const each_array = ensure_array_like(toasts);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let t = each_array[$$index];
      $$renderer2.push(`<div${attr_class(`flex items-start gap-3 p-3 brutal-border brutal-shadow ${getBg(t.type)} animate-in slide-in-from-right duration-200`)}><div class="flex-1 space-y-2"><div class="text-sm font-bold leading-snug uppercase tracking-wide">${escape_html(t.message)}</div> `);
      if (t.action) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button type="button" class="text-[11px] font-black uppercase tracking-wider px-2 py-1 border-2 border-current hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white transition-colors">${escape_html(t.action.label)}</button>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <button type="button" class="p-1 border-2 border-current hover:bg-white hover:text-black dark:hover:bg-black dark:hover:text-white transition-colors flex-shrink-0" aria-label="Dismiss">`);
      X($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----></button></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function ErrorBoundary($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      fallback = "An error occurred",
      showDetails = false,
      children
    } = $$props;
    onDestroy(() => {
    });
    {
      $$renderer2.push("<!--[!-->");
      children($$renderer2);
      $$renderer2.push(`<!---->`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function PomodoroTimer($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let {
      duration = 25 * 60,
      // 25 minutes in seconds
      breakDuration = 5 * 60,
      // 5 minutes
      onComplete
    } = $$props;
    let timeLeft = duration;
    let sessions = 0;
    let progress = (duration - timeLeft) / duration * 100;
    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;
    let displayTime = `${minutes}:${seconds.toString().padStart(2, "0")}`;
    onDestroy(() => {
    });
    $$renderer2.push(`<div class="pomodoro-timer brutal-card bg-card p-8 relative overflow-hidden"><div class="absolute inset-0 pointer-events-none opacity-[0.03] bg-grid-pattern"></div> <div class="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-white/5 to-transparent h-1 bg-[length:100%_4px] animate-scan-line"></div> <div class="relative z-10 text-center mb-8 border-b-2 border-border pb-6"><h2 class="text-3xl font-black uppercase tracking-tighter mb-2">${escape_html("🎯 Focus Protocol")}</h2> <div class="flex items-center justify-center gap-4"><p class="text-[10px] font-bold uppercase tracking-widest text-muted-foreground bg-secondary px-2 py-0.5">Sessions: ${escape_html(sessions.toString().padStart(2, "0"))}</p> <p${attr_class(`text-[10px] font-bold uppercase tracking-widest ${stringify("text-system-red")}`)}>Status: ${escape_html("IDLE")}</p></div></div> <div class="relative z-10 flex flex-col items-center justify-center mb-8"><div class="text-8xl font-mono font-black tracking-widest mb-6 tabular-nums">${escape_html(displayTime)}</div> <div class="w-full h-8 border-2 border-border bg-secondary relative overflow-hidden"><div class="h-full bg-terminal-green transition-all duration-1000 ease-linear"${attr_style(`width: ${stringify(progress)}%`)}></div> <div class="absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.1)_1px,transparent_1px)] bg-[size:20px_100%]"></div></div> <div class="w-full flex justify-between mt-1"><span class="text-[9px] font-bold uppercase text-muted-foreground">0%</span> <span class="text-[9px] font-bold uppercase text-muted-foreground">Progress: ${escape_html(Math.round(progress))}%</span> <span class="text-[9px] font-bold uppercase text-muted-foreground">100%</span></div></div> <div class="relative z-10 flex flex-col sm:flex-row justify-center gap-4">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<button class="btn btn-primary px-10 py-4 text-xl">▶ Initiate</button>`);
    }
    $$renderer2.push(`<!--]--> <button class="btn btn-secondary px-10 py-4 text-xl">↻ Reset</button></div> <div class="relative z-10 mt-8 pt-6 border-t-2 border-border"><p class="text-[10px] font-bold uppercase tracking-widest text-center mb-4 text-muted-foreground">Preset Intervals</p> <div class="flex justify-center flex-wrap gap-3"><button${attr_class(`btn btn-sm ${stringify(duration === 25 * 60 ? "bg-terminal-green text-black" : "bg-card")}`)}>25M</button> <button${attr_class(`btn btn-sm ${stringify(duration === 50 * 60 ? "bg-terminal-green text-black" : "bg-card")}`)}>50M</button> <button${attr_class(`btn btn-sm ${stringify(duration === 90 * 60 ? "bg-terminal-green text-black" : "bg-card")}`)}>90M</button></div></div></div>`);
    bind_props($$props, { duration });
  });
}
function PomodoroView($$renderer) {
  $$renderer.push(`<div class="space-y-6"><div><h2 class="text-3xl font-black uppercase tracking-tighter">Focus Protocol</h2> <p class="text-muted-foreground font-mono text-sm mt-1">Deep focus sessions using the Pomodoro technique.</p></div> <div class="max-w-2xl mx-auto">`);
  PomodoroTimer($$renderer, {});
  $$renderer.push(`<!----></div> <div class="brutal-card bg-terminal-green/10 p-6 border-2 border-terminal-green"><h3 class="text-lg font-black uppercase mb-3 text-terminal-green">Why use the Focus Protocol?</h3> <ul class="space-y-2 text-sm font-mono"><li class="flex items-start gap-2"><span class="text-terminal-green font-bold">[01]</span> <span>Reduces cognitive load by breaking work into segments.</span></li> <li class="flex items-start gap-2"><span class="text-terminal-green font-bold">[02]</span> <span>Prevents burnout with mandatory short and long breaks.</span></li> <li class="flex items-start gap-2"><span class="text-terminal-green font-bold">[03]</span> <span>Improves estimation of task duration over time.</span></li></ul></div></div>`);
}
function InfraView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="h-full flex flex-col relative overflow-hidden"><div class="flex-shrink-0 p-6 border-b-2 border-black dark:border-white flex items-center justify-between bg-background z-10"><div class="flex items-center gap-3"><div class="p-2 border-2 border-black dark:border-white bg-secondary text-secondary-foreground">`);
    Server($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></div> <div><h2 class="text-2xl font-black uppercase tracking-tighter">Infrastructure</h2> <p class="text-sm font-bold text-muted-foreground">System Status &amp; Logs</p></div></div> <button class="brutal-btn bg-white text-black flex items-center gap-2">`);
    Refresh_cw($$renderer2, {
      class: `w-4 h-4 ${stringify("")}`
    });
    $$renderer2.push(`<!----> Refresh</button></div> <div class="flex-1 overflow-y-auto p-6 space-y-6"><div class="grid grid-cols-1 md:grid-cols-3 gap-4"><div class="brutal-card p-4"><div class="flex items-center justify-between mb-2"><span class="text-xs font-black uppercase text-muted-foreground">System Health</span> `);
    Activity($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----></div> <div class="flex items-center gap-2">`);
    {
      $$renderer2.push("<!--[!-->");
      Triangle_alert($$renderer2, { class: "w-6 h-6 text-red-500" });
      $$renderer2.push(`<!----> <span class="text-xl font-black uppercase">${escape_html("Unknown")}</span>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="brutal-card p-4"><div class="flex items-center justify-between mb-2"><span class="text-xs font-black uppercase text-muted-foreground">Uptime</span> `);
    Clock($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----></div> <div class="text-xl font-black font-mono">${escape_html(0)} min</div></div> <div class="brutal-card p-4"><div class="flex items-center justify-between mb-2"><span class="text-xs font-black uppercase text-muted-foreground">Database</span> `);
    Database($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----></div> <div class="text-lg font-bold uppercase">${escape_html("Checking...")}</div></div></div> <div class="brutal-card flex flex-col h-[500px]"><div class="p-4 border-b-2 border-black dark:border-white bg-secondary flex items-center justify-between"><div class="flex items-center gap-2 font-bold uppercase">`);
    Terminal($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> System Logs</div> <div class="flex border-2 border-black dark:border-white"><button${attr_class(`px-3 py-1 text-xs font-bold uppercase ${stringify(
      "bg-black text-white dark:bg-white dark:text-black"
    )}`)}>Backend</button> <button${attr_class(`px-3 py-1 text-xs font-bold uppercase border-l-2 border-black dark:border-white ${stringify("bg-white text-black hover:bg-gray-200 dark:bg-black dark:text-white dark:hover:bg-gray-800")}`)}>Frontend</button></div></div> <div class="flex-1 overflow-auto p-4 bg-black text-green-400 font-mono text-xs"><pre class="whitespace-pre-wrap">${escape_html("Loading logs...")}</pre></div></div></div></div>`);
  });
}
function N8nHooksView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let workflows = [
      {
        id: "1",
        name: "Prospect Research (L1 Academy)",
        active: true,
        lastRun: "2 hours ago",
        status: "success"
      },
      {
        id: "2",
        name: "LinkedIn Personalization Engine",
        active: true,
        lastRun: "15 mins ago",
        status: "running"
      },
      {
        id: "3",
        name: "Stripe Invoice Reconciliation",
        active: false,
        status: "idle"
      },
      {
        id: "4",
        name: "Lab by Kraliki Provisioning Audit",
        active: true,
        lastRun: "1 day ago",
        status: "failed"
      }
    ];
    function getStatusColor(status) {
      switch (status) {
        case "success":
          return "text-terminal-green";
        case "failed":
          return "text-destructive";
        case "running":
          return "text-primary animate-pulse";
        default:
          return "text-muted-foreground";
      }
    }
    $$renderer2.push(`<div class="p-6 space-y-8 font-mono svelte-l8xqlw"><div class="flex items-center justify-between border-b-4 border-black dark:border-white pb-4 svelte-l8xqlw"><h1 class="text-3xl font-display uppercase tracking-tighter svelte-l8xqlw">Workflow Orchestration</h1> <div class="flex items-center gap-2 bg-terminal-green text-black px-3 py-1 text-xs font-bold svelte-l8xqlw">`);
    Activity($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> SYSTEM LIVE</div></div> <div class="grid gap-4 svelte-l8xqlw"><!--[-->`);
    const each_array = ensure_array_like(workflows);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let workflow = each_array[$$index];
      $$renderer2.push(`<div class="border-2 border-black dark:border-white p-4 transition-all hover:translate-x-1 hover:translate-y-1 shadow-[4px_4px_0_0_rgba(0,0,0,1)] dark:shadow-[4px_4px_0_0_rgba(255,255,255,1)] bg-card svelte-l8xqlw"><div class="flex items-start justify-between svelte-l8xqlw"><div class="space-y-1 svelte-l8xqlw"><div class="flex items-center gap-2 svelte-l8xqlw"><span class="text-lg font-black uppercase svelte-l8xqlw">${escape_html(workflow.name)}</span> `);
      if (!workflow.active) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="bg-muted text-muted-foreground px-2 py-0.5 text-[10px] font-bold svelte-l8xqlw">INACTIVE</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="flex items-center gap-4 text-xs opacity-70 svelte-l8xqlw"><span class="flex items-center gap-1 svelte-l8xqlw">`);
      Clock($$renderer2, { class: "w-3 h-3" });
      $$renderer2.push(`<!----> ${escape_html(workflow.lastRun || "Never run")}</span> <span${attr_class(`flex items-center gap-1 font-bold ${stringify(getStatusColor(workflow.status))}`, "svelte-l8xqlw")}>`);
      if (workflow.status === "success") {
        $$renderer2.push("<!--[-->");
        Check($$renderer2, { class: "w-3 h-3" });
      } else {
        $$renderer2.push("<!--[!-->");
        if (workflow.status === "failed") {
          $$renderer2.push("<!--[-->");
          Circle_alert($$renderer2, { class: "w-3 h-3" });
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--> ${escape_html(workflow.status.toUpperCase())}</span></div></div> <div class="flex items-center gap-2 svelte-l8xqlw"><button class="btn btn-sm btn-primary flex items-center gap-2 svelte-l8xqlw"${attr("disabled", workflow.status === "running", true)}>`);
      Play($$renderer2, { class: "w-3 h-3 fill-current" });
      $$renderer2.push(`<!----> RUN</button> <a href="https://n8n.verduona.io" target="_blank" class="btn btn-sm btn-ghost p-2 svelte-l8xqlw" title="Open in n8n">`);
      External_link($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----></a></div></div></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="mt-8 border-t-2 border-black dark:border-white pt-6 svelte-l8xqlw"><h3 class="text-sm font-black uppercase mb-4 svelte-l8xqlw">Latest Execution Logs</h3> <div class="bg-black text-terminal-green p-4 text-[10px] space-y-1 overflow-x-auto border-2 border-black dark:border-white shadow-[4px_4px_0_0_rgba(0,0,0,1)] svelte-l8xqlw"><p class="svelte-l8xqlw">[2025-12-22 18:35:01] INFO: Triggering flow 'Prospect
                Research'...</p> <p class="svelte-l8xqlw">[2025-12-22 18:35:04] SUCCESS: 14 new leads extracted and pushed
                to CRM.</p> <p class="svelte-l8xqlw">[2025-12-22 18:36:12] WARNING: LinkedIn rate limits detected.
                Throttling engine...</p> <p class="animate-pulse svelte-l8xqlw">_</p></div></div></div>`);
  });
}
function VoiceView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let promptText = "";
    let detectedScenario = [
      {
        id: "1",
        type: "trigger",
        label: "LinkedIn Lead Detected",
        description: "Triggered when a new contact is added."
      },
      {
        id: "2",
        type: "action",
        label: "Prospect Research",
        description: "Enriching lead data via n8n."
      },
      {
        id: "3",
        type: "action",
        label: "Draft DM",
        description: "Creating a personalized connection request."
      }
    ];
    $$renderer2.push(`<div class="h-full flex flex-col bg-background font-mono select-none"><div class="p-4 border-b-4 border-black dark:border-white flex items-center justify-between bg-card shrink-0"><div class="flex items-center gap-2">`);
    Sparkles($$renderer2, { class: "w-6 h-6 fill-terminal-green text-black" });
    $$renderer2.push(`<!----> <h1 class="text-xl font-display uppercase tracking-tighter">VOICE BY KRALIKI ALPHA</h1></div> <div class="flex items-center gap-1 bg-black text-white px-2 py-0.5 text-[10px] font-bold"><span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span> REMOTE ON</div></div> <div class="flex-1 overflow-y-auto p-4 space-y-6"><div class="space-y-4"><div class="relative"><textarea placeholder="DESCRIBE YOUR SCENARIO..." class="w-full h-32 p-4 bg-white dark:bg-black border-2 border-black dark:border-white focus:outline-none focus:shadow-[4px_4px_0px_0px_var(--color-terminal-green)] transition-all uppercase text-sm font-bold">`);
    const $$body = escape_html(promptText);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea> <button${attr_class(`absolute bottom-4 right-4 p-4 rounded-full border-4 border-black dark:border-white transition-all active:scale-95 ${stringify("bg-terminal-green text-black shadow-[4px_4px_0_0_rgba(0,0,0,1)]")}`)}>`);
    Circle($$renderer2, {
      class: `w-8 h-8 ${stringify("")}`
    });
    $$renderer2.push(`<!----></button></div> <p class="text-[10px] text-muted-foreground uppercase text-center font-bold">Hold button to speak</p></div> <div class="space-y-3"><h3 class="text-xs font-black uppercase flex items-center gap-2">`);
    Funnel($$renderer2, { class: "w-3 h-3" });
    $$renderer2.push(`<!----> Detected Logic Chain</h3> <!--[-->`);
    const each_array = ensure_array_like(detectedScenario);
    for (let i = 0, $$length = each_array.length; i < $$length; i++) {
      let step = each_array[i];
      $$renderer2.push(`<div class="border-2 border-black dark:border-white p-3 bg-card shadow-[4px_4px_0_0_rgba(0,0,0,1)] dark:shadow-[4px_4px_0_0_rgba(255,255,255,1)] flex items-center gap-3 transition-transform active:translate-x-1"><div class="text-xs font-black opacity-30">${escape_html(i + 1)}</div> <div class="flex-1"><div class="text-xs font-black uppercase tracking-tight">${escape_html(step.label)}</div> <div class="text-[9px] opacity-60 leading-tight uppercase font-bold">${escape_html(step.description)}</div></div> <div class="p-1 border border-black dark:border-white bg-secondary/20">`);
      if (step.type === "trigger") {
        $$renderer2.push("<!--[-->");
        Sparkles($$renderer2, { class: "w-3 h-3 text-terminal-green" });
      } else {
        $$renderer2.push("<!--[!-->");
        Play($$renderer2, { class: "w-3 h-3" });
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="p-6 border-t-4 border-black dark:border-white bg-card shrink-0"><button class="w-full py-4 border-2 border-black dark:border-white bg-terminal-green text-black font-black uppercase text-sm tracking-widest shadow-[6px_6px_0_0_rgba(0,0,0,1)] active:translate-x-1 active:translate-y-1 active:shadow-none transition-all flex items-center justify-center gap-3">`);
    Check($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----> Activate Protocol</button></div></div>`);
  });
}
function CapturesView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="p-4 space-y-4"><div class="flex items-center justify-between"><div class="flex items-center gap-2">`);
    Paperclip($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----> <span class="text-sm font-bold uppercase tracking-widest">Recent Captures</span></div> <button class="text-xs uppercase font-bold text-muted-foreground hover:text-foreground">Refresh</button></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-8"><div class="animate-pulse text-muted-foreground">Loading captures...</div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function ContextPanel($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let panelState = store_get($$store_subs ??= {}, "$contextPanelStore", contextPanelStore);
    let isOpen = panelState.isOpen;
    let panelType = panelState.type;
    const panelTitles = {
      tasks: "Tasks",
      projects: "Projects",
      knowledge: "Knowledge Base",
      calendar: "Calendar",
      analytics: "Analytics",
      settings: "Settings",
      workflow: "Workflows",
      shadow: "Shadow Work",
      time: "Time Tracking",
      pomodoro: "Focus Protocol",
      infra: "Infrastructure",
      n8n: "Workflows",
      voice: "Voice by Kraliki Remote",
      captures: "Captures"
    };
    if (isOpen) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="fixed inset-0 bg-black/40 z-40 transition-opacity duration-300" role="button" tabindex="-1" aria-label="Close panel"></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div${attr_class("fixed top-0 right-0 h-full w-full md:w-[600px] lg:w-[800px] bg-background z-50 border-l-2 border-black dark:border-white shadow-[-8px_0_0_0_rgba(0,0,0,1)] dark:shadow-[-8px_0_0_0_rgba(255,255,255,1)] transform transition-transform duration-300 flex flex-col", void 0, { "translate-x-full": !isOpen, "translate-x-0": isOpen })}><div class="flex-shrink-0 flex items-center justify-between p-4 border-b-2 border-black dark:border-white bg-card"><div class="flex items-center gap-3"><h2 class="text-xl font-display uppercase tracking-tighter">${escape_html(panelType ? panelTitles[panelType] : "")}</h2> <span class="text-[9px] uppercase font-bold tracking-widest text-muted-foreground opacity-60 hidden md:inline">Manual Mode</span></div> <button type="button" class="btn btn-sm btn-ghost p-2" title="Close panel (ESC)">`);
    X($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></button></div> <div class="flex-1 overflow-y-auto">`);
    if (panelType === "tasks") {
      $$renderer2.push("<!--[-->");
      TasksView($$renderer2);
    } else {
      $$renderer2.push("<!--[!-->");
      if (panelType === "projects") {
        $$renderer2.push("<!--[-->");
        ProjectsView($$renderer2);
      } else {
        $$renderer2.push("<!--[!-->");
        if (panelType === "knowledge") {
          $$renderer2.push("<!--[-->");
          KnowledgeView($$renderer2);
        } else {
          $$renderer2.push("<!--[!-->");
          if (panelType === "calendar") {
            $$renderer2.push("<!--[-->");
            CalendarView($$renderer2);
          } else {
            $$renderer2.push("<!--[!-->");
            if (panelType === "analytics") {
              $$renderer2.push("<!--[-->");
              AnalyticsView($$renderer2);
            } else {
              $$renderer2.push("<!--[!-->");
              if (panelType === "settings") {
                $$renderer2.push("<!--[-->");
                SettingsView($$renderer2);
              } else {
                $$renderer2.push("<!--[!-->");
                if (panelType === "workflow") {
                  $$renderer2.push("<!--[-->");
                  WorkflowTemplatesView($$renderer2);
                } else {
                  $$renderer2.push("<!--[!-->");
                  if (panelType === "shadow") {
                    $$renderer2.push("<!--[-->");
                    ShadowView($$renderer2);
                  } else {
                    $$renderer2.push("<!--[!-->");
                    if (panelType === "time") {
                      $$renderer2.push("<!--[-->");
                      TimeTrackingView($$renderer2);
                    } else {
                      $$renderer2.push("<!--[!-->");
                      if (panelType === "pomodoro") {
                        $$renderer2.push("<!--[-->");
                        PomodoroView($$renderer2);
                      } else {
                        $$renderer2.push("<!--[!-->");
                        if (panelType === "infra") {
                          $$renderer2.push("<!--[-->");
                          InfraView($$renderer2);
                        } else {
                          $$renderer2.push("<!--[!-->");
                          if (panelType === "n8n") {
                            $$renderer2.push("<!--[-->");
                            N8nHooksView($$renderer2);
                          } else {
                            $$renderer2.push("<!--[!-->");
                            if (panelType === "voice") {
                              $$renderer2.push("<!--[-->");
                              VoiceView($$renderer2);
                            } else {
                              $$renderer2.push("<!--[!-->");
                              if (panelType === "captures") {
                                $$renderer2.push("<!--[-->");
                                CapturesView($$renderer2);
                              } else {
                                $$renderer2.push("<!--[!-->");
                              }
                              $$renderer2.push(`<!--]-->`);
                            }
                            $$renderer2.push(`<!--]-->`);
                          }
                          $$renderer2.push(`<!--]-->`);
                        }
                        $$renderer2.push(`<!--]-->`);
                      }
                      $$renderer2.push(`<!--]-->`);
                    }
                    $$renderer2.push(`<!--]-->`);
                  }
                  $$renderer2.push(`<!--]-->`);
                }
                $$renderer2.push(`<!--]-->`);
              }
              $$renderer2.push(`<!--]-->`);
            }
            $$renderer2.push(`<!--]-->`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function OnboardingModal($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]-->`);
  });
}
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let { children } = $$props;
    let user = store_get($$store_subs ??= {}, "$authStore", authStore).user;
    onDestroy(() => {
      logger.info("[Dashboard] WebSocket connection closed");
    });
    ErrorBoundary($$renderer2, {
      fallback: "Critical Failure in Dashboard Kernel",
      children: ($$renderer3) => {
        AssistantShell($$renderer3, {
          user,
          children: ($$renderer4) => {
            children($$renderer4);
            $$renderer4.push(`<!---->`);
          }
        });
      }
    });
    $$renderer2.push(`<!----> `);
    ErrorBoundary($$renderer2, {
      fallback: "Panel Protocol Error",
      children: ($$renderer3) => {
        ContextPanel($$renderer3);
      }
    });
    $$renderer2.push(`<!----> `);
    ToastStack($$renderer2);
    $$renderer2.push(`<!----> `);
    OnboardingModal($$renderer2);
    $$renderer2.push(`<!---->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _layout as default
};

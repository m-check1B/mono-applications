import { s as sanitize_props, a as spread_props, c as slot, g as ensure_array_like, f as stringify } from "../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../chunks/index-server.js";
import { B as Bot } from "../../../../chunks/bot.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { T as Terminal, C as Circle_alert } from "../../../../chunks/terminal.js";
import { S as Settings } from "../../../../chunks/settings.js";
import { S as Sparkles } from "../../../../chunks/sparkles.js";
import { L as Loader_circle } from "../../../../chunks/loader-circle.js";
import { a as attr } from "../../../../chunks/attributes.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function Circle_check_big($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M21.801 10A10 10 0 1 1 17 3.335" }],
    ["path", { "d": "m9 11 3 3L22 4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "circle-check-big" },
    $$sanitized_props,
    {
      /**
       * @component @name CircleCheckBig
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjEuODAxIDEwQTEwIDEwIDAgMSAxIDE3IDMuMzM1IiAvPgogIDxwYXRoIGQ9Im05IDExIDMgM0wyMiA0IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/circle-check-big
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
function Message_square($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "message-square" },
    $$sanitized_props,
    {
      /**
       * @component @name MessageSquare
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMjEgMTVhMiAyIDAgMCAxLTIgMkg3bC00IDRWNWEyIDIgMCAwIDEgMi0yaDE0YTIgMiAwIDAgMSAyIDJ6IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/message-square
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
function Power($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M12 2v10" }],
    ["path", { "d": "M18.4 6.6a9 9 0 1 1-12.77.04" }]
  ];
  Icon($$renderer, spread_props([
    { name: "power" },
    $$sanitized_props,
    {
      /**
       * @component @name Power
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTIgMnYxMCIgLz4KICA8cGF0aCBkPSJNMTguNCA2LjZhOSA5IDAgMSAxLTEyLjc3LjA0IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/power
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
function Wrench($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
      }
    ]
  ];
  Icon($$renderer, spread_props([
    { name: "wrench" },
    $$sanitized_props,
    {
      /**
       * @component @name Wrench
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTQuNyA2LjNhMSAxIDAgMCAwIDAgMS40bDEuNiAxLjZhMSAxIDAgMCAwIDEuNCAwbDMuNzctMy43N2E2IDYgMCAwIDEtNy45NCA3Ljk0bC02LjkxIDYuOTFhMi4xMiAyLjEyIDAgMCAxLTMtM2w2LjkxLTYuOTFhNiA2IDAgMCAxIDcuOTQtNy45NGwtMy43NiAzLjc2eiIgLz4KPC9zdmc+Cg==) - https://lucide.dev/icons/wrench
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
var EventType = /* @__PURE__ */ ((EventType2) => {
  EventType2["CONNECTION_ESTABLISHED"] = "connection_established";
  EventType2["AGENT_INITIALIZED"] = "agent_initialized";
  EventType2["WORKSPACE_INFO"] = "workspace_info";
  EventType2["PROCESSING"] = "processing";
  EventType2["AGENT_THINKING"] = "agent_thinking";
  EventType2["TOOL_CALL"] = "tool_call";
  EventType2["TOOL_RESULT"] = "tool_result";
  EventType2["AGENT_RESPONSE"] = "agent_response";
  EventType2["AGENT_RESPONSE_INTERRUPTED"] = "agent_response_interrupted";
  EventType2["STREAM_COMPLETE"] = "stream_complete";
  EventType2["ERROR"] = "error";
  EventType2["SYSTEM"] = "system";
  EventType2["PONG"] = "pong";
  EventType2["UPLOAD_SUCCESS"] = "upload_success";
  EventType2["BROWSER_USE"] = "browser_use";
  EventType2["FILE_EDIT"] = "file_edit";
  EventType2["USER_MESSAGE"] = "user_message";
  EventType2["PROMPT_GENERATED"] = "prompt_generated";
  return EventType2;
})(EventType || {});
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let connectionState = {
      isConnecting: false
    };
    let eventLog = [];
    onDestroy(() => {
    });
    function formatTime(date) {
      return new Intl.DateTimeFormat("en-US", {
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
      }).format(date);
    }
    function getEventIcon(type) {
      switch (type) {
        case EventType.CONNECTION_ESTABLISHED:
          return Circle_check_big;
        case EventType.AGENT_INITIALIZED:
          return Circle_check_big;
        case EventType.PROCESSING:
          return Loader_circle;
        case EventType.AGENT_THINKING:
          return Sparkles;
        case EventType.TOOL_CALL:
          return Wrench;
        case EventType.TOOL_RESULT:
          return Terminal;
        case EventType.AGENT_RESPONSE:
          return Bot;
        case EventType.ERROR:
          return Circle_alert;
        case EventType.SYSTEM:
          return Settings;
        case EventType.USER_MESSAGE:
          return Message_square;
        default:
          return Terminal;
      }
    }
    function getEventColor(type) {
      switch (type) {
        case EventType.CONNECTION_ESTABLISHED:
        case EventType.AGENT_INITIALIZED:
          return "text-green-500";
        case EventType.PROCESSING:
        case EventType.AGENT_THINKING:
          return "text-blue-500";
        case EventType.TOOL_CALL:
        case EventType.TOOL_RESULT:
          return "text-purple-500";
        case EventType.AGENT_RESPONSE:
          return "text-primary";
        case EventType.ERROR:
          return "text-red-500";
        case EventType.SYSTEM:
          return "text-muted-foreground";
        case EventType.USER_MESSAGE:
          return "text-yellow-500";
        default:
          return "text-muted-foreground";
      }
    }
    $$renderer2.push(`<div class="flex flex-col h-[calc(100vh-8rem)]"><div class="flex items-center justify-between pb-4 border-b border-border"><div><h1 class="text-3xl font-bold flex items-center gap-2">`);
    Bot($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> Agent Workbench</h1> <p class="text-muted-foreground mt-1">II-Agent Integration</p></div> <div class="flex items-center gap-2">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<button${attr("disabled", connectionState.isConnecting, true)} class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2">`);
      {
        $$renderer2.push("<!--[!-->");
        Power($$renderer2, { class: "w-4 h-4" });
        $$renderer2.push(`<!----> Connect`);
      }
      $$renderer2.push(`<!--]--></button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="flex-1 mt-4 flex flex-col min-h-0"><div class="flex items-center justify-between mb-2"><h3 class="text-lg font-semibold">Event Stream</h3> <button class="px-3 py-1 text-sm bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors">Clear Log</button></div> <div class="flex-1 overflow-y-auto bg-card border border-border rounded-lg p-4 space-y-2 font-mono text-sm">`);
    if (eventLog.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<p class="text-muted-foreground text-center py-8">No events yet. Connect to II-Agent to get started.</p>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array_1 = ensure_array_like(eventLog);
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let entry = each_array_1[$$index_1];
        $$renderer2.push(`<div class="flex items-start gap-2 p-2 rounded hover:bg-accent/50 transition-colors"><span class="text-xs text-muted-foreground whitespace-nowrap pt-1">${escape_html(formatTime(entry.timestamp))}</span> <!---->`);
        getEventIcon(entry.type)?.($$renderer2, {
          class: `w-4 h-4 flex-shrink-0 mt-1 ${stringify(getEventColor(entry.type))}`
        });
        $$renderer2.push(`<!----> <div class="flex-1 min-w-0"><div class="text-xs text-muted-foreground uppercase">${escape_html(entry.type)}</div> <pre class="whitespace-pre-wrap break-words mt-1">${escape_html(entry.formattedContent || "")}</pre></div></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

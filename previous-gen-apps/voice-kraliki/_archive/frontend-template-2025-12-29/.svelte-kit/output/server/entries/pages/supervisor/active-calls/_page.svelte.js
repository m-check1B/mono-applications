import { e as ensure_array_like, d as attr_class, f as stringify } from "../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../chunks/index-server.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let activeCalls = [];
    const statusColors = {
      ringing: "bg-blue-100 text-blue-800",
      connected: "bg-green-100 text-green-800",
      on_hold: "bg-yellow-100 text-yellow-800",
      transferring: "bg-purple-100 text-purple-800",
      completed: "bg-gray-100 text-gray-800",
      failed: "bg-red-100 text-red-800"
    };
    const sentimentColors = {
      positive: "text-green-600",
      neutral: "text-gray-600",
      negative: "text-red-600"
    };
    onDestroy(() => {
    });
    function formatDuration(seconds) {
      if (seconds === null) return "-";
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, "0")}`;
    }
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="mb-6 flex items-center justify-between"><div><h1 class="text-3xl font-bold">Active Calls</h1> <p class="text-gray-600 mt-1">Monitor and intervene in real-time calls</p></div> <button class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50">← Back to Dashboard</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="mb-6 bg-white p-4 rounded-lg shadow"><div class="text-lg font-semibold">${escape_html(activeCalls.length)} Active ${escape_html(activeCalls.length === 1 ? "Call" : "Calls")}</div></div> `);
    if (activeCalls.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div> <p class="mt-4 text-gray-600">Loading active calls...</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (activeCalls.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-center py-12 bg-gray-50 rounded-lg"><p class="text-gray-600">No active calls</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"><!--[-->`);
        const each_array = ensure_array_like(activeCalls);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let call = each_array[$$index];
          $$renderer2.push(`<div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow"><div class="flex items-start justify-between mb-3"><div class="flex-1"><div class="font-medium">${escape_html(call.caller_name || "Unknown")}</div> <div class="text-sm text-gray-600">${escape_html(call.caller_phone)}</div></div> <span${attr_class(`px-2 py-1 text-xs font-semibold rounded-full capitalize ${stringify(statusColors[call.status])}`)}>${escape_html(call.status.replace("_", " "))}</span></div> <div class="space-y-2 text-sm"><div class="flex justify-between"><span class="text-gray-600">Duration:</span> <span class="font-medium">${escape_html(formatDuration(call.duration_seconds))}</span></div> <div class="flex justify-between"><span class="text-gray-600">Direction:</span> <span class="font-medium capitalize">${escape_html(call.direction)}</span></div> `);
          if (call.current_sentiment) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="flex justify-between"><span class="text-gray-600">Sentiment:</span> <span${attr_class(`font-medium capitalize ${stringify(sentimentColors[call.current_sentiment])}`)}>${escape_html(call.current_sentiment)}</span></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (call.detected_intent) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="flex justify-between"><span class="text-gray-600">Intent:</span> <span class="font-medium">${escape_html(call.detected_intent)}</span></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (call.is_on_hold) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="flex items-center gap-2 text-orange-600"><span>🔇</span> <span>On Hold (${escape_html(call.hold_count)}x)</span></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> `);
          if (call.is_being_monitored) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="flex items-center gap-2 text-blue-600"><span>👁️</span> <span>Being Monitored</span></div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div> <div class="mt-4 flex gap-2">`);
          if (!call.is_being_monitored) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<button class="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">Monitor</button>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <button class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50">Details</button></div></div>`);
        }
        $$renderer2.push(`<!--]--></div> <div class="mt-6 text-center text-sm text-gray-500"><span>🔄 Auto-refreshing every 3 seconds</span></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

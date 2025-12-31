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
    let queueEntries = [];
    let statusFilter = "waiting";
    const statusColors = {
      waiting: "bg-yellow-100 text-yellow-800",
      routing: "bg-blue-100 text-blue-800",
      assigned: "bg-green-100 text-green-800",
      abandoned: "bg-red-100 text-red-800",
      answered: "bg-gray-100 text-gray-800"
    };
    onDestroy(() => {
    });
    function formatDuration(seconds) {
      if (seconds === null) return "-";
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, "0")}`;
    }
    function formatTimeSince(dateString) {
      const date = new Date(dateString);
      const now = /* @__PURE__ */ new Date();
      const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1e3);
      if (diffSeconds < 60) return `${diffSeconds}s`;
      const diffMins = Math.floor(diffSeconds / 60);
      if (diffMins < 60) return `${diffMins}m`;
      const diffHours = Math.floor(diffMins / 60);
      return `${diffHours}h ${diffMins % 60}m`;
    }
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="mb-6 flex items-center justify-between"><div><h1 class="text-3xl font-bold">Call Queue</h1> <p class="text-gray-600 mt-1">Manage incoming call queue and routing</p></div> <button class="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50">← Back to Dashboard</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="mb-6 bg-white rounded-lg shadow p-4"><div class="flex gap-2"><!--[-->`);
    const each_array = ensure_array_like(["all", "waiting", "routing", "assigned", "abandoned"]);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let status = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-4 py-2 rounded-md capitalize ${stringify(statusFilter === status ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300")}`)}>${escape_html(status)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    if (queueEntries.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div> <p class="mt-4 text-gray-600">Loading queue...</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      if (queueEntries.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-center py-12 bg-gray-50 rounded-lg"><p class="text-gray-600">No calls in queue</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="bg-white rounded-lg shadow overflow-hidden"><table class="min-w-full divide-y divide-gray-200"><thead class="bg-gray-50"><tr><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Caller</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Direction</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Wait Time</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Est. Wait</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skills</th><th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th></tr></thead><tbody class="bg-white divide-y divide-gray-200"><!--[-->`);
        const each_array_1 = ensure_array_like(queueEntries);
        for (let $$index_2 = 0, $$length = each_array_1.length; $$index_2 < $$length; $$index_2++) {
          let entry = each_array_1[$$index_2];
          $$renderer2.push(`<tr class="hover:bg-gray-50"><td class="px-6 py-4 whitespace-nowrap"><div class="text-sm font-medium text-gray-900">${escape_html(entry.queue_position || "-")}</div></td><td class="px-6 py-4 whitespace-nowrap"><div class="text-sm font-medium text-gray-900">${escape_html(entry.caller_name || "Unknown")}</div> <div class="text-sm text-gray-500">${escape_html(entry.caller_phone)}</div></td><td class="px-6 py-4 whitespace-nowrap"><div class="text-sm text-gray-900 capitalize">${escape_html(entry.direction)}</div></td><td class="px-6 py-4 whitespace-nowrap"><div class="text-sm text-gray-900">${escape_html(formatTimeSince(entry.queued_at))}</div></td><td class="px-6 py-4 whitespace-nowrap"><div class="text-sm text-gray-900">${escape_html(formatDuration(entry.estimated_wait_time))}</div></td><td class="px-6 py-4 whitespace-nowrap"><div class="text-sm">`);
          if (entry.priority > 0) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">High (${escape_html(entry.priority)})</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<span class="text-gray-500">Normal</span>`);
          }
          $$renderer2.push(`<!--]--></div></td><td class="px-6 py-4"><div class="flex flex-wrap gap-1"><!--[-->`);
          const each_array_2 = ensure_array_like(entry.required_skills);
          for (let $$index_1 = 0, $$length2 = each_array_2.length; $$index_1 < $$length2; $$index_1++) {
            let skill = each_array_2[$$index_1];
            $$renderer2.push(`<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">${escape_html(skill)}</span>`);
          }
          $$renderer2.push(`<!--]--> `);
          if (entry.required_language) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">${escape_html(entry.required_language)}</span>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div></td><td class="px-6 py-4 whitespace-nowrap"><span${attr_class(`px-2 py-1 text-xs font-semibold rounded-full capitalize ${stringify(statusColors[entry.status])}`)}>${escape_html(entry.status)}</span> `);
          if (entry.routing_attempts > 0) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="text-xs text-gray-500 mt-1">${escape_html(entry.routing_attempts)} attempts</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></td></tr>`);
        }
        $$renderer2.push(`<!--]--></tbody></table></div> <div class="mt-4 text-sm text-gray-600 flex items-center justify-between"><div>Showing ${escape_html(queueEntries.length)} calls</div> <div class="flex items-center gap-2"><span>🔄</span> <span>Auto-refreshing every 3 seconds</span></div></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

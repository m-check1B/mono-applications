import { e as ensure_array_like, d as attr_class, f as stringify } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let statusFilter = "all";
    const statusOptions = [
      "all",
      "offline",
      "available",
      "busy",
      "on_call",
      "break",
      "training",
      "away"
    ];
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="mb-6 flex items-center justify-between"><div><h1 class="text-3xl font-bold">Agents</h1> <p class="text-gray-600 mt-1">Manage agent profiles and monitor status</p></div> <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">+ New Agent</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="mb-6 bg-white rounded-lg shadow p-4"><div class="flex gap-4 mb-4"><input type="text" placeholder="Search by name or employee ID..." class="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/></div> <div class="flex gap-2 flex-wrap"><!--[-->`);
    const each_array = ensure_array_like(statusOptions);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let status = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-4 py-2 rounded-md capitalize ${stringify(statusFilter === status ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300")}`)}>${escape_html(status === "all" ? "All" : status.replace("_", " "))}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div> <p class="mt-4 text-gray-600">Loading agents...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

import { e as ensure_array_like, d as attr_class, c as attr, f as stringify } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let shifts = [];
    let filteredShifts = [];
    let viewMode = "today";
    let statusFilter = "all";
    let selectedDate = (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
    const statusOptions = [
      "all",
      "scheduled",
      "in_progress",
      "completed",
      "cancelled",
      "no_show"
    ];
    function filterShifts() {
      (/* @__PURE__ */ new Date()).toISOString().split("T")[0];
      new Date(Date.now() - 7 * 24 * 60 * 60 * 1e3).toISOString().split("T")[0];
      filteredShifts = shifts.filter((shift) => {
        let matchesDate = true;
        {
          matchesDate = shift.shift_date === selectedDate;
        }
        return matchesDate;
      });
      filteredShifts.sort((a, b) => {
        const dateCompare = a.shift_date.localeCompare(b.shift_date);
        if (dateCompare !== 0) return dateCompare;
        return a.start_time.localeCompare(b.start_time);
      });
    }
    $$renderer2.push(`<div class="container mx-auto p-6"><div class="mb-6 flex items-center justify-between"><div><h1 class="text-3xl font-bold">Shift Management</h1> <p class="text-gray-600 mt-1">View and manage agent schedules</p></div> <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">+ Schedule Shift</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="mb-6 bg-white rounded-lg shadow p-4"><div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4"><div><label class="block text-sm font-medium text-gray-700 mb-2">View Mode</label> <div class="flex gap-2"><!--[-->`);
    const each_array = ensure_array_like(["today", "week", "all"]);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let mode = each_array[$$index];
      $$renderer2.push(`<button${attr_class(`px-4 py-2 rounded-md capitalize ${stringify(viewMode === mode ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300")}`)}>${escape_html(mode)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div><label for="date" class="block text-sm font-medium text-gray-700 mb-2">Select Date</label> <input type="date" id="date"${attr("value", selectedDate)} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/></div>`);
    }
    $$renderer2.push(`<!--]--> <div><label class="block text-sm font-medium text-gray-700 mb-2">Status</label> `);
    $$renderer2.select(
      {
        value: statusFilter,
        onchange: () => filterShifts(),
        class: "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 capitalize"
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array_1 = ensure_array_like(statusOptions);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let status = each_array_1[$$index_1];
          $$renderer3.option({ value: status, class: "capitalize" }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(status === "all" ? "All Statuses" : status.replace("_", " "))}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</div></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div> <p class="mt-4 text-gray-600">Loading shifts...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

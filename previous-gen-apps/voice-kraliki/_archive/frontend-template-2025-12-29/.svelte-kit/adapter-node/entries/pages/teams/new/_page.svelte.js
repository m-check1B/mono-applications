import { c as attr, e as ensure_array_like, d as attr_class, f as stringify } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let formData = {
      name: "",
      description: "",
      parent_team_id: null,
      timezone: "UTC",
      working_hours: { start: "09:00", end: "17:00" },
      working_days: [1, 2, 3, 4, 5],
      // Monday-Friday
      tags: []
    };
    let teams = [];
    let saving = false;
    let tagInput = "";
    const timezones = [
      "UTC",
      "America/New_York",
      "America/Chicago",
      "America/Denver",
      "America/Los_Angeles",
      "Europe/London",
      "Europe/Paris",
      "Asia/Tokyo",
      "Asia/Shanghai",
      "Australia/Sydney"
    ];
    const daysOfWeek = [
      { value: 1, label: "Mon" },
      { value: 2, label: "Tue" },
      { value: 3, label: "Wed" },
      { value: 4, label: "Thu" },
      { value: 5, label: "Fri" },
      { value: 6, label: "Sat" },
      { value: 0, label: "Sun" }
    ];
    $$renderer2.push(`<div class="container mx-auto p-6 max-w-4xl"><div class="mb-6"><button class="text-gray-600 hover:text-gray-900 mb-2">← Back to Teams</button> <h1 class="text-3xl font-bold">Create New Team</h1> <p class="text-gray-600 mt-1">Set up a new team with working hours and structure</p></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <form class="bg-white rounded-lg shadow-lg p-6 space-y-6"><div><h2 class="text-xl font-semibold mb-4">Basic Information</h2> <div class="space-y-4"><div><label for="name" class="block text-sm font-medium text-gray-700 mb-1">Team Name *</label> <input type="text" id="name"${attr("value", formData.name)} required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" placeholder="e.g., Sales Team, Support Team"/></div> <div><label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label> <textarea id="description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" placeholder="Describe the team's purpose and responsibilities">`);
    const $$body = escape_html(formData.description);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea></div> <div><label for="parent_team" class="block text-sm font-medium text-gray-700 mb-1">Parent Team (Optional)</label> `);
    $$renderer2.select(
      {
        id: "parent_team",
        value: formData.parent_team_id,
        class: "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
      },
      ($$renderer3) => {
        $$renderer3.option({ value: null }, ($$renderer4) => {
          $$renderer4.push(`None (Top-level team)`);
        });
        $$renderer3.push(`<!--[-->`);
        const each_array = ensure_array_like(teams);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let team = each_array[$$index];
          $$renderer3.option({ value: team.id }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(team.name)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(` <p class="mt-1 text-sm text-gray-500">Create a hierarchical structure by selecting a parent team</p></div></div></div> <div class="border-t pt-6"><h2 class="text-xl font-semibold mb-4">Working Schedule</h2> <div class="space-y-4"><div><label for="timezone" class="block text-sm font-medium text-gray-700 mb-1">Timezone *</label> `);
    $$renderer2.select(
      {
        id: "timezone",
        value: formData.timezone,
        class: "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
      },
      ($$renderer3) => {
        $$renderer3.push(`<!--[-->`);
        const each_array_1 = ensure_array_like(timezones);
        for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
          let tz = each_array_1[$$index_1];
          $$renderer3.option({ value: tz }, ($$renderer4) => {
            $$renderer4.push(`${escape_html(tz)}`);
          });
        }
        $$renderer3.push(`<!--]-->`);
      }
    );
    $$renderer2.push(`</div> <div class="grid grid-cols-2 gap-4"><div><label for="start_time" class="block text-sm font-medium text-gray-700 mb-1">Start Time</label> <input type="time" id="start_time"${attr("value", formData.working_hours.start)} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/></div> <div><label for="end_time" class="block text-sm font-medium text-gray-700 mb-1">End Time</label> <input type="time" id="end_time"${attr("value", formData.working_hours.end)} class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"/></div></div> <div><label class="block text-sm font-medium text-gray-700 mb-2">Working Days *</label> <div class="flex gap-2"><!--[-->`);
    const each_array_2 = ensure_array_like(daysOfWeek);
    for (let $$index_2 = 0, $$length = each_array_2.length; $$index_2 < $$length; $$index_2++) {
      let day = each_array_2[$$index_2];
      $$renderer2.push(`<button type="button"${attr_class(`px-4 py-2 rounded-md font-medium ${stringify(formData.working_days.includes(day.value) ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300")}`)}>${escape_html(day.label)}</button>`);
    }
    $$renderer2.push(`<!--]--></div></div></div></div> <div class="border-t pt-6"><h2 class="text-xl font-semibold mb-4">Tags (Optional)</h2> <div class="space-y-3"><div class="flex gap-2"><input type="text"${attr("value", tagInput)} class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" placeholder="Add tags (e.g., sales, support, tier1)"/> <button type="button" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Add Tag</button></div> `);
    if (formData.tags.length > 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex flex-wrap gap-2"><!--[-->`);
      const each_array_3 = ensure_array_like(formData.tags);
      for (let $$index_3 = 0, $$length = each_array_3.length; $$index_3 < $$length; $$index_3++) {
        let tag = each_array_3[$$index_3];
        $$renderer2.push(`<span class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">${escape_html(tag)} <button type="button" class="text-blue-600 hover:text-blue-800">×</button></span>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div> <div class="flex justify-end gap-3 pt-4 border-t"><button type="button" class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">Cancel</button> <button type="submit"${attr("disabled", saving, true)} class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed">${escape_html("Create Team")}</button></div></form></div>`);
  });
}
export {
  _page as default
};

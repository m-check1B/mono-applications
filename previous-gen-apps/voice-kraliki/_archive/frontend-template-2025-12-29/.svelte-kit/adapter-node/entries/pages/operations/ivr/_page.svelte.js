import { c as attr } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { P as Phone } from "../../../../chunks/phone.js";
import { P as Play } from "../../../../chunks/play.js";
import { S as Search } from "../../../../chunks/search.js";
import { P as Plus } from "../../../../chunks/plus.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let searchQuery = "";
    let statusFilter = "all";
    let stats = {
      total_flows: 0,
      active_flows: 0,
      inactive_flows: 0,
      total_nodes: 0
    };
    $$renderer2.push(`<div class="p-6 max-w-7xl mx-auto"><div class="mb-6"><h1 class="text-3xl font-bold text-gray-900 mb-2">IVR Flow Management</h1> <p class="text-gray-600">Configure and manage Interactive Voice Response (IVR) flows for call routing</p></div> <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"><div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Total Flows</p> <p class="text-2xl font-bold text-gray-900">${escape_html(stats.total_flows)}</p></div> `);
    Phone($$renderer2, { class: "w-8 h-8 text-blue-500" });
    $$renderer2.push(`<!----></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Active Flows</p> <p class="text-2xl font-bold text-green-600">${escape_html(stats.active_flows)}</p></div> `);
    Play($$renderer2, { class: "w-8 h-8 text-green-500" });
    $$renderer2.push(`<!----></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Inactive Flows</p> <p class="text-2xl font-bold text-gray-600">${escape_html(stats.inactive_flows)}</p></div> `);
    Phone($$renderer2, { class: "w-8 h-8 text-gray-400" });
    $$renderer2.push(`<!----></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4"><div class="flex items-center justify-between"><div><p class="text-sm text-gray-600">Total Nodes</p> <p class="text-2xl font-bold text-blue-600">${escape_html(stats.total_nodes)}</p></div> `);
    Phone($$renderer2, { class: "w-8 h-8 text-blue-400" });
    $$renderer2.push(`<!----></div></div></div> <div class="bg-white rounded-lg border border-gray-200 p-4 mb-4"><div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4"><div class="flex flex-col md:flex-row gap-4 flex-1"><div class="relative flex-1">`);
    Search($$renderer2, {
      class: "absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
    });
    $$renderer2.push(`<!----> <input type="text" placeholder="Search flows..."${attr("value", searchQuery)} class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> `);
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
    $$renderer2.push(`</div> <a href="/operations/ivr/builder" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">`);
    Plus($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Create Flow</a></div></div> <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="p-8 text-center"><div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div> <p class="mt-2 text-gray-600">Loading IVR flows...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
export {
  _page as default
};

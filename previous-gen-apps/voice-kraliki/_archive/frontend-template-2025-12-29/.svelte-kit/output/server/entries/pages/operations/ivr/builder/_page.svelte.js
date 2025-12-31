import { c as attr, e as ensure_array_like, d as attr_class, f as stringify } from "../../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../../chunks/exports.js";
import "../../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../../chunks/state.svelte.js";
import { A as Arrow_left } from "../../../../../chunks/arrow-left.js";
import { S as Save } from "../../../../../chunks/save.js";
import { P as Plus } from "../../../../../chunks/plus.js";
import { M as Menu, P as Pen } from "../../../../../chunks/pen.js";
import { T as Trash_2 } from "../../../../../chunks/trash-2.js";
import { P as Phone } from "../../../../../chunks/phone.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let flow = {
      name: "",
      description: "",
      is_active: true,
      timeout_seconds: 30,
      max_retries: 3
    };
    let nodes = [];
    let saving = false;
    const nodeTypes = [
      {
        value: "menu",
        label: "Menu",
        description: "Present options to caller"
      },
      {
        value: "play",
        label: "Play Message",
        description: "Play audio message"
      },
      {
        value: "gather",
        label: "Gather Input",
        description: "Collect DTMF/speech input"
      },
      {
        value: "transfer",
        label: "Transfer",
        description: "Transfer to phone/agent"
      },
      {
        value: "voicemail",
        label: "Voicemail",
        description: "Send to voicemail"
      },
      {
        value: "webhook",
        label: "Webhook",
        description: "Call external API"
      },
      {
        value: "conditional",
        label: "Conditional",
        description: "Branch based on condition"
      },
      {
        value: "variable",
        label: "Set Variable",
        description: "Store value in variable"
      },
      {
        value: "end",
        label: "End Call",
        description: "Terminate the call"
      }
    ];
    function getNodeTypeLabel(type) {
      return nodeTypes.find((t) => t.value === type)?.label || type;
    }
    function getNodeColor(type) {
      const colors = {
        menu: "bg-blue-100 border-blue-300 text-blue-800",
        play: "bg-green-100 border-green-300 text-green-800",
        gather: "bg-purple-100 border-purple-300 text-purple-800",
        transfer: "bg-orange-100 border-orange-300 text-orange-800",
        voicemail: "bg-yellow-100 border-yellow-300 text-yellow-800",
        webhook: "bg-pink-100 border-pink-300 text-pink-800",
        conditional: "bg-indigo-100 border-indigo-300 text-indigo-800",
        variable: "bg-teal-100 border-teal-300 text-teal-800",
        end: "bg-red-100 border-red-300 text-red-800"
      };
      return colors[type] || "bg-gray-100 border-gray-300 text-gray-800";
    }
    $$renderer2.push(`<div class="p-6 max-w-7xl mx-auto"><div class="mb-6 flex items-center justify-between"><div class="flex items-center gap-4"><a href="/operations/ivr" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">`);
    Arrow_left($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></a> <div><h1 class="text-3xl font-bold text-gray-900">${escape_html("Create IVR Flow")}</h1> <p class="text-gray-600">Design your interactive voice response flow</p></div></div> <button${attr("disabled", saving, true)} class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors">`);
    Save($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> ${escape_html("Save Flow")}</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="grid grid-cols-1 lg:grid-cols-3 gap-6"><div class="lg:col-span-2 space-y-6"><div class="bg-white rounded-lg border border-gray-200 p-6"><h2 class="text-xl font-semibold text-gray-900 mb-4">Flow Configuration</h2> <div class="grid grid-cols-1 md:grid-cols-2 gap-4"><div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Flow Name *</label> <input type="text"${attr("value", flow.name)} placeholder="e.g., Main Menu" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Description</label> <textarea placeholder="Describe the purpose of this IVR flow..." rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">`);
      const $$body = escape_html(flow.description);
      if ($$body) {
        $$renderer2.push(`${$$body}`);
      }
      $$renderer2.push(`</textarea></div> <div><label class="block text-sm font-medium text-gray-700 mb-1">Timeout (seconds)</label> <input type="number"${attr("value", flow.timeout_seconds)} min="5" max="300" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> <div><label class="block text-sm font-medium text-gray-700 mb-1">Max Retries</label> <input type="number"${attr("value", flow.max_retries)} min="1" max="10" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> <div class="flex items-center"><input type="checkbox" id="is_active"${attr("checked", flow.is_active, true)} class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"/> <label for="is_active" class="ml-2 text-sm text-gray-700">Active (enable this flow)</label></div></div></div> <div class="bg-white rounded-lg border border-gray-200 p-6"><div class="flex items-center justify-between mb-4"><h2 class="text-xl font-semibold text-gray-900">Flow Nodes</h2> <button class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">`);
      Plus($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> Add Node</button></div> `);
      if (nodes.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-center py-8">`);
        Menu($$renderer2, { class: "w-12 h-12 text-gray-300 mx-auto mb-2" });
        $$renderer2.push(`<!----> <p class="text-gray-600">No nodes yet. Click "Add Node" to start building your flow.</p></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="space-y-3"><!--[-->`);
        const each_array = ensure_array_like(nodes);
        for (let index = 0, $$length = each_array.length; index < $$length; index++) {
          let node = each_array[index];
          $$renderer2.push(`<div class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"><div class="flex items-center justify-between"><div class="flex items-center gap-3 flex-1"><span${attr_class(`px-3 py-1 rounded-full border text-xs font-medium ${stringify(getNodeColor(node.node_type))}`)}>${escape_html(getNodeTypeLabel(node.node_type))}</span> <div class="flex-1"><div class="font-medium text-gray-900">${escape_html(node.name)}</div> <div class="text-sm text-gray-500">${escape_html(node.prompt_text ? node.prompt_text.substring(0, 60) + "..." : "No prompt text")}</div></div></div> <div class="flex items-center gap-2"><button class="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors" title="Edit">`);
          Pen($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button> <button class="p-2 text-red-600 hover:bg-red-50 rounded transition-colors" title="Delete">`);
          Trash_2($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="lg:col-span-1">`);
      {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="bg-gray-50 rounded-lg border border-gray-200 p-6 text-center">`);
        Phone($$renderer2, { class: "w-12 h-12 text-gray-300 mx-auto mb-2" });
        $$renderer2.push(`<!----> <p class="text-gray-600">Select a node to edit its properties</p></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

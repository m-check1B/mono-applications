import { c as attr, e as ensure_array_like } from "../../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../../chunks/exports.js";
import "../../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../../chunks/state.svelte.js";
import { A as Arrow_left } from "../../../../../chunks/arrow-left.js";
import { S as Save } from "../../../../../chunks/save.js";
import { P as Plus } from "../../../../../chunks/plus.js";
import { X } from "../../../../../chunks/x.js";
import { e as escape_html } from "../../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let rule = {
      name: "",
      description: "",
      priority: 100,
      strategy: "skill_based",
      is_active: true,
      conditions: [],
      targets: [],
      fallback_action: "voicemail",
      business_hours_only: false
    };
    let saving = false;
    const strategies = [
      {
        value: "skill_based",
        label: "Skill-Based",
        description: "Route based on agent skills"
      },
      {
        value: "least_busy",
        label: "Least Busy",
        description: "Route to agent with fewest calls"
      },
      {
        value: "longest_idle",
        label: "Longest Idle",
        description: "Route to agent idle longest"
      },
      {
        value: "round_robin",
        label: "Round Robin",
        description: "Distribute calls evenly"
      },
      {
        value: "priority",
        label: "Priority",
        description: "Route by priority level"
      },
      {
        value: "language",
        label: "Language",
        description: "Match caller language"
      },
      {
        value: "vip",
        label: "VIP",
        description: "Prioritize VIP callers"
      },
      {
        value: "custom",
        label: "Custom",
        description: "Custom routing logic"
      }
    ];
    const conditionFields = [
      { value: "caller_phone", label: "Caller Phone" },
      { value: "caller_country", label: "Caller Country" },
      { value: "time_of_day", label: "Time of Day" },
      { value: "day_of_week", label: "Day of Week" },
      { value: "queue_wait_time", label: "Queue Wait Time" },
      { value: "required_skills", label: "Required Skills" },
      { value: "language", label: "Language" },
      { value: "campaign_id", label: "Campaign" },
      { value: "custom_field", label: "Custom Field" }
    ];
    const operators = [
      { value: "equals", label: "Equals" },
      { value: "not_equals", label: "Not Equals" },
      { value: "contains", label: "Contains" },
      { value: "starts_with", label: "Starts With" },
      { value: "greater_than", label: "Greater Than" },
      { value: "less_than", label: "Less Than" },
      { value: "in_list", label: "In List" }
    ];
    const targetTypes = [
      { value: "agent", label: "Agent" },
      { value: "team", label: "Team" },
      { value: "queue", label: "Queue" },
      { value: "phone", label: "Phone Number" },
      { value: "ivr", label: "IVR Flow" }
    ];
    const fallbackActions = [
      { value: "voicemail", label: "Send to Voicemail" },
      { value: "queue", label: "Add to Queue" },
      { value: "transfer", label: "Transfer to Number" },
      { value: "hangup", label: "Hangup" },
      { value: "callback", label: "Offer Callback" }
    ];
    $$renderer2.push(`<div class="p-6 max-w-5xl mx-auto"><div class="mb-6 flex items-center justify-between"><div class="flex items-center gap-4"><a href="/operations/routing" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">`);
    Arrow_left($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></a> <div><h1 class="text-3xl font-bold text-gray-900">${escape_html("Create Routing Rule")}</h1> <p class="text-gray-600">Configure intelligent call routing</p></div></div> <button${attr("disabled", saving, true)} class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors">`);
    Save($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> ${escape_html("Save Rule")}</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="space-y-6"><div class="bg-white rounded-lg border border-gray-200 p-6"><h2 class="text-xl font-semibold text-gray-900 mb-4">Basic Configuration</h2> <div class="grid grid-cols-1 md:grid-cols-2 gap-4"><div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Rule Name *</label> <input type="text"${attr("value", rule.name)} placeholder="e.g., VIP Customer Routing" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> <div class="md:col-span-2"><label class="block text-sm font-medium text-gray-700 mb-1">Description</label> <textarea placeholder="Describe the purpose of this routing rule..." rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">`);
      const $$body = escape_html(rule.description);
      if ($$body) {
        $$renderer2.push(`${$$body}`);
      }
      $$renderer2.push(`</textarea></div> <div><label class="block text-sm font-medium text-gray-700 mb-1">Routing Strategy *</label> `);
      $$renderer2.select(
        {
          value: rule.strategy,
          class: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array = ensure_array_like(strategies);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let strategy = each_array[$$index];
            $$renderer3.option({ value: strategy.value }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(strategy.label)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(` <p class="mt-1 text-sm text-gray-500">${escape_html(strategies.find((s) => s.value === rule.strategy)?.description || "")}</p></div> <div><label class="block text-sm font-medium text-gray-700 mb-1">Priority (Lower = Higher Priority)</label> <input type="number"${attr("value", rule.priority)} min="1" max="1000" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"/></div> <div><label class="block text-sm font-medium text-gray-700 mb-1">Fallback Action</label> `);
      $$renderer2.select(
        {
          value: rule.fallback_action,
          class: "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array_1 = ensure_array_like(fallbackActions);
          for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
            let action = each_array_1[$$index_1];
            $$renderer3.option({ value: action.value }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(action.label)}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</div> <div class="flex items-center gap-4"><div class="flex items-center"><input type="checkbox" id="is_active"${attr("checked", rule.is_active, true)} class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"/> <label for="is_active" class="ml-2 text-sm text-gray-700">Active</label></div> <div class="flex items-center"><input type="checkbox" id="business_hours"${attr("checked", rule.business_hours_only, true)} class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"/> <label for="business_hours" class="ml-2 text-sm text-gray-700">Business Hours Only</label></div></div></div></div> <div class="bg-white rounded-lg border border-gray-200 p-6"><div class="flex items-center justify-between mb-4"><h2 class="text-xl font-semibold text-gray-900">Routing Conditions</h2> <button class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">`);
      Plus($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> Add Condition</button></div> `);
      if (rule.conditions.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<p class="text-gray-500 text-center py-4">No conditions added. Rule will apply to all calls.</p>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="space-y-3"><!--[-->`);
        const each_array_2 = ensure_array_like(rule.conditions);
        for (let index = 0, $$length = each_array_2.length; index < $$length; index++) {
          let condition = each_array_2[index];
          $$renderer2.push(`<div class="border border-gray-200 rounded-lg p-4"><div class="grid grid-cols-1 md:grid-cols-4 gap-3">`);
          if (index > 0) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="md:col-span-4">`);
            $$renderer2.select(
              {
                value: condition.logic_operator,
                class: "px-3 py-1 border border-gray-300 rounded text-sm"
              },
              ($$renderer3) => {
                $$renderer3.option({ value: "AND" }, ($$renderer4) => {
                  $$renderer4.push(`AND`);
                });
                $$renderer3.option({ value: "OR" }, ($$renderer4) => {
                  $$renderer4.push(`OR`);
                });
              }
            );
            $$renderer2.push(`</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--> <div><label class="block text-xs font-medium text-gray-600 mb-1">Field</label> `);
          $$renderer2.select(
            {
              value: condition.field,
              class: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            },
            ($$renderer3) => {
              $$renderer3.push(`<!--[-->`);
              const each_array_3 = ensure_array_like(conditionFields);
              for (let $$index_2 = 0, $$length2 = each_array_3.length; $$index_2 < $$length2; $$index_2++) {
                let field = each_array_3[$$index_2];
                $$renderer3.option({ value: field.value }, ($$renderer4) => {
                  $$renderer4.push(`${escape_html(field.label)}`);
                });
              }
              $$renderer3.push(`<!--]-->`);
            }
          );
          $$renderer2.push(`</div> <div><label class="block text-xs font-medium text-gray-600 mb-1">Operator</label> `);
          $$renderer2.select(
            {
              value: condition.operator,
              class: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            },
            ($$renderer3) => {
              $$renderer3.push(`<!--[-->`);
              const each_array_4 = ensure_array_like(operators);
              for (let $$index_3 = 0, $$length2 = each_array_4.length; $$index_3 < $$length2; $$index_3++) {
                let op = each_array_4[$$index_3];
                $$renderer3.option({ value: op.value }, ($$renderer4) => {
                  $$renderer4.push(`${escape_html(op.label)}`);
                });
              }
              $$renderer3.push(`<!--]-->`);
            }
          );
          $$renderer2.push(`</div> <div class="md:col-span-2 flex gap-2"><div class="flex-1"><label class="block text-xs font-medium text-gray-600 mb-1">Value</label> <input type="text"${attr("value", condition.value)} placeholder="Enter value..." class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"/></div> <button class="self-end p-2 text-red-600 hover:bg-red-50 rounded transition-colors" title="Remove Condition">`);
          X($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div> <div class="bg-white rounded-lg border border-gray-200 p-6"><div class="flex items-center justify-between mb-4"><h2 class="text-xl font-semibold text-gray-900">Routing Targets *</h2> <button class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">`);
      Plus($$renderer2, { class: "w-4 h-4" });
      $$renderer2.push(`<!----> Add Target</button></div> `);
      if (rule.targets.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<p class="text-gray-500 text-center py-4">No targets added. Please add at least one routing target.</p>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="space-y-3"><!--[-->`);
        const each_array_5 = ensure_array_like(rule.targets);
        for (let index = 0, $$length = each_array_5.length; index < $$length; index++) {
          let target = each_array_5[index];
          $$renderer2.push(`<div class="border border-gray-200 rounded-lg p-4"><div class="grid grid-cols-1 md:grid-cols-4 gap-3"><div><label class="block text-xs font-medium text-gray-600 mb-1">Target Type</label> `);
          $$renderer2.select(
            {
              value: target.target_type,
              class: "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            },
            ($$renderer3) => {
              $$renderer3.push(`<!--[-->`);
              const each_array_6 = ensure_array_like(targetTypes);
              for (let $$index_5 = 0, $$length2 = each_array_6.length; $$index_5 < $$length2; $$index_5++) {
                let type = each_array_6[$$index_5];
                $$renderer3.option({ value: type.value }, ($$renderer4) => {
                  $$renderer4.push(`${escape_html(type.label)}`);
                });
              }
              $$renderer3.push(`<!--]-->`);
            }
          );
          $$renderer2.push(`</div> <div><label class="block text-xs font-medium text-gray-600 mb-1">Target ID</label> <input type="number"${attr("value", target.target_id)} placeholder="ID or leave blank" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"/></div> <div><label class="block text-xs font-medium text-gray-600 mb-1">Weight</label> <input type="number"${attr("value", target.weight)} min="1" max="1000" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"/></div> <div class="flex gap-2"><div class="flex-1"><label class="block text-xs font-medium text-gray-600 mb-1">Max Capacity</label> <input type="number"${attr("value", target.max_capacity)} placeholder="Optional" min="1" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"/></div> <button class="self-end p-2 text-red-600 hover:bg-red-50 rounded transition-colors" title="Remove Target">`);
          X($$renderer2, { class: "w-4 h-4" });
          $$renderer2.push(`<!----></button></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

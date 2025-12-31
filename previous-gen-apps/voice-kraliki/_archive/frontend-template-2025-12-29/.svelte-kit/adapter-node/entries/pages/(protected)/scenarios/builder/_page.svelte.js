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
    let scenario = {
      name: "",
      description: "",
      category: "Customer Service",
      difficulty: "Medium"
    };
    let nodes = [];
    let selectedNode = null;
    let saving = false;
    const nodeTypes = [
      {
        value: "statement",
        label: "Statement",
        description: "Agent or Customer makes a statement"
      },
      {
        value: "question",
        label: "Question",
        description: "Ask a question with multiple choices"
      },
      {
        value: "conditional",
        label: "Conditional",
        description: "Branch based on variable/state"
      },
      {
        value: "goTo",
        label: "Go To",
        description: "Jump to another node"
      },
      {
        value: "setVariable",
        label: "Set Variable",
        description: "Update scenario state"
      },
      {
        value: "end",
        label: "End Scenario",
        description: "Terminate the scenario"
      }
    ];
    function getNodeTypeLabel(type) {
      return nodeTypes.find((t) => t.value === type)?.label || type;
    }
    function getNodeColor(type) {
      const colors = {
        statement: "bg-terminal-green text-void",
        question: "bg-primary text-primary-foreground",
        conditional: "bg-accent text-accent-foreground",
        goTo: "bg-cyan-data text-void",
        setVariable: "bg-muted text-foreground",
        end: "bg-system-red text-white"
      };
      return colors[type] || "bg-secondary text-foreground";
    }
    $$renderer2.push(`<div class="p-6 max-w-7xl mx-auto bg-grid-pattern min-h-screen"><div class="mb-8 flex flex-col md:flex-row md:items-center justify-between border-b-4 border-foreground pb-6 gap-4"><div class="flex items-center gap-6"><a href="/scenarios" class="p-2 border-2 border-foreground hover:bg-terminal-green hover:text-void transition-all hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-card">`);
    Arrow_left($$renderer2, { class: "w-6 h-6" });
    $$renderer2.push(`<!----></a> <div><h1 class="text-4xl font-display text-foreground tracking-tighter">${escape_html("New Scenario")}</h1> <p class="text-muted-foreground uppercase font-bold tracking-[0.2em] text-[10px] mt-1">Design your training scenario // V1.0 // SYSTEM_READY</p></div></div> <div class="flex items-center gap-4">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button${attr("disabled", saving, true)} class="brutal-btn bg-primary text-primary-foreground">`);
    Save($$renderer2, { class: "w-5 h-5 inline mr-2" });
    $$renderer2.push(`<!----> ${escape_html("Save Scenario")}</button></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="grid grid-cols-1 lg:grid-cols-12 gap-8"><div class="lg:col-span-8 space-y-8"><div class="brutal-card"><div class="flex items-center gap-3 mb-6 border-b-2 border-foreground pb-2"><div class="w-3 h-3 bg-terminal-green"></div> <h2 class="text-2xl font-display uppercase tracking-tight">Global Settings</h2></div> <div class="grid grid-cols-1 md:grid-cols-2 gap-6"><div class="md:col-span-2"><label for="scenario-name" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">// Scenario Name</label> <input id="scenario-name" type="text"${attr("value", scenario.name)} placeholder="e.g., Dealing with Angry Customer" class="w-full brutal-input focus:border-terminal-green"/></div> <div class="md:col-span-2"><label for="scenario-desc" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">// Description</label> <textarea id="scenario-desc" placeholder="What should the agent learn from this scenario?" rows="3" class="w-full brutal-input focus:border-terminal-green">`);
      const $$body = escape_html(scenario.description);
      if ($$body) {
        $$renderer2.push(`${$$body}`);
      }
      $$renderer2.push(`</textarea></div> <div><label for="scenario-cat" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">// Category</label> `);
      $$renderer2.select(
        {
          id: "scenario-cat",
          value: scenario.category,
          class: "w-full brutal-input"
        },
        ($$renderer3) => {
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Customer Service`);
          });
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Sales`);
          });
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Technical Support`);
          });
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Compliance`);
          });
        }
      );
      $$renderer2.push(`</div> <div><label for="scenario-diff" class="block text-xs font-bold uppercase mb-2 tracking-wider text-muted-foreground">// Difficulty</label> `);
      $$renderer2.select(
        {
          id: "scenario-diff",
          value: scenario.difficulty,
          class: "w-full brutal-input"
        },
        ($$renderer3) => {
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Easy`);
          });
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Medium`);
          });
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Hard`);
          });
          $$renderer3.option({}, ($$renderer4) => {
            $$renderer4.push(`Expert`);
          });
        }
      );
      $$renderer2.push(`</div></div></div> <div class="brutal-card relative overflow-hidden"><div class="scanline opacity-10"></div> <div class="flex items-center justify-between mb-6 border-b-2 border-foreground pb-2"><div class="flex items-center gap-3"><div class="w-3 h-3 bg-cyan-data"></div> <h2 class="text-2xl font-display uppercase tracking-tight">Scenario Flow</h2></div> <button class="brutal-btn py-2 px-4 text-sm bg-terminal-green text-void">`);
      Plus($$renderer2, { class: "w-4 h-4 inline mr-1" });
      $$renderer2.push(`<!----> Add Node</button></div> `);
      if (nodes.length === 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-center py-20 border-2 border-dashed border-muted bg-muted/5">`);
        Menu($$renderer2, { class: "w-16 h-16 text-muted/30 mx-auto mb-4" });
        $$renderer2.push(`<!----> <p class="text-muted-foreground font-bold uppercase tracking-widest text-xs">No nodes defined in buffer.</p> <button class="mt-4 text-terminal-green font-bold uppercase text-xs hover:underline cursor-pointer">Create your first node</button></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="grid grid-cols-1 md:grid-cols-2 gap-4"><!--[-->`);
        const each_array = ensure_array_like(nodes);
        for (let index = 0, $$length = each_array.length; index < $$length; index++) {
          let node = each_array[index];
          $$renderer2.push(`<div role="button" tabindex="0"${attr_class(`text-left w-full brutal-card p-4 hover:border-terminal-green hover:shadow-[6px_6px_0px_0px_rgba(51,255,0,1)] transition-all group cursor-pointer ${stringify(selectedNode === node ? "border-terminal-green shadow-[6px_6px_0px_0px_rgba(51,255,0,1)]" : "")}`)}><div class="flex items-start justify-between gap-4"><div class="flex-1"><div class="flex items-center gap-2 mb-3"><span${attr_class(`px-2 py-0.5 border-2 border-foreground text-[9px] font-bold uppercase ${stringify(getNodeColor(node.node_type))}`)}>${escape_html(getNodeTypeLabel(node.node_type))}</span> <div class="font-display text-sm truncate max-w-[150px] uppercase tracking-tight">${escape_html(node.name)}</div></div> <div class="text-[11px] text-muted-foreground font-mono line-clamp-2 bg-muted/20 p-2 border border-muted/30">${escape_html(node.text_content || "EMPTY_BUFFER")}</div></div> <div class="flex flex-col gap-2"><div class="p-1 border-2 border-foreground group-hover:border-terminal-green transition-colors bg-card">`);
          Pen($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----></div> <button class="p-1 border-2 border-foreground hover:bg-system-red hover:text-white transition-colors bg-card">`);
          Trash_2($$renderer2, { class: "w-3 h-3" });
          $$renderer2.push(`<!----></button></div></div></div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--></div></div> <div class="lg:col-span-4">`);
      {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="brutal-card text-center py-32 bg-muted/5 border-dashed"><div class="relative inline-block">`);
        Phone($$renderer2, { class: "w-16 h-16 text-muted/20 mx-auto mb-4" });
        $$renderer2.push(`<!----> <div class="absolute inset-0 flex items-center justify-center"><div class="w-8 h-8 border-2 border-terminal-green/30 animate-ping"></div></div></div> <p class="text-muted-foreground font-bold uppercase tracking-widest text-[10px]">Awaiting Node Selection // BUFFER_IDLE</p></div>`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

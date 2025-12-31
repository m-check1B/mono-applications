import { c as attr, d as attr_class, e as ensure_array_like, f as stringify } from "../../../../chunks/index2.js";
import { o as onDestroy } from "../../../../chunks/index-server.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import { A as Arrow_left } from "../../../../chunks/arrow-left.js";
import { P as Play } from "../../../../chunks/play.js";
import { P as Phone } from "../../../../chunks/phone.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let sessionState = "idle";
    let transcript = [];
    onDestroy(() => {
    });
    function formatTimestamp(iso) {
      return new Date(iso).toLocaleTimeString();
    }
    $$renderer2.push(`<div class="p-6 max-w-7xl mx-auto min-h-screen space-y-6"><header class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b-4 border-foreground pb-6"><div class="flex items-center gap-4"><a href="/scenarios" class="p-2 border-2 border-foreground hover:bg-terminal-green hover:text-void transition-all bg-card">`);
    Arrow_left($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></a> <div><h1 class="text-4xl font-display text-foreground tracking-tighter uppercase">Voice <span class="text-terminal-green">Arena</span></h1> <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground mt-1">1:1 AI TRAINING // STATUS: ${escape_html(sessionState.toUpperCase())}</p></div></div> <div class="flex items-center gap-4">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></header> <div class="grid grid-cols-1 lg:grid-cols-12 gap-6"><div class="lg:col-span-4 space-y-6"><div class="brutal-card"><div class="flex items-center gap-2 mb-4 border-b-2 border-foreground pb-2"><div class="w-3 h-3 bg-terminal-green"></div> <h2 class="text-xl font-display uppercase tracking-tight">Select Persona</h2></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="p-8 text-center"><div class="inline-block w-8 h-8 border-4 border-terminal-green/30 border-t-terminal-green animate-spin"></div> <p class="mt-2 text-xs font-bold uppercase text-muted-foreground">Loading personas...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="brutal-card"><div class="flex items-center gap-2 mb-4 border-b-2 border-foreground pb-2"><div class="w-3 h-3 bg-cyan-data"></div> <h2 class="text-xl font-display uppercase tracking-tight">Controls</h2></div> <div class="space-y-4">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<button${attr("disabled", true, true)}${attr_class(`w-full brutal-btn bg-terminal-green text-void ${stringify("opacity-50 cursor-not-allowed")}`)}>`);
      Play($$renderer2, { class: "w-5 h-5 inline mr-2" });
      $$renderer2.push(`<!----> Start Session</button>`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div></div> <div class="lg:col-span-8"><div class="brutal-card h-full flex flex-col"><div class="flex items-center justify-between gap-2 mb-4 border-b-2 border-foreground pb-2"><div class="flex items-center gap-2"><div class="w-3 h-3 bg-primary"></div> <h2 class="text-xl font-display uppercase tracking-tight">Conversation</h2></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> <div class="flex-1 min-h-[400px] max-h-[600px] overflow-y-auto space-y-3 mb-4 p-4 bg-muted/5 border border-muted">`);
    if (transcript.length === 0) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-12 text-muted-foreground">`);
      Phone($$renderer2, { class: "w-12 h-12 mx-auto mb-4 opacity-20" });
      $$renderer2.push(`<!----> <p class="text-xs font-bold uppercase">Select a persona and start the session</p></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<!--[-->`);
      const each_array_1 = ensure_array_like(transcript);
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let entry = each_array_1[$$index_1];
        $$renderer2.push(`<div${attr_class(`flex ${stringify(entry.role === "trainee" ? "justify-end" : "justify-start")}`)}><div${attr_class(`max-w-[80%] p-3 ${stringify(entry.role === "trainee" ? "bg-terminal-green/20 border-terminal-green text-foreground" : entry.role === "persona" ? "bg-primary/20 border-primary text-foreground" : "bg-muted/20 border-muted text-muted-foreground italic")} border-2`)}>`);
        if (entry.role !== "system") {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="text-[9px] font-bold uppercase opacity-70 mb-1">${escape_html(entry.role === "trainee" ? "You" : "AI")}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--> <div class="text-sm">${escape_html(entry.content)}</div> <div class="text-[9px] opacity-50 mt-1">${escape_html(formatTimestamp(entry.timestamp))}</div></div></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div></div></div>`);
  });
}
export {
  _page as default
};

import "clsx";
import "@sveltejs/kit/internal";
import "../../../../../chunks/exports.js";
import "../../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../../chunks/state.svelte.js";
import { A as Arrow_left } from "../../../../../chunks/arrow-left.js";
import { R as Refresh_cw } from "../../../../../chunks/refresh-cw.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let nodes = [];
    new Map(nodes.map((n) => [n.id, n]));
    $$renderer2.push(`<div class="min-h-screen bg-grid-pattern"><div class="max-w-4xl mx-auto p-6"><header class="mb-8 flex items-center justify-between border-b-4 border-foreground pb-6"><div class="flex items-center gap-4"><a href="/scenarios" class="p-2 border-2 border-foreground hover:bg-terminal-green hover:text-void transition-all bg-card">`);
    Arrow_left($$renderer2, { class: "w-5 h-5" });
    $$renderer2.push(`<!----></a> <div><h1 class="text-3xl font-display uppercase tracking-tighter">Practice <span class="text-terminal-green">Mode</span></h1> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div> <button class="brutal-btn py-2 px-4 text-sm bg-muted hover:bg-accent transition-colors" title="Restart Scenario">`);
    Refresh_cw($$renderer2, { class: "w-4 h-4 inline mr-1" });
    $$renderer2.push(`<!----> Restart</button></header> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="brutal-card p-12 text-center bg-void text-terminal-green"><div class="inline-block animate-spin h-10 w-10 border-4 border-terminal-green/30 border-t-terminal-green"></div> <p class="mt-4 font-bold uppercase tracking-widest animate-pulse">Loading Simulation...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
  });
}
export {
  _page as default
};

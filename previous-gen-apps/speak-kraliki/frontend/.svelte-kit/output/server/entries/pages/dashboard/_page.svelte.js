import { h as head, s as store_get, u as unsubscribe_stores } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import { V as escape_html } from "../../../chunks/context.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import "../../../chunks/auth.js";
import { t } from "../../../chunks/index3.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    head("x1i5gj", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("dashboard.title"))} - Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="container mx-auto p-6 bg-grid-pattern min-h-screen"><div class="flex flex-col md:flex-row md:items-end justify-between mb-12 border-b-2 border-foreground pb-8 gap-6"><div><h1 class="text-5xl font-display tracking-tighter uppercase mb-2">VOP <span class="text-terminal-green">INTELLIGENCE</span></h1> <p class="text-[11px] font-mono font-bold uppercase tracking-[0.3em] text-muted-foreground flex items-center gap-2"><span class="w-2 h-2 bg-terminal-green animate-pulse"></span> Status: Live_Stream // Feed: Enterprise_Feedback_Loop</p></div> <div class="flex items-center gap-4"><a href="/dashboard/surveys" class="brutal-btn bg-terminal-green text-void font-display text-lg">${escape_html((store_get($$store_subs ??= {}, "$t", t)("dashboard.newCampaign") || "NEW_CAMPAIGN").toUpperCase())}</a></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-24 brutal-card bg-void text-terminal-green border-terminal-green"><span class="animate-pulse font-mono font-black tracking-[0.5em] text-xl">>> INITIALIZING_DATA_STREAM...</span></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

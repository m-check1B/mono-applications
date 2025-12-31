import { e as escape_html } from "../../../../chunks/escaping.js";
import "clsx";
import { C as Chart_column } from "../../../../chunks/chart-column.js";
import { S as Sparkles } from "../../../../chunks/sparkles.js";
import { S as Shield } from "../../../../chunks/shield.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="space-y-6"><header class="flex flex-col gap-4"><div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><div><h1 class="text-3xl font-bold flex items-center gap-2">`);
    Chart_column($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> Insights</h1> <p class="text-muted-foreground">Usage, subscription, and orchestration telemetry at a glance.</p></div> <button class="flex items-center gap-2 px-3 py-2 text-sm rounded-full border border-border hover:bg-accent/40 transition-colors">`);
    Sparkles($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Ask assistant</button></div> <div class="bg-gradient-to-br from-primary/10 via-accent/10 to-secondary/10 border border-primary/20 rounded-2xl p-4"><div class="flex items-center justify-between flex-wrap gap-3"><div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">`);
    Shield($$renderer2, { class: "w-5 h-5 text-primary" });
    $$renderer2.push(`<!----></div> <div><p class="text-xs text-muted-foreground">Account Status</p> <p class="font-semibold">${escape_html("Free Tier")}</p></div></div> <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">`);
    Chart_column($$renderer2, { class: "w-5 h-5 text-blue-600" });
    $$renderer2.push(`<!----></div> <div><p class="text-xs text-muted-foreground">BYOK Status</p> <p class="font-semibold">${escape_html("Disabled")}</p></div></div> <div class="flex items-center gap-3"><div class="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">`);
    Sparkles($$renderer2, { class: "w-5 h-5 text-green-600" });
    $$renderer2.push(`<!----></div> <div><p class="text-xs text-muted-foreground">Orchestrations</p> <p class="font-semibold">${escape_html(0)}</p></div></div></div></div></header> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex items-center justify-center h-64"><div class="flex items-center gap-3"><div class="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div> <p class="text-sm text-muted-foreground">Loading insights…</p></div></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

import { a as attr } from "../../../../chunks/attributes.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { B as Brain } from "../../../../chunks/brain.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let isAnalyzing = false;
    $$renderer2.push(`<div class="space-y-6"><div class="flex items-center justify-between"><div><h1 class="text-3xl font-bold flex items-center gap-2">`);
    Brain($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> Shadow Work</h1> <p class="text-muted-foreground mt-1">Jungian psychology insights for productivity and self-awareness</p></div> <button${attr("disabled", isAnalyzing, true)} class="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors">`);
    Brain($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> ${escape_html("Run Analysis")}</button></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="flex items-center justify-center h-64"><p class="text-muted-foreground">Loading shadow insights...</p></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

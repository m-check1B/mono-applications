import { e as escape_html } from "./escaping.js";
import "clsx";
import "@sveltejs/kit/internal";
import "./exports.js";
import "./utils.js";
import "@sveltejs/kit/internal/server";
import "./state.svelte.js";
import "./contextPanel.js";
function PanelRedirect($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let { panel, deepLink = false } = $$props;
    $$renderer2.push(`<div class="min-h-screen bg-background flex items-center justify-center"><div class="text-center"><div class="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div> <p class="text-sm text-muted-foreground uppercase font-bold tracking-wide">Opening ${escape_html(panel)}...</p></div></div>`);
  });
}
export {
  PanelRedirect as P
};

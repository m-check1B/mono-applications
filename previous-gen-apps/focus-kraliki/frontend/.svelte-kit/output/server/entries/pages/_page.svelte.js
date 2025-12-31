import "clsx";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
import "../../chunks/auth2.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="flex items-center justify-center min-h-screen"><p class="text-muted-foreground">Loading...</p></div>`);
  });
}
export {
  _page as default
};

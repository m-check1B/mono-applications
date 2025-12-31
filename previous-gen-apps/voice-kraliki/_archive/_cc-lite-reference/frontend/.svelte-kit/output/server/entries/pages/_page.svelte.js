import "clsx";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
import "../../chunks/client.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<div class="min-h-screen flex items-center justify-center"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>`);
  });
}
export {
  _page as default
};

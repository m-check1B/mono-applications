import { w as head } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import { e as escape_html } from "../../../../chunks/context.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import "marked";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    head("9utcqn", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html("Loading...")} - Learn by Kraliki</title>`);
      });
    });
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="max-w-4xl mx-auto px-4 py-12 text-center"><div class="text-2xl font-bold">Loading course...</div></div>`);
    }
    $$renderer2.push(`<!--]-->`);
  });
}
export {
  _page as default
};

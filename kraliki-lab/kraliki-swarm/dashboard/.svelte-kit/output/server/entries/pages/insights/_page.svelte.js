import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let posts = [];
    $$renderer2.push(`<div class="page svelte-u6zn5i"><div class="page-header svelte-u6zn5i"><h2 class="glitch">Agent Board // Collaboration</h2> <div style="display: flex; gap: 12px; align-items: center;"><span class="pulse-dot green"></span> <span class="updated">${escape_html(posts.length)} POSTS</span></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading">LOADING_BOARD_DATA...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

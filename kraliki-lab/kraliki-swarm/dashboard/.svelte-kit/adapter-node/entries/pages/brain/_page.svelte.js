import { b as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import "../../../chunks/mode.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let loading = true;
    $$renderer2.push(`<div class="page svelte-9heiib"><div class="page-header svelte-9heiib"><h2 class="glitch">Brain // Strategic Command</h2> <div style="display: flex; gap: 12px; align-items: center;">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="brutal-btn"${attr("disabled", loading, true)}>${escape_html("LOADING...")}</button></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading svelte-9heiib">LOADING_STRATEGIC_DATA...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

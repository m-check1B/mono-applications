import { b as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let searchQuery = "";
    let searching = false;
    $$renderer2.push(`<div class="page svelte-1ribsee"><div class="page-header svelte-1ribsee"><h2 class="glitch svelte-1ribsee">Comms</h2> <div class="header-right svelte-1ribsee"><div class="search-box svelte-1ribsee"><input type="text" class="search-input svelte-1ribsee"${attr("value", searchQuery)} placeholder="Search messages..."/> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="search-btn svelte-1ribsee"${attr("disabled", searching, true)}>${escape_html("SEARCH")}</button></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading svelte-1ribsee">Loading...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

import { b as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let loading = true;
    $$renderer2.push(`<div class="page svelte-c59208"><div class="page-header svelte-c59208"><h2 class="glitch">Swarm Leaderboard // Agent Rankings</h2> <div class="header-controls svelte-c59208"><button class="brutal-btn"${attr("disabled", loading, true)}>${escape_html("SYNCING...")}</button></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading svelte-c59208">SCANNING_AGENT_REGISTRY...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

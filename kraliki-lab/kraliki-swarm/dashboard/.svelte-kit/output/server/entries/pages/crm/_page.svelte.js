import { a as attr_class } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { b as attr } from "../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let online = false;
    let opportunities = [];
    let loading = true;
    const CRM_URL = "http://127.0.0.1:8080";
    opportunities.reduce((sum, opp) => sum + opp.amount * opp.probability / 100, 0);
    $$renderer2.push(`<div class="page svelte-8nqzdj"><div class="page-header svelte-8nqzdj"><h2 class="glitch">CRM // Customer Relations</h2> <div style="display: flex; gap: 12px; align-items: center;"><span${attr_class("status-badge svelte-8nqzdj", void 0, { "online": online, "offline": !online })}>${escape_html("ESPOCRM OFFLINE")}</span> <a${attr("href", CRM_URL)} target="_blank" class="brutal-btn">OPEN CRM</a> <button class="brutal-btn"${attr("disabled", loading, true)}>${escape_html("LOADING...")}</button></div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading svelte-8nqzdj">LOADING_CRM_DATA...</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

import { h as head, a as attr_class } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let content = "";
    let status = "";
    head("a7gkw2", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Notebook // Kraliki Swarm</title>`);
      });
    });
    $$renderer2.push(`<div class="notebook-container svelte-a7gkw2"><div class="card brutal-pulse-on-load svelte-a7gkw2"><div class="header-row svelte-a7gkw2"><h2 class="glitch svelte-a7gkw2">NOTEBOOK // SCRATCHPAD</h2> <div class="controls svelte-a7gkw2"><span${attr_class("status-indicator svelte-a7gkw2", void 0, { "visible": status !== "" })}>${escape_html(status)}</span> <button class="brutal-btn small red-btn">CLEAR</button></div></div> <textarea class="brutal-textarea svelte-a7gkw2" placeholder="ENTER_DATA_STREAM..." spellcheck="false">`);
    const $$body = escape_html(content);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea> <div class="footer-info svelte-a7gkw2">LOCAL_STORAGE_PERSISTENCE // ENABLED</div></div></div>`);
  });
}
export {
  _page as default
};

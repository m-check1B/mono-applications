import { b as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let loading = true;
    $$renderer2.push(`<div class="page svelte-h62oi9"><div class="page-header svelte-h62oi9"><h2 class="glitch svelte-h62oi9">Agent Cost Analytics // Claude Code Agents Only</h2> <div class="controls svelte-h62oi9"><button class="brutal-btn svelte-h62oi9"${attr("disabled", loading, true)}>${escape_html("LOADING...")}</button></div></div> <div class="tracking-notice svelte-h62oi9"><span class="notice-icon svelte-h62oi9">ℹ️</span> <div class="notice-content svelte-h62oi9"><strong class="svelte-h62oi9">TRACKING SCOPE:</strong> This dashboard tracks costs from Claude Code agents spawned via the Task tool.
			Interactive CLI usage (claude, codex, gemini, opencode commands) is not currently tracked.</div></div> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="loading-state svelte-h62oi9"><span class="loading-text svelte-h62oi9">CALCULATING_EXPENDITURES...</span></div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
export {
  _page as default
};

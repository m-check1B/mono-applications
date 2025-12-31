import { a as store_get, u as unsubscribe_stores } from "../../../chunks/index2.js";
import { o as onDestroy } from "../../../chunks/index-server.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import "../../../chunks/queryClient.js";
import { t } from "../../../chunks/index3.js";
import "../../../chunks/auth2.js";
function _layout($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const { children } = $$props;
    onDestroy(() => {
    });
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="flex min-h-screen items-center justify-center bg-background text-text-muted"><span class="text-sm">${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.redirecting_sign_in"))}</span></div>`);
    }
    $$renderer2.push(`<!--]-->`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _layout as default
};

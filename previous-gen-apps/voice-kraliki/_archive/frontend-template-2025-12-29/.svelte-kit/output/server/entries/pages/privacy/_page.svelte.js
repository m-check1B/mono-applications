import { a as store_get, u as unsubscribe_stores } from "../../../chunks/index2.js";
import { t } from "../../../chunks/index3.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    const lastUpdated = "2026-01-01";
    $$renderer2.push(`<section class="mx-auto w-full max-w-2xl px-4 py-12 text-text-primary"><header class="space-y-2"><p class="text-xs uppercase tracking-widest text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("legal.section_label"))}</p> <h1 class="text-3xl font-bold">${escape_html(store_get($$store_subs ??= {}, "$t", t)("legal.privacy_title"))}</h1> <p class="text-sm text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("legal.privacy_subtitle"))}</p></header> <article class="card space-y-4"><p>${escape_html(store_get($$store_subs ??= {}, "$t", t)("legal.privacy_body"))}</p> <p class="text-sm text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("legal.last_updated", { date: lastUpdated }))}</p></article></section>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

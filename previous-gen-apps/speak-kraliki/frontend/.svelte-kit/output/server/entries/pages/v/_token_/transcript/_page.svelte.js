import { s as store_get, h as head, u as unsubscribe_stores } from "../../../../../chunks/index2.js";
import { p as page } from "../../../../../chunks/stores.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    store_get($$store_subs ??= {}, "$page", page).params.token;
    head("sc5ook", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>Prepis rozhovoru - Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="min-h-screen flex items-center justify-center p-4 bg-void"><div class="brutal-card max-w-2xl w-full p-6"><h1 class="text-xl mb-6">PREPIS TVEHO ROZHOVORU</h1> `);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center py-8"><span class="animate-pulse">Nacitam...</span></div>`);
    }
    $$renderer2.push(`<!--]--></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

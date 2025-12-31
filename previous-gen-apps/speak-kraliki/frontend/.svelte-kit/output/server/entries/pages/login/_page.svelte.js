import { h as head, s as store_get, d as attr, u as unsubscribe_stores } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import "../../../chunks/auth.js";
import { t } from "../../../chunks/index3.js";
import { V as escape_html } from "../../../chunks/context.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let email = "";
    let password = "";
    let loading = false;
    head("1x05zx6", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.login"))} - Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="min-h-[calc(100vh-60px)] flex items-center justify-center p-4"><div class="brutal-card max-w-md w-full p-8"><div class="text-center mb-8"><h1 class="text-2xl mb-2">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.login").toUpperCase())}</h1> <p class="text-sm text-muted-foreground">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.loginDescription"))}</p></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <form><div class="mb-4"><label for="email" class="block text-sm mb-2">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.email").toUpperCase())}</label> <input id="email" type="email"${attr("value", email)} class="brutal-input w-full" required${attr("disabled", loading, true)}/></div> <div class="mb-6"><label for="password" class="block text-sm mb-2">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.password").toUpperCase())}</label> <input id="password" type="password"${attr("value", password)} class="brutal-input w-full" required${attr("disabled", loading, true)}/></div> <button type="submit" class="brutal-btn brutal-btn-primary w-full mb-4"${attr("disabled", loading, true)}>${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.login").toUpperCase())}</button></form> <div class="text-center text-sm"><span class="text-muted-foreground">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.noAccount"))}</span> <a href="/register" class="text-terminal-green hover:underline">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.register").toUpperCase())}</a></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

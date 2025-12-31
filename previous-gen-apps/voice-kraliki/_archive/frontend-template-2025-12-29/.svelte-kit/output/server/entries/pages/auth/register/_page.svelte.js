import { c as attr, a as store_get, u as unsubscribe_stores } from "../../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../../chunks/exports.js";
import "../../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../../chunks/state.svelte.js";
import "../../../../chunks/auth2.js";
import "../../../../chunks/queryClient.js";
import { t } from "../../../../chunks/index3.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let name = "";
    let email = "";
    let password = "";
    let confirmPassword = "";
    let isSubmitting = false;
    $$renderer2.push(`<section class="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-6 px-4 py-12 text-text-primary"><div class="space-y-2 text-center"><h1 class="text-2xl font-semibold">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.register_title"))}</h1> <p class="text-sm text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.register_subtitle"))}</p></div> <form class="space-y-4"><div class="field"><label for="name" class="field-label">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.full_name_label"))}</label> <input id="name" type="text" class="input-field" autocomplete="name"${attr("value", name)} placeholder="Alex Operator"/></div> <div class="field"><label for="email" class="field-label">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.work_email_label"))}</label> <input id="email" type="email" class="input-field" autocomplete="email"${attr("value", email)} placeholder="you@example.com"/></div> <div class="field"><label for="password" class="field-label">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.password_label"))}</label> <input id="password" type="password" class="input-field" autocomplete="new-password"${attr("value", password)} placeholder="••••••••"/></div> <div class="field"><label for="confirm-password" class="field-label">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.confirm_password_label"))}</label> <input id="confirm-password" type="password" class="input-field" autocomplete="new-password"${attr("value", confirmPassword)} placeholder="••••••••"/></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="btn btn-primary w-full" type="submit"${attr("disabled", isSubmitting, true)}>`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<span>${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.sign_up_button"))}</span>`);
    }
    $$renderer2.push(`<!--]--></button></form> <p class="text-center text-sm text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.already_registered"))} <a class="text-primary hover:underline" href="/auth/login">${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.sign_in"))}</a></p></section>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

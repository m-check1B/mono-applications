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
    let email = "";
    let password = "";
    let isSubmitting = false;
    $$renderer2.push(`<section class="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-6 px-4 py-12 text-text-primary"><div class="space-y-2 text-center"><h1 class="text-2xl font-semibold">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.sign_in_title"))}</h1> <p class="text-sm text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.sign_in_subtitle"))}</p></div> <form class="space-y-4"><div class="field"><label for="email" class="field-label">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.work_email_label"))}</label> <input id="email" type="email" class="input-field" autocomplete="email"${attr("value", email)} placeholder="you@example.com"/></div> <div class="field"><label for="password" class="field-label">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.password_label"))}</label> <input id="password" type="password" class="input-field" autocomplete="current-password"${attr("value", password)} placeholder="••••••••"/></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <button class="btn btn-primary w-full" type="submit"${attr("disabled", isSubmitting, true)}>`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<span>${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.sign_in"))}</span>`);
    }
    $$renderer2.push(`<!--]--></button></form> <div class="relative"><div class="absolute inset-0 flex items-center"><div class="w-full border-t border-text-muted/30"></div></div> <div class="relative flex justify-center text-xs"><span class="bg-background px-2 text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.continue_with"))}</span></div></div> <a href="/auth/sso" class="btn w-full border border-primary bg-primary/10 hover:bg-primary hover:text-white flex items-center justify-center gap-2"><svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg> ${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.sso_button"))}</a> <p class="text-center text-sm text-text-muted">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.need_account"))} <a class="text-primary hover:underline" href="/auth/register">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.create_account"))}</a></p></section>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

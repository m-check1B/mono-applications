import { h as head, s as store_get, e as ensure_array_like, u as unsubscribe_stores } from "../../../../chunks/index2.js";
import { i as isAuthenticated, c as currentUser } from "../../../../chunks/auth.js";
import { s as setLocale, t, l as locale, S as SUPPORTED_LOCALES, g as getLocaleName } from "../../../../chunks/index3.js";
import { V as escape_html } from "../../../../chunks/context.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    function handleLocaleChange(event) {
      const target = event.target;
      setLocale(target.value);
    }
    head("a30v8d", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.settings"))} | Speak by Kraliki</title>`);
      });
    });
    $$renderer2.push(`<div class="container mx-auto px-4 py-8 max-w-2xl"><h1 class="font-display text-3xl mb-8">${escape_html(store_get($$store_subs ??= {}, "$t", t)("nav.settings").toUpperCase())}</h1> `);
    if (store_get($$store_subs ??= {}, "$isAuthenticated", isAuthenticated) && store_get($$store_subs ??= {}, "$currentUser", currentUser)) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<section class="brutal-card p-6 mb-6"><h2 class="font-display text-xl mb-4 text-terminal-green">${escape_html(store_get($$store_subs ??= {}, "$t", t)("settings.profile"))}</h2> <div class="space-y-4"><div><span class="block text-sm text-muted-foreground mb-1">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.firstName"))}</span> <div class="text-lg">${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser).first_name)}</div></div> <div><span class="block text-sm text-muted-foreground mb-1">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.lastName"))}</span> <div class="text-lg">${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser).last_name)}</div></div> <div><span class="block text-sm text-muted-foreground mb-1">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.email"))}</span> <div class="text-lg">${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser).email)}</div></div></div></section> `);
      if (store_get($$store_subs ??= {}, "$currentUser", currentUser).company_name) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<section class="brutal-card p-6 mb-6"><h2 class="font-display text-xl mb-4 text-terminal-green">${escape_html(store_get($$store_subs ??= {}, "$t", t)("settings.company"))}</h2> <div><span class="block text-sm text-muted-foreground mb-1">${escape_html(store_get($$store_subs ??= {}, "$t", t)("auth.companyName"))}</span> <div class="text-lg">${escape_html(store_get($$store_subs ??= {}, "$currentUser", currentUser).company_name)}</div></div></section>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> <section class="brutal-card p-6 mb-6"><h2 class="font-display text-xl mb-4 text-terminal-green">${escape_html(store_get($$store_subs ??= {}, "$t", t)("settings.preferences"))}</h2> <div><label for="language" class="block text-sm text-muted-foreground mb-2">${escape_html(store_get($$store_subs ??= {}, "$t", t)("settings.language"))}</label> `);
      $$renderer2.select(
        {
          id: "language",
          class: "brutal-input w-full max-w-xs",
          value: store_get($$store_subs ??= {}, "$locale", locale),
          onchange: handleLocaleChange
        },
        ($$renderer3) => {
          $$renderer3.push(`<!--[-->`);
          const each_array = ensure_array_like(SUPPORTED_LOCALES);
          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
            let loc = each_array[$$index];
            $$renderer3.option({ value: loc }, ($$renderer4) => {
              $$renderer4.push(`${escape_html(getLocaleName(loc))}`);
            });
          }
          $$renderer3.push(`<!--]-->`);
        }
      );
      $$renderer2.push(`</div></section>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="brutal-card p-6 text-center text-muted-foreground">${escape_html(store_get($$store_subs ??= {}, "$t", t)("common.loading"))}</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

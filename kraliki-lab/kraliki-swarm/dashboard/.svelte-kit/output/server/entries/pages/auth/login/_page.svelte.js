import { c as bind_props } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let form = $$props["form"];
    let data = $$props["data"];
    $$renderer2.push(`<div class="login-container svelte-1i2smtp"><div class="login-box svelte-1i2smtp"><h1 class="svelte-1i2smtp">KRALIKI // LOGIN</h1> <p class="subtitle svelte-1i2smtp">Unified Intelligence Control Center</p> `);
    if (form?.error) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="error svelte-1i2smtp">${escape_html(form.error)}</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <form method="POST"><div class="field svelte-1i2smtp"><label for="email" class="svelte-1i2smtp">Email</label> <input type="email" name="email" id="email" required placeholder="your@email.com" class="svelte-1i2smtp"/></div> <div class="field svelte-1i2smtp"><label for="password" class="svelte-1i2smtp">Password</label> <input type="password" name="password" id="password" required placeholder="********" class="svelte-1i2smtp"/></div> <button type="submit" class="svelte-1i2smtp">ACCESS SYSTEM</button></form> `);
    if (!data.localAuthConfigured) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="notice svelte-1i2smtp">No local users yet. Create an account below.</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (data.authConfigured && !data.ssoDisabled) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<a class="sso-button svelte-1i2smtp" href="/auth/sso">SIGN IN WITH KRALIKI SSO</a>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> `);
    if (!data.localAuthConfigured && !data.authConfigured && !data.ssoDisabled) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="error svelte-1i2smtp">SSO is not configured yet. Use local registration to get access.</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="footer-links svelte-1i2smtp"><a href="/auth/register" class="svelte-1i2smtp">CREATE_ACCOUNT</a> <span class="divider svelte-1i2smtp">|</span> <a href="/" class="svelte-1i2smtp">CONTINUE_AS_LOCAL</a></div></div></div>`);
    bind_props($$props, { form, data });
  });
}
export {
  _page as default
};

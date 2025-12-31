import { c as bind_props } from "../../../../chunks/index2.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
import { b as attr } from "../../../../chunks/attributes.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let form = $$props["form"];
    $$renderer2.push(`<div class="register-container svelte-8bdjn9"><div class="register-box svelte-8bdjn9"><h1 class="svelte-8bdjn9">KRALIKI // CREATE ACCOUNT</h1> <p class="subtitle svelte-8bdjn9">AI Swarm Command Center</p> `);
    if (form?.error) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="error svelte-8bdjn9">${escape_html(form.error)}</div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <form method="POST"><div class="field svelte-8bdjn9"><label for="name" class="svelte-8bdjn9">Name</label> <input type="text" name="name" id="name" required placeholder="Your Name"${attr("value", form?.name ?? "")} class="svelte-8bdjn9"/></div> <div class="field svelte-8bdjn9"><label for="email" class="svelte-8bdjn9">Email</label> <input type="email" name="email" id="email" required placeholder="your@email.com"${attr("value", form?.email ?? "")} class="svelte-8bdjn9"/></div> <div class="field svelte-8bdjn9"><label for="password" class="svelte-8bdjn9">Password</label> <input type="password" name="password" id="password" required placeholder="********" class="svelte-8bdjn9"/></div> <div class="field svelte-8bdjn9"><label for="confirmPassword" class="svelte-8bdjn9">Confirm Password</label> <input type="password" name="confirmPassword" id="confirmPassword" required placeholder="********" class="svelte-8bdjn9"/></div> <div class="field svelte-8bdjn9"><label for="registrationPin" class="svelte-8bdjn9">Registration PIN</label> <input type="password" name="registrationPin" id="registrationPin" required placeholder="Enter PIN"${attr("value", form?.registrationPin ?? "")} class="svelte-8bdjn9"/></div> <button type="submit" class="svelte-8bdjn9">CREATE_ACCOUNT</button></form> <div class="footer-links svelte-8bdjn9"><a href="/auth/login" class="svelte-8bdjn9">BACK_TO_LOGIN</a> <span class="divider svelte-8bdjn9">|</span> <a href="/" class="svelte-8bdjn9">CONTINUE_AS_LOCAL</a></div></div></div>`);
    bind_props($$props, { form });
  });
}
export {
  _page as default
};

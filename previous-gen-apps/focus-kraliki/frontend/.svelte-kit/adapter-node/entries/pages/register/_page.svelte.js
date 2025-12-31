import { a as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import "../../../chunks/auth2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let email = "";
    let password = "";
    let confirmPassword = "";
    let fullName = "";
    let isLoading = false;
    $$renderer2.push(`<div class="flex items-center justify-center min-h-screen bg-background"><div class="w-full max-w-md p-8 space-y-6 brutal-card"><div class="space-y-2 text-center"><h1 class="text-3xl font-black uppercase tracking-tighter">Create Account</h1> <p class="text-sm text-muted-foreground font-mono">Get started with Focus by Kraliki</p></div> <form class="space-y-4">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="space-y-2"><label for="fullName" class="text-xs font-black uppercase tracking-wide">Full Name</label> <input id="fullName" type="text"${attr("value", fullName)} placeholder="John Doe"${attr("disabled", isLoading, true)} class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]" required/></div> <div class="space-y-2"><label for="email" class="text-xs font-black uppercase tracking-wide">Email</label> <input id="email" type="email"${attr("value", email)} placeholder="you@example.com"${attr("disabled", isLoading, true)} class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]" required/></div> <div class="space-y-2"><label for="password" class="text-xs font-black uppercase tracking-wide">Password</label> <input id="password" type="password"${attr("value", password)} placeholder="********"${attr("disabled", isLoading, true)} class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]" required minlength="8"/> <p class="text-xs text-muted-foreground font-mono uppercase font-bold">At least 8 characters</p></div> <div class="space-y-2"><label for="confirmPassword" class="text-xs font-black uppercase tracking-wide">Confirm Password</label> <input id="confirmPassword" type="password"${attr("value", confirmPassword)} placeholder="********"${attr("disabled", isLoading, true)} class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]" required/></div> <button type="submit"${attr("disabled", isLoading, true)} class="brutal-btn w-full disabled:opacity-50 disabled:cursor-not-allowed">${escape_html("CREATE ACCOUNT")}</button></form> <div class="text-center text-sm font-mono"><span class="text-muted-foreground">Already have an account?</span> <button type="button" class="text-primary hover:underline font-bold uppercase">Sign in</button></div></div></div>`);
  });
}
export {
  _page as default
};

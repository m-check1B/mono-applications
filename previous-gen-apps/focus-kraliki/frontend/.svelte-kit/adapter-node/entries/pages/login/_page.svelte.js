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
    let isLoading = false;
    $$renderer2.push(`<div class="flex items-center justify-center min-h-screen bg-background"><div class="w-full max-w-md p-8 space-y-6 brutal-card"><div class="space-y-2 text-center"><h1 class="text-3xl font-black uppercase tracking-tighter">Focus <span class="text-muted-foreground text-lg font-normal">by Kraliki</span></h1> <p class="text-sm text-muted-foreground font-mono">Sign in to your account</p></div> <form class="space-y-4">`);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="space-y-2"><label for="email" class="text-xs font-black uppercase tracking-wide">Email</label> <input id="email" type="email"${attr("value", email)} placeholder="you@example.com"${attr("disabled", isLoading, true)} class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]" required/></div> <div class="space-y-2"><label for="password" class="text-xs font-black uppercase tracking-wide">Password</label> <input id="password" type="password"${attr("value", password)} placeholder="********"${attr("disabled", isLoading, true)} class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]" required/></div> <button type="submit"${attr("disabled", isLoading, true)} class="brutal-btn w-full disabled:opacity-50 disabled:cursor-not-allowed">${escape_html("SIGN IN")}</button></form> <div class="relative"><div class="absolute inset-0 flex items-center"><div class="w-full brutal-border border-t-2"></div></div> <div class="relative flex justify-center text-xs font-black uppercase"><span class="px-2 bg-card text-muted-foreground">Or continue with</span></div></div> <div class="flex flex-col gap-2"><button type="button" class="w-full px-4 py-2 text-sm font-bold uppercase brutal-border hover:bg-accent hover:text-accent-foreground flex items-center justify-center gap-2"><svg class="w-5 h-5 mr-2 inline" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"></path><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"></path><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"></path><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"></path></svg> Continue with Google</button> <a href="/auth/sso" class="w-full px-4 py-2 text-sm font-bold uppercase brutal-border hover:bg-primary hover:text-primary-foreground flex items-center justify-center gap-2 bg-primary/10"><svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg> Sign in with Kraliki SSO</a></div> <div class="text-center text-sm font-mono"><span class="text-muted-foreground">Don't have an account?</span> <button type="button" class="text-primary hover:underline font-bold uppercase">Sign up</button></div></div></div>`);
  });
}
export {
  _page as default
};

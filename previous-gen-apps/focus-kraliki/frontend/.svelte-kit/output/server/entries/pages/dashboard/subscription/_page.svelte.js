import { s as sanitize_props, a as spread_props, c as slot, d as store_get, u as unsubscribe_stores } from "../../../../chunks/index2.js";
import { a as authStore } from "../../../../chunks/auth2.js";
import { I as Icon } from "../../../../chunks/Icon.js";
import { L as Loader_circle } from "../../../../chunks/loader-circle.js";
import { C as Check } from "../../../../chunks/check.js";
function Crown($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M11.562 3.266a.5.5 0 0 1 .876 0L15.39 8.87a1 1 0 0 0 1.516.294L21.183 5.5a.5.5 0 0 1 .798.519l-2.834 10.246a1 1 0 0 1-.956.734H5.81a1 1 0 0 1-.957-.734L2.02 6.02a.5.5 0 0 1 .798-.519l4.276 3.664a1 1 0 0 0 1.516-.294z"
      }
    ],
    ["path", { "d": "M5 21h14" }]
  ];
  Icon($$renderer, spread_props([
    { name: "crown" },
    $$sanitized_props,
    {
      /**
       * @component @name Crown
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTEuNTYyIDMuMjY2YS41LjUgMCAwIDEgLjg3NiAwTDE1LjM5IDguODdhMSAxIDAgMCAwIDEuNTE2LjI5NEwyMS4xODMgNS41YS41LjUgMCAwIDEgLjc5OC41MTlsLTIuODM0IDEwLjI0NmExIDEgMCAwIDEtLjk1Ni43MzRINS44MWExIDEgMCAwIDEtLjk1Ny0uNzM0TDIuMDIgNi4wMmEuNS41IDAgMCAxIC43OTgtLjUxOWw0LjI3NiAzLjY2NGExIDEgMCAwIDAgMS41MTYtLjI5NHoiIC8+CiAgPHBhdGggZD0iTTUgMjFoMTQiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/crown
       * @see https://lucide.dev/guide/packages/lucide-svelte - Documentation
       *
       * @param {Object} props - Lucide icons props and any valid SVG attribute
       * @returns {FunctionalComponent} Svelte component
       *
       */
      iconNode,
      children: ($$renderer2) => {
        $$renderer2.push(`<!--[-->`);
        slot($$renderer2, $$props, "default", {});
        $$renderer2.push(`<!--]-->`);
      },
      $$slots: { default: true }
    }
  ]));
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let currentUser, isPremium;
    currentUser = store_get($$store_subs ??= {}, "$authStore", authStore).user;
    isPremium = currentUser?.isPremium || false;
    $$renderer2.push(`<div class="max-w-4xl mx-auto space-y-8 p-6"><div class="text-center"><h1 class="text-3xl font-bold flex items-center justify-center gap-3">`);
    Crown($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> Upgrade to Pro</h1> <p class="text-muted-foreground mt-2">Unlock unlimited AI capabilities and premium features</p></div> `);
    if (isPremium) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="bg-primary/10 border border-primary/20 rounded-lg p-6 text-center"><div class="flex items-center justify-center gap-2 mb-4">`);
      Crown($$renderer2, { class: "w-6 h-6 text-primary" });
      $$renderer2.push(`<!----> <span class="text-xl font-semibold text-primary">You're a Pro member!</span></div> <p class="text-muted-foreground mb-4">Thank you for supporting Focus by Kraliki. You have access to all premium features.</p> <button class="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">Manage Subscription</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="flex items-center justify-center py-12">`);
        Loader_circle($$renderer2, { class: "w-8 h-8 animate-spin text-primary" });
        $$renderer2.push(`<!----></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="bg-muted/50 rounded-lg p-6"><h3 class="font-semibold mb-3">Current Free Tier Includes:</h3> <ul class="grid md:grid-cols-2 gap-2 text-sm text-muted-foreground"><li class="flex items-center gap-2">`);
    Check($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Limited AI requests per day</li> <li class="flex items-center gap-2">`);
    Check($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Basic task management</li> <li class="flex items-center gap-2">`);
    Check($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> Standard support</li> <li class="flex items-center gap-2">`);
    Check($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> BYOK (Bring Your Own Key) option</li></ul> <p class="text-sm text-muted-foreground mt-4">Want unlimited AI without subscribing? <a href="/dashboard/settings" class="text-primary hover:underline">Use your own OpenRouter API key</a></p></div> <div class="space-y-4"><h3 class="text-xl font-semibold">Frequently Asked Questions</h3> <div class="space-y-3"><details class="bg-card border border-border rounded-lg p-4"><summary class="font-medium cursor-pointer">Can I cancel anytime?</summary> <p class="mt-2 text-sm text-muted-foreground">Yes! You can cancel your subscription at any time. You'll continue to have access until the end of your billing period.</p></details> <details class="bg-card border border-border rounded-lg p-4"><summary class="font-medium cursor-pointer">What payment methods do you accept?</summary> <p class="mt-2 text-sm text-muted-foreground">We accept all major credit cards (Visa, Mastercard, American Express) through our secure payment processor, Stripe.</p></details> <details class="bg-card border border-border rounded-lg p-4"><summary class="font-medium cursor-pointer">What's the difference between Pro and BYOK?</summary> <p class="mt-2 text-sm text-muted-foreground">Pro gives you unlimited AI requests through our hosted infrastructure. BYOK (Bring Your Own Key) lets you use your own OpenRouter API key, giving you complete control over your AI usage and billing.</p></details> <details class="bg-card border border-border rounded-lg p-4"><summary class="font-medium cursor-pointer">Is there a free trial?</summary> <p class="mt-2 text-sm text-muted-foreground">The free tier gives you a taste of Focus by Kraliki's capabilities. You can use it indefinitely with limited AI requests, or upgrade to Pro for unlimited access.</p></details></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

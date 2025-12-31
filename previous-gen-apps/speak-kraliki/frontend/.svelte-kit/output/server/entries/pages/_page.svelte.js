import { h as head, e as ensure_array_like, c as attr_style, s as store_get, u as unsubscribe_stores, b as stringify } from "../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../chunks/exports.js";
import "../../chunks/utils.js";
import { V as escape_html } from "../../chunks/context.js";
import "clsx";
import "@sveltejs/kit/internal/server";
import "../../chunks/state.svelte.js";
import { t } from "../../chunks/index3.js";
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    head("1uha8ag", $$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.title"))} - AI Voice Employee Intelligence</title>`);
      });
    });
    $$renderer2.push(`<div class="min-h-[calc(100vh-60px)] flex flex-col items-center justify-center p-8 relative overflow-hidden bg-grid-pattern"><div class="scanline"></div> <div class="scanline-fast"></div> <div class="absolute inset-0 z-0 opacity-10 pointer-events-none flex items-center justify-center"><div class="grid grid-cols-12 gap-4 w-[150%] h-[150%] rotate-12"><!--[-->`);
    const each_array = ensure_array_like(Array(144));
    for (let i = 0, $$length = each_array.length; i < $$length; i++) {
      each_array[i];
      $$renderer2.push(`<div class="w-full h-8 bg-terminal-green"${attr_style(`animation: pulse-glow ${stringify(2 + i % 5)}s ease-in-out infinite; animation-delay: ${stringify(i % 10 * 0.2)}s; opacity: ${stringify(0.1 + i % 3 * 0.1)}`)}></div>`);
    }
    $$renderer2.push(`<!--]--></div></div> <div class="brutal-card max-w-2xl w-full p-8 text-center relative z-20"><h1 class="text-4xl md:text-5xl mb-4 text-terminal-green font-display hover:animate-glitch cursor-default">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.title").toUpperCase())}</h1> <p class="text-lg mb-2 text-muted-foreground font-mono">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.subtitle"))}</p> <div class="my-8 border-t-2 border-foreground"></div> <p class="mb-8 text-foreground/80 font-mono">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.description"))}</p> <div class="flex flex-col sm:flex-row gap-6 justify-center"><button class="brutal-btn brutal-btn-primary hover:animate-pulse-glow">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.login").toUpperCase())}</button> <button class="brutal-btn hover:animate-pulse-glow">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.register").toUpperCase())}</button></div> <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left"><div class="p-4 border-2 border-foreground bg-card brutal-shadow-sm"><div class="text-terminal-green text-2xl mb-2 font-display">01</div> <h3 class="text-sm font-bold mb-1 uppercase">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.feature1.title"))}</h3> <p class="text-xs text-muted-foreground font-mono">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.feature1.desc"))}</p></div> <div class="p-4 border-2 border-foreground bg-card brutal-shadow-sm"><div class="text-terminal-green text-2xl mb-2 font-display">02</div> <h3 class="text-sm font-bold mb-1 uppercase">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.feature2.title"))}</h3> <p class="text-xs text-muted-foreground font-mono">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.feature2.desc"))}</p></div> <div class="p-4 border-2 border-foreground bg-card brutal-shadow-sm"><div class="text-terminal-green text-2xl mb-2 font-display">03</div> <h3 class="text-sm font-bold mb-1 uppercase">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.feature3.title"))}</h3> <p class="text-xs text-muted-foreground font-mono">${escape_html(store_get($$store_subs ??= {}, "$t", t)("landing.feature3.desc"))}</p></div></div></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};

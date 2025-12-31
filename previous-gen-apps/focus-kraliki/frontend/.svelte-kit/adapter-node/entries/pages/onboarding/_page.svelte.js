import { s as sanitize_props, a as spread_props, c as slot, j as attr_style, g as ensure_array_like, e as attr_class, f as stringify } from "../../../chunks/index2.js";
import "@sveltejs/kit/internal";
import "../../../chunks/exports.js";
import "../../../chunks/utils.js";
import { a as attr } from "../../../chunks/attributes.js";
import "@sveltejs/kit/internal/server";
import "../../../chunks/state.svelte.js";
import "../../../chunks/auth2.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { B as Briefcase } from "../../../chunks/briefcase.js";
import { C as Check } from "../../../chunks/check.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function Calendar_check($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M8 2v4" }],
    ["path", { "d": "M16 2v4" }],
    [
      "rect",
      { "width": "18", "height": "18", "x": "3", "y": "4", "rx": "2" }
    ],
    ["path", { "d": "M3 10h18" }],
    ["path", { "d": "m9 16 2 2 4-4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "calendar-check" },
    $$sanitized_props,
    {
      /**
       * @component @name CalendarCheck
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNOCAydjQiIC8+CiAgPHBhdGggZD0iTTE2IDJ2NCIgLz4KICA8cmVjdCB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHg9IjMiIHk9IjQiIHJ4PSIyIiAvPgogIDxwYXRoIGQ9Ik0zIDEwaDE4IiAvPgogIDxwYXRoIGQ9Im05IDE2IDIgMiA0LTQiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/calendar-check
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
function Code($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["polyline", { "points": "16 18 22 12 16 6" }],
    ["polyline", { "points": "8 6 2 12 8 18" }]
  ];
  Icon($$renderer, spread_props([
    { name: "code" },
    $$sanitized_props,
    {
      /**
       * @component @name Code
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cG9seWxpbmUgcG9pbnRzPSIxNiAxOCAyMiAxMiAxNiA2IiAvPgogIDxwb2x5bGluZSBwb2ludHM9IjggNiAyIDEyIDggMTgiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/code
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
function Compass($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "m16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z"
      }
    ],
    ["circle", { "cx": "12", "cy": "12", "r": "10" }]
  ];
  Icon($$renderer, spread_props([
    { name: "compass" },
    $$sanitized_props,
    {
      /**
       * @component @name Compass
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJtMTYuMjQgNy43Ni0xLjgwNCA1LjQxMWEyIDIgMCAwIDEtMS4yNjUgMS4yNjVMNy43NiAxNi4yNGwxLjgwNC01LjQxMWEyIDIgMCAwIDEgMS4yNjUtMS4yNjV6IiAvPgogIDxjaXJjbGUgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/compass
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
    let currentStep = 0;
    let selectedPersona = null;
    let personas = [];
    let loading = false;
    const personaIcons = {
      "solo-developer": Code,
      "freelancer": Briefcase,
      "explorer": Compass,
      "operations-lead": Calendar_check
    };
    $$renderer2.push(`<div class="min-h-screen bg-gradient-to-br from-background to-accent/10 flex items-center justify-center p-4"><div class="max-w-4xl w-full"><div class="mb-8"><div class="flex items-center justify-between mb-2"><span class="text-sm text-muted-foreground">Step ${escape_html(currentStep + 1)} of 4</span> <button${attr("disabled", loading, true)} class="text-sm text-muted-foreground hover:text-foreground transition">Skip onboarding</button></div> <div class="h-2 bg-muted rounded-full overflow-hidden"><div class="h-full bg-primary transition-all duration-300"${attr_style(`width: ${stringify((currentStep + 1) / 4 * 100)}%`)}></div></div></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="bg-card border border-border rounded-xl shadow-lg p-8">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center mb-8"><h1 class="text-3xl font-bold mb-2">Welcome to Focus by Kraliki!</h1> <p class="text-muted-foreground">Let's personalize your experience. Choose the profile that best describes you:</p></div> <div class="grid grid-cols-1 md:grid-cols-3 gap-6"><!--[-->`);
      const each_array = ensure_array_like(personas);
      for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
        let persona = each_array[$$index];
        const PersonaIcon = personaIcons[persona.id] || Compass;
        $$renderer2.push(`<button${attr("disabled", loading, true)}${attr_class(`group relative p-6 border-2 rounded-lg transition-all hover:border-primary hover:shadow-lg disabled:opacity-50 ${stringify(selectedPersona === persona.id ? "border-primary bg-primary/5" : "border-border")}`)}><div class="flex flex-col items-center text-center space-y-4"><div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition"><!---->`);
        PersonaIcon($$renderer2, { class: "w-8 h-8 text-primary" });
        $$renderer2.push(`<!----></div> <div><h3 class="font-semibold text-lg mb-1">${escape_html(persona.name)}</h3> <p class="text-sm text-muted-foreground">${escape_html(persona.description)}</p></div> `);
        if (selectedPersona === persona.id) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="absolute top-3 right-3">`);
          Check($$renderer2, { class: "w-5 h-5 text-primary" });
          $$renderer2.push(`<!----></div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]--></div></button>`);
      }
      $$renderer2.push(`<!--]--></div>`);
    }
    $$renderer2.push(`<!--]--></div> <div class="text-center mt-6 text-sm text-muted-foreground"><p>Need help? <a href="/docs" class="text-primary hover:underline">Visit our documentation</a></p></div></div></div>`);
  });
}
export {
  _page as default
};

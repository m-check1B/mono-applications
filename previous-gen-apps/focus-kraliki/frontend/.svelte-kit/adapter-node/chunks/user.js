import { s as sanitize_props, a as spread_props, c as slot } from "./index2.js";
import { I as Icon } from "./Icon.js";
function Send($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"
      }
    ],
    ["path", { "d": "m21.854 2.147-10.94 10.939" }]
  ];
  Icon($$renderer, spread_props([
    { name: "send" },
    $$sanitized_props,
    {
      /**
       * @component @name Send
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTQuNTM2IDIxLjY4NmEuNS41IDAgMCAwIC45MzctLjAyNGw2LjUtMTlhLjQ5Ni40OTYgMCAwIDAtLjYzNS0uNjM1bC0xOSA2LjVhLjUuNSAwIDAgMC0uMDI0LjkzN2w3LjkzIDMuMThhMiAyIDAgMCAxIDEuMTEyIDEuMTF6IiAvPgogIDxwYXRoIGQ9Im0yMS44NTQgMi4xNDctMTAuOTQgMTAuOTM5IiAvPgo8L3N2Zz4K) - https://lucide.dev/icons/send
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
function User($$renderer, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" }],
    ["circle", { "cx": "12", "cy": "7", "r": "4" }]
  ];
  Icon($$renderer, spread_props([
    { name: "user" },
    $$sanitized_props,
    {
      /**
       * @component @name User
       * @description Lucide SVG icon component, renders SVG Element with children.
       *
       * @preview ![img](data:image/svg+xml;base64,PHN2ZyAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogIHdpZHRoPSIyNCIKICBoZWlnaHQ9IjI0IgogIHZpZXdCb3g9IjAgMCAyNCAyNCIKICBmaWxsPSJub25lIgogIHN0cm9rZT0iIzAwMCIgc3R5bGU9ImJhY2tncm91bmQtY29sb3I6ICNmZmY7IGJvcmRlci1yYWRpdXM6IDJweCIKICBzdHJva2Utd2lkdGg9IjIiCiAgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIgogIHN0cm9rZS1saW5lam9pbj0icm91bmQiCj4KICA8cGF0aCBkPSJNMTkgMjF2LTJhNCA0IDAgMCAwLTQtNEg5YTQgNCAwIDAgMC00IDR2MiIgLz4KICA8Y2lyY2xlIGN4PSIxMiIgY3k9IjciIHI9IjQiIC8+Cjwvc3ZnPgo=) - https://lucide.dev/icons/user
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
export {
  Send as S,
  User as U
};

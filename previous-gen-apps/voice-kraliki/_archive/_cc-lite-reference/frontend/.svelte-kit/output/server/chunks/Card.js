import { z as attr_class, G as stringify } from "./index2.js";
function Card($$renderer, $$props) {
  let { class: className = "", header, children, footer } = $$props;
  $$renderer.push(`<div${attr_class(`bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 ${stringify(className)}`)}>`);
  if (header) {
    $$renderer.push("<!--[-->");
    $$renderer.push(`<div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">`);
    header($$renderer);
    $$renderer.push(`<!----></div>`);
  } else {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--> <div class="px-6 py-4">`);
  children?.($$renderer);
  $$renderer.push(`<!----></div> `);
  if (footer) {
    $$renderer.push("<!--[-->");
    $$renderer.push(`<div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">`);
    footer($$renderer);
    $$renderer.push(`<!----></div>`);
  } else {
    $$renderer.push("<!--[!-->");
  }
  $$renderer.push(`<!--]--></div>`);
}
export {
  Card as C
};

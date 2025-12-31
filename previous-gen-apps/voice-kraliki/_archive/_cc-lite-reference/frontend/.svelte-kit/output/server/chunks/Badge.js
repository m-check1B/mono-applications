import { z as attr_class, G as stringify } from "./index2.js";
function Badge($$renderer, $$props) {
  let { variant = "gray", class: className = "", children } = $$props;
  const variantClasses = {
    primary: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    success: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
    danger: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
    gray: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
  };
  $$renderer.push(`<span${attr_class(`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${stringify(variantClasses[variant])} ${stringify(className)}`)}>`);
  children?.($$renderer);
  $$renderer.push(`<!----></span>`);
}
export {
  Badge as B
};

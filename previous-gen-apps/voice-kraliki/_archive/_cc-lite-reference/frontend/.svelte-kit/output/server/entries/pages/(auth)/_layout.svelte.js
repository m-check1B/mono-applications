import "clsx";
function _layout($$renderer, $$props) {
  let { children } = $$props;
  $$renderer.push(`<div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900 px-4"><div class="w-full max-w-md">`);
  children?.($$renderer);
  $$renderer.push(`<!----></div></div>`);
}
export {
  _layout as default
};

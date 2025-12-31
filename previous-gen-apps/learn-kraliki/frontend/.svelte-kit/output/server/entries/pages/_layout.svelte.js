import "clsx";
function _layout($$renderer, $$props) {
  let { children } = $$props;
  $$renderer.push(`<div class="min-h-screen flex flex-col"><nav class="bg-black text-white border-b-4 border-black"><div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between"><a href="/" class="text-2xl font-black tracking-tight hover:text-gray-300 transition-colors">LEARN<span class="text-blue-400">.</span>KRALIKI</a> <div class="flex items-center gap-6"><a href="/" class="font-bold hover:text-gray-300 transition-colors">COURSES</a> <a href="https://kraliki.verduona.dev" class="font-bold hover:text-gray-300 transition-colors">DASHBOARD</a></div></div></nav> <main class="flex-1">`);
  children($$renderer);
  $$renderer.push(`<!----></main> <footer class="bg-black text-white border-t-4 border-black py-8"><div class="max-w-6xl mx-auto px-4 text-center"><p class="font-bold">Learn by Kraliki - Part of the Verduona Ecosystem</p> <p class="text-gray-400 mt-2">Business education and AI training</p></div></footer></div>`);
}
export {
  _layout as default
};

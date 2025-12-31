import { c as create_ssr_component, a as subscribe, e as each, b as add_attribute, d as escape } from "../../chunks/ssr.js";
import { w as writable } from "../../chunks/index.js";
import { p as page } from "../../chunks/stores.js";
function getInitialTheme() {
  return "light";
}
const theme = writable(getInitialTheme());
const css = {
  code: ".container{max-width:1000px}",
  map: `{"version":3,"file":"+layout.svelte","sources":["+layout.svelte"],"sourcesContent":["<script lang=\\"ts\\">import \\"../app.css\\";\\nimport { theme, toggleTheme } from \\"$lib/stores/theme\\";\\nimport { page } from \\"$app/stores\\";\\nconst navItems = [\\n  { href: \\"/\\", label: \\"Search\\", icon: \\"\\\\u{1F50D}\\" },\\n  { href: \\"/capture\\", label: \\"Capture\\", icon: \\"\\\\u{1F4E5}\\" },\\n  { href: \\"/graph\\", label: \\"Graph\\", icon: \\"\\\\u{1F578}\\\\uFE0F\\" },\\n  { href: \\"/recent\\", label: \\"Recent\\", icon: \\"\\\\u{1F552}\\" }\\n];\\n<\/script>\\n\\n<div class=\\"min-h-screen flex flex-col\\">\\n\\t<div class=\\"scanline\\"></div>\\n\\n\\t<!-- Header -->\\n\\t<header class=\\"border-b-2 border-border bg-card\\">\\n\\t\\t<div class=\\"container mx-auto px-4\\">\\n\\t\\t\\t<div class=\\"flex flex-col md:flex-row items-center justify-between py-4 gap-4\\">\\n\\t\\t\\t\\t<a href=\\"/\\" class=\\"flex items-center space-x-3 group\\">\\n\\t\\t\\t\\t\\t<span class=\\"text-3xl brutal-card p-1 bg-void group-hover:bg-terminal-green transition-colors\\">🎯</span>\\n\\t\\t\\t\\t\\t<div class=\\"flex flex-col\\">\\n\\t\\t\\t\\t\\t\\t<span class=\\"text-2xl font-display tracking-tighter\\">RECALL-LITE</span>\\n\\t\\t\\t\\t\\t\\t<span class=\\"text-[10px] font-mono font-bold tracking-[0.2em] opacity-50 uppercase -mt-1\\">Memory_Engine // v0.1.0</span>\\n\\t\\t\\t\\t\\t</div>\\n\\t\\t\\t\\t</a>\\n\\n\\t\\t\\t\\t<nav class=\\"flex items-center space-x-2\\">\\n\\t\\t\\t\\t\\t{#each navItems as item}\\n\\t\\t\\t\\t\\t\\t<a \\n\\t\\t\\t\\t\\t\\t\\thref={item.href} \\n\\t\\t\\t\\t\\t\\t\\tclass=\\"px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider transition-all border-2 {$page.url.pathname === item.href ? 'bg-terminal-green text-void border-terminal-green' : 'border-transparent hover:border-border hover:bg-secondary'}\\"\\n\\t\\t\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t\\t\\t<span class=\\"mr-1 opacity-50\\">{item.icon}</span> {item.label}\\n\\t\\t\\t\\t\\t\\t</a>\\n\\t\\t\\t\\t\\t{/each}\\n\\n\\t\\t\\t\\t\\t<!-- Dark Mode Toggle -->\\n\\t\\t\\t\\t\\t<button\\n\\t\\t\\t\\t\\t\\ton:click={toggleTheme}\\n\\t\\t\\t\\t\\t\\tclass=\\"ml-2 brutal-btn !p-1.5 !px-2.5 text-sm\\"\\n\\t\\t\\t\\t\\t\\taria-label=\\"Toggle dark mode\\"\\n\\t\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t\\t{#if $theme === 'dark'}\\n\\t\\t\\t\\t\\t\\t\\t☀️\\n\\t\\t\\t\\t\\t\\t{:else}\\n\\t\\t\\t\\t\\t\\t\\t🌙\\n\\t\\t\\t\\t\\t\\t{/if}\\n\\t\\t\\t\\t\\t</button>\\n\\t\\t\\t\\t</nav>\\n\\t\\t\\t</div>\\n\\t\\t</div>\\n\\t</header>\\n\\n\\t<!-- Main Content -->\\n\\t<main class=\\"flex-1 container mx-auto px-4 py-8 relative\\">\\n\\t\\t<div class=\\"absolute top-0 left-0 w-full h-1 bg-terminal-green opacity-20\\"></div>\\n\\t\\t<slot />\\n\\t</main>\\n\\n\\t<!-- Footer -->\\n\\t<footer class=\\"border-t-2 border-border bg-void text-concrete py-6 mt-8\\">\\n\\t\\t<div class=\\"container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4\\">\\n\\t\\t\\t<div class=\\"text-[10px] font-mono font-bold tracking-widest opacity-50 uppercase\\">\\n\\t\\t\\t\\t&copy; 2026 VERDUONA S.R.O. // OCELOT_PLATFORM\\n\\t\\t\\t</div>\\n\\t\\t\\t<div class=\\"flex space-x-6 text-[10px] font-mono font-bold uppercase tracking-widest\\">\\n\\t\\t\\t\\t<a href=\\"https://github.com/adminmatej/github\\" class=\\"hover:text-terminal-green transition-colors\\">[ GITHUB ]</a>\\n\\t\\t\\t\\t<a href=\\"/privacy\\" class=\\"hover:text-terminal-green transition-colors\\">[ PRIVACY ]</a>\\n\\t\\t\\t\\t<span class=\\"text-cyan-data\\">STATUS: NOMINAL</span>\\n\\t\\t\\t</div>\\n\\t\\t</div>\\n\\t</footer>\\n</div>\\n\\n<style>\\n\\t:global(.container) {\\n\\t\\tmax-width: 1000px;\\n\\t}\\n</style>"],"names":[],"mappings":"AA2ES,UAAY,CACnB,SAAS,CAAE,MACZ"}`
};
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $page, $$unsubscribe_page;
  let $theme, $$unsubscribe_theme;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  $$unsubscribe_theme = subscribe(theme, (value) => $theme = value);
  const navItems = [
    {
      href: "/",
      label: "Search",
      icon: "🔍"
    },
    {
      href: "/capture",
      label: "Capture",
      icon: "📥"
    },
    {
      href: "/graph",
      label: "Graph",
      icon: "🕸️"
    },
    {
      href: "/recent",
      label: "Recent",
      icon: "🕒"
    }
  ];
  $$result.css.add(css);
  $$unsubscribe_page();
  $$unsubscribe_theme();
  return `<div class="min-h-screen flex flex-col"><div class="scanline"></div>  <header class="border-b-2 border-border bg-card"><div class="container mx-auto px-4"><div class="flex flex-col md:flex-row items-center justify-between py-4 gap-4"><a href="/" class="flex items-center space-x-3 group" data-svelte-h="svelte-3s41fe"><span class="text-3xl brutal-card p-1 bg-void group-hover:bg-terminal-green transition-colors">🎯</span> <div class="flex flex-col"><span class="text-2xl font-display tracking-tighter">RECALL-LITE</span> <span class="text-[10px] font-mono font-bold tracking-[0.2em] opacity-50 uppercase -mt-1">Memory_Engine // v0.1.0</span></div></a> <nav class="flex items-center space-x-2">${each(navItems, (item) => {
    return `<a${add_attribute("href", item.href, 0)} class="${"px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider transition-all border-2 " + escape(
      $page.url.pathname === item.href ? "bg-terminal-green text-void border-terminal-green" : "border-transparent hover:border-border hover:bg-secondary",
      true
    )}"><span class="mr-1 opacity-50">${escape(item.icon)}</span> ${escape(item.label)} </a>`;
  })}  <button class="ml-2 brutal-btn !p-1.5 !px-2.5 text-sm" aria-label="Toggle dark mode">${$theme === "dark" ? `☀️` : `🌙`}</button></nav></div></div></header>  <main class="flex-1 container mx-auto px-4 py-8 relative"><div class="absolute top-0 left-0 w-full h-1 bg-terminal-green opacity-20"></div> ${slots.default ? slots.default({}) : ``}</main>  <footer class="border-t-2 border-border bg-void text-concrete py-6 mt-8" data-svelte-h="svelte-1ozta3l"><div class="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4"><div class="text-[10px] font-mono font-bold tracking-widest opacity-50 uppercase">© 2026 VERDUONA S.R.O. // OCELOT_PLATFORM</div> <div class="flex space-x-6 text-[10px] font-mono font-bold uppercase tracking-widest"><a href="https://github.com/adminmatej/github" class="hover:text-terminal-green transition-colors">[ GITHUB ]</a> <a href="/privacy" class="hover:text-terminal-green transition-colors">[ PRIVACY ]</a> <span class="text-cyan-data">STATUS: NOMINAL</span></div></div></footer> </div>`;
});
export {
  Layout as default
};

import { c as create_ssr_component, b as add_attribute, e as each, d as escape } from "../../chunks/ssr.js";
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let query = "";
  let results = [];
  const categories = [
    "all",
    "decisions",
    "insights",
    "ideas",
    "learnings",
    "customers",
    "competitors",
    "research",
    "sessions"
  ];
  return `${$$result.head += `<!-- HEAD_svelte-tmwd1m_START -->${$$result.title = `<title>Search • RECALL-LITE</title>`, ""}<!-- HEAD_svelte-tmwd1m_END -->`, ""} <div class="max-w-4xl mx-auto"><div class="mb-10" data-svelte-h="svelte-8ndd10"><h1 class="text-4xl font-display mb-2">SEARCH_KNOWLEDGE_BASE</h1> <div class="flex items-center gap-2 text-xs font-mono font-bold text-muted-foreground uppercase tracking-wider"><span class="text-terminal-green">&gt;&gt; STATUS:</span> READY_FOR_QUERY</div></div>  <div class="brutal-card p-6 mb-8 bg-card relative overflow-hidden"><div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[80px] leading-none pointer-events-none select-none" data-svelte-h="svelte-lofhoo">SEARCH</div> <div class="mb-6"><label for="query" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70" data-svelte-h="svelte-b8bade">Query String</label> <input id="query" type="text" placeholder="Find decisions, insights, learnings..." class="brutal-input text-lg"${add_attribute("value", query, 0)}></div> <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6"><div><label for="category" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70" data-svelte-h="svelte-kdga2z">Filter: Category</label> <select id="category" class="brutal-input appearance-none cursor-pointer">${each(categories, (cat) => {
    return `<option${add_attribute("value", cat === "all" ? "" : cat, 0)}>${escape(cat.toUpperCase())}</option>`;
  })}</select></div> <div><label for="searchType" class="block text-xs font-bold uppercase tracking-widest mb-2 opacity-70" data-svelte-h="svelte-1pt3xv7">Engine: Search Type</label> <select id="searchType" class="brutal-input appearance-none cursor-pointer"><option value="hybrid" data-svelte-h="svelte-1iri7ah">HYBRID (KEYWORD + SEMANTIC)</option><option value="keyword" data-svelte-h="svelte-193m0e9">KEYWORD_ONLY</option><option value="semantic" data-svelte-h="svelte-1xtcdxj">SEMANTIC_ONLY</option></select></div></div> <button ${!query.trim() ? "disabled" : ""} class="brutal-btn w-full !bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed">${escape("EXECUTE_QUERY")}</button></div>  ${``}  ${results.length > 0 ? `<div class="mb-4 flex items-center justify-between border-b-2 border-border pb-2"><div class="text-[10px] font-mono font-bold uppercase tracking-widest">QUERY_RESULTS: ${escape(results.length)} ITEMS_FOUND</div> <div class="text-[10px] font-mono font-bold text-terminal-green uppercase tracking-widest">TIME: ${escape((/* @__PURE__ */ new Date()).toLocaleTimeString())}</div></div> <div class="space-y-6">${each(results, (result) => {
    return `<div class="brutal-card p-6 bg-card group hover:border-terminal-green transition-colors"><div class="flex items-start justify-between mb-4"><div class="flex-1"><div class="flex flex-wrap items-center gap-3 mb-3"><span class="text-[10px] font-bold px-2 py-0.5 bg-void text-terminal-green border border-terminal-green uppercase tracking-widest">${escape(result.category)}</span> <h2 class="text-xl font-display group-hover:text-terminal-green transition-colors">${escape(result.title)}</h2></div> ${result.tags.length > 0 ? `<div class="flex flex-wrap gap-2 mb-4">${each(result.tags, (tag) => {
      return `<span class="text-[9px] font-bold px-2 py-0.5 border border-border opacity-60 uppercase tracking-tighter">#${escape(tag)} </span>`;
    })} </div>` : ``} <p class="text-sm font-mono opacity-80 mb-6 line-clamp-3 leading-relaxed">${escape(result.content)}</p> <a href="${"/item/" + escape(result.category, true) + "/" + escape(result.id, true)}" class="inline-flex items-center text-xs font-bold uppercase tracking-widest text-primary hover:text-terminal-green transition-colors"><span class="mr-1" data-svelte-h="svelte-1ipc5ay">&gt;&gt;</span> VIEW_FULL_ITEM</a> </div></div> </div>`;
  })}</div>` : `${``}`}</div>`;
});
export {
  Page as default
};

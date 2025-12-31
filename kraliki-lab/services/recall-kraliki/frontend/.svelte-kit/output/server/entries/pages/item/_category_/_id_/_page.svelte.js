import { c as create_ssr_component, a as subscribe, d as escape, e as each } from "../../../../../chunks/ssr.js";
import { p as page } from "../../../../../chunks/stores.js";
import { a as getItem } from "../../../../../chunks/api.js";
function parseWikilinks(content) {
  return content.replace(/\[\[([^\]|]+)(\|([^\]]+))?\]\]/g, (match, target, _, label) => {
    const displayText = label || target;
    return `<a href="/item/${target}" class="text-primary hover:text-terminal-green font-bold underline decoration-2 underline-offset-4 decoration-primary/30 transition-colors">${displayText}</a>`;
  });
}
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let category;
  let id;
  let $page, $$unsubscribe_page;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  let item = null;
  let loading = true;
  let error = "";
  async function loadItem() {
    if (!category || !id) return;
    loading = true;
    error = "";
    item = null;
    try {
      item = await getItem(category, id);
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load item";
    } finally {
      loading = false;
    }
  }
  category = $page.params.category;
  id = $page.params.id;
  {
    if (category && id) {
      loadItem();
    }
  }
  $$unsubscribe_page();
  return `${$$result.head += `<!-- HEAD_svelte-1dqu8u9_START -->${$$result.title = `<title>${escape(item?.title || "RECORD")} • RECALL-LITE</title>`, ""}<!-- HEAD_svelte-1dqu8u9_END -->`, ""} <div class="max-w-4xl mx-auto">${loading ? `<div class="brutal-card text-center py-20 bg-card"><div class="text-2xl font-display text-terminal-green animate-pulse" data-svelte-h="svelte-h02blq">ACCESSING_MEMORY_OBJECT...</div> <div class="mt-4 font-mono text-[10px] opacity-40 uppercase tracking-[0.3em]">Address: ${escape(category)}/${escape(id)}</div></div>` : `${error ? `<div class="brutal-card border-system-red bg-system-red/10 text-system-red p-4 font-mono text-sm"><span class="font-bold uppercase" data-svelte-h="svelte-p97r4s">[ ACCESS_DENIED ]</span> ${escape(error)}</div>` : `${item ? ` <div class="mb-8 border-b-2 border-border pb-6 relative"><div class="absolute -top-4 -left-4 bg-void text-terminal-green font-bold text-[10px] px-2 py-1 uppercase border border-terminal-green shadow-brutal" data-svelte-h="svelte-1mkx04k">RECORD_ACTIVE</div> <div class="flex flex-wrap items-center gap-3 mb-4"><span class="text-xs font-bold px-3 py-1 bg-void text-terminal-green border-2 border-terminal-green uppercase tracking-widest">${escape(item.category)}</span> <h1 class="text-4xl font-display tracking-tight">${escape(item.title)}</h1></div> ${item.tags && item.tags.length > 0 ? `<div class="flex flex-wrap gap-2">${each(item.tags, (tag) => {
    return `<span class="text-[10px] font-bold px-2 py-0.5 border border-border opacity-70 uppercase tracking-tighter">#${escape(tag)} </span>`;
  })}</div>` : ``}</div>  <div class="brutal-card p-8 bg-card mb-8 relative"><div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[60px] leading-none pointer-events-none select-none" data-svelte-h="svelte-doeilf">CONTENT</div> <div class="markdown relative z-10"><!-- HTML_TAG_START -->${parseWikilinks(item.content)}<!-- HTML_TAG_END --></div></div> <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8"> ${item.related && item.related.length > 0 ? `<div class="brutal-card p-6 bg-card relative"><div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[40px] leading-none pointer-events-none select-none" data-svelte-h="svelte-zdjffh">LINKS</div> <h3 class="font-display text-sm border-b border-border pb-2 mb-4">🔗 RELATED_ITEMS (${escape(item.related.length)})</h3> <div class="space-y-3">${each(item.related, (relatedId) => {
    return `${relatedId.includes("/") ? (() => {
      let [cat, rid] = relatedId.split("/");
      return ` <a href="${"/item/" + escape(cat, true) + "/" + escape(rid, true)}" class="block p-3 border-2 border-transparent hover:border-terminal-green bg-void/5 hover:bg-terminal-green/5 transition-all group"><div class="flex items-center justify-between"><span class="text-[9px] font-bold px-1.5 py-0.5 bg-void text-terminal-green uppercase tracking-widest">${escape(cat)}</span> <span class="text-[10px] font-mono opacity-50" data-svelte-h="svelte-h2ygp0">&gt;&gt; OPEN</span></div> <div class="text-xs font-bold mt-1 group-hover:text-terminal-green">${escape(rid)}</div> </a>`;
    })() : ``}`;
  })}</div></div>` : ``}  ${item.wikilinks && item.wikilinks.length > 0 ? `<div class="brutal-card p-6 bg-card relative"><div class="absolute top-0 right-0 p-2 opacity-10 font-mono text-[40px] leading-none pointer-events-none select-none" data-svelte-h="svelte-q2xnwa">REFS</div> <h3 class="font-display text-sm border-b border-border pb-2 mb-4">📎 WIKILINKS (${escape(item.wikilinks.length)})</h3> <div class="space-y-3">${each(item.wikilinks, (wikilink) => {
    let parsed = wikilink.match(/\[\[([^\]|]+)(\|([^\]]+))?\]\]/);
    return ` ${parsed ? (() => {
      let target = parsed[1], label = parsed[3] || target;
      return `  <a href="${"/item/" + escape(target, true)}" class="block p-3 border-2 border-transparent hover:border-cyan-data bg-void/5 hover:bg-cyan-data/5 transition-all group"><div class="flex items-center justify-between"><span class="text-xs font-bold group-hover:text-cyan-data">${escape(label)}</span> <span class="text-[10px] font-mono opacity-50">-&gt; ${escape(target)}</span></div> </a>`;
    })() : ``}`;
  })}</div></div>` : ``}</div>  <div class="brutal-card p-6 bg-void text-concrete mb-10"><h3 class="font-display text-sm border-b border-concrete/20 pb-2 mb-4 text-terminal-green" data-svelte-h="svelte-7akhy7">ℹ️ OBJECT_METADATA</h3> <div class="space-y-3 text-[11px] font-mono uppercase tracking-wider"><div class="flex justify-between border-b border-concrete/10 pb-1"><span class="opacity-50" data-svelte-h="svelte-wflk5d">UNIQUE_ID:</span> <span class="font-bold">${escape(item.id)}</span></div> <div class="flex justify-between border-b border-concrete/10 pb-1"><span class="opacity-50" data-svelte-h="svelte-p2i75r">CLASS_TYPE:</span> <span class="text-terminal-green font-bold">${escape(item.category)}</span></div> <div class="flex justify-between border-b border-concrete/10 pb-1"><span class="opacity-50" data-svelte-h="svelte-1ycycqc">SOURCE_FILE:</span> <span class="text-cyan-data font-bold truncate max-w-[200px]">${escape(item.file_path)}</span></div></div></div>  <div class="flex flex-wrap gap-4" data-svelte-h="svelte-q8yyuf"><a href="/" class="brutal-btn !bg-secondary !text-secondary-foreground !py-2 !px-4 text-xs">&lt;&lt; RETURN_TO_SEARCH</a> <a href="/recent" class="brutal-btn !bg-void !text-concrete !py-2 !px-4 text-xs border-concrete/20">VIEW_RECENT_STREAM</a></div>` : ``}`}`}</div>`;
});
export {
  Page as default
};

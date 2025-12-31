import { h as head, e as attr_class, f as stringify, g as ensure_array_like } from "../../../../chunks/index2.js";
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js/lib/core";
import javascript from "highlight.js/lib/languages/javascript";
import typescript from "highlight.js/lib/languages/typescript";
import python from "highlight.js/lib/languages/python";
import json from "highlight.js/lib/languages/json";
import bash from "highlight.js/lib/languages/bash";
import sql from "highlight.js/lib/languages/sql";
import xml from "highlight.js/lib/languages/xml";
import css from "highlight.js/lib/languages/css";
import "dompurify";
/* empty css                                                                */
import { h as html } from "../../../../chunks/html.js";
import { S as Sparkles } from "../../../../chunks/sparkles.js";
import { U as User, S as Send } from "../../../../chunks/user.js";
import { B as Bot } from "../../../../chunks/bot.js";
import { a as attr } from "../../../../chunks/attributes.js";
import { e as escape_html } from "../../../../chunks/escaping.js";
function MarkdownRenderer($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    hljs.registerLanguage("javascript", javascript);
    hljs.registerLanguage("typescript", typescript);
    hljs.registerLanguage("python", python);
    hljs.registerLanguage("json", json);
    hljs.registerLanguage("bash", bash);
    hljs.registerLanguage("sql", sql);
    hljs.registerLanguage("html", xml);
    hljs.registerLanguage("xml", xml);
    hljs.registerLanguage("css", css);
    let { className = "" } = $$props;
    let renderedHtml = "";
    marked.use(markedHighlight({
      langPrefix: "hljs language-",
      highlight(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : "plaintext";
        return hljs.highlight(code, { language }).value;
      }
    }));
    marked.setOptions({ breaks: true, gfm: true });
    head("1fegv8i", $$renderer2, ($$renderer3) => {
      $$renderer3.push(`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"/>`);
    });
    $$renderer2.push(`<div${attr_class(`markdown-content ${stringify(className)}`)}>${html(renderedHtml)}</div>`);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let messages = [];
    let inputMessage = "";
    let isLoading = false;
    let useOrchestrator = false;
    function formatTime(date) {
      return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(date);
    }
    $$renderer2.push(`<div class="flex flex-col h-[calc(100vh-8rem)]"><div class="flex items-center justify-between pb-4 border-b border-border"><div><h1 class="text-3xl font-bold flex items-center gap-2">`);
    Sparkles($$renderer2, { class: "w-8 h-8 text-primary" });
    $$renderer2.push(`<!----> AI Chat</h1> <p class="text-muted-foreground mt-1">Powered by Claude &amp; GPT-4</p></div> <div class="flex items-center gap-4"><label class="inline-flex items-center gap-2 text-sm"><input type="checkbox"${attr("checked", useOrchestrator, true)} class="rounded border-border"/> Use Orchestrator</label> <button class="px-4 py-2 text-sm bg-accent text-accent-foreground rounded-md hover:bg-accent/80 transition-colors">Clear Chat</button></div></div> <div class="flex-1 overflow-y-auto py-6 space-y-4"><!--[-->`);
    const each_array = ensure_array_like(messages);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let message = each_array[$$index];
      $$renderer2.push(`<div${attr_class(`flex items-start gap-3 ${stringify(message.role === "user" ? "flex-row-reverse" : "")}`)}><div${attr_class(`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${stringify(message.role === "user" ? "bg-primary text-primary-foreground" : "bg-accent text-accent-foreground")}`)}>`);
      if (message.role === "user") {
        $$renderer2.push("<!--[-->");
        User($$renderer2, { class: "w-4 h-4" });
      } else {
        $$renderer2.push("<!--[!-->");
        Bot($$renderer2, { class: "w-4 h-4" });
      }
      $$renderer2.push(`<!--]--></div> <div class="flex-1 max-w-3xl"><div${attr_class(`p-4 rounded-lg ${stringify(message.role === "user" ? "bg-primary text-primary-foreground ml-auto" : "bg-card border border-border")}`)}>`);
      if (message.role === "user") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<p class="whitespace-pre-wrap break-words">${escape_html(message.content)}</p>`);
      } else {
        $$renderer2.push("<!--[!-->");
        MarkdownRenderer($$renderer2, { content: message.content });
      }
      $$renderer2.push(`<!--]--></div> <p${attr_class(`text-xs text-muted-foreground mt-1 ${stringify(message.role === "user" ? "text-right" : "")}`)}>${escape_html(formatTime(message.timestamp))}</p></div></div>`);
    }
    $$renderer2.push(`<!--]--> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--> <div class="pt-4 border-t border-border"><form class="flex gap-3"><input type="text"${attr("value", inputMessage)} placeholder="Type your message... (e.g., 'Create a task for tomorrow')"${attr("disabled", isLoading, true)} class="flex-1 px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"/> <button type="submit"${attr("disabled", !inputMessage.trim(), true)} class="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2">`);
    Send($$renderer2, { class: "w-4 h-4" });
    $$renderer2.push(`<!----> <span class="hidden sm:inline">Send</span></button></form> <p class="text-xs text-muted-foreground mt-2">Try: "Create a high priority task for tomorrow" or "Analyze my productivity patterns"</p></div></div>`);
  });
}
export {
  _page as default
};

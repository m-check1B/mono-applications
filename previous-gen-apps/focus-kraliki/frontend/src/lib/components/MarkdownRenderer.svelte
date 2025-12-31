<script lang="ts">
	import { marked } from "marked";
	import { markedHighlight } from "marked-highlight";
	import hljs from "highlight.js/lib/core";
	import DOMPurify from "dompurify";
	import { logger } from "$lib/utils/logger";

	// Import commonly used languages
	import javascript from "highlight.js/lib/languages/javascript";
	import typescript from "highlight.js/lib/languages/typescript";
	import python from "highlight.js/lib/languages/python";
	import json from "highlight.js/lib/languages/json";
	import bash from "highlight.js/lib/languages/bash";
	import sql from "highlight.js/lib/languages/sql";
	import xml from "highlight.js/lib/languages/xml"; // for HTML
	import css from "highlight.js/lib/languages/css";

	// Register languages
	hljs.registerLanguage("javascript", javascript);
	hljs.registerLanguage("typescript", typescript);
	hljs.registerLanguage("python", python);
	hljs.registerLanguage("json", json);
	hljs.registerLanguage("bash", bash);
	hljs.registerLanguage("sql", sql);
	hljs.registerLanguage("html", xml);
	hljs.registerLanguage("xml", xml);
	hljs.registerLanguage("css", css);

	// Configure marked once at module level
	marked.use(
		markedHighlight({
			langPrefix: "hljs language-",
			highlight(code, lang) {
				const language = hljs.getLanguage(lang) ? lang : "plaintext";
				try {
					return hljs.highlight(code, { language }).value;
				} catch (e) {
					return code;
				}
			},
		}),
	);

	marked.setOptions({
		breaks: true,
		gfm: true,
	});

	interface Props {
		content: string;
		className?: string;
	}

	let { content, className = "" }: Props = $props();

	let renderedHtml = $state("");

	$effect(() => {
		try {
			// Parse markdown to HTML
			const rawHtml = marked.parse(content || "") as string;
			// Sanitize the resulting HTML to prevent XSS
			renderedHtml = DOMPurify.sanitize(rawHtml, {
				USE_PROFILES: { html: true },
				ADD_ATTR: ["target"], // Allow target="_blank" for links if needed
			});
		} catch (error) {
			logger.error("Markdown parsing error", error);
			// Fallback with sanitization
			renderedHtml = DOMPurify.sanitize(`<p>${content || ""}</p>`);
		}
	});
</script>

<!-- Import highlight.js theme -->
<svelte:head>
	<link
		rel="stylesheet"
		href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"
	/>
</svelte:head>

<div class="markdown-content {className}">
	{@html renderedHtml}
</div>

<style>
	:global(.markdown-content) {
		font-size: 0.875rem;
		line-height: 1.625;
		color: inherit;
		font-family: var(--font-mono);
	}

	:global(.markdown-content p) {
		margin-bottom: 0.75rem;
	}

	:global(.markdown-content h1) {
		font-size: 1.75rem;
		line-height: 1.1;
		font-family: var(--font-display);
		text-transform: uppercase;
		margin: 1.5rem 0 1rem;
		border-bottom: 4px solid currentColor;
		display: inline-block;
	}

	:global(.markdown-content h2) {
		font-size: 1.5rem;
		line-height: 1.2;
		font-family: var(--font-display);
		text-transform: uppercase;
		margin: 1.25rem 0 0.75rem;
		border-bottom: 2px solid currentColor;
		display: inline-block;
	}

	:global(.markdown-content h3) {
		font-size: 1.25rem;
		line-height: 1.2;
		font-family: var(--font-display);
		text-transform: uppercase;
		margin: 1rem 0 0.5rem;
	}

	:global(.markdown-content ul),
	:global(.markdown-content ol) {
		margin-bottom: 1rem;
		padding-left: 1.25rem;
	}

	:global(.markdown-content ul) {
		list-style: square;
	}

	:global(.markdown-content ol) {
		list-style: decimal;
	}

	:global(.markdown-content li) {
		margin-bottom: 0.25rem;
	}

	:global(.markdown-content code) {
		display: inline-block;
		background-color: var(--color-terminal-green);
		color: black;
		padding: 0.125rem 0.375rem;
		font-weight: 700;
		border: 1px solid black;
	}

	:global(.markdown-content pre) {
		margin: 1rem 0;
		border: 2px solid black;
		background-color: #0f172a;
		box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
		overflow-x: auto;
	}

	:global(.dark .markdown-content pre) {
		border-color: white;
		box-shadow: 4px 4px 0px 0px rgba(255, 255, 255, 1);
		background-color: #020617;
	}

	:global(.markdown-content pre code) {
		display: block;
		padding: 1.25rem;
		background: transparent;
		border: none;
		color: inherit;
	}

	:global(.markdown-content blockquote) {
		border-left: 8px solid var(--color-terminal-green);
		padding: 0.5rem 1rem;
		margin: 1rem 0;
		background: rgba(51, 255, 0, 0.05);
		font-weight: 600;
	}

	:global(.markdown-content a) {
		color: var(--color-terminal-green);
		text-decoration: none;
		border-bottom: 2px solid currentColor;
		font-weight: 800;
	}

	:global(.markdown-content a:hover) {
		background: var(--color-terminal-green);
		color: black;
	}

	:global(.markdown-content table) {
		width: 100%;
		border-collapse: collapse;
		margin: 1rem 0;
		border: 2px solid black;
	}

	:global(.dark .markdown-content table) {
		border-color: white;
	}

	:global(.markdown-content th) {
		border: 2px solid black;
		background-color: black;
		color: white;
		padding: 0.75rem;
		font-family: var(--font-display);
		text-transform: uppercase;
		text-align: left;
	}

	:global(.dark .markdown-content th) {
		border-color: white;
		background-color: white;
		color: black;
	}

	:global(.markdown-content td) {
		border: 2px solid black;
		padding: 0.75rem;
	}

	:global(.dark .markdown-content td) {
		border-color: white;
	}

	:global(.markdown-content hr) {
		border: none;
		border-top: 4px solid currentColor;
		margin: 2rem 0;
	}

	:global(.markdown-content img) {
		max-width: 100%;
		height: auto;
		border: 2px solid black;
		margin: 1rem 0;
		box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
	}

	:global(.dark .markdown-content img) {
		border-color: white;
		box-shadow: 4px 4px 0px 0px rgba(255, 255, 255, 1);
	}

	:global(.hljs) {
		background-color: transparent !important;
	}
</style>

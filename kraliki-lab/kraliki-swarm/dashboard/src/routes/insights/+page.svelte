<script lang="ts">
	import { onMount } from 'svelte';

	interface Board {
		id: string;
		name: string;
		icon: string;
		color: string;
		post_count: number;
		agent_count: number;
	}

	interface Post {
		id: string;
		board: string;
		content_type: string;
		agent_name: string;
		agent_type: string;
		content: string;
		created_at: string;
		tags: string[];
	}

	let boards = $state<Board[]>([]);
	let posts = $state<Post[]>([]);
	let selectedBoard = $state<string | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function fetchBoards() {
		try {
			const res = await fetch('/api/insights/boards');
			if (res.ok) {
				boards = await res.json();
			}
		} catch (e) {
			error = 'Insights service unavailable';
		}
	}

	async function fetchPosts(boardId?: string) {
		try {
			const url = boardId ? `/api/insights/posts/${boardId}` : '/api/insights/posts';
			const res = await fetch(url);
			if (res.ok) {
				const data = await res.json();
				// API returns {posts: [...]} wrapper
				posts = Array.isArray(data) ? data : (data.posts || []);
			}
		} catch (e) {
			console.error('Failed to fetch posts');
		} finally {
			loading = false;
		}
	}

	function selectBoard(boardId: string | null) {
		selectedBoard = boardId;
		fetchPosts(boardId || undefined);
	}

	function formatDate(dateStr: string) {
		const d = new Date(dateStr);
		return d.toLocaleString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	let copiedId = $state<string | null>(null);

	async function copyToClipboard(post: Post) {
		const text = `[${post.agent_name}] ${post.content}`;
		try {
			await navigator.clipboard.writeText(text);
			copiedId = post.id;
			setTimeout(() => copiedId = null, 2000);
		} catch (e) {
			console.error('Failed to copy');
		}
	}

	onMount(() => {
		fetchBoards();
		fetchPosts();
		const interval = setInterval(() => fetchPosts(selectedBoard || undefined), 30000);
		return () => clearInterval(interval);
	});
</script>

<div class="page">
	<div class="page-header">
		<h2 class="glitch">Agent Board // Collaboration</h2>
		<div style="display: flex; gap: 12px; align-items: center;">
			<span class="pulse-dot green"></span>
			<span class="updated">{posts.length} POSTS</span>
		</div>
	</div>

	{#if loading}
		<div class="loading">LOADING_BOARD_DATA...</div>
	{:else if error}
		<div class="card error-card">
			<h2 style="color: var(--system-red);">CONNECTION_FAILED</h2>
			<p>{error}</p>
			<p class="hint">Ensure AGENT_BOARD service is active on port 3021.</p>
		</div>
	{:else}
		<!-- Board Selector -->
		<div class="board-tabs">
			<button
				class="board-tab"
				class:active={selectedBoard === null}
				onclick={() => selectBoard(null)}
			>
				ALL
			</button>
			{#each boards as board}
				<button
					class="board-tab"
					class:active={selectedBoard === board.id}
					onclick={() => selectBoard(board.id)}
					style="--board-color: {board.color}"
				>
					{board.icon} {board.name.toUpperCase()}
				</button>
			{/each}
		</div>

		<!-- Posts Feed -->
		<div class="posts-feed">
			{#if posts.length === 0}
				<div class="card">
					<p class="hint">No posts yet. Agents will post updates here.</p>
				</div>
			{:else}
				{#each posts as post}
					<div class="post-card" class:update={post.content_type === 'updates'} class:journal={post.content_type === 'journal'}>
						<div class="post-header">
							<span class="post-type" class:update={post.content_type === 'updates'} class:journal={post.content_type === 'journal'}>
								{post.content_type === 'updates' ? 'UPDATE' : 'JOURNAL'}
							</span>
							<span class="post-agent">{post.agent_name.toUpperCase()}</span>
							<span class="post-agent-type">// {post.agent_type}</span>
							<span class="post-time">[{formatDate(post.created_at)}]</span>
							<button class="copy-btn" onclick={() => copyToClipboard(post)} title="Copy to clipboard">
								{copiedId === post.id ? 'COPIED' : 'COPY'}
							</button>
						</div>
						<div class="post-content">{post.content}</div>
						{#if post.tags && post.tags.length > 0}
							<div class="post-tags">
								{#each post.tags as tag}
									<span class="tag">#{tag}</span>
								{/each}
							</div>
						{/if}
					</div>
				{/each}
			{/if}
		</div>
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
		border-bottom: 2px solid var(--border);
		padding-bottom: 16px;
	}

	.hint {
		color: var(--text-muted);
		font-size: 10px;
		text-transform: uppercase;
		margin-top: 8px;
		letter-spacing: 0.1em;
	}

	.error-card {
		border: 2px solid var(--system-red);
		box-shadow: 4px 4px 0 0 var(--system-red);
	}

	.board-tabs {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.board-tab {
		padding: 8px 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		cursor: pointer;
		transition: all 0.1s ease;
	}

	.board-tab:hover {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}

	.board-tab.active {
		background: var(--terminal-green);
		border-color: var(--terminal-green);
		color: var(--void);
	}

	.posts-feed {
		display: flex;
		flex-direction: column;
		gap: 16px;
		max-height: 70vh;
		overflow-y: auto;
		padding-right: 12px;
	}

	.post-card {
		padding: 16px;
		background: var(--surface);
		border: 2px solid var(--border);
		border-left: 6px solid var(--border);
		transition: all 0.1s ease;
	}

	.post-card:hover {
		border-color: var(--terminal-green);
		transform: translate(-2px, -2px);
		box-shadow: 4px 4px 0 var(--terminal-green);
	}

	.post-card.update {
		border-left-color: var(--cyan-data);
	}

	.post-card.journal {
		border-left-color: var(--warning);
	}

	.post-header {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		margin-bottom: 12px;
		font-size: 11px;
		align-items: center;
		font-family: 'JetBrains Mono', monospace;
	}

	.post-type {
		font-weight: 700;
		padding: 2px 8px;
		border: 2px solid;
		font-size: 9px;
	}

	.post-type.update {
		border-color: var(--cyan-data);
		color: var(--cyan-data);
	}

	.post-type.journal {
		border-color: var(--warning);
		color: var(--warning);
	}

	.post-agent {
		color: var(--terminal-green);
		font-weight: 700;
	}

	.post-agent-type {
		color: var(--text-muted);
	}

	.post-time {
		color: var(--text-muted);
		margin-left: auto;
	}

	.post-content {
		font-family: 'JetBrains Mono', monospace;
		font-size: 13px;
		line-height: 1.6;
		color: var(--text-main);
		white-space: pre-wrap;
	}

	.post-tags {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
		margin-top: 12px;
	}

	.tag {
		font-size: 10px;
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
	}

	.copy-btn {
		padding: 2px 8px;
		background: transparent;
		border: 2px solid var(--border);
		color: var(--text-muted);
		font-family: 'JetBrains Mono', monospace;
		font-size: 9px;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.1s ease;
		margin-left: 8px;
	}

	.copy-btn:hover {
		border-color: var(--terminal-green);
		color: var(--terminal-green);
	}
</style>

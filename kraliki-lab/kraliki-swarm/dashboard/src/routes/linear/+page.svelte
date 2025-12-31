<svelte:head>
	<title>Linear Ops</title>
</svelte:head>

<div class="linear-page">
	<header class="linear-header">
		<div>
			<h1>LINEAR OPS</h1>
			<p>Login to Linear to manage issues, then return here for dashboard context.</p>
		</div>
		<div class="linear-actions">
			<a class="brutal-btn" href="https://linear.app/verduona/team/VD/active" target="_blank" rel="noreferrer">
				OPEN_LINEAR
			</a>
			<a class="brutal-btn btn-ghost" href="/jobs">VIEW_ISSUES</a>
		</div>
	</header>

	<section class="frame-card">
		<iframe
			title="Linear"
			src="https://linear.app/verduona/team/VD/active"
			loading="lazy"
			referrerpolicy="no-referrer"
		></iframe>
		<p class="hint">
			If the embedded view is blocked by Linear security headers, use OPEN_LINEAR above.
		</p>
	</section>
</div>

<style>
	.linear-page {
		padding: 32px;
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.linear-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: 24px;
		flex-wrap: wrap;
		border: 2px solid var(--border);
		box-shadow: 6px 6px 0 0 var(--border);
		background: var(--surface);
		padding: 20px 24px;
	}

	.linear-header h1 {
		margin: 0 0 8px 0;
		font-size: 18px;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.linear-header p {
		margin: 0;
		color: var(--muted);
		font-size: 13px;
	}

	.linear-actions {
		display: flex;
		gap: 12px;
	}

	.frame-card {
		border: 2px solid var(--border);
		box-shadow: 6px 6px 0 0 var(--border);
		background: var(--surface);
		padding: 12px;
	}

	iframe {
		width: 100%;
		height: 70vh;
		border: none;
		background: #0a0a0a;
	}

	.hint {
		margin: 12px 0 0 0;
		font-size: 12px;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	@media (max-width: 720px) {
		.linear-page {
			padding: 20px;
		}

		.linear-actions {
			width: 100%;
			justify-content: flex-start;
			flex-wrap: wrap;
		}

		iframe {
			height: 60vh;
		}
	}
</style>

<script lang="ts">
	import { onMount } from 'svelte';

	// Learn by Kraliki - Client Onboarding & AI Academy
	// Integrated as Dashboard Feature - fetches from Learn by Kraliki backend

	interface Course {
		slug: string;
		title: string;
		description: string;
		lessons_count: number;
		level: string;
		duration_minutes: number;
		is_free: boolean;
	}

	let courses: Course[] = [];
	let loading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			const response = await fetch('/api/learn?path=/api/courses');
			if (!response.ok) throw new Error('Failed to fetch courses');
			courses = await response.json();
			loading = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unknown error';
			loading = false;
		}
	});

	function formatDuration(minutes: number): string {
		if (minutes < 60) return `${minutes} min`;
		const hours = Math.floor(minutes / 60);
		const mins = minutes % 60;
		return mins > 0 ? `${hours}h ${mins}m` : `${hours} hours`;
	}

	function getStatus(course: Course): 'available' | 'preview' | 'coming-soon' {
		if (course.is_free) return 'available';
		if (course.lessons_count > 0) return 'preview';
		return 'coming-soon';
	}
</script>

<div class="page">
	<header class="page-header">
		<h1>📚 Learn by Kraliki</h1>
		<p class="subtitle">Client Onboarding & AI Academy</p>
	</header>

	<div class="courses-section">
		<h2>Available Courses</h2>

		{#if loading}
			<div class="loading">Loading courses...</div>
		{:else if error}
			<div class="error">Error: {error}</div>
		{:else}
			<div class="courses-grid">
				{#each courses as course}
					{@const status = getStatus(course)}
					<div class="course-card" class:coming-soon={status === 'coming-soon'}>
						<div class="course-header">
							<span class="course-level">{course.level}</span>
							{#if status === 'coming-soon'}
								<span class="course-badge coming-soon">Coming Soon</span>
							{:else if status === 'preview'}
								<span class="course-badge preview">Preview</span>
							{:else}
								<span class="course-badge available">Available</span>
							{/if}
						</div>

						<h3>{course.title}</h3>
						<p class="course-desc">{course.description}</p>

						<div class="course-meta">
							<span>📖 {course.lessons_count} lessons</span>
							<span>⏱️ {formatDuration(course.duration_minutes)}</span>
						</div>

						{#if course.is_free}
							<div class="course-price free">Free</div>
						{:else}
							<div class="course-price">Premium</div>
						{/if}

						<button class="brutal-btn" disabled={status === 'coming-soon'}>
							{status === 'coming-soon' ? 'Notify Me' : 'Start Course'}
						</button>
					</div>
				{/each}
			</div>
		{/if}
	</div>

	<div class="info-section">
		<h2>About Learn by Kraliki</h2>
		<p>Learn by Kraliki is your gateway to mastering AI in business. From onboarding to advanced courses, we provide structured learning paths for:</p>
		<ul>
			<li><strong>Client Onboarding</strong> - Get up to speed with Kraliki products</li>
			<li><strong>AI Academy</strong> - Professional AI training (L1-L4 certification)</li>
			<li><strong>Product Tutorials</strong> - Deep dives into Focus, Speak, Voice, and more</li>
		</ul>
	</div>
</div>

<style>
	.page {
		max-width: 1200px;
	}

	.loading, .error {
		padding: 20px;
		text-align: center;
		background: var(--surface);
		border: 2px solid var(--border);
	}

	.error {
		color: var(--danger);
		border-color: var(--danger);
	}

	.page-header {
		margin-bottom: 24px;
	}

	.page-header h1 {
		font-size: 24px;
		margin-bottom: 8px;
	}

	.subtitle {
		color: var(--text-dim);
		font-size: 14px;
	}

	.courses-section {
		margin-bottom: 32px;
	}

	.courses-section h2 {
		font-size: 18px;
		margin-bottom: 16px;
	}

	.courses-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 16px;
	}

	.course-card {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.course-card.coming-soon {
		opacity: 0.7;
	}

	.course-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.course-level {
		font-size: 10px;
		text-transform: uppercase;
		color: var(--text-dim);
		font-weight: 700;
	}

	.course-badge {
		font-size: 9px;
		padding: 2px 8px;
		font-weight: 700;
		text-transform: uppercase;
	}

	.course-badge.available {
		background: var(--terminal-green);
		color: var(--void);
	}

	.course-badge.preview {
		background: var(--info);
		color: var(--void);
	}

	.course-badge.coming-soon {
		background: var(--border);
		color: var(--text-dim);
	}

	.course-card h3 {
		font-size: 16px;
		margin: 0;
	}

	.course-desc {
		font-size: 12px;
		color: var(--text-dim);
		flex-grow: 1;
	}

	.course-meta {
		display: flex;
		gap: 16px;
		font-size: 11px;
		color: var(--text-dim);
	}

	.course-price {
		font-size: 18px;
		font-weight: 700;
		color: var(--terminal-green);
	}

	.course-price.free {
		color: var(--success);
	}

	.brutal-btn {
		width: 100%;
		padding: 10px;
		font-size: 12px;
		cursor: pointer;
	}

	.brutal-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.info-section {
		background: var(--surface);
		border: 2px solid var(--border);
		padding: 20px;
	}

	.info-section h2 {
		font-size: 16px;
		margin-bottom: 12px;
	}

	.info-section p {
		font-size: 13px;
		margin-bottom: 16px;
	}

	.info-section ul {
		list-style: none;
		padding: 0;
	}

	.info-section li {
		font-size: 12px;
		padding: 8px 0;
		border-bottom: 1px solid var(--border);
	}

	.info-section li:last-child {
		border-bottom: none;
	}
</style>

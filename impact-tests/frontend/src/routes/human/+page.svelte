<script lang="ts">
	import { submitHuman, type HumanRequest, type HumanResponse } from '$lib/api';

	let form: HumanRequest = {
		name: '',
		email: '',
		country: '',
		city: '',
		role: '',
		languages: '',
		interest_operations: false,
		interest_sales: false,
		interest_marketing: false,
		interest_tech: false,
		interest_other: false,
		consent_marketing: true,
		hq1: 3,
		hq2: 3,
		hq3: 3,
		hq4: 3,
		hq5: 3,
		hq6: 3,
		hq7: 3,
		hq8: 3,
		hq9: 3,
		hq10: 3
	};

	let result: HumanResponse | null = null;
	let loading = false;
	let error = '';

	const scaleOptions = [1, 2, 3, 4, 5];

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		error = '';
		result = null;

		try {
			result = await submitHuman(form);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to submit test';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Human AI Readiness Test • impact-tests</title>
</svelte:head>

<form on:submit|preventDefault={handleSubmit} class="space-y-8">
	<header class="space-y-2">
		<h1 class="text-2xl font-black uppercase tracking-tighter">Human AI Readiness Test</h1>
		<p class="text-muted-foreground text-sm">
			Rate each statement from <span class="font-bold">1 (not true at all)</span> to
			<span class="font-bold">5 (completely true)</span>.
		</p>
	</header>

	<section class="grid gap-4 md:grid-cols-2">
		<div>
			<label class="block text-sm font-medium mb-1">Name *</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.name}
				required
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Email *</label>
			<input
				type="email"
				class="w-full px-3 py-2 text-sm"
				bind:value={form.email}
				required
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Country</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.country}
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">City</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.city}
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Current role or “Student”</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.role}
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Languages (e.g. CZ, EN)</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.languages}
			/>
		</div>
	</section>

	<section class="space-y-3">
		<h2 class="text-lg font-bold uppercase">Interests</h2>
		<p class="text-xs text-muted-foreground">Which paths are you interested in?</p>
		<div class="flex flex-wrap gap-3 text-sm">
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.interest_operations} />
				Operations
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.interest_sales} />
				Sales
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.interest_marketing} />
				Marketing
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.interest_tech} />
				Tech/Dev
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.interest_other} />
				Other
			</label>
		</div>
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-bold uppercase">AI Usage Today</h2>
		{#each [
			[1, 'I use tools like ChatGPT, Claude, Perplexity, Gemini at least a few times per week.'],
			[2, 'I can usually get useful results from AI by adjusting my prompts.'],
			[3, 'I have used AI to speed up or improve my work/study tasks.']
		] as [idx, text]}
			<div class="space-y-1">
				<p class="text-sm">Q{idx}. {text}</p>
				<div class="flex gap-3 text-xs">
					{#each scaleOptions as val}
						<label class="inline-flex items-center gap-1">
							<input type="radio" name={`hq${idx}`} value={val} bind:group={form[`hq${idx}`]} />
							<span>{val}</span>
						</label>
					{/each}
				</div>
			</div>
		{/each}
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-bold uppercase">Tools &amp; Workflows</h2>
		{#each [
			[4, 'I feel comfortable learning and using new SaaS tools on my own.'],
			[5, 'I have built, or could build, simple automations (no-code tools, scripts, or integrations).'],
			[6, 'I can document a workflow so another person can follow it.'],
			[7, 'I can explain to someone non‑technical how a tool or process works.']
		] as [idx, text]}
			<div class="space-y-1">
				<p class="text-sm">Q{idx}. {text}</p>
				<div class="flex gap-3 text-xs">
					{#each scaleOptions as val}
						<label class="inline-flex items-center gap-1">
							<input type="radio" name={`hq${idx}`} value={val} bind:group={form[`hq${idx}`]} />
							<span>{val}</span>
						</label>
					{/each}
				</div>
			</div>
		{/each}
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-bold uppercase">Communication &amp; Sales Orientation</h2>
		{#each [
			[8, 'I feel comfortable communicating with customers or stakeholders via email or chat.'],
			[9, 'I am okay with hearing “no” and trying again in sales or outreach.'],
			[10, 'I enjoy understanding business problems and proposing solutions, not just doing tasks.']
		] as [idx, text]}
			<div class="space-y-1">
				<p class="text-sm">Q{idx}. {text}</p>
				<div class="flex gap-3 text-xs">
					{#each scaleOptions as val}
						<label class="inline-flex items-center gap-1">
							<input type="radio" name={`hq${idx}`} value={val} bind:group={form[`hq${idx}`]} />
							<span>{val}</span>
						</label>
					{/each}
				</div>
			</div>
		{/each}
	</section>

	<section class="space-y-3">
		<label class="inline-flex items-center gap-2 text-xs text-muted-foreground">
			<input type="checkbox" bind:checked={form.consent_marketing} required />
			I agree to be contacted about training, opportunities or roles based on my answers.
		</label>
	</section>

	<section class="space-y-3">
		{#if error}
			<p class="text-sm text-destructive">{error}</p>
		{/if}

		<button
			type="submit"
			class="brutal-btn disabled:opacity-50"
			disabled={loading}
		>
			{loading ? 'Calculating…' : 'See my readiness score'}
		</button>
	</section>
</form>

{#if result}
	<section class="mt-8 brutal-card p-5 space-y-3">
		<p class="text-sm">
			<strong>Score:</strong> {result.total_score} / 50
			{#if result.bucket === 'low'}
				<span class="badge ml-2 bg-destructive text-destructive-foreground">Low readiness</span>
			{:else if result.bucket === 'medium'}
				<span class="badge ml-2 bg-accent text-accent-foreground">Medium readiness</span>
			{:else}
				<span class="badge ml-2 bg-[#33FF00] text-black">High readiness</span>
			{/if}
		</p>

		<h2 class="text-lg font-bold uppercase">{result.title}</h2>
		<p class="text-sm">{result.recommendation}</p>

		{#if result.interests.length}
			<p class="text-xs text-muted-foreground">
				Your interests: <span class="font-bold">{result.interests.join(', ')}</span>
			</p>
		{/if}
	</section>
{/if}


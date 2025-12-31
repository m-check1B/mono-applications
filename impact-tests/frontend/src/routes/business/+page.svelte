<script lang="ts">
	import { submitBusiness, type BusinessRequest, type BusinessResponse } from '$lib/api';

	let form: BusinessRequest = {
		company_name: '',
		website: '',
		country: '',
		industry: '',
		employees: '',
		contact_name: '',
		contact_role: '',
		email: '',
		consent_marketing: true,
		priority_sales: false,
		priority_support: false,
		priority_operations: false,
		priority_finance: false,
		priority_hr: false,
		q1: 3,
		q2: 3,
		q3: 3,
		q4: 3,
		q5: 3,
		q6: 3,
		q7: 3,
		q8: 3,
		q9: 3,
		q10: 3,
		q11: 3,
		q12: 3
	};

	let result: BusinessResponse | null = null;
	let loading = false;
	let error = '';

	const scaleOptions = [1, 2, 3, 4, 5];

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		error = '';
		result = null;

		try {
			result = await submitBusiness(form);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to submit test';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Business AI Readiness Test • impact-tests</title>
</svelte:head>

<form on:submit|preventDefault={handleSubmit} class="space-y-8">
	<header class="space-y-2">
		<h1 class="text-2xl font-black uppercase tracking-tighter">Business AI Readiness Test</h1>
		<p class="text-muted-foreground text-sm">
			Rate each statement from <span class="font-bold">1 (not true at all)</span> to
			<span class="font-bold">5 (completely true)</span>.
		</p>
	</header>

	<section class="grid gap-4 md:grid-cols-2">
		<div>
			<label class="block text-sm font-medium mb-1">Company name *</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.company_name}
				required
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Website</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.website}
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
			<label class="block text-sm font-medium mb-1">Industry</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.industry}
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Number of employees</label>
			<select
				class="w-full px-3 py-2 text-sm"
				bind:value={form.employees}
			>
				<option value="">Select…</option>
				<option value="1-9">1–9</option>
				<option value="10-49">10–49</option>
				<option value="50-199">50–199</option>
				<option value="200-499">200–499</option>
				<option value="500+">500+</option>
			</select>
		</div>
	</section>

	<section class="grid gap-4 md:grid-cols-2">
		<div>
			<label class="block text-sm font-medium mb-1">Contact name *</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.contact_name}
				required
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Role</label>
			<input
				class="w-full px-3 py-2 text-sm"
				bind:value={form.contact_role}
			/>
		</div>
		<div>
			<label class="block text-sm font-medium mb-1">Work email *</label>
			<input
				type="email"
				class="w-full px-3 py-2 text-sm"
				bind:value={form.email}
				required
			/>
		</div>
	</section>

	<section class="space-y-3">
		<h2 class="text-lg font-bold uppercase">Priorities</h2>
		<p class="text-xs text-muted-foreground">Where do you feel the biggest pressure today?</p>
		<div class="flex flex-wrap gap-3 text-sm">
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.priority_sales} />
				Sales
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.priority_support} />
				Support
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.priority_operations} />
				Operations
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.priority_finance} />
				Finance
			</label>
			<label class="inline-flex items-center gap-2">
				<input type="checkbox" bind:checked={form.priority_hr} />
				HR
			</label>
		</div>
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-bold uppercase">Processes &amp; Data</h2>
		{#each [
			[1, 'Our core processes (sales, support, operations, finance) are clearly documented and followed.'],
			[2, 'Most of our core processes already run through digital tools (CRM, ERP, ticketing, spreadsheets, etc.).'],
			[3, 'We have central, reasonably clean data about customers, deals and operations.'],
			[4, 'We can export or access our data from current systems without major obstacles.']
		] as [idx, text]}
			<div class="space-y-1">
				<p class="text-sm">Q{idx}. {text}</p>
				<div class="flex gap-3 text-xs">
					{#each scaleOptions as val}
						<label class="inline-flex items-center gap-1">
							<input type="radio" name={`q${idx}`} value={val} bind:group={form[`q${idx}`]} />
							<span>{val}</span>
						</label>
					{/each}
				</div>
			</div>
		{/each}
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-bold uppercase">People &amp; Tools</h2>
		{#each [
			[5, 'People in our company use tools like ChatGPT/Claude/Perplexity at least weekly for their work.'],
			[6, 'At least one team has already built internal “AI workflows” (prompts, templates, automations).'],
			[7, 'We have someone internally who acts as an “AI champion” or go‑to person for AI questions.'],
			[8, 'Our team is generally positive and curious about using AI at work.']
		] as [idx, text]}
			<div class="space-y-1">
				<p class="text-sm">Q{idx}. {text}</p>
				<div class="flex gap-3 text-xs">
					{#each scaleOptions as val}
						<label class="inline-flex items-center gap-1">
							<input type="radio" name={`q${idx}`} value={val} bind:group={form[`q${idx}`]} />
							<span>{val}</span>
						</label>
					{/each}
				</div>
			</div>
		{/each}
	</section>

	<section class="space-y-4">
		<h2 class="text-lg font-bold uppercase">Leadership, Budget &amp; Risk</h2>
		{#each [
			[9, 'Leadership sees AI as strategically important for the company.'],
			[10, 'There is at least a small budget allocated for AI/automation experiments in the next 12 months.'],
			[11, 'We have basic rules/policies for safe and compliant use of AI tools (even if simple).'],
			[12, 'We are willing to change processes, not just add tools, if the ROI is clear.']
		] as [idx, text]}
			<div class="space-y-1">
				<p class="text-sm">Q{idx}. {text}</p>
				<div class="flex gap-3 text-xs">
					{#each scaleOptions as val}
						<label class="inline-flex items-center gap-1">
							<input type="radio" name={`q${idx}`} value={val} bind:group={form[`q${idx}`]} />
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
			I agree to be contacted about my results and related AI offers.
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
			<strong>Score:</strong> {result.total_score} / 60
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

		{#if result.priorities.length}
			<p class="text-xs text-muted-foreground">
				Your pressure points: <span class="font-bold">{result.priorities.join(', ')}</span>
			</p>
		{/if}
	</section>
{/if}


<script lang="ts">
	import { createQuery } from '@tanstack/svelte-query';
	import { Building2, UploadCloud, CheckCircle } from 'lucide-svelte';
	import { fetchCompanies, importCompaniesCSV, type CompanySummary } from '$lib/services/calls';
	import { queryClient } from '$lib/stores';

	const companiesQuery = createQuery<CompanySummary[]>({
		queryKey: ['companies'],
		queryFn: fetchCompanies,
		staleTime: 30_000
	});

	let companies = $state<CompanySummary[]>([]);
	let isLoading = $state(false);
	let errorMessage = $state<string | null>(null);
	let importSuccess = $state<string | null>(null);
	let fileInput: HTMLInputElement;

	const unsubscribe = companiesQuery.subscribe((result) => {
		companies = result.data ?? [];
		isLoading = result.isPending;
		errorMessage = result.isError ? (result.error?.message ?? 'Failed to load companies.') : null;
	});

	$effect(() => () => {
		unsubscribe();
	});

	async function handleCSVImport() {
		fileInput.click();
	}

	async function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (!file) return;

		if (!file.name.endsWith('.csv')) {
			errorMessage = 'Please select a CSV file';
			return;
		}

		isLoading = true;
		errorMessage = null;
		importSuccess = null;

		try {
			const text = await file.text();
			const result = await importCompaniesCSV(text);

			if (result.success) {
				importSuccess = `Successfully imported ${result.count} companies`;
				await queryClient.invalidateQueries({ queryKey: ['companies'] });
			} else {
				errorMessage = result.error || 'Failed to import CSV';
			}
		} catch (error) {
			errorMessage = 'Failed to import CSV file';
		} finally {
			isLoading = false;
			// Reset file input
			target.value = '';
		}
	}
</script>

<section class="space-y-6">
	<header class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
		<div class="space-y-1">
			<h1 class="text-2xl font-semibold text-text-primary">Target Companies</h1>
			<p class="text-sm text-text-muted">
				Centralize lead lists, sync CRM exports, and monitor outbound status in one responsive surface.
			</p>
		</div>
		<button class="btn btn-primary" onclick={handleCSVImport} disabled={isLoading}>
			<UploadCloud class="size-4" /> Import CSV
		</button>
		<input
			bind:this={fileInput}
			type="file"
			accept=".csv"
			onchange={handleFileSelect}
			class="hidden"
		/>
	</header>

	{#if importSuccess}
		<div class="rounded-lg border border-green-500/40 bg-green-500/10 px-3 py-2 text-sm text-green-600 dark:text-green-400 flex items-center gap-2">
			<CheckCircle class="size-4" />
			{importSuccess}
		</div>
	{/if}

	{#if errorMessage}
		<div class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">
			{errorMessage}
			<button
				class="ml-2 text-primary underline"
				type="button"
				onclick={() => {
					void queryClient.invalidateQueries({ queryKey: ['companies'] });
				}}
			>
				Retry
			</button>
		</div>
	{/if}

	{#if isLoading && !companies.length}
		<p class="text-xs text-text-muted">Loading companies…</p>
	{:else if companies.length === 0}
		<p class="text-sm text-text-secondary">No companies found.</p>
	{:else}
		<div class="grid gap-3">
			{#each companies as company}
				<article class="card flex items-center justify-between bg-secondary/80">
					<div class="flex items-center gap-3 text-text-primary">
						<Building2 class="size-5" />
						<div>
							<p class="text-sm font-semibold">{company.name}</p>
							<p class="text-xs text-text-muted">{company.phone}</p>
						</div>
					</div>
					<span class="text-xs text-text-muted uppercase tracking-wide">{company.status ?? 'Pending'}</span>
				</article>
			{/each}
		</div>
	{/if}
</section>

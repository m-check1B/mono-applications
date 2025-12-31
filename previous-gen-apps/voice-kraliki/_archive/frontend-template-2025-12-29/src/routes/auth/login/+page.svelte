<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores';
	import { t } from '$lib/i18n';

	let email = $state('');
	let password = $state('');
	let isSubmitting = $state(false);
	let errorMessage = $state('');

	onMount(() => {
		const snapshot = authStore.getSnapshot();
		if (snapshot.status === 'authenticated') {
			goto('/dashboard', { replaceState: true });
		}
	});

	async function handleSubmit(event: Event) {
		event.preventDefault();
		errorMessage = '';
		if (!email || !password) {
			errorMessage = $t('auth.error_missing_credentials');
			return;
		}

		isSubmitting = true;
		const result = await authStore.login({ email, password });
		isSubmitting = false;

		if (result.success) {
			goto('/dashboard', { replaceState: true });
			return;
		}

		errorMessage = result.error ?? $t('auth.error_sign_in_failed');
	}
</script>

<section class="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-6 px-4 py-12 text-text-primary">
	<div class="space-y-2 text-center">
		<h1 class="text-2xl font-semibold">{$t('auth.sign_in_title')}</h1>
		<p class="text-sm text-text-muted">{$t('auth.sign_in_subtitle')}</p>
	</div>

	<form class="space-y-4" onsubmit={handleSubmit}>
		<div class="field">
			<label for="email" class="field-label">{$t('auth.work_email_label')}</label>
			<input
				id="email"
				type="email"
				class="input-field"
				autocomplete="email"
				value={email}
				oninput={(event) => (email = (event.currentTarget as HTMLInputElement).value)}
				placeholder="you@example.com"
			/>
		</div>

		<div class="field">
			<label for="password" class="field-label">{$t('auth.password_label')}</label>
			<input
				id="password"
				type="password"
				class="input-field"
				autocomplete="current-password"
				value={password}
				oninput={(event) => (password = (event.currentTarget as HTMLInputElement).value)}
				placeholder="••••••••"
			/>
		</div>

		{#if errorMessage}
			<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">{errorMessage}</p>
		{/if}

		<button class="btn btn-primary w-full" type="submit" disabled={isSubmitting}>
			{#if isSubmitting}
				<span class="size-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
				<span>{$t('auth.sign_in_loading')}</span>
			{:else}
				<span>{$t('common.sign_in')}</span>
			{/if}
		</button>
	</form>

	<div class="relative">
		<div class="absolute inset-0 flex items-center">
			<div class="w-full border-t border-text-muted/30"></div>
		</div>
	<div class="relative flex justify-center text-xs">
			<span class="bg-background px-2 text-text-muted">{$t('auth.continue_with')}</span>
	</div>
	</div>

	<a
		href="/auth/sso"
		class="btn w-full border border-primary bg-primary/10 hover:bg-primary hover:text-white flex items-center justify-center gap-2"
	>
		<svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<path d="M12 2L2 7l10 5 10-5-10-5z"/>
			<path d="M2 17l10 5 10-5"/>
			<path d="M2 12l10 5 10-5"/>
		</svg>
		{$t('auth.sso_button')}
	</a>

	<p class="text-center text-sm text-text-muted">
		{$t('auth.need_account')}
		<a class="text-primary hover:underline" href="/auth/register">{$t('auth.create_account')}</a>
	</p>
</section>

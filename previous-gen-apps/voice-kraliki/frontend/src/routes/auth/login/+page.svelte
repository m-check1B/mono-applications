<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores';

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
			errorMessage = 'Email and password are required.';
			return;
		}

		isSubmitting = true;
		const result = await authStore.login({ email, password });
		isSubmitting = false;

		if (result.success) {
			goto('/dashboard', { replaceState: true });
			return;
		}

		errorMessage = result.error ?? 'Unable to sign in.';
	}
</script>

<section class="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-6 px-4 py-12 text-text-primary">
	<div class="space-y-2 text-center">
		<h1 class="text-2xl font-semibold">Sign in to Operator Console</h1>
		<p class="text-sm text-text-muted">Access the outbound and inbound call management tools.</p>
	</div>

	<form class="space-y-4" onsubmit={handleSubmit}>
		<div class="field">
			<label for="email" class="field-label">Work Email</label>
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
			<label for="password" class="field-label">Password</label>
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
				<span>Signing in...</span>
			{:else}
				<span>Sign in</span>
			{/if}
		</button>
	</form>

	<div class="relative">
		<div class="absolute inset-0 flex items-center">
			<div class="w-full border-t border-text-muted/30"></div>
		</div>
		<div class="relative flex justify-center text-xs">
			<span class="bg-background px-2 text-text-muted">Or continue with</span>
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
		Sign in with Kraliki SSO
	</a>

	<p class="text-center text-sm text-text-muted">
		Need an account? <a class="text-primary hover:underline" href="/auth/register">Create one</a>
	</p>
</section>

<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let fullName = $state('');
	let isLoading = $state(false);
	let error = $state('');

	async function handleRegister() {
		// Validation
		if (!email || !password || !fullName) {
			error = 'Please fill in all fields';
			return;
		}

		if (password.length < 8) {
			error = 'Password must be at least 8 characters';
			return;
		}

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		isLoading = true;
		error = '';

		const result = await authStore.register(email, password, fullName);

		if (result.success) {
			goto('/dashboard');
		} else {
			error = result.error || 'Registration failed';
			isLoading = false;
		}
	}

	function goToLogin() {
		goto('/login');
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		handleRegister();
	}
</script>

<div class="flex items-center justify-center min-h-screen bg-background">
	<div class="w-full max-w-md p-8 space-y-6 brutal-card">
		<div class="space-y-2 text-center">
			<h1 class="text-3xl font-black uppercase tracking-tighter">Create Account</h1>
			<p class="text-sm text-muted-foreground font-mono">Get started with Focus by Kraliki</p>
		</div>

		<form onsubmit={handleSubmit} class="space-y-4">
			{#if error}
				<div class="p-3 text-sm font-bold bg-destructive text-destructive-foreground brutal-border uppercase shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]">
					{error}
				</div>
			{/if}

			<div class="space-y-2">
				<label for="fullName" class="text-xs font-black uppercase tracking-wide">Full Name</label>
				<input
					id="fullName"
					type="text"
					bind:value={fullName}
					placeholder="John Doe"
					disabled={isLoading}
					class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]"
					required
				/>
			</div>

			<div class="space-y-2">
				<label for="email" class="text-xs font-black uppercase tracking-wide">Email</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					placeholder="you@example.com"
					disabled={isLoading}
					class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]"
					required
				/>
			</div>

			<div class="space-y-2">
				<label for="password" class="text-xs font-black uppercase tracking-wide">Password</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					placeholder="********"
					disabled={isLoading}
					class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]"
					required
					minlength="8"
				/>
				<p class="text-xs text-muted-foreground font-mono uppercase font-bold">At least 8 characters</p>
			</div>

			<div class="space-y-2">
				<label for="confirmPassword" class="text-xs font-black uppercase tracking-wide">Confirm Password</label>
				<input
					id="confirmPassword"
					type="password"
					bind:value={confirmPassword}
					placeholder="********"
					disabled={isLoading}
					class="w-full px-3 py-2 bg-background brutal-border font-mono focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:focus:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]"
					required
				/>
			</div>

			<button
				type="submit"
				disabled={isLoading}
				class="brutal-btn w-full disabled:opacity-50 disabled:cursor-not-allowed"
			>
				{isLoading ? 'CREATING ACCOUNT...' : 'CREATE ACCOUNT'}
			</button>
		</form>

		<div class="text-center text-sm font-mono">
			<span class="text-muted-foreground">Already have an account? </span>
			<button
				onclick={goToLogin}
				type="button"
				class="text-primary hover:underline font-bold uppercase"
			>
				Sign in
			</button>
		</div>
	</div>
</div>

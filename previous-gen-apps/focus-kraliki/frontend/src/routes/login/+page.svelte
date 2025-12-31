<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { Button } from 'bits-ui';

	let email = $state('');
	let password = $state('');
	let isLoading = $state(false);
	let error = $state('');

	async function handleLogin() {
		if (!email || !password) {
			error = 'Please enter email and password';
			return;
		}

		isLoading = true;
		error = '';

		const result = await authStore.login(email, password);

		if (result.success) {
			goto('/dashboard');
		} else {
			error = result.error || 'Login failed';
			isLoading = false;
		}
	}

	async function handleGoogleLogin() {
		isLoading = true;
		error = '';

		try {
			// Generate random state for CSRF protection
			const state = crypto.randomUUID();

			// Call backend to get Google OAuth URL and CSRF token
			const response: any = await authStore.getGoogleAuthUrl(state);

			// Open popup window for OAuth flow
			const popup = window.open(
				response.url,
				'Google Sign In',
				'width=500,height=600,left=200,top=100'
			);

			if (!popup) {
				error = 'Please allow popups for Google Sign In';
				isLoading = false;
				return;
			}

			// Listen for OAuth callback
			const handleMessage = async (event: MessageEvent) => {
				if (event.origin !== window.location.origin) return;

				if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
					window.removeEventListener('message', handleMessage);
					popup.close();

					// Exchange code for tokens via backend
					const loginResult = await authStore.loginWithGoogle(
						event.data.code,
						event.data.redirectUri
					);

					if (loginResult.success) {
						goto('/dashboard');
					} else {
						error = loginResult.error || 'Google login failed';
						isLoading = false;
					}
				} else if (event.data.type === 'GOOGLE_AUTH_ERROR') {
					window.removeEventListener('message', handleMessage);
					popup.close();
					error = event.data.error || 'Google login failed';
					isLoading = false;
				}
			};

			window.addEventListener('message', handleMessage);

			// Check if popup was closed without completing auth
			const checkPopup = setInterval(() => {
				if (popup.closed) {
					clearInterval(checkPopup);
					window.removeEventListener('message', handleMessage);
					if (error === '') {
						error = 'Google login cancelled';
					}
					isLoading = false;
				}
			}, 500);
		} catch (err: any) {
			error = err.detail || 'Failed to initiate Google login';
			isLoading = false;
		}
	}

	function goToRegister() {
		goto('/register');
	}

	function handleSubmit(event: Event) {
		event.preventDefault();
		handleLogin();
	}
</script>

<div class="flex items-center justify-center min-h-screen bg-background">
	<div class="w-full max-w-md p-8 space-y-6 brutal-card">
		<div class="space-y-2 text-center">
			<h1 class="text-3xl font-black uppercase tracking-tighter">Focus <span class="text-muted-foreground text-lg font-normal">by Kraliki</span></h1>
			<p class="text-sm text-muted-foreground font-mono">Sign in to your account</p>
		</div>

		<form onsubmit={handleSubmit} class="space-y-4">
			{#if error}
				<div class="p-3 text-sm font-bold bg-destructive text-destructive-foreground brutal-border uppercase shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]">
					{error}
				</div>
			{/if}

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
				/>
			</div>

			<button
				type="submit"
				disabled={isLoading}
				class="brutal-btn w-full disabled:opacity-50 disabled:cursor-not-allowed"
			>
				{isLoading ? 'SIGNING IN...' : 'SIGN IN'}
			</button>
		</form>

		<div class="relative">
			<div class="absolute inset-0 flex items-center">
				<div class="w-full brutal-border border-t-2"></div>
			</div>
			<div class="relative flex justify-center text-xs font-black uppercase">
				<span class="px-2 bg-card text-muted-foreground">Or continue with</span>
			</div>
		</div>

		<div class="flex flex-col gap-2">
			<button
				onclick={handleGoogleLogin}
				type="button"
				class="w-full px-4 py-2 text-sm font-bold uppercase brutal-border hover:bg-accent hover:text-accent-foreground flex items-center justify-center gap-2"
			>
				<svg class="w-5 h-5 mr-2 inline" viewBox="0 0 24 24">
					<path
						fill="currentColor"
						d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
					/>
					<path
						fill="currentColor"
						d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
					/>
					<path
						fill="currentColor"
						d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
					/>
					<path
						fill="currentColor"
						d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
					/>
				</svg>
				Continue with Google
			</button>

			<a
				href="/auth/sso"
				class="w-full px-4 py-2 text-sm font-bold uppercase brutal-border hover:bg-primary hover:text-primary-foreground flex items-center justify-center gap-2 bg-primary/10"
			>
				<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M12 2L2 7l10 5 10-5-10-5z"/>
					<path d="M2 17l10 5 10-5"/>
					<path d="M2 12l10 5 10-5"/>
				</svg>
				Sign in with Kraliki SSO
			</a>
		</div>

		<div class="text-center text-sm font-mono">
			<span class="text-muted-foreground">Don't have an account? </span>
			<button
				onclick={goToRegister}
				type="button"
				class="text-primary hover:underline font-bold uppercase"
			>
				Sign up
			</button>
		</div>
	</div>
</div>

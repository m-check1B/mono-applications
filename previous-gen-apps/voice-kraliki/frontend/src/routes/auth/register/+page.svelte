<script lang="ts">
        import { goto } from '$app/navigation';
        import { onMount } from 'svelte';
        import { authStore } from '$lib/stores';

        let name = $state('');
        let email = $state('');
        let password = $state('');
        let confirmPassword = $state('');
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
                if (password !== confirmPassword) {
                        errorMessage = 'Passwords do not match.';
                        return;
                }

                isSubmitting = true;
                const result = await authStore.register({ email, password, full_name: name });
                isSubmitting = false;

                if (result.success) {
                        goto('/dashboard', { replaceState: true });
                        return;
                }

                errorMessage = result.error ?? 'Unable to register.';
        }
</script>

<section class="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-6 px-4 py-12 text-text-primary">
        <div class="space-y-2 text-center">
                <h1 class="text-2xl font-semibold">Create your operator account</h1>
                <p class="text-sm text-text-muted">Provision a new user to access the call console.</p>
        </div>

        <form class="space-y-4" onsubmit={handleSubmit}>
                <div class="field">
                        <label for="name" class="field-label">Full Name</label>
                        <input
                                id="name"
                                type="text"
                                class="input-field"
                                autocomplete="name"
                                value={name}
                                oninput={(event) => (name = (event.currentTarget as HTMLInputElement).value)}
                                placeholder="Alex Operator"
                        />
                </div>

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
                                autocomplete="new-password"
                                value={password}
                                oninput={(event) => (password = (event.currentTarget as HTMLInputElement).value)}
                                placeholder="••••••••"
                        />
                </div>

                <div class="field">
                        <label for="confirm-password" class="field-label">Confirm Password</label>
                        <input
                                id="confirm-password"
                                type="password"
                                class="input-field"
                                autocomplete="new-password"
                                value={confirmPassword}
                                oninput={(event) => (confirmPassword = (event.currentTarget as HTMLInputElement).value)}
                                placeholder="••••••••"
                        />
                </div>

                {#if errorMessage}
                        <p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">{errorMessage}</p>
                {/if}

                <button class="btn btn-primary w-full" type="submit" disabled={isSubmitting}>
                        {#if isSubmitting}
                                <span class="size-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                                <span>Creating account...</span>
                        {:else}
                                <span>Sign up</span>
                        {/if}
                </button>
        </form>

        <p class="text-center text-sm text-text-muted">
                Already registered? <a class="text-primary hover:underline" href="/auth/login">Sign in</a>
        </p>
</section>

<script lang="ts">
	import type { ActionData, PageData } from './$types';

	export let form: ActionData;
	export let data: PageData;
</script>

<div class="login-container">
	<div class="login-box">
		<h1>KRALIKI // LOGIN</h1>
		<p class="subtitle">Unified Intelligence Control Center</p>

		{#if form?.error}
			<div class="error">{form.error}</div>
		{/if}

		<form method="POST">
			<div class="field">
				<label for="email">Email</label>
				<input type="email" name="email" id="email" required placeholder="your@email.com" />
			</div>

			<div class="field">
				<label for="password">Password</label>
				<input type="password" name="password" id="password" required placeholder="********" />
			</div>

			<button type="submit">ACCESS SYSTEM</button>
		</form>

		{#if !data.localAuthConfigured}
			<div class="notice">No local users yet. Create an account below.</div>
		{/if}

		{#if data.authConfigured && !data.ssoDisabled}
			<a class="sso-button" href="/auth/sso">SIGN IN WITH KRALIKI SSO</a>
		{/if}

		{#if !data.localAuthConfigured && !data.authConfigured && !data.ssoDisabled}
			<div class="error">SSO is not configured yet. Use local registration to get access.</div>
		{/if}

		<div class="footer-links">
			<a href="/auth/register">CREATE_ACCOUNT</a>
			<span class="divider">|</span>
			<a href="/">CONTINUE_AS_LOCAL</a>
		</div>
	</div>
</div>

<style>
	.login-container {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #0a0a0a;
		font-family: 'JetBrains Mono', monospace;
	}

	.login-box {
		background: #111;
		border: 1px solid #39ff14;
		padding: 3rem;
		width: 100%;
		max-width: 400px;
	}

	h1 {
		color: #39ff14;
		font-size: 1.5rem;
		margin: 0 0 0.5rem 0;
		text-transform: uppercase;
	}

	.subtitle {
		color: #666;
		font-size: 0.75rem;
		margin: 0 0 2rem 0;
		text-transform: uppercase;
	}

	.error {
		background: rgba(255, 0, 0, 0.1);
		border: 1px solid #ff3333;
		color: #ff3333;
		padding: 0.75rem;
		margin-bottom: 1rem;
		font-size: 0.875rem;
	}

	.notice {
		margin-top: 1rem;
		padding: 0.75rem;
		border: 1px solid #333;
		color: #999;
		font-size: 0.8rem;
		text-transform: uppercase;
	}

	.field {
		margin-bottom: 1.5rem;
	}

	label {
		display: block;
		color: #39ff14;
		font-size: 0.75rem;
		text-transform: uppercase;
		margin-bottom: 0.5rem;
	}

	input {
		width: 100%;
		padding: 0.75rem;
		background: #0a0a0a;
		border: 1px solid #333;
		color: #fff;
		font-family: inherit;
		font-size: 1rem;
		box-sizing: border-box;
	}

	input:focus {
		outline: none;
		border-color: #39ff14;
	}

	button {
		width: 100%;
		padding: 1rem;
		background: #39ff14;
		border: none;
		color: #000;
		font-family: inherit;
		font-size: 0.875rem;
		font-weight: bold;
		text-transform: uppercase;
		cursor: pointer;
		transition: background 0.2s;
	}

	button:hover {
		background: #2ecc0f;
	}

	.sso-button {
		display: block;
		width: 100%;
		padding: 1rem;
		margin-top: 1rem;
		border: 1px solid #39ff14;
		color: #39ff14;
		text-align: center;
		text-transform: uppercase;
		font-weight: bold;
		text-decoration: none;
		transition: background 0.2s, color 0.2s;
	}

	.sso-button:hover {
		background: #39ff14;
		color: #000;
	}

	.footer-links {
		margin-top: 1.5rem;
		text-align: center;
		font-size: 0.75rem;
	}

	.footer-links a {
		color: #39ff14;
		text-decoration: none;
		text-transform: uppercase;
	}

	.footer-links a:hover {
		text-decoration: underline;
	}

	.divider {
		color: #333;
		margin: 0 0.5rem;
	}
</style>

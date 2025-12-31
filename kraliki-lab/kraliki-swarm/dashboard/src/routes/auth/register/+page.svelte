<script lang="ts">
	import type { ActionData } from './$types';

	export let form: ActionData;
</script>

<div class="register-container">
	<div class="register-box">
		<h1>KRALIKI // CREATE ACCOUNT</h1>
		<p class="subtitle">AI Swarm Command Center</p>

		{#if form?.error}
			<div class="error">{form.error}</div>
		{/if}

		<form method="POST">
			<div class="field">
				<label for="name">Name</label>
				<input
					type="text"
					name="name"
					id="name"
					required
					placeholder="Your Name"
					value={form?.name ?? ''}
				/>
			</div>

			<div class="field">
				<label for="email">Email</label>
				<input
					type="email"
					name="email"
					id="email"
					required
					placeholder="your@email.com"
					value={form?.email ?? ''}
				/>
			</div>

			<div class="field">
				<label for="password">Password</label>
				<input
					type="password"
					name="password"
					id="password"
					required
					placeholder="********"
				/>
			</div>

			<div class="field">
				<label for="confirmPassword">Confirm Password</label>
				<input
					type="password"
					name="confirmPassword"
					id="confirmPassword"
					required
					placeholder="********"
				/>
			</div>

			<div class="field">
				<label for="registrationPin">Registration PIN</label>
				<input
					type="password"
					name="registrationPin"
					id="registrationPin"
					required
					placeholder="Enter PIN"
					value={form?.registrationPin ?? ''}
				/>
			</div>

			<button type="submit">CREATE_ACCOUNT</button>
		</form>

		<div class="footer-links">
			<a href="/auth/login">BACK_TO_LOGIN</a>
			<span class="divider">|</span>
			<a href="/">CONTINUE_AS_LOCAL</a>
		</div>
	</div>
</div>

<style>
	.register-container {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #0a0a0a;
		font-family: 'JetBrains Mono', monospace;
	}

	.register-box {
		background: #111;
		border: 1px solid #39ff14;
		padding: 3rem;
		width: 100%;
		max-width: 450px;
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

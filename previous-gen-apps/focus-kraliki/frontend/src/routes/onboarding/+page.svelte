<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { authStore } from '$lib/stores/auth';
	import { logger } from '$lib/utils/logger';
	import { Code, Briefcase, Compass, Check, Shield, Settings, Sparkles, AlertCircle, CalendarCheck } from 'lucide-svelte';

	let currentStep = $state(0);
	let selectedPersona: string | null = $state(null);
	let personas: any[] = $state([]);
	let loading = $state(false);
	let error: string | null = $state(null);

	// Privacy preferences
	let privacyPreferences = $state({
		geminiFileSearchEnabled: true,
		iiAgentEnabled: true,
		dataPrivacyAcknowledged: false
	});

	// Feature toggles
	let featureToggles = $state({
		geminiFileSearch: true,
		iiAgent: true,
		voiceTranscription: true
	});

	const personaIcons: Record<string, any> = {
		'solo-developer': Code,
		'freelancer': Briefcase,
		'explorer': Compass,
		'operations-lead': CalendarCheck
	};

	onMount(async () => {
		await loadOnboardingStatus();
		await loadPersonas();
	});

	async function loadOnboardingStatus() {
		try {
			const status: any = await api.onboarding.getStatus();
			if (status.completed) {
				// Already onboarded, redirect to dashboard
				goto('/dashboard');
			} else {
				currentStep = status.currentStep || 0;
				selectedPersona = status.selectedPersona;
				if (status.featureToggles) {
					featureToggles = status.featureToggles;
				}
			}
		} catch (err: any) {
			logger.error('Failed to load onboarding status', err);
		}
	}

	async function loadPersonas() {
		try {
			const data: any = await api.onboarding.listPersonas();
			personas = data.personas || [];
		} catch (err: any) {
			error = 'Failed to load personas. Please refresh the page.';
			logger.error('Failed to load personas', err);
		}
	}

	async function selectPersona(personaId: string) {
		loading = true;
		error = null;
		try {
			await api.onboarding.selectPersona({ personaId });
			selectedPersona = personaId;
			currentStep = 1;
		} catch (err: any) {
			error = err.detail || 'Failed to select persona';
		} finally {
			loading = false;
		}
	}

	async function savePrivacyPreferences() {
		if (!privacyPreferences.dataPrivacyAcknowledged) {
			error = 'Please acknowledge the privacy policy to continue';
			return;
		}

		loading = true;
		error = null;
		try {
			await api.onboarding.updatePrivacyPreferences(privacyPreferences);
			currentStep = 2;
		} catch (err: any) {
			error = err.detail || 'Failed to save privacy preferences';
		} finally {
			loading = false;
		}
	}

	async function saveFeatureToggles() {
		loading = true;
		error = null;
		try {
			await api.onboarding.updateFeatureToggles(featureToggles);
			currentStep = 3;
		} catch (err: any) {
			error = err.detail || 'Failed to save feature toggles';
		} finally {
			loading = false;
		}
	}

	async function completeOnboarding() {
		loading = true;
		error = null;
		try {
			await api.onboarding.complete({});
			goto('/dashboard');
		} catch (err: any) {
			error = err.detail || 'Failed to complete onboarding';
		} finally {
			loading = false;
		}
	}

	async function skipOnboarding() {
		if (!confirm('Are you sure you want to skip onboarding? You can customize settings later.')) {
			return;
		}

		loading = true;
		try {
			await api.onboarding.skip();
			goto('/dashboard');
		} catch (err: any) {
			error = err.detail || 'Failed to skip onboarding';
		} finally {
			loading = false;
		}
	}

	function getPersonaDescription(persona: any): string {
		return persona.description || '';
	}

	function getPersonaFeatureList(persona: any): string[] {
		const features = persona.features || {};
		return Object.keys(features)
			.filter(key => features[key])
			.map(key => {
				// Convert camelCase to readable text
				return key.replace(/([A-Z])/g, ' $1').trim();
			});
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-background to-accent/10 flex items-center justify-center p-4">
	<div class="max-w-4xl w-full">
		<!-- Progress Bar -->
		<div class="mb-8">
			<div class="flex items-center justify-between mb-2">
				<span class="text-sm text-muted-foreground">Step {currentStep + 1} of 4</span>
				<button
					onclick={skipOnboarding}
					disabled={loading}
					class="text-sm text-muted-foreground hover:text-foreground transition"
				>
					Skip onboarding
				</button>
			</div>
			<div class="h-2 bg-muted rounded-full overflow-hidden">
				<div
					class="h-full bg-primary transition-all duration-300"
					style="width: {((currentStep + 1) / 4) * 100}%"
				></div>
			</div>
		</div>

		<!-- Error Message -->
		{#if error}
			<div class="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3">
				<AlertCircle class="w-5 h-5 text-destructive mt-0.5" />
				<p class="text-sm text-destructive">{error}</p>
			</div>
		{/if}

		<!-- Onboarding Card -->
		<div class="bg-card border border-border rounded-xl shadow-lg p-8">
			{#if currentStep === 0}
				<!-- Step 1: Persona Selection -->
				<div class="text-center mb-8">
					<h1 class="text-3xl font-bold mb-2">Welcome to Focus by Kraliki!</h1>
					<p class="text-muted-foreground">Let's personalize your experience. Choose the profile that best describes you:</p>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					{#each personas as persona}
						{@const PersonaIcon = personaIcons[persona.id] || Compass}
						<button
							onclick={() => selectPersona(persona.id)}
							disabled={loading}
							class="group relative p-6 border-2 rounded-lg transition-all hover:border-primary hover:shadow-lg disabled:opacity-50 {selectedPersona === persona.id ? 'border-primary bg-primary/5' : 'border-border'}"
						>
							<div class="flex flex-col items-center text-center space-y-4">
								<div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition">
									<PersonaIcon class="w-8 h-8 text-primary" />
								</div>

								<div>
									<h3 class="font-semibold text-lg mb-1">{persona.name}</h3>
									<p class="text-sm text-muted-foreground">{persona.description}</p>
								</div>

								{#if selectedPersona === persona.id}
									<div class="absolute top-3 right-3">
										<Check class="w-5 h-5 text-primary" />
									</div>
								{/if}
							</div>
						</button>
					{/each}
				</div>

			{:else if currentStep === 1}
				<!-- Step 2: Privacy Preferences -->
				<div class="text-center mb-8">
					<Shield class="w-12 h-12 text-primary mx-auto mb-4" />
					<h2 class="text-2xl font-bold mb-2">Privacy & Data Controls</h2>
					<p class="text-muted-foreground">Your data, your control. Configure how Focus by Kraliki handles your information.</p>
				</div>

				<div class="space-y-6 max-w-2xl mx-auto">
					<!-- BYOK Information -->
					<div class="p-6 bg-primary/5 border border-primary/20 rounded-lg">
						<h3 class="font-semibold text-lg mb-3 flex items-center gap-2">
							<Sparkles class="w-5 h-5 text-primary" />
							Bring Your Own Key (BYOK)
						</h3>
						<p class="text-sm text-muted-foreground mb-4">
							You can use your own API keys for OpenRouter, giving you:
						</p>
						<ul class="space-y-2 text-sm text-muted-foreground">
							<li class="flex items-start gap-2">
								<Check class="w-4 h-4 text-primary mt-0.5" />
								<span>Complete control over your data and AI usage</span>
							</li>
							<li class="flex items-start gap-2">
								<Check class="w-4 h-4 text-primary mt-0.5" />
								<span>Unlimited AI requests without upgrading to Premium</span>
							</li>
							<li class="flex items-start gap-2">
								<Check class="w-4 h-4 text-primary mt-0.5" />
								<span>Your data never touches our AI servers</span>
							</li>
						</ul>
						<p class="text-xs text-muted-foreground mt-4">
							You can configure BYOK later in Settings.
						</p>
					</div>

					<!-- AI Feature Toggles -->
					<div class="space-y-4">
						<div class="flex items-center justify-between p-4 bg-accent/30 rounded-lg">
							<div class="flex-1">
								<p class="font-medium">Gemini File Search</p>
								<p class="text-sm text-muted-foreground">
									AI-powered semantic search over your knowledge base using Google Gemini
								</p>
							</div>
							<input
								type="checkbox"
								bind:checked={privacyPreferences.geminiFileSearchEnabled}
								class="w-5 h-5 accent-primary"
							/>
						</div>

						<div class="flex items-center justify-between p-4 bg-accent/30 rounded-lg">
							<div class="flex-1">
								<p class="font-medium">II-Agent Assistance</p>
								<p class="text-sm text-muted-foreground">
									Advanced AI agent for complex workflows and multi-step tasks
								</p>
							</div>
							<input
								type="checkbox"
								bind:checked={privacyPreferences.iiAgentEnabled}
								class="w-5 h-5 accent-primary"
							/>
						</div>
					</div>

					<!-- Privacy Acknowledgment -->
					<div class="p-4 border-2 border-dashed border-border rounded-lg">
						<label class="flex items-start gap-3 cursor-pointer">
							<input
								type="checkbox"
								bind:checked={privacyPreferences.dataPrivacyAcknowledged}
								class="w-5 h-5 accent-primary mt-0.5"
							/>
							<span class="text-sm">
								I understand that AI features process my data using third-party services (OpenRouter, Google Gemini).
								I can disable features or use BYOK for full control.
								<a href="/privacy" target="_blank" class="text-primary hover:underline ml-1">Read Privacy Policy</a>
							</span>
						</label>
					</div>

					<button
						onclick={savePrivacyPreferences}
						disabled={loading || !privacyPreferences.dataPrivacyAcknowledged}
						class="w-full px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition font-medium"
					>
						{loading ? 'Saving...' : 'Continue'}
					</button>
				</div>

			{:else if currentStep === 2}
				<!-- Step 3: Feature Configuration -->
				<div class="text-center mb-8">
					<Settings class="w-12 h-12 text-primary mx-auto mb-4" />
					<h2 class="text-2xl font-bold mb-2">Feature Configuration</h2>
					<p class="text-muted-foreground">Fine-tune which features are enabled. You can change these anytime in Settings.</p>
				</div>

				<div class="space-y-4 max-w-2xl mx-auto">
					<div class="flex items-center justify-between p-4 bg-accent/30 rounded-lg">
						<div class="flex-1">
							<p class="font-medium">Gemini File Search</p>
							<p class="text-sm text-muted-foreground">
								Semantic search with AI-generated answers from your knowledge
							</p>
						</div>
						<input
							type="checkbox"
							bind:checked={featureToggles.geminiFileSearch}
							class="w-5 h-5 accent-primary"
						/>
					</div>

					<div class="flex items-center justify-between p-4 bg-accent/30 rounded-lg">
						<div class="flex-1">
							<p class="font-medium">II-Agent</p>
							<p class="text-sm text-muted-foreground">
								AI agent for complex multi-step workflows and automation
							</p>
						</div>
						<input
							type="checkbox"
							bind:checked={featureToggles.iiAgent}
							class="w-5 h-5 accent-primary"
						/>
					</div>

					<div class="flex items-center justify-between p-4 bg-accent/30 rounded-lg">
						<div class="flex-1">
							<p class="font-medium">Voice Transcription</p>
							<p class="text-sm text-muted-foreground">
								Capture tasks and notes using voice commands
							</p>
						</div>
						<input
							type="checkbox"
							bind:checked={featureToggles.voiceTranscription}
							class="w-5 h-5 accent-primary"
						/>
					</div>

					<div class="flex gap-3">
						<button
							onclick={() => currentStep = 1}
							disabled={loading}
							class="px-6 py-3 border border-border rounded-lg hover:bg-accent transition"
						>
							Back
						</button>
						<button
							onclick={saveFeatureToggles}
							disabled={loading}
							class="flex-1 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition font-medium"
						>
							{loading ? 'Saving...' : 'Continue'}
						</button>
					</div>
				</div>

			{:else if currentStep === 3}
				<!-- Step 4: Complete -->
				<div class="text-center max-w-2xl mx-auto">
					<div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
						<Check class="w-8 h-8 text-primary" />
					</div>

					<h2 class="text-2xl font-bold mb-2">You're all set!</h2>
					<p class="text-muted-foreground mb-8">
						Focus by Kraliki is ready to help you stay productive and focused.
					</p>

					{#if selectedPersona}
						{@const persona = personas.find(p => p.id === selectedPersona)}
						{#if persona && persona.onboardingTasks}
							<div class="text-left mb-8 p-6 bg-accent/30 rounded-lg">
								<h3 class="font-semibold mb-4">Recommended next steps for {persona.name}:</h3>
								<ul class="space-y-3">
									{#each persona.onboardingTasks as task}
										<li class="flex items-start gap-3">
											<div class="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
												<span class="text-xs text-primary font-medium">{persona.onboardingTasks.indexOf(task) + 1}</span>
											</div>
											<span class="text-sm">{task}</span>
										</li>
									{/each}
								</ul>
							</div>
						{/if}
					{/if}

					<button
						onclick={completeOnboarding}
						disabled={loading}
						class="px-8 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition font-medium text-lg"
					>
						{loading ? 'Loading...' : 'Go to Dashboard'}
					</button>
				</div>
			{/if}
		</div>

		<!-- Footer -->
		<div class="text-center mt-6 text-sm text-muted-foreground">
			<p>Need help? <a href="/docs" class="text-primary hover:underline">Visit our documentation</a></p>
		</div>
	</div>
</div>

<script lang="ts">
import { onDestroy, onMount } from 'svelte';
import { browser } from '$app/environment';
import { useAppConfig } from '$lib/hooks/useAppConfig';
import {
	fetchAvailableModels,
	fetchAvailableVoices,
	fetchVoiceConfig,
	fetchCampaignScript,
	makeOutboundCall,
	updateSessionConfig,
	fetchCallResult,
	endOutboundCall,
	type VoiceDetails,
	type CallResult,
	type AvailableVoicesResponse,
	type AvailableModelsResponse,
	type VoiceConfigResponse
} from '$lib/services/calls';
import { createQuery } from '@tanstack/svelte-query';
import { Activity, Loader2, PhoneOutgoing, PhoneOff, Plus, Trash2, FileText, RefreshCcw } from 'lucide-svelte';
import { createProviderSession, type ProviderType } from '$lib/services/audioSession';
import { createAudioManager } from '$lib/services/audioManager';
import AIInsightsPanel from '$lib/components/AIInsightsPanel.svelte';
import ProviderSwitcher from '$lib/components/ProviderSwitcher.svelte';

	type AudioMode = 'telnyx' | 'twilio' | 'local';
	type CallStatus = 'idle' | 'configuring' | 'initiating-call' | 'in-progress' | 'polling-results' | 'completed' | 'failed';

	interface Company {
		name: string;
		phone: string;
		status?: 'pending' | 'in-progress' | 'polling-results' | 'completed' | 'failed';
		callSid?: string;
	}

	interface CampaignOption {
		id: number;
		title: string;
		description: string;
	}

	const config = useAppConfig();

	const AVAILABLE_LANGUAGES = [
		{ code: 'en', label: 'English' },
		{ code: 'es', label: 'Spanish' },
		{ code: 'cz', label: 'Czech' }
	];

	const AVAILABLE_COUNTRIES = [
		{
			code: 'US',
			name: 'United States',
			flag: '🇺🇸',
			phoneNumber: config.countryFromNumbers.US ?? config.defaultFromNumber
		},
		{
			code: 'CZ',
			name: 'Czech Republic',
			flag: '🇨🇿',
			phoneNumber: config.countryFromNumbers.CZ ?? config.defaultFromNumber
		},
		{
			code: 'ES',
			name: 'Spain',
			flag: '🇪🇸',
			phoneNumber: config.countryFromNumbers.ES ?? config.defaultFromNumber
		}
	];

	const SAMPLE_CAMPAIGNS: CampaignOption[] = [
		{ id: 1, title: 'Insurance Renewal', description: 'Multi-step follow-up call with sentiment tracking.' },
		{ id: 2, title: 'Solar Outreach', description: 'Energy-efficiency appointment setting.' },
		{ id: 3, title: 'Customer Re-engagement', description: 'Generic follow-up script for dormant accounts.' }
	];

	const COMPANIES_STORAGE_KEY = 'operator-console.target-companies';

let audioMode = $state<AudioMode>('telnyx');
let enableDeEssing = $state(false);
let selectedCountry = $state('CZ');
let fromPhoneNumber = $state(config.defaultFromNumber);
let selectedModel = $state('');
let selectedVoice = $state('');
let selectedLanguage = $state('en');
let aiInstructions = $state('');
let isLoadingScript = $state(false);
let isProcessing = $state(false);
let lastError = $state<string | null>(null);
	let callStatus = $state<CallStatus>('idle');
let companies = $state<Company[]>([{ name: '', phone: '' }]);
let currentCallSid = $state<string | null>(null);
let latestSummary = $state<CallResult | null>(null);
let hasBootstrappedCompanies = $state(false);
let pollInterval: ReturnType<typeof setTimeout> | null = null;

// AI Insights state
interface TranscriptMessage {
	role: 'user' | 'assistant';
	content: string;
	timestamp: Date;
}

interface IntentAnalysis {
	intent: string;
	confidence: number;
	category: 'inquiry' | 'complaint' | 'purchase' | 'support' | 'general';
	keywords: string[];
}

interface SentimentAnalysis {
	sentiment: 'positive' | 'neutral' | 'negative';
	score: number;
	confidence: number;
	emotions: {
		joy?: number;
		anger?: number;
		fear?: number;
		sadness?: number;
	};
}

interface Suggestion {
	id: string;
	type: 'response' | 'action' | 'escalation';
	title: string;
	description: string;
	priority: 'high' | 'medium' | 'low';
	confidence: number;
	status: 'pending' | 'accepted' | 'rejected';
	timestamp: Date;
}

let transcriptMessages = $state<TranscriptMessage[]>([]);
let currentIntent = $state<IntentAnalysis | null>(null);
let currentSentiment = $state<SentimentAnalysis | null>(null);
let suggestions = $state<Suggestion[]>([]);

// Provider state
interface Provider {
	id: string;
	name: string;
	status: 'active' | 'available' | 'unavailable';
	capabilities?: {
		realtime: boolean;
		multimodal: boolean;
		functionCalling: boolean;
	};
}
let availableProviders = $state<Provider[]>([
	{
		id: 'gemini',
		name: 'Google Gemini Live',
		status: 'available',
		capabilities: { realtime: true, multimodal: true, functionCalling: true }
	},
	{
		id: 'openai',
		name: 'OpenAI Realtime',
		status: 'available',
		capabilities: { realtime: true, multimodal: false, functionCalling: true }
	},
	{
		id: 'deepgram_nova3',
		name: 'Deepgram Nova 3',
		status: 'available',
		capabilities: { realtime: true, multimodal: false, functionCalling: true }
	}
]);
let currentProvider = $state<ProviderType>('gemini');

	function resolveTelephonyLabel(mode: AudioMode): string {
		if (mode === 'telnyx') return 'Telnyx';
		if (mode === 'twilio') return 'Twilio';
		return 'Telephony';
	}

// Create provider-aware session
const providerSession = createProviderSession({
	provider: currentProvider,
	path: '/test-outbound'
});
let sessionState = $state(providerSession.getState());
let hasSentStartMessage = $state(false);

const unsubscribeSession = providerSession.subscribe((value) => {
	sessionState = value;
});

const audioManager = createAudioManager();
let audioState = $state(audioManager.getState());
const unsubscribeAudio = audioManager.subscribe((value) => {
	audioState = value;
});

audioManager.sendCapturedFrame((buffer) => {
	try {
		const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer.buffer)));
		providerSession.send(
			JSON.stringify({
				type: 'audio-data',
				audioData: base64
			})
		);
	} catch (error) {
		console.error('Failed to send captured audio frame', error);
	}
});

let lastProcessedEventAt = $state<number | null>(null);

let hasRequestedTurnComplete = $state(false);

const voicesQuery = createQuery<AvailableVoicesResponse>({
	queryKey: ['available-voices'],
	queryFn: fetchAvailableVoices
});

const modelsQuery = createQuery<AvailableModelsResponse>({
	queryKey: ['available-models'],
	queryFn: fetchAvailableModels
});

const voiceConfigQuery = createQuery<VoiceConfigResponse>({
	queryKey: ['voice-config'],
	queryFn: fetchVoiceConfig
});

const voicesData = $derived($voicesQuery.data);
const modelsData = $derived($modelsQuery.data);
const voiceConfigData = $derived($voiceConfigQuery.data);

const availableVoiceDetails = $derived<Record<string, VoiceDetails>>(voicesData?.voices ?? {});
const availableVoices = $derived(Object.keys(availableVoiceDetails));
const voiceDescriptions = $derived<Record<string, string>>(voiceConfigData?.voiceDescriptions ?? {});
const availableModels = $derived<Record<string, unknown>>(modelsData?.availableModels ?? {});
const defaultVoice = $derived(voicesData?.currentDefault);
const defaultModel = $derived(modelsData?.defaultModel);
const isConfigurationLoading = $derived(
	$voicesQuery.isPending || $modelsQuery.isPending || $voiceConfigQuery.isPending
);

$effect(() => {
	const voices = availableVoices;
	if (!voices.length) return;
	if (!voices.includes(selectedVoice)) {
		const fallback = defaultVoice && voices.includes(defaultVoice) ? defaultVoice : voices[0];
		selectedVoice = fallback ?? '';
	}
});

$effect(() => {
	const models = Object.keys(availableModels);
	if (!models.length) return;
	if (!models.includes(selectedModel)) {
		const fallback = defaultModel && models.includes(defaultModel) ? defaultModel : models[0];
		selectedModel = fallback ?? '';
	}
});

function sendTurnComplete() {
	if (sessionState.status !== 'connected') return;
	if (hasRequestedTurnComplete) return;
	providerSession.send(JSON.stringify({ type: 'turn-complete' }));
	hasRequestedTurnComplete = true;
}

onMount(() => {
	hydrateCompanies();
});

onDestroy(() => {
	if (pollInterval) {
		clearTimeout(pollInterval);
	}
	providerSession.disconnect();
	unsubscribeSession();
	void audioManager.cleanup();
	unsubscribeAudio();
});

	$effect(() => {
		const country = AVAILABLE_COUNTRIES.find((option) => option.code === selectedCountry);
		fromPhoneNumber = country?.phoneNumber ?? config.defaultFromNumber;
	});

	$effect(() => {
		if (!browser || !hasBootstrappedCompanies) return;
		try {
			localStorage.setItem(COMPANIES_STORAGE_KEY, JSON.stringify(companies));
		} catch (error) {
			console.warn('Failed to persist companies', error);
		}
	});

async function hydrateCompanies() {
		if (!browser) return;
		try {
			const stored = localStorage.getItem(COMPANIES_STORAGE_KEY);
			if (stored) {
				const parsed = JSON.parse(stored) as Company[];
				if (Array.isArray(parsed) && parsed.length > 0) {
					companies = parsed.map((company) => ({ name: company.name ?? '', phone: company.phone ?? '' }));
				}
			}
		} catch (error) {
			console.warn('Failed to hydrate companies', error);
		}
		hasBootstrappedCompanies = true;
	}

	$effect(() => {
	if (sessionState.status === 'connected' && !hasSentStartMessage) {
		const payload = buildStartSessionPayload();
		providerSession.send(JSON.stringify(payload));
		hasSentStartMessage = true;
	}
	if (sessionState.status !== 'connected') {
		hasSentStartMessage = false;
	}
});

$effect(() => {
	if (!sessionState.lastEventAt) return;
	if (lastProcessedEventAt === sessionState.lastEventAt) return;

	lastProcessedEventAt = sessionState.lastEventAt;
	const payload = sessionState.lastEvent;
	if (payload && typeof payload === 'object' && 'type' in payload) {
		const event = payload as {
			type?: string;
			audio?: string;
			mimeType?: string | null;
			text?: string;
			role?: 'user' | 'assistant';
			data?: any;
		};
		if (event.type === 'audio' && event.audio) {
			void audioManager.playBase64Audio(event.audio, event.mimeType).catch((error) => {
				console.error('Failed to play realtime audio chunk', error);
			});
			hasRequestedTurnComplete = false;
		}
		if (event.type === 'session-started') {
			audioManager.setMessage('Session ready. Speak to interact with Gemini.');
			transcriptMessages = [];
		}
		if (event.type === 'turn-complete') {
			audioManager.setMessage('Gemini turn complete. Awaiting new input.');
			hasRequestedTurnComplete = false;
		}
		// Capture transcription events
		if (event.type === 'transcription' && event.text && event.role) {
			addTranscriptMessage(event.role, event.text);
		}
		// Capture text output events
		if (event.type === 'text' && event.text) {
			addTranscriptMessage('assistant', event.text);
		}
		// Capture AI insights events
		if (event.type === 'intent-analysis') {
			currentIntent = event.data as IntentAnalysis;
		}
		if (event.type === 'sentiment-analysis') {
			currentSentiment = event.data as SentimentAnalysis;
		}
		if (event.type === 'suggestion') {
			const suggestion: Suggestion = {
				id: event.data.id || Math.random().toString(36).substr(2, 9),
				type: event.data.type || 'response',
				title: event.data.title || 'AI Suggestion',
				description: event.data.description || '',
				priority: event.data.priority || 'medium',
				confidence: event.data.confidence || 0.5,
				status: 'pending',
				timestamp: new Date()
			};
			suggestions = [...suggestions, suggestion];
		}
	}
});

function updateCompanyField(index: number, field: 'name' | 'phone', value: string) {
	companies = companies.map((company, i) => (i === index ? { ...company, [field]: value } : company));
}

	function handleCompanyNameInput(index: number) {
		return (event: Event) => {
			const target = event.currentTarget as HTMLInputElement;
			updateCompanyField(index, 'name', target.value);
		};
	}

	function handleCompanyPhoneInput(index: number) {
		return (event: Event) => {
			const target = event.currentTarget as HTMLInputElement;
			updateCompanyField(index, 'phone', target.value);
		};
	}

	function removeCompany(index: number) {
		if (companies.length === 1) {
			companies = [{ name: '', phone: '' }];
			return;
		}
		companies = companies.filter((_, i) => i !== index);
	}

	function addCompany() {
		companies = [...companies, { name: '', phone: '' }];
	}

	function resolveVoiceLabel(voice: string) {
		const description = voiceDescriptions[voice];
		if (description) return description;
		const detail = availableVoiceDetails[voice];
		if (detail) {
			const meta = [detail.gender, detail.characteristics].filter(Boolean).join(' · ');
			return meta ? `${voice} — ${meta}` : voice;
		}
		return voice;
	}

	async function loadCampaign(id: number) {
		isLoadingScript = true;
		lastError = null;
		try {
			const campaign = await fetchCampaignScript(id);
			const readableName = campaign.name ?? `Campaign ${id}`;
			selectedLanguage = (campaign.language ?? selectedLanguage) as string;
			aiInstructions = convertCampaignToInstructions(campaign, readableName);
		} catch (error) {
			console.error('Failed to load campaign', error);
			lastError = `Unable to load campaign script ${id}.`;
		} finally {
			isLoadingScript = false;
		}
	}

	function convertCampaignToInstructions(campaign: Record<string, unknown>, name: string) {
		try {
			return `You are an enterprise outreach agent executing the “${name}” campaign. Follow this structured conversation:\n\n${JSON.stringify(campaign, null, 2)}\n\nMaintain professional tone, capture key details, and escalate if transfer steps are present.`;
		} catch (error) {
			console.warn('Failed to convert campaign to instructions', error);
			return aiInstructions;
		}
	}

	function validateBeforeCall(company: Company) {
		if (!selectedModel || !selectedVoice) {
			lastError = 'Select an AI model and voice before starting a call.';
			return false;
		}
		if (!aiInstructions.trim()) {
			lastError = 'Load a campaign script or provide AI instructions.';
			return false;
		}
		if (!company.phone.trim()) {
			lastError = 'Target phone number is required.';
			return false;
		}
		return true;
	}

	async function handleSingleCall(company: Company, index: number) {
		if (!validateBeforeCall(company)) return;
		isProcessing = true;
		lastError = null;
		callStatus = 'configuring';

		try {
			const telephonyProvider = audioMode === 'local' ? undefined : audioMode;

			await updateSessionConfig({
				model: selectedModel,
				voice: selectedVoice,
				language: selectedLanguage,
				fromPhoneNumber,
				audioMode,
				aiInstructions,
				deEssing: enableDeEssing
			});

			callStatus = 'initiating-call';
			const response = await makeOutboundCall({
				company: { name: company.name, phone: company.phone },
				voice: selectedVoice,
				model: selectedModel,
				language: selectedLanguage,
				audioMode,
				deEssing: enableDeEssing,
				fromPhoneNumber,
				aiInstructions,
				countryCode: selectedCountry,
				provider: telephonyProvider
			});

			currentCallSid = response.callSid;
			companies = companies.map((c, i) =>
				i === index
					? {
						...c,
						status: 'in-progress',
						callSid: response.callSid
					}
					: c
			);
			callStatus = 'in-progress';
			await pollForResult(response.callSid, index);
		} catch (error) {
			console.error('Failed to process outbound call', error);
			lastError = error instanceof Error ? error.message : 'Failed to start outbound call.';
			companies = companies.map((c, i) => (i === index ? { ...c, status: 'failed' } : c));
			callStatus = 'failed';
		} finally {
			isProcessing = false;
		}
	}

	async function pollForResult(callSid: string, companyIndex: number, attempt = 0): Promise<void> {
		if (attempt === 0) {
			callStatus = 'polling-results';
		}
		try {
			const result = await fetchCallResult(callSid);
			if (result?.status && ['completed', 'failed'].includes(result.status)) {
				latestSummary = result;
				companies = companies.map((company, index) =>
					index === companyIndex
						? { ...company, status: result.status === 'completed' ? 'completed' : 'failed' }
						: company
				);
				callStatus = result.status === 'completed' ? 'completed' : 'failed';
				return;
			}
		} catch (error) {
			console.warn('Failed to poll call result', error);
		}

		if (attempt > 20) {
			callStatus = 'failed';
			return;
		}

		pollInterval = setTimeout(async () => {
			await pollForResult(callSid, companyIndex, attempt + 1);
		}, 3000);
	}

	async function handleStopCall(callSid: string | undefined, index: number) {
		if (!callSid) return;
		isProcessing = true;
		try {
			await endOutboundCall(callSid);
			companies = companies.map((company, i) => (i === index ? { ...company, status: 'failed' } : company));
			callStatus = 'failed';
		} catch (error) {
			console.warn('Failed to stop call', error);
		} finally {
			isProcessing = false;
		}
	}

	function resetSummary() {
		latestSummary = null;
		callStatus = 'idle';
		currentCallSid = null;
	}

	function statusLabel(status: Company['status']) {
		switch (status) {
			case 'in-progress':
				return 'In progress';
			case 'polling-results':
				return 'Processing results';
			case 'completed':
				return 'Completed';
			case 'failed':
				return 'Failed';
			default:
				return 'Pending';
		}
	}

	function callStatusDescription(status: CallStatus) {
		switch (status) {
			case 'configuring':
				return 'Sending session configuration to backend...';
			case 'initiating-call':
				return 'Dialing target company via telephony provider...';
			case 'in-progress':
				return 'Live call in progress.';
			case 'polling-results':
				return 'Awaiting call summary and analytics...';
			case 'completed':
				return 'Call completed successfully. Review summary below.';
			case 'failed':
				return 'Call failed or was stopped. Check logs and retry.';
			default:
				return 'Ready to launch the next outbound call.';
		}
	}

async function connectRealtimeSession() {
	if (audioState.status !== 'recording') {
		const result = await audioManager.startMicrophone();
		if (!result.success) {
			lastError = result.error ?? 'Unable to start microphone.';
			return;
		}
	}
	providerSession.connect();
}

function disconnectRealtimeSession() {
	providerSession.disconnect();
	audioManager.stop();
}

function buildStartSessionPayload() {
	const targetCompany = companies[0] ?? { name: '', phone: '' };
	return {
		type: 'start-session',
		voice: selectedVoice,
		model: selectedModel,
		language: selectedLanguage,
		aiInstructions,
		company: targetCompany
	};
}

async function handleStartAudio() {
	const result = await audioManager.startMicrophone();
	if (!result.success) {
		lastError = result.error ?? 'Unable to access microphone.';
	}
}

function handleStopAudio() {
	audioManager.stop();
}

async function handleProviderSwitch(providerId: string) {
	console.log('Switching to provider:', providerId);
	const newProvider = providerId as ProviderType;

	if (newProvider === currentProvider) return;

	// Switch the provider session
	try {
		await providerSession.switchProvider(newProvider);
		currentProvider = newProvider;

		// Update provider status
		availableProviders = availableProviders.map(p => ({
			...p,
			status: p.id === providerId ? 'active' : 'available'
		}));

		// Add system message to transcript
		transcriptMessages = [
			...transcriptMessages,
			{
				role: 'assistant',
				content: `🔄 Switched to ${availableProviders.find(p => p.id === providerId)?.name}`,
				timestamp: new Date()
			}
		];
	} catch (error) {
		console.error('Failed to switch provider:', error);
		lastError = 'Failed to switch provider. Please try again.';
	}
}

function addTranscriptMessage(role: 'user' | 'assistant', content: string) {
	transcriptMessages = [
		...transcriptMessages,
		{
			role,
			content,
			timestamp: new Date()
		}
	];
}

function handleSuggestionAction(suggestionId: string, action: 'accept' | 'reject') {
	suggestions = suggestions.map(s => 
		s.id === suggestionId 
			? { ...s, status: action === 'accept' ? 'accepted' : 'rejected' }
			: s
	);
	
	// Send the action back to the backend for logging/execution
	if (action === 'accept') {
		const suggestion = suggestions.find(s => s.id === suggestionId);
		if (suggestion) {
			providerSession.send(JSON.stringify({
				type: 'suggestion-action',
				suggestionId,
				action: 'accept',
				suggestion
			}));
		}
	}
}
</script>

<section class="space-y-6">
	<header class="space-y-1">
		<h1 class="text-2xl font-semibold text-text-primary">Outbound Call Orchestration</h1>
		<p class="text-sm text-text-muted">
			Configure AI voice, language, and campaign script, then launch targeted outbound sessions with Stack 2026 ergonomics.
		</p>
	</header>

	{#if lastError}
		<div class="rounded-xl border border-error/40 bg-error/10 px-4 py-3 text-sm text-error">
			{lastError}
		</div>
	{/if}

	<div class="grid gap-4 xl:grid-cols-[2fr_3fr]">
		<div class="space-y-4">
			<ProviderSwitcher
				providers={availableProviders}
				{currentProvider}
				isLive={callStatus === 'in-progress' || sessionState.status === 'connected'}
				onSwitch={handleProviderSwitch}
			/>

			<article class="card">
				<div class="card-header">
					<h2 class="text-lg font-semibold text-text-primary">Call Configuration</h2>
					<span class="text-xs text-text-muted">Telephony source • AI runtime • Output language</span>
				</div>
				<div class="space-y-4">
					{#if $voicesQuery.isError || $modelsQuery.isError}
						<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-sm text-error">
							Failed to load voice/model configuration. <button class="text-primary underline" type="button" onclick={() => { $voicesQuery.refetch(); $modelsQuery.refetch(); }}>Retry</button>
						</p>
					{/if}
					{#if isConfigurationLoading}
						<p class="text-xs text-text-muted">Loading configuration…</p>
					{/if}
					<label class="field" for="country-select">
						<span class="field-label">Country &amp; {resolveTelephonyLabel(audioMode)} Number</span>
						<select id="country-select" class="select-field" bind:value={selectedCountry}>
							{#each AVAILABLE_COUNTRIES as country}
								<option value={country.code}>
									{country.flag} {country.name} ({country.phoneNumber})
								</option>
							{/each}
						</select>
					</label>

					<label class="field" for="from-number">
						<span class="field-label">From Phone Number</span>
						<input id="from-number" class="input-field" value={fromPhoneNumber} readonly />
					</label>

					<label class="field" for="model-select">
						<span class="field-label">AI Model</span>
						<select id="model-select" class="select-field" bind:value={selectedModel}>
							{#each Object.entries(availableModels) as [modelId, modelInfo]}
								<option value={modelId}>
									{typeof modelInfo === 'object' && modelInfo && 'name' in modelInfo ? (modelInfo as { name: string }).name : modelId}
								</option>
							{/each}
						</select>
					</label>

					<label class="field" for="voice-select">
						<span class="field-label">AI Voice</span>
						<select id="voice-select" class="select-field" bind:value={selectedVoice}>
							{#each availableVoices as voice}
								<option value={voice}>{resolveVoiceLabel(voice)}</option>
							{/each}
						</select>
					</label>

					<div class="grid gap-4 md:grid-cols-2">
						<label class="field" for="language-select">
							<span class="field-label">Language</span>
							<select id="language-select" class="select-field" bind:value={selectedLanguage}>
								{#each AVAILABLE_LANGUAGES as language}
									<option value={language.code}>{language.label}</option>
								{/each}
							</select>
						</label>
						<label class="field" for="audio-mode">
							<span class="field-label">Telephony Provider</span>
							<select id="audio-mode" class="select-field" bind:value={audioMode}>
								<option value="telnyx">Telnyx PSTN (primary)</option>
								<option value="twilio">Twilio PSTN (optional)</option>
								<option value="local">Local WebRTC (beta)</option>
							</select>
						</label>
					</div>

					<div class="flex items-center justify-between rounded-xl border border-divider bg-secondary px-4 py-3">
						<div>
							<p class="text-sm font-medium text-text-primary">AI De-essing</p>
							<p class="text-xs text-text-muted">Reduce harsh sibilance for sharp telephony audio.</p>
						</div>
						<label class="relative inline-flex cursor-pointer items-center">
							<input type="checkbox" class="peer sr-only" bind:checked={enableDeEssing} />
							<span class="peer h-6 w-11 rounded-full bg-divider transition peer-checked:bg-primary-soft"></span>
							<span class="absolute left-1 top-1 h-4 w-4 rounded-full bg-text-muted transition peer-checked:translate-x-5 peer-checked:bg-primary"></span>
						</label>
					</div>
				</div>
			</article>

			<article class="card">
				<div class="card-header">
					<h2 class="text-lg font-semibold text-text-primary">Campaign Script &amp; Instructions</h2>
					<button class="btn btn-ghost" onclick={resetSummary}>
						<RefreshCcw class="size-4" /> Reset Summary
					</button>
				</div>
				<div class="space-y-4">
					<div class="grid gap-2 md:grid-cols-3">
						{#each SAMPLE_CAMPAIGNS as campaign}
							<button
								class="btn btn-secondary"
								disabled={isLoadingScript}
								onclick={() => loadCampaign(campaign.id)}
							>
								<FileText class="size-4" />
								{campaign.title}
							</button>
						{/each}
					</div>
					<textarea
						class="textarea-field"
						rows="8"
						bind:value={aiInstructions}
						placeholder="Paste or generate AI instructions here..."
					></textarea>
				</div>
			</article>
		</div>

		<div class="space-y-4">
			<article class="card">
				<div class="card-header">
					<h2 class="text-lg font-semibold text-text-primary">Target Companies</h2>
					<button class="btn btn-ghost" onclick={addCompany}>
						<Plus class="size-4" /> Add company
					</button>
				</div>
				<div class="space-y-3">
					{#each companies as company, index}
						<div class="rounded-2xl border border-divider bg-secondary/80 p-4">
							<div class="flex items-start justify-between gap-3">
								<div class="grid flex-1 gap-3 md:grid-cols-2">
									<label class="field" for={`company-${index}`}>
										<span class="field-label">Company</span>
										<input
											id={`company-${index}`}
											class="input-field"
											value={company.name}
											oninput={handleCompanyNameInput(index)}
										/>
									</label>
									<label class="field" for={`phone-${index}`}>
										<span class="field-label">Phone</span>
										<input
											id={`phone-${index}`}
											class="input-field"
											value={company.phone}
											oninput={handleCompanyPhoneInput(index)}
										/>
									</label>
								</div>
								<div class="flex items-center gap-2">
									<button
										class="btn btn-primary"
										disabled={isProcessing}
										onclick={() => handleSingleCall(company, index)}
									>
										{#if company.status === 'in-progress'}
											<Loader2 class="size-4 animate-spin" />
										{:else}
											<PhoneOutgoing class="size-4" />
										{/if}
										Launch Call
									</button>
									<button
										class="btn btn-ghost"
										disabled={!company.callSid || isProcessing}
										onclick={() => handleStopCall(company.callSid, index)}
									>
										<PhoneOff class="size-4" /> Stop
									</button>
									<button class="btn btn-ghost" onclick={() => removeCompany(index)}>
										<Trash2 class="size-4" />
									</button>
								</div>
							</div>
							<p class="mt-3 text-xs text-text-muted">Status: {statusLabel(company.status)}</p>
						</div>
					{/each}
				</div>
			</article>

			<AIInsightsPanel
				messages={transcriptMessages}
				isLive={callStatus === 'in-progress' || sessionState.status === 'connected'}
				intent={currentIntent}
				sentiment={currentSentiment}
				suggestions={suggestions}
				onSuggestionAction={handleSuggestionAction}
			/>

			<article class="card">
				<div class="card-header">
					<h2 class="text-lg font-semibold text-text-primary">Local Audio Tester</h2>
					<div class="text-xs text-text-muted">Status: {audioState.status}</div>
				</div>
				<div class="space-y-3 text-sm text-text-secondary">
					{#if audioState.error}
						<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-error">{audioState.error}</p>
					{/if}
					{#if audioState.message}
						<p class="text-xs text-text-muted">{audioState.message}</p>
					{/if}
					<div class="flex gap-2">
						<button
							type="button"
							class="btn btn-primary"
							onclick={handleStartAudio}
							disabled={audioState.status === 'requesting-mic' || audioState.status === 'recording'}
						>
							{audioState.status === 'requesting-mic' ? 'Requesting…' : 'Start microphone'}
						</button>
						<button
							type="button"
							class="btn btn-ghost"
							onclick={handleStopAudio}
							disabled={audioState.status === 'idle' || audioState.status === 'ready'}
						>
							Stop
						</button>
					</div>
					{#if audioState.lastPlaybackAt}
						<p class="text-xs text-text-muted">
							Last playback: {new Date(audioState.lastPlaybackAt).toLocaleTimeString()}
						</p>
					{/if}
				</div>
			</article>

			<article class="card">
				<div class="card-header">
					<div class="flex items-center gap-2 text-text-primary">
						<Activity class="size-4" />
						<h2 class="text-lg font-semibold">Session Monitor</h2>
					</div>
				</div>
				<div class="space-y-3">
					<p class="text-sm text-text-muted">{callStatusDescription(callStatus)}</p>
					{#if latestSummary}
						<div class="rounded-xl border border-divider bg-secondary/70 p-4 text-sm text-text-secondary">
							<p class="font-semibold text-text-primary">Latest Summary</p>
							<p class="mt-2 whitespace-pre-wrap text-sm text-text-primary">{latestSummary.call_summary}</p>
							<div class="mt-3 grid gap-2 text-xs text-text-muted md:grid-cols-2">
								<p>Sentiment: {latestSummary.customer_sentiment ?? 'N/A'}</p>
								<p>Duration: {latestSummary.duration ?? 'N/A'}</p>
								<p>Recorded: {latestSummary.recordingTimestamp ?? 'Not available'}</p>
								<p>Recording URL: {latestSummary.recordingUrl ?? 'Not available'}</p>
							</div>
						</div>
					{:else}
						<p class="text-xs text-text-muted">No call summaries available yet. Launch a call to populate analytics.</p>
					{/if}
				</div>
			</article>

			<article class="card">
				<div class="card-header">
					<h2 class="text-lg font-semibold text-text-primary">Realtime Session</h2>
					<div class="text-xs text-text-muted">
						Provider: {sessionState.provider} • Status: {sessionState.status}
					</div>
				</div>
				<div class="space-y-3 text-sm text-text-secondary">
					{#if sessionState.error}
						<p class="rounded-lg border border-error/40 bg-error/10 px-3 py-2 text-error">{sessionState.error}</p>
					{/if}
					<div class="flex gap-2">
						<button
							type="button"
							class="btn btn-secondary"
							onclick={connectRealtimeSession}
							disabled={sessionState.status === 'connecting' || sessionState.status === 'connected'}
						>
							{sessionState.status === 'connecting' ? 'Connecting…' : 'Connect session'}
						</button>
						<button
							type="button"
							class="btn btn-ghost"
							onclick={disconnectRealtimeSession}
							disabled={sessionState.status === 'idle' || sessionState.status === 'disconnected'}
						>
							Disconnect
						</button>
					</div>
					<p class="text-xs text-text-muted">
						Last event: {sessionState.lastEventAt ? new Date(sessionState.lastEventAt).toLocaleTimeString() : '—'}
					</p>
				</div>
			</article>
		</div>
	</div>
</section>

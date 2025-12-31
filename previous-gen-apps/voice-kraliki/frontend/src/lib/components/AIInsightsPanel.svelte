<script lang="ts">
	import { MessageCircle, User, Bot, Brain, TrendingUp, AlertTriangle, Lightbulb, CheckCircle, XCircle } from 'lucide-svelte';

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
		score: number; // -1 to 1
		confidence: number; // 0 to 1
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

	interface Props {
		messages?: TranscriptMessage[];
		isLive?: boolean;
		intent?: IntentAnalysis | null;
		sentiment?: SentimentAnalysis | null;
		suggestions?: Suggestion[];
		onSuggestionAction?: (suggestionId: string, action: 'accept' | 'reject') => void;
	}

	let { 
		messages = [], 
		isLive = false, 
		intent = null, 
		sentiment = null, 
		suggestions = [],
		onSuggestionAction
	}: Props = $props();

	let activeTab = $state<'transcript' | 'insights' | 'suggestions'>('transcript');

	function formatTime(date: Date): string {
		return date.toLocaleTimeString('en-US', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		});
	}

	function getRoleLabel(role: string): string {
		return role === 'user' ? 'Customer' : 'AI Agent';
	}

	function getRoleIcon(role: string) {
		return role === 'user' ? User : Bot;
	}

	function getRoleColor(role: string): string {
		return role === 'user' ? 'text-blue-500' : 'text-primary';
	}

	function getSentimentColor(sentiment: string): string {
		switch (sentiment) {
			case 'positive': return 'text-green-500';
			case 'negative': return 'text-red-500';
			default: return 'text-yellow-500';
		}
	}

	function getSentimentIcon(sentiment: string) {
		switch (sentiment) {
			case 'positive': return TrendingUp;
			case 'negative': return AlertTriangle;
			default: return Brain;
		}
	}

	function getIntentColor(category: string): string {
		switch (category) {
			case 'purchase': return 'text-green-500';
			case 'complaint': return 'text-red-500';
			case 'support': return 'text-blue-500';
			case 'inquiry': return 'text-purple-500';
			default: return 'text-gray-500';
		}
	}

	function getSuggestionIcon(type: string) {
		switch (type) {
			case 'action': return CheckCircle;
			case 'escalation': return AlertTriangle;
			default: return Lightbulb;
		}
	}

	function getSuggestionPriorityColor(priority: string): string {
		switch (priority) {
			case 'high': return 'border-red-500 bg-red-50';
			case 'medium': return 'border-yellow-500 bg-yellow-50';
			default: return 'border-gray-300 bg-gray-50';
		}
	}

	function handleSuggestionAction(suggestionId: string, action: 'accept' | 'reject') {
		if (onSuggestionAction) {
			onSuggestionAction(suggestionId, action);
		}
	}

	let hasInsights = $derived(intent || sentiment);
	let hasSuggestions = $derived(suggestions && suggestions.length > 0);
</script>

<article class="card h-full">
	<div class="card-header">
		<div class="flex items-center gap-2">
			<Brain class="size-5 text-text-primary" />
			<h2 class="text-lg font-semibold text-text-primary">AI Insights</h2>
			{#if isLive}
				<span class="inline-flex items-center gap-1.5 rounded-full bg-primary/20 px-2 py-0.5 text-xs font-medium text-primary">
					<span class="size-1.5 animate-pulse rounded-full bg-primary"></span>
					Live
				</span>
			{/if}
		</div>
		
		<!-- Tab Navigation -->
		<div class="flex gap-1 rounded-lg bg-secondary p-1">
			<button
				class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors {activeTab === 'transcript' ? 'bg-background text-text-primary shadow-sm' : 'text-text-muted hover:text-text-primary'}"
				onclick={() => activeTab = 'transcript'}
			>
				Transcript ({messages.length})
			</button>
			<button
				class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors {activeTab === 'insights' ? 'bg-background text-text-primary shadow-sm' : 'text-text-muted hover:text-text-primary'}"
				onclick={() => activeTab = 'insights'}
				disabled={!hasInsights}
			>
				Insights {hasInsights ? '✓' : ''}
			</button>
			<button
				class="rounded-md px-3 py-1.5 text-xs font-medium transition-colors {activeTab === 'suggestions' ? 'bg-background text-text-primary shadow-sm' : 'text-text-muted hover:text-text-primary'}"
				onclick={() => activeTab = 'suggestions'}
				disabled={!hasSuggestions}
			>
				Suggestions ({suggestions.length})
			</button>
		</div>
	</div>

	<div class="max-h-[600px] overflow-y-auto">
		<!-- Transcript Tab -->
		{#if activeTab === 'transcript'}
			<div class="space-y-3 p-4">
				{#if messages.length === 0}
					<div class="flex flex-col items-center justify-center py-12 text-center">
						<MessageCircle class="size-12 text-text-muted opacity-30" />
						<p class="mt-3 text-sm text-text-muted">
							No conversation yet. Start a call to see real-time transcription.
						</p>
					</div>
				{:else}
					{#each messages as message (message.timestamp)}
						<div class="rounded-xl border border-divider bg-secondary/50 p-4">
							<div class="flex items-start gap-3">
								<div class={`rounded-full p-2 ${message.role === 'user' ? 'bg-blue-500/10' : 'bg-primary/10'}`}>
									<svelte:component this={getRoleIcon(message.role)} class={`size-4 ${getRoleColor(message.role)}`} />
								</div>
								<div class="flex-1 space-y-1">
									<div class="flex items-center justify-between">
										<span class={`text-sm font-medium ${getRoleColor(message.role)}`}>
											{getRoleLabel(message.role)}
										</span>
										<span class="text-xs text-text-muted">
											{formatTime(message.timestamp)}
										</span>
									</div>
									<p class="text-sm leading-relaxed text-text-secondary">
										{message.content}
									</p>
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		{/if}

		<!-- Insights Tab -->
		{#if activeTab === 'insights'}
			<div class="space-y-4 p-4">
				{#if !hasInsights}
					<div class="flex flex-col items-center justify-center py-12 text-center">
						<Brain class="size-12 text-text-muted opacity-30" />
						<p class="mt-3 text-sm text-text-muted">
							No insights available yet. Continue the conversation to see AI analysis.
						</p>
					</div>
				{:else}
					<!-- Intent Analysis -->
					{#if intent}
						<div class="rounded-xl border border-divider bg-secondary/50 p-4">
							<div class="flex items-center gap-2 mb-3">
								<Brain class="size-4 text-text-primary" />
								<h3 class="font-semibold text-text-primary">Intent Analysis</h3>
								<span class={`text-xs font-medium ${getIntentColor(intent.category)}`}>
									{intent.category.toUpperCase()}
								</span>
							</div>
							<div class="space-y-2">
								<div class="flex items-center justify-between">
									<span class="text-sm text-text-secondary">Detected Intent:</span>
									<span class="text-sm font-medium text-text-primary">{intent.intent}</span>
								</div>
								<div class="flex items-center justify-between">
									<span class="text-sm text-text-secondary">Confidence:</span>
									<span class="text-sm font-medium text-text-primary">{(intent.confidence * 100).toFixed(1)}%</span>
								</div>
								{#if intent.keywords.length > 0}
									<div class="mt-3">
										<span class="text-sm text-text-secondary">Keywords:</span>
										<div class="mt-1 flex flex-wrap gap-1">
											{#each intent.keywords as keyword}
												<span class="rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">
													{keyword}
												</span>
											{/each}
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Sentiment Analysis -->
					{#if sentiment}
						<div class="rounded-xl border border-divider bg-secondary/50 p-4">
							<div class="flex items-center gap-2 mb-3">
								<svelte:component this={getSentimentIcon(sentiment.sentiment)} class={`size-4 ${getSentimentColor(sentiment.sentiment)}`} />
								<h3 class="font-semibold text-text-primary">Sentiment Analysis</h3>
								<span class={`text-xs font-medium ${getSentimentColor(sentiment.sentiment)}`}>
									{sentiment.sentiment.toUpperCase()}
								</span>
							</div>
							<div class="space-y-2">
								<div class="flex items-center justify-between">
									<span class="text-sm text-text-secondary">Score:</span>
									<span class="text-sm font-medium text-text-primary">{sentiment.score.toFixed(2)}</span>
								</div>
								<div class="flex items-center justify-between">
									<span class="text-sm text-text-secondary">Confidence:</span>
									<span class="text-sm font-medium text-text-primary">{(sentiment.confidence * 100).toFixed(1)}%</span>
								</div>
								{#if Object.keys(sentiment.emotions).length > 0}
									<div class="mt-3">
										<span class="text-sm text-text-secondary">Emotions:</span>
										<div class="mt-2 space-y-1">
											{#each Object.entries(sentiment.emotions) as [emotion, score]}
												<div class="flex items-center justify-between">
													<span class="text-xs text-text-muted capitalize">{emotion}:</span>
													<div class="flex items-center gap-2">
														<div class="h-2 w-16 rounded-full bg-secondary">
															<div 
																class="h-2 rounded-full bg-primary" 
																style="width: {score * 100}%"
															></div>
														</div>
														<span class="text-xs text-text-primary">{(score * 100).toFixed(0)}%</span>
													</div>
												</div>
											{/each}
										</div>
									</div>
								{/if}
							</div>
						</div>
					{/if}
				{/if}
			</div>
		{/if}

		<!-- Suggestions Tab -->
		{#if activeTab === 'suggestions'}
			<div class="space-y-3 p-4">
				{#if !hasSuggestions}
					<div class="flex flex-col items-center justify-center py-12 text-center">
						<Lightbulb class="size-12 text-text-muted opacity-30" />
						<p class="mt-3 text-sm text-text-muted">
							No suggestions available yet. AI will provide recommendations as the conversation progresses.
						</p>
					</div>
				{:else}
					{#each suggestions as suggestion (suggestion.id)}
						<div class={`rounded-xl border ${getSuggestionPriorityColor(suggestion.priority)} p-4`}>
							<div class="flex items-start gap-3">
								<div class="rounded-full p-2 bg-white/50">
									<svelte:component this={getSuggestionIcon(suggestion.type)} class="size-4 text-text-primary" />
								</div>
								<div class="flex-1 space-y-2">
									<div class="flex items-center justify-between">
										<h4 class="font-semibold text-text-primary">{suggestion.title}</h4>
										<div class="flex items-center gap-2">
											<span class="text-xs text-text-muted">
												{(suggestion.confidence * 100).toFixed(0)}% confidence
											</span>
											{#if suggestion.status !== 'pending'}
												{#if suggestion.status === 'accepted'}
													<CheckCircle class="size-4 text-green-500" />
												{:else}
													<XCircle class="size-4 text-red-500" />
												{/if}
											{/if}
										</div>
									</div>
									<p class="text-sm text-text-secondary">{suggestion.description}</p>
									{#if suggestion.status === 'pending'}
										<div class="flex gap-2">
											<button
												class="btn btn-primary btn-sm"
												onclick={() => handleSuggestionAction(suggestion.id, 'accept')}
											>
												<CheckCircle class="size-3" /> Accept
											</button>
											<button
												class="btn btn-ghost btn-sm"
												onclick={() => handleSuggestionAction(suggestion.id, 'reject')}
											>
												<XCircle class="size-3" /> Reject
											</button>
										</div>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		{/if}
	</div>
</article>
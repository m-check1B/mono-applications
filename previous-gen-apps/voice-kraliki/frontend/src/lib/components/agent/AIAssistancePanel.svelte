<script lang="ts">
	/**
	 * AI Assistance Panel
	 *
	 * Displays real-time AI-powered agent assistance:
	 * - Suggested responses
	 * - Knowledge base articles
	 * - Compliance warnings
	 * - Performance coaching tips
	 * - Click-to-use suggestions
	 */

	import type { AssistanceSuggestion } from '$lib/api/aiServices';

	interface Props {
		suggestions?: AssistanceSuggestion[];
		onUseSuggestion?: (suggestion: AssistanceSuggestion) => void;
		onDismissSuggestion?: (suggestionId: string) => void;
	}

	let {
		suggestions = $bindable([]),
		onUseSuggestion,
		onDismissSuggestion
	}: Props = $props();

	// Type icons mapping
	const typeIcons: Record<string, string> = {
		suggested_response: '💬',
		knowledge_article: '📚',
		compliance_warning: '⚠️',
		performance_tip: '💡',
		escalation_guide: '🚀'
	};

	// Priority colors
	const priorityColors: Record<string, { bg: string; border: string; text: string }> = {
		urgent: { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' },
		high: { bg: '#fff7ed', border: '#f97316', text: '#9a3412' },
		medium: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
		low: { bg: '#f0fdf4', border: '#10b981', text: '#065f46' }
	};

	// Format suggestion type
	const formatType = (type: string): string => {
		return type.split('_').map(word =>
			word.charAt(0).toUpperCase() + word.slice(1)
		).join(' ');
	};

	// Use suggestion
	const useSuggestion = (suggestion: AssistanceSuggestion) => {
		onUseSuggestion?.(suggestion);
	};

	// Dismiss suggestion
	const dismissSuggestion = (suggestionId: string) => {
		onDismissSuggestion?.(suggestionId);
	};

	// Sort suggestions by priority
	const sortedSuggestions = $derived(() => {
		const priorityOrder = ['urgent', 'high', 'medium', 'low'];
		return [...suggestions].sort((a, b) => {
			const priorityDiff = priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority);
			if (priorityDiff !== 0) return priorityDiff;
			return b.confidence - a.confidence;
		});
	});
</script>

<div class="ai-assistance-panel">
	<!-- Header -->
	<div class="header">
		<h3 class="title">
			<span class="icon">🤖</span>
			AI Assistance
		</h3>
		{#if suggestions.length > 0}
			<span class="badge">{suggestions.length} {suggestions.length === 1 ? 'suggestion' : 'suggestions'}</span>
		{/if}
	</div>

	<!-- Suggestions List -->
	<div class="suggestions-list">
		{#if sortedSuggestions().length > 0}
			{#each sortedSuggestions() as suggestion (suggestion.id)}
				{@const colors = priorityColors[suggestion.priority]}
				<div class="suggestion-card"
					style="background: {colors.bg}; border-color: {colors.border}">
					<!-- Card Header -->
					<div class="card-header">
						<div class="type-badge" style="color: {colors.text}">
							<span class="type-icon">{typeIcons[suggestion.type] || '📌'}</span>
							<span class="type-text">{formatType(suggestion.type)}</span>
						</div>
						<div class="priority-badge" style="color: {colors.text}">
							{suggestion.priority.toUpperCase()}
						</div>
					</div>

					<!-- Title -->
					<h4 class="suggestion-title" style="color: {colors.text}">{suggestion.title}</h4>

					<!-- Content -->
					<p class="suggestion-content">{suggestion.content}</p>

					<!-- Footer -->
					<div class="card-footer">
						<div class="confidence">
							<span class="confidence-label">Confidence:</span>
							<div class="confidence-bar">
								<div class="confidence-fill" style="width: {suggestion.confidence * 100}%;
									background: {colors.border}"></div>
							</div>
							<span class="confidence-value">{Math.round(suggestion.confidence * 100)}%</span>
						</div>
					</div>

					<!-- Actions -->
					<div class="card-actions">
						{#if suggestion.type === 'suggested_response'}
							<button class="action-btn primary" onclick={() => useSuggestion(suggestion)}
								style="background: {colors.border}">
								<span class="btn-icon">✓</span>
								Use Response
							</button>
						{:else if suggestion.type === 'knowledge_article'}
							<button class="action-btn secondary" onclick={() => useSuggestion(suggestion)}
								style="color: {colors.border}; border-color: {colors.border}">
								<span class="btn-icon">👁</span>
								View Article
							</button>
						{:else}
							<button class="action-btn secondary" onclick={() => useSuggestion(suggestion)}
								style="color: {colors.border}; border-color: {colors.border}">
								<span class="btn-icon">ℹ</span>
								More Info
							</button>
						{/if}
						<button class="action-btn dismiss" onclick={() => dismissSuggestion(suggestion.id)}>
							<span class="btn-icon">✕</span>
							Dismiss
						</button>
					</div>
				</div>
			{/each}
		{:else}
			<div class="no-suggestions">
				<span class="no-suggestions-icon">🤖</span>
				<p class="no-suggestions-text">No suggestions yet</p>
				<p class="no-suggestions-hint">AI assistance will appear as the conversation progresses</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.ai-assistance-panel {
		background: white;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		border: 1px solid #e5e7eb;
		height: 100%;
		display: flex;
		flex-direction: column;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 1.25rem;
		border-bottom: 1px solid #e5e7eb;
	}

	.title {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.1rem;
		font-weight: 600;
		color: #1f2937;
		margin: 0;
	}

	.title .icon {
		font-size: 1.3rem;
	}

	.badge {
		padding: 0.25rem 0.75rem;
		border-radius: 12px;
		font-size: 0.75rem;
		font-weight: 600;
		background: #f3f4f6;
		color: #4b5563;
	}

	.suggestions-list {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.suggestion-card {
		border: 2px solid;
		border-radius: 10px;
		padding: 1rem;
		transition: all 0.2s ease;
	}

	.suggestion-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
	}

	.type-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.85rem;
		font-weight: 600;
	}

	.type-icon {
		font-size: 1.2rem;
	}

	.priority-badge {
		padding: 0.25rem 0.5rem;
		border-radius: 6px;
		font-size: 0.7rem;
		font-weight: 700;
		background: rgba(255, 255, 255, 0.5);
	}

	.suggestion-title {
		font-size: 1rem;
		font-weight: 600;
		margin: 0 0 0.75rem 0;
		line-height: 1.3;
	}

	.suggestion-content {
		font-size: 0.9rem;
		color: #374151;
		line-height: 1.5;
		margin: 0 0 1rem 0;
	}

	.card-footer {
		margin-bottom: 1rem;
	}

	.confidence {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8rem;
	}

	.confidence-label {
		color: #6b7280;
		font-weight: 500;
		min-width: 75px;
	}

	.confidence-bar {
		flex: 1;
		height: 6px;
		background: rgba(0, 0, 0, 0.1);
		border-radius: 3px;
		overflow: hidden;
	}

	.confidence-fill {
		height: 100%;
		transition: width 0.3s ease;
	}

	.confidence-value {
		font-weight: 600;
		color: #374151;
		min-width: 40px;
		text-align: right;
	}

	.card-actions {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.action-btn {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		border-radius: 6px;
		font-size: 0.85rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		border: 2px solid transparent;
	}

	.action-btn:hover {
		transform: translateY(-1px);
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
	}

	.action-btn.primary {
		color: white;
		border: none;
	}

	.action-btn.secondary {
		background: white;
		border: 2px solid;
	}

	.action-btn.dismiss {
		background: #f3f4f6;
		color: #6b7280;
	}

	.action-btn.dismiss:hover {
		background: #e5e7eb;
		color: #374151;
	}

	.btn-icon {
		font-size: 1rem;
	}

	.no-suggestions {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 3rem 1rem;
		text-align: center;
		color: #9ca3af;
		flex: 1;
	}

	.no-suggestions-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
		opacity: 0.5;
	}

	.no-suggestions-text {
		font-size: 1rem;
		font-weight: 500;
		color: #6b7280;
		margin: 0 0 0.5rem 0;
	}

	.no-suggestions-hint {
		font-size: 0.85rem;
		color: #d1d5db;
		margin: 0;
	}

	/* Scrollbar styling */
	.suggestions-list::-webkit-scrollbar {
		width: 6px;
	}

	.suggestions-list::-webkit-scrollbar-track {
		background: #f3f4f6;
		border-radius: 3px;
	}

	.suggestions-list::-webkit-scrollbar-thumb {
		background: #d1d5db;
		border-radius: 3px;
	}

	.suggestions-list::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}

	@media (max-width: 768px) {
		.card-actions {
			flex-direction: column;
		}

		.action-btn {
			width: 100%;
			justify-content: center;
		}
	}
</style>

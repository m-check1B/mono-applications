<script lang="ts">
	/**
	 * Sentiment Indicator Component
	 *
	 * Displays real-time customer sentiment analysis:
	 * - Current sentiment score and emotion
	 * - Visual polarity indicator
	 * - Emotion icons
	 * - Sentiment trend
	 * - Alert badges for negative sentiment
	 */

	import type { SentimentAnalysis, SentimentTrend } from '$lib/api/aiServices';

	interface Props {
		sentiment: SentimentAnalysis | null;
		trend?: SentimentTrend | null;
	}

	let {
		sentiment = $bindable(null),
		trend = $bindable(null)
	}: Props = $props();

	// Emotion icon mapping
	const emotionIcons: Record<string, string> = {
		happy: '😊',
		satisfied: '🙂',
		neutral: '😐',
		frustrated: '😤',
		angry: '😠',
		confused: '😕',
		anxious: '😰'
	};

	// Sentiment color mapping
	const sentimentColors: Record<string, string> = {
		very_positive: '#10b981',
		positive: '#84cc16',
		neutral: '#a3a3a3',
		negative: '#f59e0b',
		very_negative: '#ef4444'
	};

	// Get sentiment color
	const getSentimentColor = (sentiment: string): string => {
		return sentimentColors[sentiment] || '#a3a3a3';
	};

	// Get polarity position (0-100%)
	const getPolarityPosition = (polarity: number): number => {
		// Convert -1 to 1 range to 0 to 100%
		return ((polarity + 1) / 2) * 100;
	};

	// Format sentiment text
	const formatSentiment = (sentiment: string): string => {
		return sentiment.split('_').map(word =>
			word.charAt(0).toUpperCase() + word.slice(1)
		).join(' ');
	};
</script>

<div class="sentiment-indicator" role="region" aria-label="Customer sentiment analysis">
	{#if sentiment}
		<!-- Header -->
		<div class="header">
			<h3 class="title">Customer Sentiment</h3>
			{#if trend && trend.alert_level !== 'none'}
				<span class="alert-badge" role="alert" aria-live="assertive"
					class:high={trend.alert_level === 'high'}
					class:medium={trend.alert_level === 'medium'}
					class:low={trend.alert_level === 'low'}>
					<span aria-hidden="true">⚠</span> {trend.alert_level.toUpperCase()}
					<span class="sr-only">Alert: {trend.alert_level} sentiment level detected</span>
				</span>
			{/if}
		</div>

		<!-- Current Sentiment -->
		<div class="current-sentiment" role="status" aria-live="polite" aria-atomic="true" aria-label="Current sentiment: {formatSentiment(sentiment.sentiment)}">
			<div class="sentiment-label">
				<span class="sentiment-text" style="color: {getSentimentColor(sentiment.sentiment)}">
					{formatSentiment(sentiment.sentiment)}
				</span>
				<span class="confidence">({Math.round(sentiment.confidence * 100)}% confident)</span>
				<span class="sr-only">
					Customer sentiment is {formatSentiment(sentiment.sentiment)} with {Math.round(sentiment.confidence * 100)} percent confidence
				</span>
			</div>

			<!-- Emotions -->
			<div class="emotions" role="list" aria-label="Detected emotions">
				{#each sentiment.emotions as emotion}
					<span class="emotion-badge" role="listitem" aria-label="{emotion} emotion" title={emotion}>
						<span aria-hidden="true">{emotionIcons[emotion] || '😐'}</span>
					</span>
				{/each}
			</div>
		</div>

		<!-- Polarity Bar -->
		<div class="polarity-bar" role="group" aria-label="Sentiment polarity indicator">
			<div class="polarity-labels" aria-hidden="true">
				<span class="label-negative">Negative</span>
				<span class="label-neutral">Neutral</span>
				<span class="label-positive">Positive</span>
			</div>
			<div class="polarity-track" role="img" aria-label="Polarity score: {sentiment.polarity_score.toFixed(2)} out of range -1 to 1">
				<div class="polarity-fill" style="width: {getPolarityPosition(sentiment.polarity_score)}%;
					background: {getSentimentColor(sentiment.sentiment)}" aria-hidden="true"></div>
				<div class="polarity-indicator" style="left: {getPolarityPosition(sentiment.polarity_score)}%;
					background: {getSentimentColor(sentiment.sentiment)}" aria-hidden="true"></div>
			</div>
			<div class="polarity-value" role="status">
				Score: {sentiment.polarity_score.toFixed(2)}
				<span class="sr-only">
					Polarity score is {sentiment.polarity_score.toFixed(2)}, ranging from -1 (very negative) to 1 (very positive)
				</span>
			</div>
		</div>

		<!-- Intensity Meter -->
		<div class="intensity-meter" role="group" aria-label="Sentiment intensity meter">
			<span class="intensity-label" id="intensity-label">Intensity:</span>
			<div class="intensity-bar" role="progressbar"
				aria-labelledby="intensity-label"
				aria-valuenow={Math.round(sentiment.intensity * 100)}
				aria-valuemin="0"
				aria-valuemax="100"
				aria-valuetext="{Math.round(sentiment.intensity * 100)} percent">
				<div class="intensity-fill" style="width: {sentiment.intensity * 100}%;
					background: {getSentimentColor(sentiment.sentiment)}" aria-hidden="true"></div>
			</div>
			<span class="intensity-value">{Math.round(sentiment.intensity * 100)}%</span>
		</div>

		<!-- Trend Information -->
		{#if trend}
			<div class="trend-info" role="group" aria-label="Sentiment trend information">
				<div class="trend-item">
					<span class="trend-label">Trend:</span>
					<span class="trend-value" role="status" aria-live="polite"
						class:improving={trend.is_improving}
						class:declining={!trend.is_improving}>
						<span aria-hidden="true">{trend.is_improving ? '📈' : '📉'}</span>
						{trend.is_improving ? 'Improving' : 'Declining'}
						<span class="sr-only">
							Sentiment trend is {trend.is_improving ? 'improving' : 'declining'}
						</span>
					</span>
				</div>
				<div class="trend-item">
					<span class="trend-label">Avg Polarity:</span>
					<span class="trend-value" role="status">{trend.average_polarity.toFixed(2)}</span>
				</div>
				<div class="trend-item">
					<span class="trend-label">Changes:</span>
					<span class="trend-value" role="status">{trend.sentiment_changes}</span>
				</div>
			</div>
		{/if}

		<!-- Last Updated -->
		<div class="footer" role="contentinfo">
			<span class="speaker-badge">
				<span aria-hidden="true">{sentiment.speaker === 'customer' ? '👤' : '👨‍💼'}</span>
				{sentiment.speaker === 'customer' ? 'Customer' : 'Agent'}
			</span>
			<time class="timestamp" datetime={new Date(sentiment.timestamp).toISOString()}>
				{new Date(sentiment.timestamp).toLocaleTimeString()}
			</time>
		</div>
	{:else}
		<div class="no-data" role="status" aria-live="polite">
			<span class="icon" aria-hidden="true">😐</span>
			<p>No sentiment data yet</p>
			<p class="hint">Sentiment will appear once the conversation starts</p>
		</div>
	{/if}
</div>

<style>
	.sentiment-indicator {
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal);
		padding: 1.25rem;
		color: hsl(var(--foreground));
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.title {
		font-size: 1.1rem;
		font-weight: 900;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.alert-badge {
		padding: 0.35rem 0.6rem;
		border: 2px solid hsl(var(--border));
		font-size: 0.8rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		box-shadow: var(--shadow-brutal-subtle);
		background: hsl(var(--card));
		color: hsl(var(--foreground));
	}

	.alert-badge.low { background: hsl(var(--accent) / 0.3); }
	.alert-badge.medium { background: hsl(var(--accent) / 0.5); }
	.alert-badge.high { background: var(--color-system-red); color: #000; animation: pulse-alert 2s infinite; }

	.current-sentiment { margin-bottom: 0.5rem; }

	.sentiment-label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.35rem;
	}

	.sentiment-text { font-size: 1.25rem; font-weight: 900; }
	.confidence { font-size: 0.9rem; color: hsl(var(--muted-foreground)); }

	.emotions { display: flex; gap: 0.5rem; }
	.emotion-badge { font-size: 1.3rem; }

	.polarity-bar { margin: 1rem 0; }

	.polarity-labels {
		display: flex;
		justify-content: space-between;
		font-size: 0.8rem;
		color: hsl(var(--muted-foreground));
		margin-bottom: 0.35rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		font-weight: 800;
	}

	.polarity-track {
		position: relative;
		height: 14px;
		background: hsl(var(--secondary));
		border: 2px solid hsl(var(--border));
		box-shadow: var(--shadow-brutal-subtle);
		overflow: hidden;
		margin-bottom: 0.35rem;
	}

	.polarity-fill {
		position: absolute;
		left: 0;
		top: 0;
		height: 100%;
		background: hsl(var(--primary));
		opacity: 0.5;
		transition: width 0.2s linear;
	}

	.polarity-indicator {
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
		width: 16px;
		height: 16px;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
		transition: left 0.2s linear;
	}

	.polarity-value { text-align: center; font-size: 0.9rem; font-weight: 900; }

	.intensity-meter { display: flex; align-items: center; gap: 0.75rem; margin: 1rem 0; }
	.intensity-label { font-size: 0.85rem; font-weight: 800; color: hsl(var(--muted-foreground)); min-width: 70px; text-transform: uppercase; letter-spacing: 0.04em; }
	.intensity-bar { flex: 1; height: 10px; background: hsl(var(--secondary)); border: 2px solid hsl(var(--border)); box-shadow: var(--shadow-brutal-subtle); }
	.intensity-fill { height: 100%; transition: width 0.2s linear; background: hsl(var(--primary)); }
	.intensity-value { font-size: 0.9rem; font-weight: 900; color: hsl(var(--foreground)); min-width: 40px; text-align: right; }

	.trend-info {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.75rem;
		margin: 1rem 0;
		padding: 0.75rem;
		border: 2px solid hsl(var(--border));
		background: hsl(var(--card));
		box-shadow: var(--shadow-brutal-subtle);
	}

	.trend-item { display: flex; flex-direction: column; gap: 0.25rem; }
	.trend-label { font-size: 0.8rem; color: hsl(var(--muted-foreground)); text-transform: uppercase; letter-spacing: 0.04em; font-weight: 800; }
	.trend-value { font-size: 0.95rem; font-weight: 900; }
	.trend-value.improving { color: var(--color-terminal-green); }
	.trend-value.declining { color: var(--color-system-red); }

	.footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 1rem;
		border-top: 2px solid hsl(var(--border));
		font-size: 0.9rem;
		color: hsl(var(--muted-foreground));
	}

	.speaker-badge { font-weight: 800; text-transform: uppercase; }
	.timestamp { font-variant-numeric: tabular-nums; }

	.no-data {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		text-align: center;
		color: hsl(var(--muted-foreground));
		border: 2px dashed hsl(var(--border));
	}

	.no-data .icon { font-size: 3rem; margin-bottom: 1rem; }
	.no-data p { margin: 0.25rem 0; }
	.no-data .hint { font-size: 0.85rem; color: hsl(var(--muted-foreground)); }

	@keyframes pulse-alert {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.7; }
	}

	@media (max-width: 768px) {
		.trend-info { grid-template-columns: 1fr; }
	}
</style>


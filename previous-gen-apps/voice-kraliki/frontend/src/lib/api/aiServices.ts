/**
 * AI Services API Client
 *
 * Provides typed API calls to backend AI services:
 * - Transcription management
 * - Call summarization
 * - Agent assistance
 * - Sentiment analysis
 */

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export interface TranscriptionConfig {
	language?: 'en' | 'es' | 'cs' | 'de' | 'fr';
	enable_interim_results?: boolean;
	enable_speaker_detection?: boolean;
	enable_punctuation?: boolean;
}

export interface TranscriptionSegment {
	id: string;
	session_id: string;
	text: string;
	speaker: 'agent' | 'customer' | 'system';
	confidence: number;
	is_final: boolean;
	timestamp: string;
}

export interface SummarizationConfig {
	language?: string;
	include_action_items?: boolean;
	include_sentiment?: boolean;
	include_topics?: boolean;
	max_summary_length?: number;
}

export interface CallSummary {
	session_id: string;
	summary: string;
	key_points: string[];
	action_items: Array<{
		description: string;
		priority: 'low' | 'medium' | 'high';
		due_date?: string;
		assigned_to?: string;
	}>;
	outcome: 'resolved' | 'escalated' | 'pending' | 'callback_required';
	customer_sentiment: string;
	agent_performance_score: number;
	topics: string[];
	duration_seconds: number;
	timestamp: string;
}

export interface AssistanceConfig {
	enable_suggestions?: boolean;
	enable_knowledge_base?: boolean;
	enable_compliance?: boolean;
	enable_coaching?: boolean;
	suggestion_threshold?: number;
	max_suggestions?: number;
}

export interface AssistanceSuggestion {
	id: string;
	session_id: string;
	type: 'suggested_response' | 'knowledge_article' | 'compliance_warning' | 'performance_tip' | 'escalation_guide';
	priority: 'low' | 'medium' | 'high' | 'urgent';
	title: string;
	content: string;
	confidence: number;
	timestamp: string;
	context: Record<string, unknown>;
}

export interface SentimentConfig {
	enable_real_time?: boolean;
	enable_emotions?: boolean;
	alert_on_negative?: boolean;
	negative_threshold?: number;
	track_trends?: boolean;
}

export interface SentimentAnalysis {
	id: string;
	session_id: string;
	sentiment: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative';
	emotions: string[];
	confidence: number;
	polarity_score: number;
	intensity: number;
	timestamp: string;
	text_analyzed: string;
	speaker: string;
}

export interface SentimentTrend {
	session_id: string;
	current_sentiment: string;
	average_polarity: number;
	sentiment_changes: number;
	is_improving: boolean;
	alert_level: 'none' | 'low' | 'medium' | 'high';
}

// ============================================================================
// API Functions - Transcription
// ============================================================================

export async function startTranscription(sessionId: string, config: TranscriptionConfig): Promise<void> {
	const response = await fetch(`${API_BASE}/ai/transcription/start`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ session_id: sessionId, config })
	});

	if (!response.ok) {
		throw new Error(`Failed to start transcription: ${response.statusText}`);
	}
}

export async function stopTranscription(sessionId: string): Promise<void> {
	const response = await fetch(`${API_BASE}/ai/transcription/stop?session_id=${sessionId}`, {
		method: 'POST'
	});

	if (!response.ok) {
		throw new Error(`Failed to stop transcription: ${response.statusText}`);
	}
}

export async function addTranscription(
	sessionId: string,
	text: string,
	speaker: 'agent' | 'customer' | 'system',
	confidence = 1.0,
	isFinal = true
): Promise<TranscriptionSegment> {
	const response = await fetch(`${API_BASE}/ai/transcription/add`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			session_id: sessionId,
			text,
			speaker,
			confidence,
			is_final: isFinal
		})
	});

	if (!response.ok) {
		throw new Error(`Failed to add transcription: ${response.statusText}`);
	}

	return response.json();
}

export async function getTranscriptionHistory(sessionId: string, limit?: number): Promise<TranscriptionSegment[]> {
	const url = new URL(`${API_BASE}/ai/transcription/history/${sessionId}`);
	if (limit) url.searchParams.set('limit', limit.toString());

	const response = await fetch(url.toString());

	if (!response.ok) {
		throw new Error(`Failed to get transcription history: ${response.statusText}`);
	}

	return response.json();
}

export async function getFullTranscript(sessionId: string, includeInterim = false): Promise<{ session_id: string; transcript: string }> {
	const url = new URL(`${API_BASE}/ai/transcription/full/${sessionId}`);
	url.searchParams.set('include_interim', includeInterim.toString());

	const response = await fetch(url.toString());

	if (!response.ok) {
		throw new Error(`Failed to get full transcript: ${response.statusText}`);
	}

	return response.json();
}

export async function getTranscriptionStats(sessionId: string): Promise<Record<string, unknown>> {
	const response = await fetch(`${API_BASE}/ai/transcription/stats/${sessionId}`);

	if (!response.ok) {
		throw new Error(`Failed to get transcription stats: ${response.statusText}`);
	}

	return response.json();
}

// ============================================================================
// API Functions - Summarization
// ============================================================================

export async function generateSummary(sessionId: string, transcript: string, config: SummarizationConfig): Promise<CallSummary> {
	const response = await fetch(`${API_BASE}/ai/summarization/generate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ session_id: sessionId, transcript, config })
	});

	if (!response.ok) {
		throw new Error(`Failed to generate summary: ${response.statusText}`);
	}

	return response.json();
}

export async function getSummary(sessionId: string): Promise<CallSummary> {
	const response = await fetch(`${API_BASE}/ai/summarization/${sessionId}`);

	if (!response.ok) {
		throw new Error(`Failed to get summary: ${response.statusText}`);
	}

	return response.json();
}

// ============================================================================
// API Functions - Agent Assistance
// ============================================================================

export async function startAssistance(sessionId: string, config: AssistanceConfig): Promise<void> {
	const response = await fetch(`${API_BASE}/ai/assistance/start`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ session_id: sessionId, config })
	});

	if (!response.ok) {
		throw new Error(`Failed to start assistance: ${response.statusText}`);
	}
}

export async function stopAssistance(sessionId: string): Promise<void> {
	const response = await fetch(`${API_BASE}/ai/assistance/stop?session_id=${sessionId}`, {
		method: 'POST'
	});

	if (!response.ok) {
		throw new Error(`Failed to stop assistance: ${response.statusText}`);
	}
}

export async function getAssistance(sessionId: string, transcript: string, context: Record<string, unknown> = {}): Promise<AssistanceSuggestion[]> {
	const response = await fetch(`${API_BASE}/ai/assistance/analyze`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ session_id: sessionId, transcript, context })
	});

	if (!response.ok) {
		throw new Error(`Failed to get assistance: ${response.statusText}`);
	}

	return response.json();
}

export async function getAssistanceHistory(sessionId: string, limit?: number): Promise<AssistanceSuggestion[]> {
	const url = new URL(`${API_BASE}/ai/assistance/history/${sessionId}`);
	if (limit) url.searchParams.set('limit', limit.toString());

	const response = await fetch(url.toString());

	if (!response.ok) {
		throw new Error(`Failed to get assistance history: ${response.statusText}`);
	}

	return response.json();
}

// ============================================================================
// API Functions - Sentiment Analysis
// ============================================================================

export async function startSentimentAnalysis(sessionId: string, config: SentimentConfig): Promise<void> {
	const response = await fetch(`${API_BASE}/ai/sentiment/start`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ session_id: sessionId, config })
	});

	if (!response.ok) {
		throw new Error(`Failed to start sentiment analysis: ${response.statusText}`);
	}
}

export async function stopSentimentAnalysis(sessionId: string): Promise<void> {
	const response = await fetch(`${API_BASE}/ai/sentiment/stop?session_id=${sessionId}`, {
		method: 'POST'
	});

	if (!response.ok) {
		throw new Error(`Failed to stop sentiment analysis: ${response.statusText}`);
	}
}

export async function analyzeSentiment(sessionId: string, text: string, speaker: string): Promise<SentimentAnalysis> {
	const response = await fetch(`${API_BASE}/ai/sentiment/analyze`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ session_id: sessionId, text, speaker })
	});

	if (!response.ok) {
		throw new Error(`Failed to analyze sentiment: ${response.statusText}`);
	}

	return response.json();
}

export async function getSentimentTrend(sessionId: string): Promise<SentimentTrend> {
	const response = await fetch(`${API_BASE}/ai/sentiment/trend/${sessionId}`);

	if (!response.ok) {
		throw new Error(`Failed to get sentiment trend: ${response.statusText}`);
	}

	return response.json();
}

export async function getSentimentHistory(sessionId: string, limit?: number): Promise<SentimentAnalysis[]> {
	const url = new URL(`${API_BASE}/ai/sentiment/history/${sessionId}`);
	if (limit) url.searchParams.set('limit', limit.toString());

	const response = await fetch(url.toString());

	if (!response.ok) {
		throw new Error(`Failed to get sentiment history: ${response.statusText}`);
	}

	return response.json();
}

export async function getSentimentAlerts(sessionId: string): Promise<Array<Record<string, unknown>>> {
	const response = await fetch(`${API_BASE}/ai/sentiment/alerts/${sessionId}`);

	if (!response.ok) {
		throw new Error(`Failed to get sentiment alerts: ${response.statusText}`);
	}

	return response.json();
}

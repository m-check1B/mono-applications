import { apiDelete, apiGet, apiPatch, apiPost } from '$lib/utils/api';

// Analytics interfaces matching backend models
export interface CallMetric {
	call_id: string;
	session_id: string;
	provider_id: string;
	agent_id?: string;
	start_time: string;
	end_time?: string;
	duration?: number;
	outcome?: 'success' | 'failed' | 'abandoned' | 'timeout';
	// Quality metrics
	average_sentiment?: number;
	transcription_accuracy?: number;
	audio_quality_score?: number;
	// Interaction metrics
	agent_messages?: number;
	customer_messages?: number;
	ai_suggestions_used?: number;
	compliance_warnings?: number;
	// Metadata
	tags?: string[];
	notes?: string;
	created_at: string;
	updated_at: string;
}

export interface AnalyticsSummary {
	total_calls: number;
	successful_calls: number;
	failed_calls: number;
	abandoned_calls: number;
	timeout_calls: number;
	average_call_duration: number;
	success_rate: number;
	// Quality metrics
	average_sentiment: number;
	average_transcription_accuracy: number;
	average_audio_quality: number;
	// Interaction metrics
	total_agent_messages: number;
	total_customer_messages: number;
	total_ai_suggestions: number;
	total_compliance_warnings: number;
	// Provider performance
	provider_performance: Record<string, {
		total_calls: number;
		successful_calls: number;
		average_latency: number;
		audio_quality_score: number;
		uptime_percentage: number;
		error_rate: number;
	}>;
	// Agent performance
	agent_performance: Record<string, {
		total_calls: number;
		successful_calls: number;
		failed_calls: number;
		average_call_duration: number;
		average_customer_sentiment: number;
		ai_suggestions_usage: number;
		compliance_warnings: number;
	}>;
	// Time series data
	time_series: Array<{
		timestamp: string;
		call_count: number;
		success_rate: number;
		average_sentiment: number;
	}>;
	// Period info
	start_time: string;
	end_time: string;
}

export type CallOutcome = 'success' | 'failed' | 'abandoned' | 'timeout';

// Request interfaces
export interface StartCallTrackingRequest {
	call_id: string;
	session_id: string;
	provider_id: string;
	agent_id?: string;
}

export interface UpdateCallMetricRequest {
	call_id: string;
	average_sentiment?: number;
	transcription_accuracy?: number;
	audio_quality_score?: number;
	agent_messages?: number;
	customer_messages?: number;
	ai_suggestions_used?: number;
	compliance_warnings?: number;
	tags?: string[];
	notes?: string;
}

export interface EndCallTrackingRequest {
	call_id: string;
	outcome: CallOutcome;
}

export interface GetAnalyticsSummaryRequest {
	start_time?: string;
	end_time?: string;
}

// Response interfaces
export interface CallTrackingResponse {
	status: string;
	message: string;
	call_metric?: CallMetric;
}

export interface AnalyticsSummaryResponse {
	status: string;
	summary: AnalyticsSummary;
}

export interface CallMetricResponse {
	status: string;
	metric?: CallMetric;
}

export interface ActiveCallsResponse {
	status: string;
	active_calls: string[];
	count: number;
}

export interface CallCountsResponse {
	status: string;
	counts: Record<string, number>;
}

export interface AgentPerformanceResponse {
	status: string;
	agent_id: string;
	performance: {
		total_calls: number;
		successful_calls: number;
		failed_calls: number;
		average_call_duration: number;
		average_customer_sentiment: number;
		ai_suggestions_usage: number;
		compliance_warnings: number;
	};
}

export interface ProviderPerformanceResponse {
	status: string;
	provider_id: string;
	performance: {
		total_calls: number;
		successful_calls: number;
		average_latency: number;
		audio_quality_score: number;
		uptime_percentage: number;
		error_rate: number;
	};
}

export interface RealtimeMetricsResponse {
	status: string;
	timestamp: string;
	active_calls: number;
	total_calls: number;
	recent_calls_last_hour: number;
	recent_success_rate: number;
	recent_average_sentiment: number;
	recent_average_duration: number;
}

// Call Tracking Operations
export function startCallTracking(request: StartCallTrackingRequest) {
	return apiPost<CallTrackingResponse>('/analytics/calls/start', request);
}

export function updateCallMetric(request: UpdateCallMetricRequest) {
	return apiPatch<CallTrackingResponse>('/analytics/calls/update', request);
}

export function endCallTracking(request: EndCallTrackingRequest) {
	return apiPost<CallTrackingResponse>('/analytics/calls/end', request);
}

// Analytics Data Retrieval
export function getAnalyticsSummary(startTime?: string, endTime?: string) {
	const params = new URLSearchParams();
	if (startTime) params.set('start_time', startTime);
	if (endTime) params.set('end_time', endTime);
	
	const query = params.toString();
	return apiGet<AnalyticsSummaryResponse>(`/analytics/summary${query ? `?${query}` : ''}`);
}

export function getCallMetric(callId: string) {
	return apiGet<CallMetricResponse>(`/analytics/calls/${callId}`);
}

export function getActiveCalls() {
	return apiGet<ActiveCallsResponse>('/analytics/calls');
}

export function getCallCounts() {
	return apiGet<CallCountsResponse>('/analytics/counts');
}

// Performance Analytics
export function getAgentPerformance(
	agentId: string,
	startTime?: string,
	endTime?: string
) {
	const params = new URLSearchParams();
	if (startTime) params.set('start_time', startTime);
	if (endTime) params.set('end_time', endTime);
	
	const query = params.toString();
	return apiGet<AgentPerformanceResponse>(`/analytics/agents/${agentId}${query ? `?${query}` : ''}`);
}

export function getProviderPerformance(
	providerId: string,
	startTime?: string,
	endTime?: string
) {
	const params = new URLSearchParams();
	if (startTime) params.set('start_time', startTime);
	if (endTime) params.set('end_time', endTime);
	
	const query = params.toString();
	return apiGet<ProviderPerformanceResponse>(`/analytics/providers/${providerId}${query ? `?${query}` : ''}`);
}

export function getRealtimeMetrics() {
	return apiGet<RealtimeMetricsResponse>('/analytics/metrics/realtime');
}

// Utility functions for common analytics operations
export interface CallMetricsFilter {
	startTime?: string;
	endTime?: string;
	providerId?: string;
	agentId?: string;
	outcome?: CallOutcome;
}

export function getFilteredMetrics(filter: CallMetricsFilter) {
	return getAnalyticsSummary(filter.startTime, filter.endTime);
}

export function getCallSuccessRate(startTime?: string, endTime?: string) {
	return getAnalyticsSummary(startTime, endTime).then(response => ({
		success_rate: response.summary.success_rate,
		total_calls: response.summary.total_calls,
		successful_calls: response.summary.successful_calls
	}));
}

export function getAverageCallDuration(startTime?: string, endTime?: string) {
	return getAnalyticsSummary(startTime, endTime).then(response => ({
		average_duration: response.summary.average_call_duration,
		total_calls: response.summary.total_calls
	}));
}

export function getProviderComparison(providerIds: string[], startTime?: string, endTime?: string) {
	const promises = providerIds.map(providerId => 
		getProviderPerformance(providerId, startTime, endTime)
	);
	
	return Promise.all(promises).then(responses => 
		responses.map(response => ({
			provider_id: response.provider_id,
			performance: response.performance
		}))
	);
}

// Real-time monitoring utilities
export function createRealtimeMonitor(refreshInterval = 5000) {
	let intervalId: ReturnType<typeof setInterval> | null = null;
	
	const startMonitoring = (callback: (metrics: RealtimeMetricsResponse) => void) => {
		const fetchMetrics = async () => {
			try {
				const metrics = await getRealtimeMetrics();
				callback(metrics);
			} catch (error) {
				console.error('Failed to fetch realtime metrics:', error);
			}
		};
		
		// Initial fetch
		fetchMetrics();
		
		// Set up interval
		intervalId = setInterval(fetchMetrics, refreshInterval);
	};
	
	const stopMonitoring = () => {
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}
	};
	
	return {
		startMonitoring,
		stopMonitoring
	};
}
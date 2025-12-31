import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	startCallTracking,
	updateCallMetric,
	endCallTracking,
	getAnalyticsSummary,
	getCallMetric,
	getActiveCalls,
	getCallCounts,
	getAgentPerformance,
	getProviderPerformance,
	getRealtimeMetrics,
	getFilteredMetrics,
	getCallSuccessRate,
	getAverageCallDuration,
	getProviderComparison,
	createRealtimeMonitor,
} from '../analytics';
import type {
	StartCallTrackingRequest,
	UpdateCallMetricRequest,
	EndCallTrackingRequest,
	CallTrackingResponse,
	AnalyticsSummaryResponse,
	RealtimeMetricsResponse,
} from '../analytics';
import * as apiUtils from '$lib/utils/api';

// Mock the api module
vi.mock('$lib/utils/api', () => ({
	apiGet: vi.fn(),
	apiPost: vi.fn(),
	apiPatch: vi.fn(),
	apiDelete: vi.fn(),
}));

describe('Analytics Service', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.restoreAllMocks();
		vi.useRealTimers();
	});

	describe('startCallTracking', () => {
		it('should start call tracking successfully', async () => {
			const request: StartCallTrackingRequest = {
				call_id: 'call-123',
				session_id: 'session-456',
				provider_id: 'twilio-1',
				agent_id: 'agent-789'
			};

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Call tracking started',
				call_metric: {
					call_id: 'call-123',
					session_id: 'session-456',
					provider_id: 'twilio-1',
					agent_id: 'agent-789',
					start_time: '2024-01-01T12:00:00Z',
					created_at: '2024-01-01T12:00:00Z',
					updated_at: '2024-01-01T12:00:00Z'
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await startCallTracking(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/analytics/calls/start', request);
			expect(result.status).toBe('success');
			expect(result.call_metric?.call_id).toBe('call-123');
		});

		it('should handle errors when starting call tracking', async () => {
			const request: StartCallTrackingRequest = {
				call_id: 'call-123',
				session_id: 'session-456',
				provider_id: 'twilio-1'
			};

			const mockError = new Error('Failed to start tracking');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(startCallTracking(request)).rejects.toThrow('Failed to start tracking');
		});

		it('should track call without agent_id', async () => {
			const request: StartCallTrackingRequest = {
				call_id: 'call-123',
				session_id: 'session-456',
				provider_id: 'twilio-1'
			};

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Call tracking started',
				call_metric: {
					call_id: 'call-123',
					session_id: 'session-456',
					provider_id: 'twilio-1',
					start_time: '2024-01-01T12:00:00Z',
					created_at: '2024-01-01T12:00:00Z',
					updated_at: '2024-01-01T12:00:00Z'
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await startCallTracking(request);

			expect(result.call_metric?.agent_id).toBeUndefined();
		});
	});

	describe('updateCallMetric', () => {
		it('should update call metrics successfully', async () => {
			const request: UpdateCallMetricRequest = {
				call_id: 'call-123',
				average_sentiment: 0.8,
				transcription_accuracy: 0.95,
				audio_quality_score: 0.9,
				agent_messages: 10,
				customer_messages: 12,
				ai_suggestions_used: 3,
				compliance_warnings: 0,
				tags: ['completed', 'positive'],
				notes: 'Call went well'
			};

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Metrics updated'
			};

			vi.mocked(apiUtils.apiPatch).mockResolvedValue(mockResponse);

			const result = await updateCallMetric(request);

			expect(apiUtils.apiPatch).toHaveBeenCalledWith('/analytics/calls/update', request);
			expect(result.status).toBe('success');
		});

		it('should handle partial metric updates', async () => {
			const request: UpdateCallMetricRequest = {
				call_id: 'call-123',
				average_sentiment: 0.5
			};

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Metrics updated'
			};

			vi.mocked(apiUtils.apiPatch).mockResolvedValue(mockResponse);

			const result = await updateCallMetric(request);

			expect(result.status).toBe('success');
		});

		it('should handle update errors', async () => {
			const request: UpdateCallMetricRequest = {
				call_id: 'invalid-call',
				average_sentiment: 0.8
			};

			const mockError = new Error('Call not found');
			vi.mocked(apiUtils.apiPatch).mockRejectedValue(mockError);

			await expect(updateCallMetric(request)).rejects.toThrow('Call not found');
		});
	});

	describe('endCallTracking', () => {
		it('should end call tracking with success outcome', async () => {
			const request: EndCallTrackingRequest = {
				call_id: 'call-123',
				outcome: 'success'
			};

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Call tracking ended'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await endCallTracking(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/analytics/calls/end', request);
			expect(result.status).toBe('success');
		});

		it('should end call tracking with failed outcome', async () => {
			const request: EndCallTrackingRequest = {
				call_id: 'call-123',
				outcome: 'failed'
			};

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Call tracking ended'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await endCallTracking(request);

			expect(result.status).toBe('success');
		});

		it('should support all outcome types', async () => {
			const outcomes: Array<'success' | 'failed' | 'abandoned' | 'timeout'> =
				['success', 'failed', 'abandoned', 'timeout'];

			const mockResponse: CallTrackingResponse = {
				status: 'success',
				message: 'Call tracking ended'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			for (const outcome of outcomes) {
				const result = await endCallTracking({ call_id: 'call-123', outcome });
				expect(result.status).toBe('success');
			}

			expect(apiUtils.apiPost).toHaveBeenCalledTimes(4);
		});
	});

	describe('getAnalyticsSummary', () => {
		it('should fetch analytics summary without time filters', async () => {
			const mockSummary: AnalyticsSummaryResponse = {
				status: 'success',
				summary: {
					total_calls: 100,
					successful_calls: 85,
					failed_calls: 10,
					abandoned_calls: 3,
					timeout_calls: 2,
					average_call_duration: 180,
					success_rate: 0.85,
					average_sentiment: 0.75,
					average_transcription_accuracy: 0.92,
					average_audio_quality: 0.88,
					total_agent_messages: 1000,
					total_customer_messages: 1200,
					total_ai_suggestions: 150,
					total_compliance_warnings: 5,
					provider_performance: {},
					agent_performance: {},
					time_series: [],
					start_time: '2024-01-01T00:00:00Z',
					end_time: '2024-01-31T23:59:59Z'
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockSummary);

			const result = await getAnalyticsSummary();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/analytics/summary');
			expect(result.summary.total_calls).toBe(100);
			expect(result.summary.success_rate).toBe(0.85);
		});

		it('should fetch analytics summary with time filters', async () => {
			const startTime = '2024-01-01T00:00:00Z';
			const endTime = '2024-01-31T23:59:59Z';

			const mockSummary: AnalyticsSummaryResponse = {
				status: 'success',
				summary: {
					total_calls: 50,
					successful_calls: 45,
					failed_calls: 5,
					abandoned_calls: 0,
					timeout_calls: 0,
					average_call_duration: 200,
					success_rate: 0.9,
					average_sentiment: 0.8,
					average_transcription_accuracy: 0.95,
					average_audio_quality: 0.9,
					total_agent_messages: 500,
					total_customer_messages: 600,
					total_ai_suggestions: 75,
					total_compliance_warnings: 2,
					provider_performance: {},
					agent_performance: {},
					time_series: [],
					start_time: startTime,
					end_time: endTime
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockSummary);

			const result = await getAnalyticsSummary(startTime, endTime);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(
				`/analytics/summary?start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}`
			);
			expect(result.summary.total_calls).toBe(50);
		});

		it('should handle errors fetching summary', async () => {
			const mockError = new Error('Analytics service unavailable');
			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(getAnalyticsSummary()).rejects.toThrow('Analytics service unavailable');
		});
	});

	describe('getCallMetric', () => {
		it('should fetch call metric by ID', async () => {
			const callId = 'call-123';
			const mockResponse = {
				status: 'success',
				metric: {
					call_id: callId,
					session_id: 'session-456',
					provider_id: 'twilio-1',
					start_time: '2024-01-01T12:00:00Z',
					end_time: '2024-01-01T12:05:00Z',
					duration: 300,
					outcome: 'success' as const,
					created_at: '2024-01-01T12:00:00Z',
					updated_at: '2024-01-01T12:05:00Z'
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getCallMetric(callId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/analytics/calls/${callId}`);
			expect(result.metric?.call_id).toBe(callId);
		});

		it('should handle missing call metric', async () => {
			const callId = 'invalid-call';
			const mockError = new Error('Metric not found');

			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(getCallMetric(callId)).rejects.toThrow('Metric not found');
		});
	});

	describe('getActiveCalls', () => {
		it('should fetch active calls list', async () => {
			const mockResponse = {
				status: 'success',
				active_calls: ['call-123', 'call-456', 'call-789'],
				count: 3
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getActiveCalls();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/analytics/calls');
			expect(result.count).toBe(3);
			expect(result.active_calls).toHaveLength(3);
		});

		it('should return empty list when no active calls', async () => {
			const mockResponse = {
				status: 'success',
				active_calls: [],
				count: 0
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getActiveCalls();

			expect(result.count).toBe(0);
		});
	});

	describe('getAgentPerformance', () => {
		it('should fetch agent performance metrics', async () => {
			const agentId = 'agent-123';
			const mockResponse = {
				status: 'success',
				agent_id: agentId,
				performance: {
					total_calls: 50,
					successful_calls: 45,
					failed_calls: 5,
					average_call_duration: 180,
					average_customer_sentiment: 0.8,
					ai_suggestions_usage: 30,
					compliance_warnings: 2
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getAgentPerformance(agentId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/analytics/agents/${agentId}`);
			expect(result.agent_id).toBe(agentId);
			expect(result.performance.total_calls).toBe(50);
		});

		it('should fetch agent performance with time filters', async () => {
			const agentId = 'agent-123';
			const startTime = '2024-01-01T00:00:00Z';
			const endTime = '2024-01-31T23:59:59Z';

			const mockResponse = {
				status: 'success',
				agent_id: agentId,
				performance: {
					total_calls: 25,
					successful_calls: 23,
					failed_calls: 2,
					average_call_duration: 200,
					average_customer_sentiment: 0.85,
					ai_suggestions_usage: 15,
					compliance_warnings: 1
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getAgentPerformance(agentId, startTime, endTime);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(
				`/analytics/agents/${agentId}?start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}`
			);
			expect(result.performance.total_calls).toBe(25);
		});
	});

	describe('getProviderPerformance', () => {
		it('should fetch provider performance metrics', async () => {
			const providerId = 'twilio-1';
			const mockResponse = {
				status: 'success',
				provider_id: providerId,
				performance: {
					total_calls: 100,
					successful_calls: 95,
					average_latency: 120,
					audio_quality_score: 0.92,
					uptime_percentage: 99.5,
					error_rate: 0.05
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getProviderPerformance(providerId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/analytics/providers/${providerId}`);
			expect(result.provider_id).toBe(providerId);
			expect(result.performance.uptime_percentage).toBe(99.5);
		});
	});

	describe('getRealtimeMetrics', () => {
		it('should fetch realtime metrics', async () => {
			const mockResponse: RealtimeMetricsResponse = {
				status: 'success',
				timestamp: '2024-01-01T12:00:00Z',
				active_calls: 5,
				total_calls: 150,
				recent_calls_last_hour: 12,
				recent_success_rate: 0.92,
				recent_average_sentiment: 0.78,
				recent_average_duration: 185
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getRealtimeMetrics();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/analytics/metrics/realtime');
			expect(result.active_calls).toBe(5);
			expect(result.recent_success_rate).toBe(0.92);
		});
	});

	describe('getCallSuccessRate', () => {
		it('should calculate call success rate', async () => {
			const mockSummary: AnalyticsSummaryResponse = {
				status: 'success',
				summary: {
					total_calls: 100,
					successful_calls: 85,
					failed_calls: 15,
					abandoned_calls: 0,
					timeout_calls: 0,
					average_call_duration: 180,
					success_rate: 0.85,
					average_sentiment: 0.75,
					average_transcription_accuracy: 0.92,
					average_audio_quality: 0.88,
					total_agent_messages: 1000,
					total_customer_messages: 1200,
					total_ai_suggestions: 150,
					total_compliance_warnings: 5,
					provider_performance: {},
					agent_performance: {},
					time_series: [],
					start_time: '2024-01-01T00:00:00Z',
					end_time: '2024-01-31T23:59:59Z'
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockSummary);

			const result = await getCallSuccessRate();

			expect(result.success_rate).toBe(0.85);
			expect(result.total_calls).toBe(100);
			expect(result.successful_calls).toBe(85);
		});
	});

	describe('getAverageCallDuration', () => {
		it('should calculate average call duration', async () => {
			const mockSummary: AnalyticsSummaryResponse = {
				status: 'success',
				summary: {
					total_calls: 100,
					successful_calls: 85,
					failed_calls: 15,
					abandoned_calls: 0,
					timeout_calls: 0,
					average_call_duration: 240,
					success_rate: 0.85,
					average_sentiment: 0.75,
					average_transcription_accuracy: 0.92,
					average_audio_quality: 0.88,
					total_agent_messages: 1000,
					total_customer_messages: 1200,
					total_ai_suggestions: 150,
					total_compliance_warnings: 5,
					provider_performance: {},
					agent_performance: {},
					time_series: [],
					start_time: '2024-01-01T00:00:00Z',
					end_time: '2024-01-31T23:59:59Z'
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockSummary);

			const result = await getAverageCallDuration();

			expect(result.average_duration).toBe(240);
			expect(result.total_calls).toBe(100);
		});
	});

	describe('getProviderComparison', () => {
		it('should compare multiple providers', async () => {
			const providerIds = ['twilio-1', 'vonage-1'];

			const mockResponses = [
				{
					status: 'success',
					provider_id: 'twilio-1',
					performance: {
						total_calls: 60,
						successful_calls: 58,
						average_latency: 100,
						audio_quality_score: 0.95,
						uptime_percentage: 99.8,
						error_rate: 0.03
					}
				},
				{
					status: 'success',
					provider_id: 'vonage-1',
					performance: {
						total_calls: 40,
						successful_calls: 37,
						average_latency: 120,
						audio_quality_score: 0.90,
						uptime_percentage: 99.2,
						error_rate: 0.075
					}
				}
			];

			vi.mocked(apiUtils.apiGet)
				.mockResolvedValueOnce(mockResponses[0])
				.mockResolvedValueOnce(mockResponses[1]);

			const result = await getProviderComparison(providerIds);

			expect(result).toHaveLength(2);
			expect(result[0].provider_id).toBe('twilio-1');
			expect(result[1].provider_id).toBe('vonage-1');
		});
	});

	describe('createRealtimeMonitor', () => {
		it('should start and stop realtime monitoring', async () => {
			const mockMetrics: RealtimeMetricsResponse = {
				status: 'success',
				timestamp: '2024-01-01T12:00:00Z',
				active_calls: 5,
				total_calls: 150,
				recent_calls_last_hour: 12,
				recent_success_rate: 0.92,
				recent_average_sentiment: 0.78,
				recent_average_duration: 185
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockMetrics);

			const callback = vi.fn();
			const monitor = createRealtimeMonitor(1000);

			monitor.startMonitoring(callback);

			// Initial call
			await vi.runOnlyPendingTimersAsync();
			expect(callback).toHaveBeenCalledWith(mockMetrics);
			const initialCalls = callback.mock.calls.length;

			// Advance time and check interval call
			await vi.advanceTimersByTimeAsync(1000);
			expect(callback.mock.calls.length).toBeGreaterThan(initialCalls);

			monitor.stopMonitoring();

			const callsBeforeStop = callback.mock.calls.length;

			// Should not call after stopping
			await vi.advanceTimersByTimeAsync(1000);
			expect(callback.mock.calls.length).toBe(callsBeforeStop);
		});

		it('should handle errors in monitoring gracefully', async () => {
			const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
			const mockError = new Error('Network error');

			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			const callback = vi.fn();
			const monitor = createRealtimeMonitor(1000);

			monitor.startMonitoring(callback);

			await vi.runOnlyPendingTimersAsync();

			expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to fetch realtime metrics:', mockError);
			expect(callback).not.toHaveBeenCalled();

			monitor.stopMonitoring();
			consoleErrorSpy.mockRestore();
		});
	});
});

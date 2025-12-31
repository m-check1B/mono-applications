import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	captureConsent,
	checkConsent,
	withdrawConsent,
	getConsentRecords,
	checkRetentionCompliance,
	scheduleDataDeletion,
	getRetentionPolicies,
	exportCustomerData,
	deleteCustomerData,
	getComplianceEvents,
	detectRegion,
	batchConsentCheck,
	captureMultipleConsents,
	getCustomerConsentProfile,
	checkDataRetentionForCustomer,
	createComplianceMonitor,
	executeConsentWorkflow,
} from '../compliance';
import type {
	ConsentRequest,
	ConsentCheckRequest,
	ConsentWithdrawRequest,
	RetentionCheckRequest,
	DataExportRequest,
	ConsentCaptureResponse,
	ConsentCheckResponse,
} from '../compliance';
import * as apiUtils from '$lib/utils/api';

// Mock the api module
vi.mock('$lib/utils/api', () => ({
	apiGet: vi.fn(),
	apiPost: vi.fn(),
	apiDelete: vi.fn(),
}));

describe('Compliance Service', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.useFakeTimers();
	});

	afterEach(() => {
		vi.restoreAllMocks();
		vi.useRealTimers();
	});

	describe('captureConsent', () => {
		it('should capture consent successfully', async () => {
			const request: ConsentRequest = {
				session_id: 'session-123',
				customer_phone: '+1234567890',
				consent_type: 'recording',
				status: 'granted',
				method: 'verbal',
				metadata: { timestamp: '2024-01-01T12:00:00Z' }
			};

			const mockResponse: ConsentCaptureResponse = {
				consent_id: 'consent-123',
				status: 'success',
				timestamp: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await captureConsent(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/compliance/consent', request);
			expect(result.consent_id).toBe('consent-123');
			expect(result.status).toBe('success');
		});

		it('should handle consent capture errors', async () => {
			const request: ConsentRequest = {
				session_id: 'session-123',
				customer_phone: '+1234567890',
				consent_type: 'recording',
				status: 'granted'
			};

			const mockError = new Error('Failed to capture consent');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(captureConsent(request)).rejects.toThrow('Failed to capture consent');
		});

		it('should capture denied consent', async () => {
			const request: ConsentRequest = {
				session_id: 'session-123',
				customer_phone: '+1234567890',
				consent_type: 'marketing',
				status: 'denied'
			};

			const mockResponse: ConsentCaptureResponse = {
				consent_id: 'consent-456',
				status: 'success',
				timestamp: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await captureConsent(request);

			expect(result.consent_id).toBe('consent-456');
		});

		it('should support all consent types', async () => {
			const consentTypes = ['recording', 'transcription', 'ai_processing', 'data_storage', 'marketing', 'analytics'] as const;

			const mockResponse: ConsentCaptureResponse = {
				consent_id: 'consent-123',
				status: 'success',
				timestamp: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			for (const consentType of consentTypes) {
				const request: ConsentRequest = {
					session_id: 'session-123',
					customer_phone: '+1234567890',
					consent_type: consentType,
					status: 'granted'
				};

				const result = await captureConsent(request);
				expect(result.status).toBe('success');
			}

			expect(apiUtils.apiPost).toHaveBeenCalledTimes(6);
		});
	});

	describe('checkConsent', () => {
		it('should check consent successfully when granted', async () => {
			const request: ConsentCheckRequest = {
				customer_phone: '+1234567890',
				consent_type: 'recording',
				session_id: 'session-123'
			};

			const mockResponse: ConsentCheckResponse = {
				has_consent: true,
				customer_phone: '+1234567890',
				consent_type: 'recording',
				region: 'us',
				checked_at: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await checkConsent(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/compliance/consent/check', request);
			expect(result.has_consent).toBe(true);
			expect(result.region).toBe('us');
		});

		it('should check consent when not granted', async () => {
			const request: ConsentCheckRequest = {
				customer_phone: '+1234567890',
				consent_type: 'marketing'
			};

			const mockResponse: ConsentCheckResponse = {
				has_consent: false,
				customer_phone: '+1234567890',
				consent_type: 'marketing',
				region: 'eu',
				checked_at: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await checkConsent(request);

			expect(result.has_consent).toBe(false);
			expect(result.region).toBe('eu');
		});

		it('should handle consent check errors', async () => {
			const request: ConsentCheckRequest = {
				customer_phone: 'invalid',
				consent_type: 'recording'
			};

			const mockError = new Error('Invalid phone number');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(checkConsent(request)).rejects.toThrow('Invalid phone number');
		});
	});

	describe('withdrawConsent', () => {
		it('should withdraw consent successfully', async () => {
			const request: ConsentWithdrawRequest = {
				consent_id: 'consent-123',
				session_id: 'session-456'
			};

			const mockResponse = {
				consent_id: 'consent-123',
				status: 'withdrawn',
				timestamp: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await withdrawConsent(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/compliance/consent/withdraw', request);
			expect(result.status).toBe('withdrawn');
		});

		it('should handle withdraw errors', async () => {
			const request: ConsentWithdrawRequest = {
				consent_id: 'invalid-consent'
			};

			const mockError = new Error('Consent not found');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(withdrawConsent(request)).rejects.toThrow('Consent not found');
		});
	});

	describe('getConsentRecords', () => {
		it('should fetch consent records for a customer', async () => {
			const customerPhone = '+1234567890';

			const mockResponse = {
				records: [
					{
						id: 'consent-1',
						session_id: 'session-123',
						customer_phone: customerPhone,
						region: 'us' as const,
						consent_type: 'recording' as const,
						status: 'granted' as const,
						method: 'verbal',
						granted_at: '2024-01-01T12:00:00Z'
					}
				],
				count: 1,
				filters: { customer_phone: customerPhone }
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getConsentRecords(customerPhone);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/compliance/consent?customer_phone=${encodeURIComponent(customerPhone)}`);
			expect(result.records).toHaveLength(1);
			expect(result.count).toBe(1);
		});

		it('should fetch consent records with multiple filters', async () => {
			const customerPhone = '+1234567890';
			const sessionId = 'session-123';
			const consentType = 'recording';

			const mockResponse = {
				records: [],
				count: 0,
				filters: {
					customer_phone: customerPhone,
					session_id: sessionId,
					consent_type: consentType as any
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			await getConsentRecords(customerPhone, sessionId, 'recording');

			expect(apiUtils.apiGet).toHaveBeenCalledWith(
				`/api/compliance/consent?customer_phone=${encodeURIComponent(customerPhone)}&session_id=${sessionId}&consent_type=recording`
			);
		});

		it('should handle empty consent records', async () => {
			const mockResponse = {
				records: [],
				count: 0,
				filters: {}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getConsentRecords();

			expect(result.records).toHaveLength(0);
		});
	});

	describe('checkRetentionCompliance', () => {
		it('should check retention compliance successfully', async () => {
			const request: RetentionCheckRequest = {
				customer_phone: '+1234567890',
				data_type: 'call_recording',
				created_at: '2024-01-01T00:00:00Z'
			};

			const mockResponse = {
				can_retain: true,
				customer_phone: '+1234567890',
				data_type: 'call_recording',
				region: 'us' as const,
				created_at: '2024-01-01T00:00:00Z',
				checked_at: '2024-01-15T12:00:00Z',
				policy: {
					retention_days: 90,
					auto_delete: true,
					requires_consent: true,
					anonymize_after_retention: true
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await checkRetentionCompliance(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/compliance/retention/check', request);
			expect(result.can_retain).toBe(true);
			expect(result.policy?.retention_days).toBe(90);
		});

		it('should indicate when data cannot be retained', async () => {
			const request: RetentionCheckRequest = {
				customer_phone: '+1234567890',
				data_type: 'call_recording',
				created_at: '2023-01-01T00:00:00Z'
			};

			const mockResponse = {
				can_retain: false,
				customer_phone: '+1234567890',
				data_type: 'call_recording',
				region: 'eu' as const,
				created_at: '2023-01-01T00:00:00Z',
				checked_at: '2024-01-15T12:00:00Z',
				policy: {
					retention_days: 30,
					auto_delete: true,
					requires_consent: true,
					anonymize_after_retention: true
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await checkRetentionCompliance(request);

			expect(result.can_retain).toBe(false);
		});
	});

	describe('scheduleDataDeletion', () => {
		it('should schedule data deletion successfully', async () => {
			const request: RetentionCheckRequest = {
				customer_phone: '+1234567890',
				data_type: 'call_recording',
				created_at: '2023-01-01T00:00:00Z'
			};

			const mockResponse = {
				customer_phone: '+1234567890',
				data_type: 'call_recording',
				deletion_date: '2024-02-01T00:00:00Z',
				scheduled_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await scheduleDataDeletion(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/compliance/retention/schedule', request);
			expect(result.deletion_date).toBe('2024-02-01T00:00:00Z');
		});
	});

	describe('getRetentionPolicies', () => {
		it('should fetch all retention policies', async () => {
			const mockResponse = {
				policies: {
					'us_call_recording': {
						region: 'us' as const,
						data_type: 'call_recording',
						retention_days: 90,
						auto_delete: true,
						requires_consent: true,
						anonymize_after_retention: true
					},
					'eu_call_recording': {
						region: 'eu' as const,
						data_type: 'call_recording',
						retention_days: 30,
						auto_delete: true,
						requires_consent: true,
						anonymize_after_retention: true
					}
				},
				count: 2
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getRetentionPolicies();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/api/compliance/policies');
			expect(result.count).toBe(2);
		});

		it('should fetch retention policies for specific region', async () => {
			const region = 'eu';

			const mockResponse = {
				policies: {
					'eu_call_recording': {
						region: 'eu' as const,
						data_type: 'call_recording',
						retention_days: 30,
						auto_delete: true,
						requires_consent: true,
						anonymize_after_retention: true
					}
				},
				count: 1,
				region_filter: 'eu' as const
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getRetentionPolicies('eu');

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/compliance/policies?region=${region}`);
			expect(result.region_filter).toBe('eu');
		});
	});

	describe('exportCustomerData', () => {
		it('should export customer data successfully', async () => {
			const request: DataExportRequest = {
				customer_phone: '+1234567890',
				format: 'json'
			};

			const mockResponse = {
				customer_phone: '+1234567890',
				data: {
					consents: [],
					calls: [],
					recordings: []
				},
				exported_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await exportCustomerData(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/compliance/export', request);
			expect(result.customer_phone).toBe('+1234567890');
		});

		it('should export customer data with default format', async () => {
			const request: DataExportRequest = {
				customer_phone: '+1234567890'
			};

			const mockResponse = {
				customer_phone: '+1234567890',
				data: {},
				exported_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await exportCustomerData(request);

			expect(result.customer_phone).toBe('+1234567890');
		});
	});

	describe('deleteCustomerData', () => {
		it('should delete customer data successfully', async () => {
			const customerPhone = '+1234567890';

			const mockResponse = {
				customer_phone: customerPhone,
				status: 'deleted',
				timestamp: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiDelete).mockResolvedValue(mockResponse);

			const result = await deleteCustomerData(customerPhone);

			expect(apiUtils.apiDelete).toHaveBeenCalledWith(`/api/compliance/customer/${customerPhone}`);
			expect(result.status).toBe('deleted');
		});

		it('should handle deletion errors', async () => {
			const customerPhone = 'invalid';

			const mockError = new Error('Customer not found');
			vi.mocked(apiUtils.apiDelete).mockRejectedValue(mockError);

			await expect(deleteCustomerData(customerPhone)).rejects.toThrow('Customer not found');
		});
	});

	describe('getComplianceEvents', () => {
		it('should fetch compliance events with default limit', async () => {
			const mockResponse = {
				events: [
					{
						id: 'event-1',
						event_type: 'consent_captured',
						session_id: 'session-123',
						customer_phone: '+1234567890',
						region: 'us' as const,
						timestamp: '2024-01-15T12:00:00Z',
						details: {},
						user_id: 'user-123'
					}
				],
				count: 1,
				filters: { limit: 100 }
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getComplianceEvents();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/api/compliance/events?limit=100');
			expect(result.events).toHaveLength(1);
		});

		it('should fetch compliance events with filters', async () => {
			const customerPhone = '+1234567890';
			const sessionId = 'session-123';
			const eventType = 'consent_captured';

			const mockResponse = {
				events: [],
				count: 0,
				filters: {
					customer_phone: customerPhone,
					session_id: sessionId,
					event_type: eventType,
					limit: 50
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			await getComplianceEvents(customerPhone, sessionId, eventType, 50);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(
				`/api/compliance/events?limit=50&customer_phone=${encodeURIComponent(customerPhone)}&session_id=${sessionId}&event_type=${eventType}`
			);
		});
	});

	describe('detectRegion', () => {
		it('should detect region from phone number', async () => {
			const phoneNumber = '+1234567890';

			const mockResponse = {
				phone_number: phoneNumber,
				region: 'us' as const,
				detected_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await detectRegion(phoneNumber);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/compliance/region/${phoneNumber}`);
			expect(result.region).toBe('us');
		});

		it('should detect EU region', async () => {
			const phoneNumber = '+44123456789';

			const mockResponse = {
				phone_number: phoneNumber,
				region: 'eu' as const,
				detected_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await detectRegion(phoneNumber);

			expect(result.region).toBe('eu');
		});
	});

	describe('batchConsentCheck', () => {
		it('should check multiple consents in batch', async () => {
			const requests = [
				{
					customer_phone: '+1234567890',
					consent_type: 'recording' as const
				},
				{
					customer_phone: '+1234567890',
					consent_type: 'transcription' as const
				}
			];

			const mockResponses: ConsentCheckResponse[] = [
				{
					has_consent: true,
					customer_phone: '+1234567890',
					consent_type: 'recording',
					region: 'us',
					checked_at: '2024-01-15T12:00:00Z'
				},
				{
					has_consent: true,
					customer_phone: '+1234567890',
					consent_type: 'transcription',
					region: 'us',
					checked_at: '2024-01-15T12:00:00Z'
				}
			];

			vi.mocked(apiUtils.apiPost)
				.mockResolvedValueOnce(mockResponses[0])
				.mockResolvedValueOnce(mockResponses[1]);

			const results = await batchConsentCheck(requests);

			expect(results).toHaveLength(2);
			expect(results[0].consent_type).toBe('recording');
			expect(results[1].consent_type).toBe('transcription');
		});
	});

	describe('captureMultipleConsents', () => {
		it('should capture multiple consent types', async () => {
			const sessionId = 'session-123';
			const customerPhone = '+1234567890';
			const consentTypes = ['recording', 'transcription', 'ai_processing'] as any;

			const mockResponse: ConsentCaptureResponse = {
				consent_id: 'consent-123',
				status: 'success',
				timestamp: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const results = await captureMultipleConsents(sessionId, customerPhone, consentTypes);

			expect(results).toHaveLength(3);
			expect(apiUtils.apiPost).toHaveBeenCalledTimes(3);
		});
	});

	describe('getCustomerConsentProfile', () => {
		it('should get customer consent profile', async () => {
			const customerPhone = '+1234567890';

			const mockResponse = {
				records: [
					{
						id: 'consent-1',
						session_id: 'session-123',
						customer_phone: customerPhone,
						region: 'us' as const,
						consent_type: 'recording' as const,
						status: 'granted' as const,
						method: 'verbal',
						granted_at: '2024-01-01T12:00:00Z'
					},
					{
						id: 'consent-2',
						session_id: 'session-123',
						customer_phone: customerPhone,
						region: 'us' as const,
						consent_type: 'transcription' as const,
						status: 'granted' as const,
						method: 'verbal',
						granted_at: '2024-01-01T12:00:00Z'
					}
				],
				count: 2,
				filters: { customer_phone: customerPhone }
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getCustomerConsentProfile(customerPhone);

			expect(result.customer_phone).toBe(customerPhone);
			expect(result.total_consents).toBe(2);
			expect(result.active_consents).toBe(2);
			expect(result.region).toBe('us');
		});
	});

	describe('checkDataRetentionForCustomer', () => {
		it('should check retention for multiple data types', async () => {
			const customerPhone = '+1234567890';
			const dataTypes = ['call_recording', 'transcription'];
			const createdAt = '2024-01-01T00:00:00Z';

			const mockResponse = {
				can_retain: true,
				customer_phone: customerPhone,
				data_type: 'call_recording',
				region: 'us' as const,
				created_at: createdAt,
				checked_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const results = await checkDataRetentionForCustomer(customerPhone, dataTypes, createdAt);

			expect(results['call_recording']).toBeDefined();
			expect(results['transcription']).toBeDefined();
			expect(apiUtils.apiPost).toHaveBeenCalledTimes(2);
		});
	});

	describe('createComplianceMonitor', () => {
		it('should start and stop compliance monitoring', async () => {
			const mockResponse = {
				events: [],
				count: 0,
				filters: { limit: 50 }
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const callback = vi.fn();
			const monitor = createComplianceMonitor(1000);

			monitor.startMonitoring(callback);

			await vi.runOnlyPendingTimersAsync();
			expect(callback).toHaveBeenCalledWith(mockResponse);
			const initialCalls = callback.mock.calls.length;

			await vi.advanceTimersByTimeAsync(1000);
			expect(callback.mock.calls.length).toBeGreaterThan(initialCalls);

			monitor.stopMonitoring();

			const callsBeforeStop = callback.mock.calls.length;

			await vi.advanceTimersByTimeAsync(1000);
			expect(callback.mock.calls.length).toBe(callsBeforeStop);
		});
	});

	describe('executeConsentWorkflow', () => {
		it('should execute consent workflow with all requirements', async () => {
			const sessionId = 'session-123';
			const customerPhone = '+1234567890';
			const config = {
				require_recording: true,
				require_transcription: true,
				require_ai_processing: true,
				require_data_storage: true,
				auto_capture: true,
				expiry_days: 365
			};

			const mockResponse: ConsentCaptureResponse = {
				consent_id: 'consent-123',
				status: 'success',
				timestamp: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const results = await executeConsentWorkflow(sessionId, customerPhone, config);

			expect(results).toHaveLength(4);
			expect(apiUtils.apiPost).toHaveBeenCalledTimes(4);
		});

		it('should handle workflow with no requirements', async () => {
			const sessionId = 'session-123';
			const customerPhone = '+1234567890';
			const config = {
				require_recording: false,
				require_transcription: false,
				require_ai_processing: false,
				require_data_storage: false,
				auto_capture: true
			};

			const results = await executeConsentWorkflow(sessionId, customerPhone, config);

			expect(results).toHaveLength(0);
			expect(apiUtils.apiPost).not.toHaveBeenCalled();
		});
	});
});

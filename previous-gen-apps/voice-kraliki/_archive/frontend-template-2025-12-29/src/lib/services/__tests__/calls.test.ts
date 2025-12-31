import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	fetchAvailableVoices,
	fetchAvailableModels,
	fetchVoiceConfig,
	fetchCampaignScript,
	updateSessionConfig,
	makeOutboundCall,
	endOutboundCall,
	fetchCallResult,
	deleteCallResult,
	updateSessionSettings,
	fetchCampaigns,
	fetchCompanies,
	importCompaniesCSV,
	fetchTelephonyStats,
} from '../calls';
import type {
	MakeCallRequest,
	MakeCallResponse,
	SessionConfigPayload,
	CallResult,
	TelephonyStats,
} from '../calls';
import * as apiUtils from '$lib/utils/api';
import * as companiesService from '../companies';

// Mock the api module and companies service
vi.mock('$lib/utils/api', () => ({
	apiGet: vi.fn(),
	apiPost: vi.fn(),
	apiDelete: vi.fn(),
	apiPatch: vi.fn(),
}));

vi.mock('../companies', () => ({
	getCompanies: vi.fn(),
	createCompany: vi.fn(),
}));

vi.mock('$lib/api/sessions', () => ({
	migrateEndpoint: vi.fn((path) => path),
}));

describe('Calls Service', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('makeOutboundCall', () => {
		it('should start a call successfully', async () => {
			const callRequest: MakeCallRequest = {
				company: {
					name: 'Test Company',
					phone: '+1234567890'
				},
				voice: 'alloy',
				model: 'gpt-4',
				language: 'en',
				audioMode: 'twilio',
				fromPhoneNumber: '+0987654321',
				aiInstructions: 'Be polite and professional',
				countryCode: 'US'
			};

			const mockResponse: MakeCallResponse = {
				callSid: 'CA123456789',
				status: 'queued',
				message: 'Call initiated successfully'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await makeOutboundCall(callRequest);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/make-call', callRequest);
			expect(result.callSid).toBe('CA123456789');
			expect(result.status).toBe('queued');
		});

		it('should handle call initiation errors', async () => {
			const callRequest: MakeCallRequest = {
				company: {
					name: 'Test Company',
					phone: 'invalid'
				},
				voice: 'alloy',
				model: 'gpt-4',
				language: 'en',
				audioMode: 'twilio',
				fromPhoneNumber: '+0987654321',
				aiInstructions: 'Test',
				countryCode: 'US'
			};

			const mockError = new Error('Invalid phone number');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(makeOutboundCall(callRequest)).rejects.toThrow('Invalid phone number');
		});

		it('should support local audio mode', async () => {
			const callRequest: MakeCallRequest = {
				company: {
					name: 'Test Company',
					phone: '+1234567890'
				},
				voice: 'echo',
				model: 'gpt-3.5-turbo',
				language: 'en',
				audioMode: 'local',
				deEssing: true,
				fromPhoneNumber: '+0987654321',
				aiInstructions: 'Test instructions',
				countryCode: 'US'
			};

			const mockResponse: MakeCallResponse = {
				callSid: 'CA987654321',
				status: 'initiated'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await makeOutboundCall(callRequest);

			expect(result.callSid).toBe('CA987654321');
			expect(apiUtils.apiPost).toHaveBeenCalledWith('/make-call', callRequest);
		});

		it('should handle insufficient credits error', async () => {
			const callRequest: MakeCallRequest = {
				company: {
					name: 'Test Company',
					phone: '+1234567890'
				},
				voice: 'alloy',
				model: 'gpt-4',
				language: 'en',
				audioMode: 'twilio',
				fromPhoneNumber: '+0987654321',
				aiInstructions: 'Test',
				countryCode: 'US'
			};

			const mockError = new Error('Insufficient credits');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(makeOutboundCall(callRequest)).rejects.toThrow('Insufficient credits');
		});
	});

	describe('endOutboundCall', () => {
		it('should end a call successfully', async () => {
			const callSid = 'CA123456789';
			const mockResponse = { success: true };

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await endOutboundCall(callSid);

			expect(apiUtils.apiPost).toHaveBeenCalledWith(`/api/sessions/${callSid}/end`, {});
			expect(result.success).toBe(true);
		});

		it('should handle ending non-existent call', async () => {
			const callSid = 'CA_INVALID';
			const mockError = new Error('Call not found');

			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(endOutboundCall(callSid)).rejects.toThrow('Call not found');
		});

		it('should handle already ended call', async () => {
			const callSid = 'CA123456789';
			const mockError = new Error('Call already ended');

			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(endOutboundCall(callSid)).rejects.toThrow('Call already ended');
		});
	});

	describe('fetchCallResult', () => {
		it('should fetch call results successfully', async () => {
			const callSid = 'CA123456789';
			const mockResult: CallResult = {
				call_summary: 'Call completed successfully',
				customer_sentiment: 'positive',
				callSid: 'CA123456789',
				targetPhone: '+1234567890',
				targetName: 'John Doe',
				status: 'completed',
				timestamp: '2024-01-01T12:00:00Z',
				duration: '180',
				callQuality: 'excellent'
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResult);

			const result = await fetchCallResult(callSid);

			expect(result.callSid).toBe(callSid);
			expect(result.customer_sentiment).toBe('positive');
			expect(result.duration).toBe('180');
		});

		it('should handle missing call results', async () => {
			const callSid = 'CA_INVALID';
			const mockError = new Error('Call result not found');

			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(fetchCallResult(callSid)).rejects.toThrow('Call result not found');
		});

		it('should include recording URL when available', async () => {
			const callSid = 'CA123456789';
			const mockResult: CallResult = {
				call_summary: 'Test call',
				customer_sentiment: 'neutral',
				callSid: 'CA123456789',
				recordingUrl: 'https://example.com/recording.mp3',
				recordingTimestamp: '2024-01-01T12:00:00Z'
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResult);

			const result = await fetchCallResult(callSid);

			expect(result.recordingUrl).toBe('https://example.com/recording.mp3');
			expect(result.recordingTimestamp).toBeDefined();
		});
	});

	describe('deleteCallResult', () => {
		it('should delete call results successfully', async () => {
			const callSid = 'CA123456789';
			const mockResponse = { success: true };

			vi.mocked(apiUtils.apiDelete).mockResolvedValue(mockResponse);

			const result = await deleteCallResult(callSid);

			expect(apiUtils.apiDelete).toHaveBeenCalled();
			expect(result.success).toBe(true);
		});

		it('should handle deletion errors', async () => {
			const callSid = 'CA123456789';
			const mockError = new Error('Failed to delete');

			vi.mocked(apiUtils.apiDelete).mockRejectedValue(mockError);

			await expect(deleteCallResult(callSid)).rejects.toThrow('Failed to delete');
		});
	});

	describe('updateSessionConfig', () => {
		it('should update session configuration successfully', async () => {
			const config: SessionConfigPayload = {
				voice: 'nova',
				model: 'gpt-4-turbo',
				language: 'en',
				fromPhoneNumber: '+1234567890',
				aiInstructions: 'Updated instructions',
				audioMode: 'twilio'
			};

			const mockResponse = { success: true, callSid: 'CA123' };

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await updateSessionConfig(config);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/v1/sessions/config', config);
			expect(result.success).toBe(true);
		});

		it('should handle invalid configuration', async () => {
			const config: SessionConfigPayload = {
				voice: '',
				model: '',
				language: 'en',
				fromPhoneNumber: '',
				aiInstructions: '',
				audioMode: 'twilio'
			};

			const mockError = new Error('Invalid configuration');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(updateSessionConfig(config)).rejects.toThrow('Invalid configuration');
		});
	});

	describe('updateSessionSettings', () => {
		it('should update session settings successfully', async () => {
			const callSid = 'CA123456789';
			const settings: Partial<SessionConfigPayload> = {
				voice: 'shimmer',
				deEssing: true
			};

			const mockResponse = { success: true };

			vi.mocked(apiUtils.apiPatch).mockResolvedValue(mockResponse);

			const result = await updateSessionSettings(callSid, settings);

			expect(apiUtils.apiPatch).toHaveBeenCalledWith(`/api/sessions/${callSid}`, settings);
			expect(result.success).toBe(true);
		});

		it('should handle partial settings updates', async () => {
			const callSid = 'CA123456789';
			const settings: Partial<SessionConfigPayload> = {
				model: 'gpt-4'
			};

			const mockResponse = { success: true };

			vi.mocked(apiUtils.apiPatch).mockResolvedValue(mockResponse);

			const result = await updateSessionSettings(callSid, settings);

			expect(result.success).toBe(true);
		});
	});

	describe('fetchAvailableVoices', () => {
		it('should fetch available voices successfully', async () => {
			const mockResponse = {
				voices: {
					alloy: { name: 'Alloy', gender: 'neutral' },
					echo: { name: 'Echo', gender: 'male' }
				},
				currentDefault: 'alloy'
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await fetchAvailableVoices();

			expect(result.voices).toBeDefined();
			expect(result.currentDefault).toBe('alloy');
		});

		it('should handle errors fetching voices', async () => {
			const mockError = new Error('Failed to fetch voices');
			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(fetchAvailableVoices()).rejects.toThrow('Failed to fetch voices');
		});
	});

	describe('fetchAvailableModels', () => {
		it('should fetch available models successfully', async () => {
			const mockResponse = {
				availableModels: {
					'gpt-4': { name: 'GPT-4' },
					'gpt-3.5-turbo': { name: 'GPT-3.5 Turbo' }
				},
				defaultModel: 'gpt-4'
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await fetchAvailableModels();

			expect(result.availableModels).toBeDefined();
			expect(result.defaultModel).toBe('gpt-4');
		});
	});

	describe('fetchTelephonyStats', () => {
		it('should fetch telephony statistics successfully', async () => {
			const mockStats: TelephonyStats = {
				total_calls: 150,
				active_calls: 5,
				completed_calls: 145,
				providers: 2,
				calls_by_provider: {
					twilio: 100,
					vonage: 50
				}
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockStats);

			const result = await fetchTelephonyStats();

			expect(result.total_calls).toBe(150);
			expect(result.active_calls).toBe(5);
			expect(result.providers).toBe(2);
		});

		it('should handle errors fetching stats', async () => {
			const mockError = new Error('Stats unavailable');
			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(fetchTelephonyStats()).rejects.toThrow('Stats unavailable');
		});
	});

	describe('importCompaniesCSV', () => {
		it('should import companies from CSV successfully', async () => {
			const csvContent = `name,phone,domain
Test Company,+1234567890,test.com
Another Company,+0987654321,another.com`;

			const mockCompany = {
				id: 1,
				name: 'Test Company',
				domain: 'test.com',
				phone_number: '+1234567890',
				is_active: true,
				settings: {},
				created_at: '2024-01-01T00:00:00Z',
				updated_at: '2024-01-01T00:00:00Z'
			};

			vi.mocked(companiesService.createCompany).mockResolvedValue(mockCompany);

			const result = await importCompaniesCSV(csvContent);

			expect(result.success).toBe(true);
			expect(result.count).toBeGreaterThan(0);
			expect(companiesService.createCompany).toHaveBeenCalled();
		});

		it('should handle empty CSV file', async () => {
			const csvContent = '';

			const result = await importCompaniesCSV(csvContent);

			expect(result.success).toBe(false);
			expect(result.error).toBe('CSV file is empty or invalid');
		});

		it('should handle CSV with missing required columns', async () => {
			const csvContent = `name
Test Company`;

			const result = await importCompaniesCSV(csvContent);

			expect(result.success).toBe(false);
			expect(result.error).toBe('CSV must have "name" and "phone" columns');
		});

		it('should handle malformed CSV data', async () => {
			const csvContent = `name,phone
Test Company,+1234567890
Invalid Company,`;

			const mockCompany = {
				id: 1,
				name: 'Test Company',
				domain: 'testcompany.com',
				phone_number: '+1234567890',
				is_active: true,
				settings: {},
				created_at: '2024-01-01T00:00:00Z',
				updated_at: '2024-01-01T00:00:00Z'
			};

			vi.mocked(companiesService.createCompany).mockResolvedValue(mockCompany);

			const result = await importCompaniesCSV(csvContent);

			expect(result.success).toBe(true);
			expect(result.count).toBe(1);
		});
	});

	describe('fetchCompanies', () => {
		it('should fetch companies and map to summary format', async () => {
			const mockCompanies = [
				{
					id: 1,
					name: 'Company A',
					domain: 'companya.com',
					phone_number: '+1234567890',
					is_active: true,
					settings: {},
					created_at: '2024-01-01T00:00:00Z',
					updated_at: '2024-01-01T00:00:00Z'
				},
				{
					id: 2,
					name: 'Company B',
					domain: 'companyb.com',
					phone_number: '+0987654321',
					is_active: false,
					settings: {},
					created_at: '2024-01-01T00:00:00Z',
					updated_at: '2024-01-01T00:00:00Z'
				}
			];

			vi.mocked(companiesService.getCompanies).mockResolvedValue(mockCompanies);

			const result = await fetchCompanies();

			expect(result).toHaveLength(2);
			expect(result[0]).toEqual({
				id: 1,
				name: 'Company A',
				phone: '+1234567890',
				status: 'active'
			});
			expect(result[1].status).toBe('inactive');
		});

		it('should handle empty companies list', async () => {
			vi.mocked(companiesService.getCompanies).mockResolvedValue([]);

			const result = await fetchCompanies();

			expect(result).toHaveLength(0);
		});
	});
});

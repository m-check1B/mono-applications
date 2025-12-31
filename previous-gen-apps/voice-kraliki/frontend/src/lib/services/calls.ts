import { apiDelete, apiGet, apiPatch, apiPost } from '$lib/utils/api';
import { migrateEndpoint } from '$lib/api/sessions';
import { getCompanies, createCompany, type Company, type CompanyCreate } from './companies';

export interface VoiceDetails {
	name?: string;
	gender?: string;
	characteristics?: string;
	description?: string;
	useCase?: string;
}

export interface AvailableVoicesResponse {
	voices: Record<string, VoiceDetails>;
	currentDefault?: string;
}

export interface AvailableModelsResponse {
	availableModels: Record<string, unknown>;
	defaultModel?: string;
}

export interface VoiceConfigResponse {
	voiceDescriptions?: Record<string, string>;
}

export interface CallResult {
	call_summary: string;
	customer_sentiment: string;
	callSid: string;
	targetPhone?: string;
	targetName?: string;
	targetPhoneNumber?: string;
	status?: string;
	timestamp?: string;
	recordingUrl?: string;
	recordingTimestamp?: string;
	duration?: string;
	callQuality?: string;
}

export interface SessionConfigPayload {
	voice: string;
	model: string;
	language: string;
	fromPhoneNumber: string;
	aiInstructions: string;
	audioMode: 'telnyx' | 'twilio' | 'local';
	deEssing?: boolean;
}

export interface MakeCallRequest {
	company: {
		name: string;
		phone: string;
	};
	voice: string;
	model: string;
	language: string;
	audioMode: 'telnyx' | 'twilio' | 'local';
	deEssing?: boolean;
	fromPhoneNumber: string;
	aiInstructions: string;
	countryCode: string;
	provider?: 'telnyx' | 'twilio';
}

export interface MakeCallResponse {
	callSid: string;
	status: string;
	message?: string;
}

export interface CampaignScriptResponse {
	id: number;
	name: string;
	language: string;
	steps: Array<Record<string, unknown>>;
	[key: string]: unknown;
}

export interface CampaignSummary {
	id: number;
	name: string;
	language?: string;
	steps?: Array<unknown>;
	stepsCount?: number;
	description?: string;
	[key: string]: unknown;
}

export interface CompanySummary {
	id: number;
	name: string;
	phone: string;
	status?: string;
	[key: string]: unknown;
}

export function fetchAvailableVoices() {
	return apiGet<AvailableVoicesResponse>(migrateEndpoint('/available-voices'));
}

export function fetchAvailableModels() {
	return apiGet<AvailableModelsResponse>(migrateEndpoint('/available-models'));
}

export function fetchVoiceConfig() {
	return apiGet<VoiceConfigResponse>(migrateEndpoint('/api/voice-config'));
}

export function fetchCampaignScript(id: number) {
	return apiGet<CampaignScriptResponse>(`/api/v1/campaign-scripts/${id}`);
}

export function updateSessionConfig(payload: SessionConfigPayload) {
	return apiPost<{ success: boolean; callSid?: string }>('/api/v1/sessions/config', payload);
}

export function makeOutboundCall(payload: MakeCallRequest) {
	return apiPost<MakeCallResponse>(migrateEndpoint('/make-call'), payload);
}

export function endOutboundCall(callSid: string) {
	return apiPost<{ success: boolean }>(`/api/sessions/${callSid}/end`, {});
}

export function fetchCallResult(callSid: string) {
	return apiGet<CallResult>(migrateEndpoint('/call-results/{callSid}', { callSid }));
}

export function deleteCallResult(callSid: string) {
	return apiDelete<{ success: boolean }>(migrateEndpoint('/call-results/{callSid}', { callSid }));
}

export function updateSessionSettings(callSid: string, payload: Partial<SessionConfigPayload>) {
	return apiPatch<{ success: boolean }>(`/api/sessions/${callSid}`, payload);
}

export function fetchCampaigns() {
	return apiGet<CampaignSummary[]>(migrateEndpoint('/campaigns'));
}

export function fetchCompanies() {
	// Use the new companies API for better data structure
	return getCompanies().then(companies => 
		companies.map(company => ({
			id: company.id,
			name: company.name,
			phone: company.phone_number || '',
			status: company.is_active ? 'active' : 'inactive'
		}))
	);
}

export interface ImportCompaniesResponse {
	success: boolean;
	count?: number;
	error?: string;
	companies?: CompanySummary[];
}

export async function importCompaniesCSV(csvContent: string): Promise<ImportCompaniesResponse> {
	try {
		// Parse CSV content
		const lines = csvContent.trim().split('\n');
		if (lines.length < 2) {
			return { success: false, error: 'CSV file is empty or invalid' };
		}

		// Get headers
		const headers = lines[0].toLowerCase().split(',').map(h => h.trim());
		const nameIndex = headers.findIndex(h => h.includes('name') || h.includes('company'));
		const phoneIndex = headers.findIndex(h => h.includes('phone') || h.includes('number'));
		const domainIndex = headers.findIndex(h => h.includes('domain') || h.includes('website'));

		if (nameIndex === -1 || phoneIndex === -1) {
			return { success: false, error: 'CSV must have "name" and "phone" columns' };
		}

		// Parse data rows and create companies using the new API
		const companies: Company[] = [];
		const errors: string[] = [];

		for (let i = 1; i < lines.length; i++) {
			try {
				const values = lines[i].split(',').map(v => v.trim());
				if (values[nameIndex] && values[phoneIndex]) {
					const companyData: CompanyCreate = {
						name: values[nameIndex].replace(/^["']|["']$/g, ''),
						domain: values[domainIndex]?.replace(/^["']|["']$/g, '') || `${values[nameIndex].toLowerCase().replace(/\s+/g, '')}.com`,
						phone_number: values[phoneIndex].replace(/^["']|["']$/g, ''),
						industry: 'Other',
						size: 'small'
					};
					
					const company = await createCompany(companyData);
					companies.push(company);
				}
			} catch (error) {
				errors.push(`Row ${i + 1}: ${error}`);
			}
		}

		if (companies.length === 0) {
			return { success: false, error: 'No valid companies found in CSV' };
		}

		return {
			success: true,
			count: companies.length,
			companies: companies.map(company => ({
				id: company.id,
				name: company.name,
				phone: company.phone_number || '',
				status: company.is_active ? 'active' : 'inactive'
			}))
		};
	} catch (error) {
		return { success: false, error: 'Failed to parse CSV file' };
	}
}

export interface TelephonyStats {
	total_calls: number;
	active_calls: number;
	completed_calls: number;
	providers: number;
	calls_by_provider: Record<string, number>;
}

export function fetchTelephonyStats() {
	return apiGet<TelephonyStats>('/api/telephony/stats');
}

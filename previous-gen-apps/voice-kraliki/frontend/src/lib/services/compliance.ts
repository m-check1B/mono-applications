import { apiDelete, apiGet, apiPost } from '$lib/utils/api';

// Compliance interfaces matching backend models
export type ConsentType = 'recording' | 'transcription' | 'ai_processing' | 'data_storage' | 'marketing' | 'analytics';
export type ConsentStatus = 'granted' | 'denied' | 'withdrawn' | 'expired' | 'pending';
export type Region = 'us' | 'eu' | 'uk' | 'ca' | 'au' | 'apac';

export interface ConsentRecord {
	id: string;
	session_id: string;
	customer_phone: string;
	region: Region;
	consent_type: ConsentType;
	status: ConsentStatus;
	method: string;
	granted_at?: string;
	denied_at?: string;
	withdrawn_at?: string;
	expires_at?: string;
	metadata?: Record<string, any>;
}

export interface RetentionPolicy {
	region: Region;
	data_type: string;
	retention_days: number;
	auto_delete: boolean;
	requires_consent: boolean;
	anonymize_after_retention: boolean;
}

export interface ComplianceEvent {
	id: string;
	event_type: string;
	session_id: string;
	customer_phone: string;
	region: Region;
	timestamp: string;
	details: Record<string, any>;
	user_id: string;
}

// Request interfaces
export interface ConsentRequest {
	session_id: string;
	customer_phone: string;
	consent_type: ConsentType;
	status: ConsentStatus;
	method?: string;
	metadata?: Record<string, any>;
}

export interface ConsentCheckRequest {
	customer_phone: string;
	consent_type: ConsentType;
	session_id?: string;
}

export interface ConsentWithdrawRequest {
	consent_id: string;
	session_id?: string;
}

export interface RetentionCheckRequest {
	customer_phone: string;
	data_type: string;
	created_at: string;
}

export interface DataExportRequest {
	customer_phone: string;
	format?: string;
}

// Response interfaces
export interface ConsentCaptureResponse {
	consent_id: string;
	status: string;
	timestamp: string;
}

export interface ConsentCheckResponse {
	has_consent: boolean;
	customer_phone: string;
	consent_type: ConsentType;
	region: Region;
	checked_at: string;
}

export interface ConsentWithdrawResponse {
	consent_id: string;
	status: string;
	timestamp: string;
}

export interface ConsentRecordsResponse {
	records: ConsentRecord[];
	count: number;
	filters: {
		customer_phone?: string;
		session_id?: string;
		consent_type?: ConsentType;
	};
}

export interface RetentionCheckResponse {
	can_retain: boolean;
	customer_phone: string;
	data_type: string;
	region: Region;
	created_at: string;
	checked_at: string;
	policy?: {
		retention_days: number;
		auto_delete: boolean;
		requires_consent: boolean;
		anonymize_after_retention: boolean;
	};
}

export interface RetentionScheduleResponse {
	customer_phone: string;
	data_type: string;
	deletion_date?: string;
	scheduled_at: string;
}

export interface CustomerDataDeleteResponse {
	customer_phone: string;
	status: string;
	timestamp: string;
}

export interface ComplianceEventsResponse {
	events: ComplianceEvent[];
	count: number;
	filters: {
		customer_phone?: string;
		session_id?: string;
		event_type?: string;
		limit: number;
	};
}

export interface RetentionPoliciesResponse {
	policies: Record<string, {
		region: Region;
		data_type: string;
		retention_days: number;
		auto_delete: boolean;
		requires_consent: boolean;
		anonymize_after_retention: boolean;
	}>;
	count: number;
	region_filter?: Region;
}

export interface RegionDetectionResponse {
	phone_number: string;
	region: Region;
	detected_at: string;
}

// Consent Management Operations
export function captureConsent(request: ConsentRequest) {
	return apiPost<ConsentCaptureResponse>('/api/compliance/consent', request);
}

export function checkConsent(request: ConsentCheckRequest) {
	return apiPost<ConsentCheckResponse>('/api/compliance/consent/check', request);
}

export function withdrawConsent(request: ConsentWithdrawRequest) {
	return apiPost<ConsentWithdrawResponse>('/api/compliance/consent/withdraw', request);
}

export function getConsentRecords(
	customerPhone?: string,
	sessionId?: string,
	consentType?: ConsentType
) {
	const params = new URLSearchParams();
	if (customerPhone) params.set('customer_phone', customerPhone);
	if (sessionId) params.set('session_id', sessionId);
	if (consentType) params.set('consent_type', consentType);
	
	const query = params.toString();
	return apiGet<ConsentRecordsResponse>(`/api/compliance/consent${query ? `?${query}` : ''}`);
}

// Retention Management Operations
export function checkRetentionCompliance(request: RetentionCheckRequest) {
	return apiPost<RetentionCheckResponse>('/api/compliance/retention/check', request);
}

export function scheduleDataDeletion(request: RetentionCheckRequest) {
	return apiPost<RetentionScheduleResponse>('/api/compliance/retention/schedule', request);
}

export function getRetentionPolicies(region?: Region) {
	const params = new URLSearchParams();
	if (region) params.set('region', region);
	
	const query = params.toString();
	return apiGet<RetentionPoliciesResponse>(`/api/compliance/policies${query ? `?${query}` : ''}`);
}

// Data Rights Operations (GDPR)
export function exportCustomerData(request: DataExportRequest) {
	return apiPost<Record<string, any>>('/api/compliance/export', request);
}

export function deleteCustomerData(customerPhone: string) {
	return apiDelete<CustomerDataDeleteResponse>(`/api/compliance/customer/${customerPhone}`);
}

// Compliance Events
export function getComplianceEvents(
	customerPhone?: string,
	sessionId?: string,
	eventType?: string,
	limit = 100
) {
	const params = new URLSearchParams({
		limit: limit.toString()
	});
	if (customerPhone) params.set('customer_phone', customerPhone);
	if (sessionId) params.set('session_id', sessionId);
	if (eventType) params.set('event_type', eventType);
	
	const query = params.toString();
	return apiGet<ComplianceEventsResponse>(`/api/compliance/events${query ? `?${query}` : ''}`);
}

// Region Detection
export function detectRegion(phoneNumber: string) {
	return apiGet<RegionDetectionResponse>(`/api/compliance/region/${phoneNumber}`);
}

// Utility functions for common compliance operations
export interface ConsentCheckBatch {
	customer_phone: string;
	consent_type: ConsentType;
	session_id?: string;
}

export function batchConsentCheck(requests: ConsentCheckBatch[]) {
	const promises = requests.map(request => checkConsent(request));
	return Promise.all(promises);
}

export function captureMultipleConsents(
	sessionId: string,
	customerPhone: string,
	consentTypes: ConsentType[],
	status: ConsentStatus = 'granted'
) {
	const promises = consentTypes.map(consentType =>
		captureConsent({
			session_id: sessionId,
			customer_phone: customerPhone,
			consent_type: consentType,
			status
		})
	);
	return Promise.all(promises);
}

export function getCustomerConsentProfile(customerPhone: string) {
	return getConsentRecords(customerPhone).then(response => {
		const consents = response.records;
		const profile: Record<ConsentType, ConsentRecord[]> = {
			recording: [],
			transcription: [],
			ai_processing: [],
			data_storage: [],
			marketing: [],
			analytics: []
		};
		
		consents.forEach(consent => {
			if (profile[consent.consent_type]) {
				profile[consent.consent_type].push(consent);
			}
		});
		
		return {
			customer_phone: customerPhone,
			total_consents: consents.length,
			active_consents: consents.filter(c => c.status === 'granted').length,
			consents_by_type: profile,
			region: consents[0]?.region || 'us'
		};
	});
}

export function checkDataRetentionForCustomer(
	customerPhone: string,
	dataTypes: string[],
	createdAt: string
) {
	const promises = dataTypes.map(dataType =>
		checkRetentionCompliance({
			customer_phone: customerPhone,
			data_type: dataType,
			created_at: createdAt
		})
	);
	
	return Promise.all(promises).then(responses => 
		responses.reduce((acc, response, index) => {
			acc[dataTypes[index]] = response;
			return acc;
		}, {} as Record<string, RetentionCheckResponse>)
	);
}

// Compliance monitoring utilities
export function createComplianceMonitor(refreshInterval = 60000) {
	let intervalId: ReturnType<typeof setInterval> | null = null;
	
	const startMonitoring = (callback: (events: ComplianceEventsResponse) => void) => {
		const fetchEvents = async () => {
			try {
				const events = await getComplianceEvents(undefined, undefined, undefined, 50);
				callback(events);
			} catch (error) {
				console.error('Failed to fetch compliance events:', error);
			}
		};
		
		// Initial fetch
		fetchEvents();
		
		// Set up interval
		intervalId = setInterval(fetchEvents, refreshInterval);
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

// Consent workflow helpers
export interface ConsentWorkflowConfig {
	require_recording: boolean;
	require_transcription: boolean;
	require_ai_processing: boolean;
	require_data_storage: boolean;
	auto_capture: boolean;
	expiry_days?: number;
}

export function executeConsentWorkflow(
	sessionId: string,
	customerPhone: string,
	config: ConsentWorkflowConfig,
	status: ConsentStatus = 'granted'
) {
	const consentTypes: ConsentType[] = [];
	
	if (config.require_recording) consentTypes.push('recording');
	if (config.require_transcription) consentTypes.push('transcription');
	if (config.require_ai_processing) consentTypes.push('ai_processing');
	if (config.require_data_storage) consentTypes.push('data_storage');
	
	if (consentTypes.length === 0) {
		return Promise.resolve([]);
	}
	
	return captureMultipleConsents(sessionId, customerPhone, consentTypes, status);
}
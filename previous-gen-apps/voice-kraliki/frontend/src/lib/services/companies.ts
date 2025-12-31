import { apiDelete, apiGet, apiPatch, apiPost } from '$lib/utils/api';

// Base Company interfaces matching backend models
export interface Company {
	id: number;
	name: string;
	domain: string;
	description?: string;
	industry?: string;
	size?: 'small' | 'medium' | 'large' | 'enterprise';
	phone_number?: string;
	email?: string;
	address?: string;
	city?: string;
	state?: string;
	country?: string;
	postal_code?: string;
	website?: string;
	logo_url?: string;
	settings: Record<string, any>;
	is_active: boolean;
	created_at: string;
	updated_at: string;
	user_count?: number;
	call_count?: number;
	script_count?: number;
}

export interface CompanyCreate {
	name: string;
	domain: string;
	description?: string;
	industry?: string;
	size?: 'small' | 'medium' | 'large' | 'enterprise';
	phone_number?: string;
	email?: string;
	address?: string;
	city?: string;
	state?: string;
	country?: string;
	postal_code?: string;
	website?: string;
	logo_url?: string;
	settings?: Record<string, any>;
}

export interface CompanyUpdate {
	name?: string;
	domain?: string;
	description?: string;
	industry?: string;
	size?: 'small' | 'medium' | 'large' | 'enterprise';
	phone_number?: string;
	email?: string;
	address?: string;
	city?: string;
	state?: string;
	country?: string;
	postal_code?: string;
	website?: string;
	logo_url?: string;
	settings?: Record<string, any>;
	is_active?: boolean;
}

export interface CompanyStats {
	company_id: number;
	total_users: number;
	active_users: number;
	total_calls: number;
	calls_this_month: number;
	total_scripts: number;
	active_scripts: number;
	average_call_duration: number;
	success_rate: number;
	cost_this_month: number;
}

export interface CompanyUser {
	id: number;
	name: string;
	email: string;
	role: string;
	is_active: boolean;
	last_login: string;
}

export interface CompanyScript {
	id: number;
	title: string;
	status: string;
	usage_count: number;
}

export interface CompanyUsersResponse {
	company_id: number;
	users: CompanyUser[];
	total: number;
}

export interface CompanyScriptsResponse {
	company_id: number;
	scripts: CompanyScript[];
	total: number;
}

export interface CompaniesListParams {
	is_active?: boolean;
	industry?: string;
	size?: string;
	search?: string;
	limit?: number;
	offset?: number;
}

export interface IndustriesResponse {
	industries: string[];
}

export interface CompanySizesResponse {
	sizes: Array<{
		value: string;
		label: string;
	}>;
}

// CRUD Operations
export function getCompanies(params?: CompaniesListParams) {
	const searchParams = new URLSearchParams();
	
	if (params?.is_active !== undefined) {
		searchParams.set('is_active', params.is_active.toString());
	}
	if (params?.industry) {
		searchParams.set('industry', params.industry);
	}
	if (params?.size) {
		searchParams.set('size', params.size);
	}
	if (params?.search) {
		searchParams.set('search', params.search);
	}
	if (params?.limit) {
		searchParams.set('limit', params.limit.toString());
	}
	if (params?.offset) {
		searchParams.set('offset', params.offset.toString());
	}

	const query = searchParams.toString();
	return apiGet<Company[]>(`/api/companies${query ? `?${query}` : ''}`);
}

export function getCompany(companyId: number) {
	return apiGet<Company>(`/api/companies/${companyId}`);
}

export function createCompany(companyData: CompanyCreate) {
	return apiPost<Company>('/api/companies', companyData);
}

export function updateCompany(companyId: number, companyData: CompanyUpdate) {
	return apiPatch<Company>(`/api/companies/${companyId}`, companyData);
}

export function deleteCompany(companyId: number) {
	return apiDelete<{ message: string }>(`/api/companies/${companyId}`);
}

// Company Statistics
export function getCompanyStats(companyId: number) {
	return apiGet<CompanyStats>(`/api/companies/${companyId}/stats`);
}

// Company Users
export function getCompanyUsers(companyId: number, limit = 20, offset = 0) {
	const params = new URLSearchParams({
		limit: limit.toString(),
		offset: offset.toString()
	});
	return apiGet<CompanyUsersResponse>(`/api/companies/${companyId}/users?${params}`);
}

// Company Scripts
export function getCompanyScripts(companyId: number, limit = 20, offset = 0) {
	const params = new URLSearchParams({
		limit: limit.toString(),
		offset: offset.toString()
	});
	return apiGet<CompanyScriptsResponse>(`/api/companies/${companyId}/scripts?${params}`);
}

// Reference Data
export function getIndustries() {
	return apiGet<IndustriesResponse>('/api/companies/industries');
}

export function getCompanySizes() {
	return apiGet<CompanySizesResponse>('/api/companies/sizes');
}

// Bulk Operations
export interface ImportCompaniesRequest {
	companies: Array<{
		name: string;
		phone: string;
		domain?: string;
		industry?: string;
		size?: string;
	}>;
}

export interface ImportCompaniesResponse {
	success: boolean;
	count?: number;
	error?: string;
	companies?: Company[];
}

export function importCompanies(request: ImportCompaniesRequest) {
	return apiPost<ImportCompaniesResponse>('/api/companies/import', request);
}
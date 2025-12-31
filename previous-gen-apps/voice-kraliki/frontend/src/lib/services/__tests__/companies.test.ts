import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	getCompanies,
	getCompany,
	createCompany,
	updateCompany,
	deleteCompany,
	getCompanyStats,
	getCompanyUsers,
	getCompanyScripts,
	getIndustries,
	getCompanySizes,
	importCompanies,
} from '../companies';
import type {
	Company,
	CompanyCreate,
	CompanyUpdate,
	CompanyStats,
	CompaniesListParams,
	ImportCompaniesRequest,
} from '../companies';
import * as apiUtils from '$lib/utils/api';

// Mock the api module
vi.mock('$lib/utils/api', () => ({
	apiGet: vi.fn(),
	apiPost: vi.fn(),
	apiPatch: vi.fn(),
	apiDelete: vi.fn(),
}));

describe('Companies Service', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('getCompanies', () => {
		it('should fetch companies list without filters', async () => {
			const mockCompanies: Company[] = [
				{
					id: 1,
					name: 'Company A',
					domain: 'companya.com',
					industry: 'Technology',
					size: 'medium',
					phone_number: '+1234567890',
					email: 'contact@companya.com',
					settings: {},
					is_active: true,
					created_at: '2024-01-01T00:00:00Z',
					updated_at: '2024-01-01T00:00:00Z'
				},
				{
					id: 2,
					name: 'Company B',
					domain: 'companyb.com',
					industry: 'Finance',
					size: 'large',
					settings: {},
					is_active: true,
					created_at: '2024-01-01T00:00:00Z',
					updated_at: '2024-01-01T00:00:00Z'
				}
			];

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockCompanies);

			const result = await getCompanies();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/api/companies');
			expect(result).toHaveLength(2);
			expect(result[0].name).toBe('Company A');
		});

		it('should fetch companies with filters', async () => {
			const params: CompaniesListParams = {
				is_active: true,
				industry: 'Technology',
				size: 'medium',
				search: 'Company',
				limit: 10,
				offset: 0
			};

			const mockCompanies: Company[] = [
				{
					id: 1,
					name: 'Tech Company',
					domain: 'tech.com',
					industry: 'Technology',
					size: 'medium',
					settings: {},
					is_active: true,
					created_at: '2024-01-01T00:00:00Z',
					updated_at: '2024-01-01T00:00:00Z'
				}
			];

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockCompanies);

			const result = await getCompanies(params);

			// URLSearchParams may order parameters differently, so just check it was called
			expect(apiUtils.apiGet).toHaveBeenCalled();
			const callArg = vi.mocked(apiUtils.apiGet).mock.calls[0][0];
			expect(callArg).toContain('/api/companies?');
			expect(callArg).toContain('is_active=true');
			expect(callArg).toContain('industry=Technology');
			expect(callArg).toContain('size=medium');
			expect(callArg).toContain('search=Company');
			expect(callArg).toContain('limit=10');
			expect(result).toHaveLength(1);
		});

		it('should handle empty companies list', async () => {
			vi.mocked(apiUtils.apiGet).mockResolvedValue([]);

			const result = await getCompanies();

			expect(result).toHaveLength(0);
		});

		it('should handle errors fetching companies', async () => {
			const mockError = new Error('Failed to fetch companies');
			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(getCompanies()).rejects.toThrow('Failed to fetch companies');
		});

		it('should fetch inactive companies', async () => {
			const params: CompaniesListParams = {
				is_active: false
			};

			const mockCompanies: Company[] = [
				{
					id: 3,
					name: 'Inactive Company',
					domain: 'inactive.com',
					settings: {},
					is_active: false,
					created_at: '2024-01-01T00:00:00Z',
					updated_at: '2024-01-01T00:00:00Z'
				}
			];

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockCompanies);

			const result = await getCompanies(params);

			expect(result[0].is_active).toBe(false);
		});
	});

	describe('getCompany', () => {
		it('should fetch a single company by ID', async () => {
			const companyId = 1;
			const mockCompany: Company = {
				id: companyId,
				name: 'Test Company',
				domain: 'test.com',
				description: 'A test company',
				industry: 'Technology',
				size: 'small',
				phone_number: '+1234567890',
				email: 'info@test.com',
				address: '123 Main St',
				city: 'San Francisco',
				state: 'CA',
				country: 'US',
				postal_code: '94105',
				website: 'https://test.com',
				logo_url: 'https://test.com/logo.png',
				settings: { notifications: true },
				is_active: true,
				created_at: '2024-01-01T00:00:00Z',
				updated_at: '2024-01-01T00:00:00Z',
				user_count: 5,
				call_count: 100,
				script_count: 3
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockCompany);

			const result = await getCompany(companyId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/companies/${companyId}`);
			expect(result.id).toBe(companyId);
			expect(result.name).toBe('Test Company');
			expect(result.user_count).toBe(5);
		});

		it('should handle company not found', async () => {
			const companyId = 999;
			const mockError = new Error('Company not found');

			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(getCompany(companyId)).rejects.toThrow('Company not found');
		});
	});

	describe('createCompany', () => {
		it('should create a new company successfully', async () => {
			const companyData: CompanyCreate = {
				name: 'New Company',
				domain: 'newcompany.com',
				description: 'A new company',
				industry: 'Technology',
				size: 'small',
				phone_number: '+1234567890',
				email: 'info@newcompany.com',
				address: '456 Tech Blvd',
				city: 'Austin',
				state: 'TX',
				country: 'US',
				postal_code: '78701',
				website: 'https://newcompany.com'
			};

			const mockResponse: Company = {
				id: 10,
				...companyData,
				settings: {},
				is_active: true,
				created_at: '2024-01-15T10:00:00Z',
				updated_at: '2024-01-15T10:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await createCompany(companyData);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/companies', companyData);
			expect(result.id).toBe(10);
			expect(result.name).toBe('New Company');
			expect(result.is_active).toBe(true);
		});

		it('should create company with minimal required fields', async () => {
			const companyData: CompanyCreate = {
				name: 'Minimal Company',
				domain: 'minimal.com'
			};

			const mockResponse: Company = {
				id: 11,
				name: 'Minimal Company',
				domain: 'minimal.com',
				settings: {},
				is_active: true,
				created_at: '2024-01-15T10:00:00Z',
				updated_at: '2024-01-15T10:00:00Z'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await createCompany(companyData);

			expect(result.name).toBe('Minimal Company');
			expect(result.domain).toBe('minimal.com');
		});

		it('should handle duplicate company creation error', async () => {
			const companyData: CompanyCreate = {
				name: 'Existing Company',
				domain: 'existing.com'
			};

			const mockError = new Error('Company already exists');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(createCompany(companyData)).rejects.toThrow('Company already exists');
		});

		it('should handle validation errors', async () => {
			const companyData: CompanyCreate = {
				name: '',
				domain: ''
			};

			const mockError = new Error('Invalid company data');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(createCompany(companyData)).rejects.toThrow('Invalid company data');
		});
	});

	describe('updateCompany', () => {
		it('should update company successfully', async () => {
			const companyId = 1;
			const updateData: CompanyUpdate = {
				name: 'Updated Company Name',
				description: 'Updated description',
				phone_number: '+9876543210'
			};

			const mockResponse: Company = {
				id: companyId,
				name: 'Updated Company Name',
				domain: 'company.com',
				description: 'Updated description',
				phone_number: '+9876543210',
				settings: {},
				is_active: true,
				created_at: '2024-01-01T00:00:00Z',
				updated_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPatch).mockResolvedValue(mockResponse);

			const result = await updateCompany(companyId, updateData);

			expect(apiUtils.apiPatch).toHaveBeenCalledWith(`/api/companies/${companyId}`, updateData);
			expect(result.name).toBe('Updated Company Name');
			expect(result.description).toBe('Updated description');
		});

		it('should update company status', async () => {
			const companyId = 1;
			const updateData: CompanyUpdate = {
				is_active: false
			};

			const mockResponse: Company = {
				id: companyId,
				name: 'Company',
				domain: 'company.com',
				settings: {},
				is_active: false,
				created_at: '2024-01-01T00:00:00Z',
				updated_at: '2024-01-15T12:00:00Z'
			};

			vi.mocked(apiUtils.apiPatch).mockResolvedValue(mockResponse);

			const result = await updateCompany(companyId, updateData);

			expect(result.is_active).toBe(false);
		});

		it('should handle update errors', async () => {
			const companyId = 999;
			const updateData: CompanyUpdate = {
				name: 'New Name'
			};

			const mockError = new Error('Company not found');
			vi.mocked(apiUtils.apiPatch).mockRejectedValue(mockError);

			await expect(updateCompany(companyId, updateData)).rejects.toThrow('Company not found');
		});
	});

	describe('deleteCompany', () => {
		it('should delete company successfully', async () => {
			const companyId = 1;
			const mockResponse = { message: 'Company deleted successfully' };

			vi.mocked(apiUtils.apiDelete).mockResolvedValue(mockResponse);

			const result = await deleteCompany(companyId);

			expect(apiUtils.apiDelete).toHaveBeenCalledWith(`/api/companies/${companyId}`);
			expect(result.message).toBe('Company deleted successfully');
		});

		it('should handle deletion of non-existent company', async () => {
			const companyId = 999;
			const mockError = new Error('Company not found');

			vi.mocked(apiUtils.apiDelete).mockRejectedValue(mockError);

			await expect(deleteCompany(companyId)).rejects.toThrow('Company not found');
		});

		it('should handle deletion with active dependencies', async () => {
			const companyId = 1;
			const mockError = new Error('Cannot delete company with active users');

			vi.mocked(apiUtils.apiDelete).mockRejectedValue(mockError);

			await expect(deleteCompany(companyId)).rejects.toThrow('Cannot delete company with active users');
		});
	});

	describe('getCompanyStats', () => {
		it('should fetch company statistics', async () => {
			const companyId = 1;
			const mockStats: CompanyStats = {
				company_id: companyId,
				total_users: 25,
				active_users: 20,
				total_calls: 500,
				calls_this_month: 75,
				total_scripts: 10,
				active_scripts: 8,
				average_call_duration: 180,
				success_rate: 0.92,
				cost_this_month: 150.50
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockStats);

			const result = await getCompanyStats(companyId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/companies/${companyId}/stats`);
			expect(result.company_id).toBe(companyId);
			expect(result.total_users).toBe(25);
			expect(result.success_rate).toBe(0.92);
		});

		it('should handle missing stats', async () => {
			const companyId = 999;
			const mockError = new Error('Stats not found');

			vi.mocked(apiUtils.apiGet).mockRejectedValue(mockError);

			await expect(getCompanyStats(companyId)).rejects.toThrow('Stats not found');
		});
	});

	describe('getCompanyUsers', () => {
		it('should fetch company users with default pagination', async () => {
			const companyId = 1;
			const mockResponse = {
				company_id: companyId,
				users: [
					{
						id: 1,
						name: 'John Doe',
						email: 'john@company.com',
						role: 'admin',
						is_active: true,
						last_login: '2024-01-15T10:00:00Z'
					},
					{
						id: 2,
						name: 'Jane Smith',
						email: 'jane@company.com',
						role: 'user',
						is_active: true,
						last_login: '2024-01-14T15:30:00Z'
					}
				],
				total: 2
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getCompanyUsers(companyId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/companies/${companyId}/users?limit=20&offset=0`);
			expect(result.users).toHaveLength(2);
			expect(result.total).toBe(2);
		});

		it('should fetch company users with custom pagination', async () => {
			const companyId = 1;
			const mockResponse = {
				company_id: companyId,
				users: [],
				total: 0
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			await getCompanyUsers(companyId, 50, 100);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/companies/${companyId}/users?limit=50&offset=100`);
		});
	});

	describe('getCompanyScripts', () => {
		it('should fetch company scripts', async () => {
			const companyId = 1;
			const mockResponse = {
				company_id: companyId,
				scripts: [
					{
						id: 1,
						title: 'Sales Script',
						status: 'active',
						usage_count: 150
					},
					{
						id: 2,
						title: 'Support Script',
						status: 'active',
						usage_count: 200
					}
				],
				total: 2
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getCompanyScripts(companyId);

			expect(apiUtils.apiGet).toHaveBeenCalledWith(`/api/companies/${companyId}/scripts?limit=20&offset=0`);
			expect(result.scripts).toHaveLength(2);
			expect(result.total).toBe(2);
		});
	});

	describe('getIndustries', () => {
		it('should fetch available industries', async () => {
			const mockResponse = {
				industries: ['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing']
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getIndustries();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/api/companies/industries');
			expect(result.industries).toHaveLength(5);
			expect(result.industries).toContain('Technology');
		});
	});

	describe('getCompanySizes', () => {
		it('should fetch available company sizes', async () => {
			const mockResponse = {
				sizes: [
					{ value: 'small', label: 'Small (1-50)' },
					{ value: 'medium', label: 'Medium (51-200)' },
					{ value: 'large', label: 'Large (201-1000)' },
					{ value: 'enterprise', label: 'Enterprise (1000+)' }
				]
			};

			vi.mocked(apiUtils.apiGet).mockResolvedValue(mockResponse);

			const result = await getCompanySizes();

			expect(apiUtils.apiGet).toHaveBeenCalledWith('/api/companies/sizes');
			expect(result.sizes).toHaveLength(4);
			expect(result.sizes[0].value).toBe('small');
		});
	});

	describe('importCompanies', () => {
		it('should import multiple companies successfully', async () => {
			const request: ImportCompaniesRequest = {
				companies: [
					{
						name: 'Import Company 1',
						phone: '+1111111111',
						domain: 'import1.com',
						industry: 'Technology',
						size: 'small'
					},
					{
						name: 'Import Company 2',
						phone: '+2222222222',
						domain: 'import2.com',
						industry: 'Finance',
						size: 'medium'
					}
				]
			};

			const mockResponse = {
				success: true,
				count: 2,
				companies: [
					{
						id: 1,
						name: 'Import Company 1',
						domain: 'import1.com',
						phone_number: '+1111111111',
						industry: 'Technology',
						size: 'small' as const,
						settings: {},
						is_active: true,
						created_at: '2024-01-15T00:00:00Z',
						updated_at: '2024-01-15T00:00:00Z'
					},
					{
						id: 2,
						name: 'Import Company 2',
						domain: 'import2.com',
						phone_number: '+2222222222',
						industry: 'Finance',
						size: 'medium' as const,
						settings: {},
						is_active: true,
						created_at: '2024-01-15T00:00:00Z',
						updated_at: '2024-01-15T00:00:00Z'
					}
				]
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await importCompanies(request);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/companies/import', request);
			expect(result.success).toBe(true);
			expect(result.count).toBe(2);
			expect(result.companies).toHaveLength(2);
		});

		it('should handle import errors', async () => {
			const request: ImportCompaniesRequest = {
				companies: [
					{
						name: 'Invalid Company',
						phone: 'invalid-phone'
					}
				]
			};

			const mockError = new Error('Invalid phone format');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(importCompanies(request)).rejects.toThrow('Invalid phone format');
		});

		it('should handle partial import success', async () => {
			const request: ImportCompaniesRequest = {
				companies: [
					{ name: 'Company 1', phone: '+1111111111' },
					{ name: 'Company 2', phone: '+2222222222' }
				]
			};

			const mockResponse = {
				success: true,
				count: 1,
				error: 'Some companies could not be imported',
				companies: [
					{
						id: 1,
						name: 'Company 1',
						domain: 'company1.com',
						phone_number: '+1111111111',
						settings: {},
						is_active: true,
						created_at: '2024-01-15T00:00:00Z',
						updated_at: '2024-01-15T00:00:00Z'
					}
				]
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await importCompanies(request);

			expect(result.success).toBe(true);
			expect(result.count).toBe(1);
			expect(result.error).toBeDefined();
		});
	});
});

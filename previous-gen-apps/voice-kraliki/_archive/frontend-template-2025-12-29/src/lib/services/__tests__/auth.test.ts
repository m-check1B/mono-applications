import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { login, logout, register } from '../auth';
import type { Credentials, RegisterPayload, AuthResponse } from '../auth';
import * as apiUtils from '$lib/utils/api';

// Mock the api module
vi.mock('$lib/utils/api', () => ({
	apiPost: vi.fn(),
}));

describe('Auth Service', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('login', () => {
		it('should login successfully with valid credentials', async () => {
			const credentials: Credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			const mockResponse: AuthResponse = {
				access_token: 'mock-access-token',
				refresh_token: 'mock-refresh-token',
				expires_at: Date.now() + 3600000,
				user: {
					id: 'user-123',
					email: 'test@example.com',
					name: 'Test User',
					role: 'user'
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await login(credentials);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/v1/auth/login', credentials);
			expect(result).toEqual(mockResponse);
			expect(result.access_token).toBe('mock-access-token');
			expect(result.user?.email).toBe('test@example.com');
		});

		it('should handle login with invalid credentials', async () => {
			const credentials: Credentials = {
				email: 'wrong@example.com',
				password: 'wrongpassword'
			};

			const mockError = new Error('Invalid credentials');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(login(credentials)).rejects.toThrow('Invalid credentials');
			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/v1/auth/login', credentials);
		});

		it('should handle login with missing email', async () => {
			const credentials: Credentials = {
				email: '',
				password: 'password123'
			};

			const mockError = new Error('Email is required');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(login(credentials)).rejects.toThrow('Email is required');
		});

		it('should handle login with missing password', async () => {
			const credentials: Credentials = {
				email: 'test@example.com',
				password: ''
			};

			const mockError = new Error('Password is required');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(login(credentials)).rejects.toThrow('Password is required');
		});

		it('should return refresh token on successful login', async () => {
			const credentials: Credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			const mockResponse: AuthResponse = {
				access_token: 'access-token',
				refresh_token: 'refresh-token'
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await login(credentials);

			expect(result.refresh_token).toBe('refresh-token');
			expect(result.access_token).toBe('access-token');
		});

		it('should handle network errors during login', async () => {
			const credentials: Credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			const mockError = new Error('Network error');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(login(credentials)).rejects.toThrow('Network error');
		});

		it('should handle server errors (500) during login', async () => {
			const credentials: Credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			const mockError = Object.assign(new Error('Internal Server Error'), {
				status: 500
			});
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(login(credentials)).rejects.toThrow('Internal Server Error');
		});

		it('should include user data in successful login response', async () => {
			const credentials: Credentials = {
				email: 'admin@example.com',
				password: 'adminpass'
			};

			const mockResponse: AuthResponse = {
				access_token: 'token',
				refresh_token: 'refresh',
				user: {
					id: 'admin-id',
					email: 'admin@example.com',
					name: 'Admin User',
					role: 'admin'
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await login(credentials);

			expect(result.user).toBeDefined();
			expect(result.user?.role).toBe('admin');
			expect(result.user?.id).toBe('admin-id');
		});

		it('should handle token expiration in login response', async () => {
			const credentials: Credentials = {
				email: 'test@example.com',
				password: 'password123'
			};

			const expiresAt = Date.now() + 7200000; // 2 hours
			const mockResponse: AuthResponse = {
				access_token: 'token',
				refresh_token: 'refresh',
				expires_at: expiresAt
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await login(credentials);

			expect(result.expires_at).toBe(expiresAt);
		});
	});

	describe('register', () => {
		it('should register a new user successfully', async () => {
			const payload: RegisterPayload = {
				email: 'newuser@example.com',
				password: 'newpassword123',
				full_name: 'New User'
			};

			const mockResponse: AuthResponse = {
				access_token: 'new-access-token',
				refresh_token: 'new-refresh-token',
				user: {
					id: 'new-user-id',
					email: 'newuser@example.com',
					name: 'New User',
					role: 'user'
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await register(payload);

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/v1/auth/register', payload);
			expect(result).toEqual(mockResponse);
			expect(result.user?.email).toBe('newuser@example.com');
		});

		it('should register user without optional name', async () => {
			const payload: RegisterPayload = {
				email: 'user@example.com',
				password: 'password123'
			};

			const mockResponse: AuthResponse = {
				access_token: 'token',
				refresh_token: 'refresh',
				user: {
					id: 'user-id',
					email: 'user@example.com',
					role: 'user'
				}
			};

			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await register(payload);

			expect(result.user?.name).toBeUndefined();
			expect(result.user?.email).toBe('user@example.com');
		});

		it('should handle registration with existing email', async () => {
			const payload: RegisterPayload = {
				email: 'existing@example.com',
				password: 'password123'
			};

			const mockError = new Error('Email already exists');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(register(payload)).rejects.toThrow('Email already exists');
		});

		it('should handle registration with weak password', async () => {
			const payload: RegisterPayload = {
				email: 'user@example.com',
				password: '123'
			};

			const mockError = new Error('Password too weak');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(register(payload)).rejects.toThrow('Password too weak');
		});

		it('should handle registration with invalid email format', async () => {
			const payload: RegisterPayload = {
				email: 'invalid-email',
				password: 'password123'
			};

			const mockError = new Error('Invalid email format');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(register(payload)).rejects.toThrow('Invalid email format');
		});
	});

	describe('logout', () => {
		it('should logout successfully', async () => {
			const mockResponse = { success: true };
			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			const result = await logout();

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/v1/auth/logout', {});
			expect(result.success).toBe(true);
		});

		it('should handle logout errors gracefully', async () => {
			const mockError = new Error('Logout failed');
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(logout()).rejects.toThrow('Logout failed');
		});

		it('should call logout endpoint with empty payload', async () => {
			const mockResponse = { success: true };
			vi.mocked(apiUtils.apiPost).mockResolvedValue(mockResponse);

			await logout();

			expect(apiUtils.apiPost).toHaveBeenCalledWith('/api/v1/auth/logout', {});
		});

		it('should handle server errors during logout', async () => {
			const mockError = Object.assign(new Error('Server error'), {
				status: 500
			});
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(logout()).rejects.toThrow('Server error');
		});

		it('should handle unauthorized logout attempts', async () => {
			const mockError = Object.assign(new Error('Unauthorized'), {
				status: 401
			});
			vi.mocked(apiUtils.apiPost).mockRejectedValue(mockError);

			await expect(logout()).rejects.toThrow('Unauthorized');
		});
	});
});

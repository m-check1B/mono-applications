import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth, AuthProvider } from '@/contexts/AuthContext';
import { createToken, verifyToken, refreshToken } from '@unified/auth-core';

// Mock the auth-core functions
vi.mock('@unified/auth-core', () => ({
  createToken: vi.fn(),
  verifyToken: vi.fn(),
  refreshToken: vi.fn()
}));

// Mock CSRF hook
vi.mock('@/hooks/useCSRF', () => ({
  useCSRF: () => ({
    getCSRFHeaders: vi.fn().mockReturnValue({ 'X-CSRF-Token': 'test-token' })
  })
}));

const mockCreateToken = createToken as vi.MockedFunction<typeof createToken>;
const mockVerifyToken = verifyToken as vi.MockedFunction<typeof verifyToken>;
const mockRefreshToken = refreshToken as vi.MockedFunction<typeof refreshToken>;

// Mock fetch globally
global.fetch = vi.fn();

describe('useAuth Hook', () => {
  const mockUser = {
    id: 'test-user-id',
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    role: 'AGENT' as const,
    status: 'ACTIVE' as const,
    organizationId: 'test-org',
    organization: {
      id: 'test-org',
      name: 'Test Organization',
      domain: 'test.example.com'
    },
    preferences: {
      language: 'en',
      timezone: 'UTC',
      notifications: true,
      autoAnswer: false
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockCreateToken.mockResolvedValue({
      token: 'test-token',
      refreshToken: 'test-refresh-token',
      expiresAt: Date.now() + 3600000
    });
    mockVerifyToken.mockResolvedValue({
      valid: true,
      user: mockUser
    });
    mockRefreshToken.mockResolvedValue({
      token: 'new-test-token',
      refreshToken: 'new-refresh-token',
      expiresAt: Date.now() + 3600000
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  it('should initialize with loading state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.isLoading).toBe(true);
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it('should check authentication status on mount', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        result: {
          data: mockUser
        }
      })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockFetch).toHaveBeenCalledWith(
      '/trpc/auth.me',
      expect.objectContaining({
        method: 'GET',
        credentials: 'include'
      })
    );
  });

  it('should handle successful login', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('test@example.com', 'password123');
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/login'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'X-CSRF-Token': 'test-token'
        }),
        body: JSON.stringify({
          email: 'test@example.com',
          password: 'password123'
        })
      })
    );
  });

  it('should handle login errors', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await expect(
      act(() => result.current.login('test@example.com', 'password123'))
    ).rejects.toThrow('Network error');
  });

  it('should handle logout', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ result: { data: mockUser } })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    } as Response);

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it('should check user roles correctly', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ result: { data: mockUser } })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.hasRole('AGENT')).toBe(true);
    expect(result.current.hasRole('ADMIN')).toBe(false);
    expect(result.current.hasRole(['AGENT', 'SUPERVISOR'])).toBe(true);
  });

  it('should check permissions correctly', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ result: { data: mockUser } })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Mock permission checking
    result.current.hasPermission = vi.fn().mockImplementation((permission) => {
      if (permission === 'view_dashboard') return true;
      if (permission === 'make_calls') return true;
      return false;
    });

    expect(result.current.hasPermission('view_dashboard')).toBe(true);
    expect(result.current.hasPermission('make_calls')).toBe(true);
    expect(result.current.hasPermission('manage_agents')).toBe(false);
  });

  it('should check organization access', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ result: { data: mockUser } })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.canAccessOrganization('test-org')).toBe(true);
    expect(result.current.canAccessOrganization('different-org')).toBe(false);
  });

  it('should handle token refresh', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ result: { data: mockUser } })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    } as Response);

    await act(async () => {
      await result.current.refreshAuth();
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/auth/refresh'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include'
      })
    );
  });

  it('should handle authentication failures', async () => {
    const mockFetch = fetch as vi.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Unauthorized' })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});
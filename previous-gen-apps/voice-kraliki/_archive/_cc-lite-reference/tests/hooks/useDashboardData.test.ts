import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDashboardData } from '@/hooks/useDashboardData';

// Mock apiClient
vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn()
  }
}));

const mockApiClient = require('@/lib/api-client').apiClient;

// Mock QueryClient
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(),
  QueryClient: vi.fn()
}));

const { useQuery } = require('@tanstack/react-query');

describe('useDashboardData Hook', () => {
  const mockDashboardData = {
    activeCalls: [
      {
        id: 'call-1',
        phoneNumber: '+1234567890',
        status: 'active',
        duration: 120,
        agent: 'John Doe'
      },
      {
        id: 'call-2',
        phoneNumber: '+0987654321',
        status: 'active',
        duration: 85,
        agent: 'Jane Smith'
      }
    ],
    recentCalls: [
      {
        id: 'call-3',
        phoneNumber: '+1234567890',
        status: 'completed',
        duration: 300,
        agent: 'John Doe',
        timestamp: new Date().toISOString()
      }
    ],
    teamStatus: {
      members: [
        {
          id: 'agent-1',
          name: 'John Doe',
          status: 'available',
          activeCall: null
        },
        {
          id: 'agent-2',
          name: 'Jane Smith',
          status: 'busy',
          activeCall: 'call-2'
        }
      ],
      stats: {
        totalMembers: 2,
        availableAgents: 1,
        busyAgents: 1,
        onBreakAgents: 0,
        offlineAgents: 0
      }
    },
    callStats: {
      totalCalls: 150,
      activeCalls: 2,
      completedCalls: 148,
      averageDuration: 240,
      handledByAI: 45,
      handledByAgents: 105,
      missedCalls: 5
    }
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockApiClient.get.mockResolvedValue({ data: mockDashboardData });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('should fetch dashboard data successfully', async () => {
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.data).toEqual(mockDashboardData);
    expect(mockApiClient.get).toHaveBeenCalledWith('/dashboard');
  });

  it('should handle loading state', () => {
    useQuery.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.isLoading).toBe(true);
  });

  it('should handle API errors', () => {
    const errorMessage = 'Failed to fetch dashboard data';
    mockApiClient.get.mockRejectedValue(new Error(errorMessage));

    useQuery.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error(errorMessage),
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.error).toBeDefined();
    expect(result.current.error.message).toBe(errorMessage);
  });

  it('should use correct query key', () => {
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    renderHook(() => useDashboardData());

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ['dashboard']
      })
    );
  });

  it('should configure automatic refetching', () => {
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    renderHook(() => useDashboardData());

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        refetchInterval: 5000, // 5 seconds
        retry: 3
      })
    );
  });

  it('should retry failed requests', () => {
    mockApiClient.get.mockRejectedValueOnce(new Error('Network error'));

    useQuery.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(useQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        retry: 3
      })
    );
  });

  it('should return proper data structure', () => {
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.data).toHaveProperty('activeCalls');
    expect(result.current.data).toHaveProperty('recentCalls');
    expect(result.current.data).toHaveProperty('teamStatus');
    expect(result.current.data).toHaveProperty('callStats');

    expect(Array.isArray(result.current.data.activeCalls)).toBe(true);
    expect(Array.isArray(result.current.data.recentCalls)).toBe(true);
    expect(typeof result.current.data.teamStatus).toBe('object');
    expect(typeof result.current.data.callStats).toBe('object');
  });

  it('should handle empty data response', () => {
    const emptyData = {
      activeCalls: [],
      recentCalls: [],
      teamStatus: {
        members: [],
        stats: {
          totalMembers: 0,
          availableAgents: 0,
          busyAgents: 0,
          onBreakAgents: 0,
          offlineAgents: 0
        }
      },
      callStats: {
        totalCalls: 0,
        activeCalls: 0,
        completedCalls: 0,
        averageDuration: 0,
        handledByAI: 0,
        handledByAgents: 0,
        missedCalls: 0
      }
    };

    mockApiClient.get.mockResolvedValue({ data: emptyData });

    useQuery.mockReturnValue({
      data: emptyData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.data).toEqual(emptyData);
    expect(result.current.data.activeCalls).toHaveLength(0);
    expect(result.current.data.teamStatus.stats.totalMembers).toBe(0);
  });

  it('should handle malformed API response', () => {
    const malformedData = {
      // Missing required fields
      activeCalls: null,
      teamStatus: undefined
    };

    mockApiClient.get.mockResolvedValue({ data: malformedData });

    useQuery.mockReturnValue({
      data: malformedData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.data).toBe(malformedData);
  });

  it('should calculate derived statistics correctly', () => {
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    const { callStats } = result.current.data;

    // Verify total calls match expected values
    expect(callStats.totalCalls).toBe(150);
    expect(callStats.activeCalls).toBe(2);
    expect(callStats.completedCalls).toBe(148);

    // Verify AI vs agent handled calls
    expect(callStats.handledByAI + callStats.handledByAgents + callStats.missedCalls)
      .toBe(callStats.totalCalls);
  });

  it('should handle team status aggregation', () => {
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    const { result } = renderHook(() => useDashboardData());

    const { teamStatus } = result.current.data;

    expect(teamStatus.members).toHaveLength(2);
    expect(teamStatus.stats.totalMembers).toBe(2);
    expect(teamStatus.stats.availableAgents).toBe(1);
    expect(teamStatus.stats.busyAgents).toBe(1);
  });

  it('should expose refetch function', () => {
    const refetchFn = vi.fn();
    useQuery.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: refetchFn
    });

    const { result } = renderHook(() => useDashboardData());

    expect(result.current.refetch).toBe(refetchFn);
  });
});
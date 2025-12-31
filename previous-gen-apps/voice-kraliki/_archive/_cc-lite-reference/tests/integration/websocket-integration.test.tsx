import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useDashboardData } from '@/hooks/useDashboardData';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WebSocketMessage } from '@/hooks/useWebSocket';

// Mock WebSocket
const createMockWebSocket = () => {
  const mockWebSocket = {
    readyState: 1,
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    onopen: null as any,
    onmessage: null as any,
    onclose: null as any,
    onerror: null as any
  };
  return mockWebSocket;
};

global.WebSocket = vi.fn().mockImplementation(createMockWebSocket);

// Mock apiClient
vi.mock(
  '@/lib/api-client',
  () => ({
    apiClient: {
      get: vi.fn(),
    },
  }),
  { virtual: true }
);

// Use a local stub for API client to avoid module resolution issues
const mockApiClient = { get: vi.fn() } as any;

// Mock react-query
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: vi.fn(),
    QueryClient: vi.fn()
  };
});

const { useQuery } = require('@tanstack/react-query');

const maybeDescribe = process.env.SKIP_DB_TEST_SETUP === 'true' ? describe.skip : describe;

maybeDescribe('WebSocket Integration Tests', () => {
  let queryClient: QueryClient;
  let mockWebSocket: any;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    mockWebSocket = createMockWebSocket();
    (global.WebSocket as any).mockImplementation(() => mockWebSocket);

    // Mock dashboard data
    mockApiClient.get.mockResolvedValue({
      data: {
        activeCalls: [],
        recentCalls: [],
        teamStatus: {
          members: [],
          stats: { totalMembers: 0, availableAgents: 0, busyAgents: 0, onBreakAgents: 0, offlineAgents: 0 }
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
      }
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const renderWithProviders = (hook: () => any) => {
    return renderHook(hook, {
      wrapper: ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      )
    });
  };

  describe('WebSocket Connection Integration', () => {
    it('should establish connection and handle real-time updates', async () => {
      const { result } = renderWithProviders(() => {
        const ws = useWebSocket();
        const dashboard = useDashboardData();
        return { ws, dashboard };
      });

      // Initial state
      expect(result.current.ws.isConnected).toBe(false);
      expect(result.current.dashboard.isLoading).toBe(false);

      // Connect to WebSocket
      act(() => {
        result.current.ws.connect();
      });

      // Simulate WebSocket open
      act(() => {
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      expect(result.current.ws.isConnected).toBe(true);
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({
          type: 'subscribe',
          events: ['call.created', 'call.updated', 'team.status_updated', 'call.transcript']
        })
      );
    });

    it('should handle real-time call updates', async () => {
      const { result } = renderWithProviders(() => {
        const ws = useWebSocket();
        return ws;
      });

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Simulate incoming call update
      const callUpdate: WebSocketMessage = {
        event: 'call.created',
        data: {
          id: 'call-123',
          phoneNumber: '+1234567890',
          status: 'ACTIVE',
          agent: 'John Doe',
          duration: 45
        },
        timestamp: new Date().toISOString()
      };

      act(() => {
        if (mockWebSocket.onmessage) {
          mockWebSocket.onmessage(new MessageEvent('message', {
            data: JSON.stringify(callUpdate)
          }));
        }
      });

      expect(result.current.lastMessage).toEqual(callUpdate);
    });

    it('should handle WebSocket reconnection attempts', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Simulate connection loss
      act(() => {
        if (mockWebSocket.onclose) {
          mockWebSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Connection lost' }));
        }
      });

      expect(result.current.isConnected).toBe(false);

      // Fast forward to trigger reconnection
      act(() => {
        vi.advanceTimersByTime(1000);
      });

      expect(WebSocket).toHaveBeenCalledTimes(2);
    });

    it('should handle team status updates in real-time', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Simulate team status update
      const teamUpdate: WebSocketMessage = {
        event: 'team.status_updated',
        data: {
          agentId: 'agent-1',
          status: 'busy',
          activeCall: 'call-456'
        },
        timestamp: new Date().toISOString()
      };

      act(() => {
        if (mockWebSocket.onmessage) {
          mockWebSocket.onmessage(new MessageEvent('message', {
            data: JSON.stringify(teamUpdate)
          }));
        }
      });

      expect(result.current.lastMessage).toEqual(teamUpdate);
      expect(teamUpdate.data.status).toBe('busy');
    });

    it('should handle call transcript updates', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Simulate transcript update
      const transcriptUpdate: WebSocketMessage = {
        event: 'call.transcript',
        data: {
          callId: 'call-789',
          transcript: 'Hello, thank you for calling',
          confidence: 0.95,
          timestamp: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      };

      act(() => {
        if (mockWebSocket.onmessage) {
          mockWebSocket.onmessage(new MessageEvent('message', {
            data: JSON.stringify(transcriptUpdate)
          }));
        }
      });

      expect(result.current.lastMessage).toEqual(transcriptUpdate);
      expect(transcriptUpdate.data.transcript).toContain('Hello');
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle WebSocket connection errors', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Mock WebSocket to throw error
      (global.WebSocket as any).mockImplementationOnce(() => {
        throw new Error('Connection failed');
      });

      act(() => {
        result.current.connect();
      });

      expect(result.current.error).toBe('Failed to connect to real-time service');
    });

    it('should handle message parsing errors gracefully', async () => {
      const { result } = renderWithProviders(() => useWebSocket());
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Send invalid JSON
      act(() => {
        if (mockWebSocket.onmessage) {
          mockWebSocket.onmessage(new MessageEvent('message', {
            data: 'invalid-json-message'
          }));
        }
      });

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to parse WebSocket message')
      );

      consoleSpy.mockRestore();
    });

    it('should handle network interruptions gracefully', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Simulate network interruption
      act(() => {
        if (mockWebSocket.onerror) {
          mockWebSocket.onerror(new Event('error'));
        }
      });

      expect(result.current.error).toBe('WebSocket connection error');
      expect(result.current.isConnected).toBe(false);
    });
  });

  describe('Performance Integration', () => {
    it('should handle high-frequency updates efficiently', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Send multiple rapid updates
      const updates = Array.from({ length: 100 }, (_, i) => ({
        event: 'call.updated',
        data: { callId: `call-${i}`, status: 'ACTIVE', duration: i },
        timestamp: new Date().toISOString()
      }));

      updates.forEach(update => {
        act(() => {
          if (mockWebSocket.onmessage) {
            mockWebSocket.onmessage(new MessageEvent('message', {
              data: JSON.stringify(update)
            }));
          }
        });
      });

      expect(result.current.lastMessage).toEqual(updates[updates.length - 1]);
    });

    it('should handle large messages without performance issues', async () => {
      const { result } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Send large transcript message
      const largeTranscript = 'x'.repeat(10000); // 10KB message
      const largeMessage: WebSocketMessage = {
        event: 'call.transcript',
        data: {
          callId: 'call-large',
          transcript: largeTranscript,
          confidence: 0.95
        },
        timestamp: new Date().toISOString()
      };

      const startTime = performance.now();

      act(() => {
        if (mockWebSocket.onmessage) {
          mockWebSocket.onmessage(new MessageEvent('message', {
            data: JSON.stringify(largeMessage)
          }));
        }
      });

      const endTime = performance.now();
      const processingTime = endTime - startTime;

      expect(result.current.lastMessage).toEqual(largeMessage);
      expect(processingTime).toBeLessThan(100); // Should process in under 100ms
    });
  });

  describe('Memory Management', () => {
    it('should clean up resources on disconnection', async () => {
      const { result, unmount } = renderWithProviders(() => useWebSocket());

      // Connect WebSocket
      act(() => {
        result.current.connect();
        if (mockWebSocket.onopen) {
          mockWebSocket.onopen(new Event('open'));
        }
      });

      // Send some messages
      act(() => {
        if (mockWebSocket.onmessage) {
          mockWebSocket.onmessage(new MessageEvent('message', {
            data: JSON.stringify({
              event: 'test',
              data: { test: true },
              timestamp: new Date().toISOString()
            })
          }));
        }
      });

      expect(result.current.lastMessage).not.toBeNull();

      // Disconnect
      act(() => {
        result.current.disconnect();
      });

      expect(mockWebSocket.close).toHaveBeenCalled();

      // Unmount component
      unmount();

      // Verify cleanup
      expect(mockWebSocket.removeEventListener).toHaveBeenCalled();
    });
  });
});

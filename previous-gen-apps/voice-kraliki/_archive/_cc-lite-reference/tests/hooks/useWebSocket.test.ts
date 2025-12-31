import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useWebSocket } from '@/hooks/useWebSocket';

// Mock WebSocket
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

global.WebSocket = vi.fn().mockImplementation(() => mockWebSocket);

describe('useWebSocket Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();

    // Reset WebSocket mock
    mockWebSocket.send.mockClear();
    mockWebSocket.close.mockClear();
    mockWebSocket.addEventListener.mockClear();
    mockWebSocket.removeEventListener.mockClear();

    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: {
        hostname: 'localhost',
        protocol: 'http:'
      },
      writable: true
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should initialize with disconnected state', () => {
    const { result } = renderHook(() => useWebSocket());

    expect(result.current.isConnected).toBe(false);
    expect(result.current.lastMessage).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should connect to WebSocket when connect is called', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();
    });

    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:3001/ws');
  });

  it('should set connected state when WebSocket opens', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('should send subscription message on connection', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify({
      type: 'subscribe',
      events: ['call.created', 'call.updated', 'team.status_updated', 'call.transcript']
    }));
  });

  it('should handle incoming messages', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    const testMessage = {
      event: 'call.created',
      data: { id: 'test-call', status: 'active' },
      timestamp: new Date().toISOString()
    };

    act(() => {
      // Simulate WebSocket message event
      if (mockWebSocket.onmessage) {
        mockWebSocket.onmessage(new MessageEvent('message', {
          data: JSON.stringify(testMessage)
        }));
      }
    });

    expect(result.current.lastMessage).toEqual(testMessage);
  });

  it('should handle invalid message format gracefully', () => {
    const { result } = renderHook(() => useWebSocket();
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    act(() => {
      // Simulate invalid JSON message
      if (mockWebSocket.onmessage) {
        mockWebSocket.onmessage(new MessageEvent('message', {
          data: 'invalid-json'
        }));
      }
    });

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Failed to parse WebSocket message')
    );

    consoleSpy.mockRestore();
  });

  it('should handle WebSocket disconnection', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    act(() => {
      // Simulate WebSocket close event
      if (mockWebSocket.onclose) {
        mockWebSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }));
      }
    });

    expect(result.current.isConnected).toBe(false);
  });

  it('should attempt to reconnect on abnormal closure', () => {
    const { result } = renderHook(() => useWebSocket();

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    act(() => {
      // Simulate abnormal close event (not manual close)
      if (mockWebSocket.onclose) {
        mockWebSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }));
      }
    });

    // Fast forward timers to trigger reconnect
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(WebSocket).toHaveBeenCalledTimes(2); // Initial connection + reconnect
  });

  it('should stop reconnecting after max attempts', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    // Simulate multiple failed connections
    for (let i = 0; i < 6; i++) {
      act(() => {
        if (mockWebSocket.onclose) {
          mockWebSocket.onclose(new CloseEvent('close', { code: 1006, reason: 'Abnormal closure' }));
        }
        vi.advanceTimersByTime(1000 * Math.pow(2, i));
      });
    }

    expect(result.current.error).toBe('Connection lost. Please refresh the page to reconnect.');
  });

  it('should handle WebSocket errors', () => {
    const { result } = renderHook(() => useWebSocket();

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    act(() => {
      // Simulate WebSocket error event
      if (mockWebSocket.onerror) {
        mockWebSocket.onerror(new Event('error'));
      }
    });

    expect(result.current.error).toBe('WebSocket connection error');
  });

  it('should disconnect manually', () => {
    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();

      // Simulate WebSocket open event
      if (mockWebSocket.onopen) {
        mockWebSocket.onopen(new Event('open'));
      }
    });

    act(() => {
      result.current.disconnect();
    });

    expect(mockWebSocket.close).toHaveBeenCalled();
  });

  it('should handle connection errors', () => {
    const { result } = renderHook(() => useWebSocket();

    // Mock WebSocket to throw error
    (WebSocket as vi.Mock).mockImplementationOnce(() => {
      throw new Error('Connection failed');
    });

    act(() => {
      result.current.connect();
    });

    expect(result.current.error).toBe('Failed to connect to real-time service');
  });

  it('should use custom port from environment', () => {
    // Mock environment variable
    const originalEnv = import.meta.env;
    (import.meta as any).env = {
      VITE_WS_PORT: '8080'
    };

    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();
    });

    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/ws');

    // Restore original environment
    (import.meta as any).env = originalEnv;
  });

  it('should use wss protocol for https', () => {
    Object.defineProperty(window, 'location', {
      value: {
        hostname: 'localhost',
        protocol: 'https:'
      },
      writable: true
    });

    const { result } = renderHook(() => useWebSocket());

    act(() => {
      result.current.connect();
    });

    expect(WebSocket).toHaveBeenCalledWith('wss://localhost:3001/ws');
  });

  it('should clear reconnect timeout on manual disconnect', () => {
    const { result } = renderHook(() => useWebSocket();

    act(() => {
      result.current.connect();
    });

    act(() => {
      result.current.disconnect();
    });

    // Verify no reconnection attempts are made after manual disconnect
    expect(mockWebSocket.close).toHaveBeenCalled();
  });
});
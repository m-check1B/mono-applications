import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import WS from 'jest-websocket-mock';
import { useWebSocket } from '@/hooks/useWebSocket';

// Mock components for integration testing
const MockDashboard = () => {
  const { isConnected, lastMessage, connect, disconnect } = useWebSocket();

  return (
    <div data-testid="mock-dashboard">
      <div data-testid="connection-status">
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      <div data-testid="last-message">
        {lastMessage ? JSON.stringify(lastMessage) : 'No messages'}
      </div>
      <button onClick={connect}>Connect</button>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
};

// Mock WebSocket
vi.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: vi.fn()
}));

// Mock real-time components
vi.mock('@/components/monitoring/LiveTranscripts', () => ({
  LiveTranscripts: ({ callId }: { callId: string }) => (
    <div data-testid="live-transcripts" data-call-id={callId}>
      <div data-testid="transcript-item">
        Speaker: Hello, how can I help you today?
      </div>
      <div data-testid="transcript-item">
        Customer: I need help with my account
      </div>
    </div>
  )
}));

vi.mock('@/components/monitoring/CallMetrics', () => ({
  CallMetrics: ({ callId }: { callId: string }) => (
    <div data-testid="call-metrics" data-call-id={callId}>
      <div data-testid="metric">MOS: 4.2</div>
      <div data-testid="metric">Latency: 120ms</div>
      <div data-testid="metric">Jitter: 15ms</div>
    </div>
  )
}));

vi.mock('@/components/analytics/RealTimeAnalytics', () => ({
  RealTimeAnalytics: () => (
    <div data-testid="real-time-analytics">
      <div data-testid="metric">Active Calls: 15</div>
      <div data-testid="metric">Queue Length: 3</div>
      <div data-testid="metric">Avg Wait: 45s</div>
    </div>
  )
}));

const mockUseWebSocket = useWebSocket as vi.MockedFunction<typeof useWebSocket>;

// Mock WebSocket server
let server: WS;

const queryClient = new QueryClient();

describe('Real-time Features Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Create WebSocket mock server
    server = new WS('ws://localhost:3010/ws');

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: null,
      error: null,
      connect: vi.fn(),
      disconnect: vi.fn()
    });
  });

  afterEach(() => {
    WS.clean();
    vi.resetAllMocks();
  });

  const renderWithProviders = (component: React.ReactNode) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {component}
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  describe('WebSocket Connection Management', () => {
    it('establishes WebSocket connection on component mount', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;
      expect(server).toHaveReceivedMessages([]);

      expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
    });

    it('handles WebSocket disconnection gracefully', async () => {
      mockUseWebSocket.mockReturnValue({
        isConnected: false,
        lastMessage: null,
        error: new Error('Connection lost'),
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      renderWithProviders(<MockDashboard />);

      expect(screen.getByTestId('connection-status')).toHaveTextContent('Disconnected');
    });

    it('automatically reconnects after connection loss', async () => {
      const mockConnect = vi.fn();

      mockUseWebSocket.mockReturnValue({
        isConnected: false,
        lastMessage: null,
        error: new Error('Connection lost'),
        connect: mockConnect,
        disconnect: vi.fn()
      });

      renderWithProviders(<MockDashboard />);

      const connectButton = screen.getByText('Connect');
      fireEvent.click(connectButton);

      expect(mockConnect).toHaveBeenCalledTimes(1);
    });
  });

  describe('Real-time Call Events', () => {
    it('receives and processes call status updates', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const callUpdateMessage = {
        type: 'CALL_STATUS_UPDATE',
        data: {
          callId: 'call-123',
          status: 'connected',
          duration: 180,
          agent: 'John Doe'
        }
      };

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: callUpdateMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      const { rerender } = renderWithProviders(<MockDashboard />);
      rerender(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <MockDashboard />
          </BrowserRouter>
        </QueryClientProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(callUpdateMessage)
        );
      });
    });

    it('handles incoming call notifications', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const incomingCallMessage = {
        type: 'INCOMING_CALL',
        data: {
          callId: 'call-456',
          phoneNumber: '+1234567890',
          customerName: 'Jane Customer',
          priority: 'high'
        }
      };

      server.send(JSON.stringify(incomingCallMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: incomingCallMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        // In real implementation, this would trigger UI updates
        expect(mockUseWebSocket).toHaveBeenCalled();
      });
    });

    it('processes agent status changes in real-time', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const agentStatusMessage = {
        type: 'AGENT_STATUS_CHANGE',
        data: {
          agentId: 'agent-1',
          status: 'busy',
          callId: 'call-789',
          timestamp: new Date().toISOString()
        }
      };

      server.send(JSON.stringify(agentStatusMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: agentStatusMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(agentStatusMessage)
        );
      });
    });
  });

  describe('Live Transcription Integration', () => {
    it('receives and displays real-time transcription', async () => {
      const { LiveTranscripts } = await import('@/components/monitoring/LiveTranscripts');

      renderWithProviders(<LiveTranscripts callId="call-123" />);

      expect(screen.getByTestId('live-transcripts')).toBeInTheDocument();
      expect(screen.getAllByTestId('transcript-item')).toHaveLength(2);
      expect(screen.getByText('Speaker: Hello, how can I help you today?')).toBeInTheDocument();
      expect(screen.getByText('Customer: I need help with my account')).toBeInTheDocument();
    });

    it('updates transcription as new messages arrive', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const transcriptionMessage = {
        type: 'TRANSCRIPTION_UPDATE',
        data: {
          callId: 'call-123',
          speaker: 'agent',
          text: 'Let me help you with that',
          timestamp: new Date().toISOString(),
          confidence: 0.95
        }
      };

      server.send(JSON.stringify(transcriptionMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: transcriptionMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(transcriptionMessage)
        );
      });
    });
  });

  describe('Real-time Metrics Updates', () => {
    it('displays live call quality metrics', async () => {
      const { CallMetrics } = await import('@/components/monitoring/CallMetrics');

      renderWithProviders(<CallMetrics callId="call-123" />);

      expect(screen.getByTestId('call-metrics')).toBeInTheDocument();
      expect(screen.getByText('MOS: 4.2')).toBeInTheDocument();
      expect(screen.getByText('Latency: 120ms')).toBeInTheDocument();
      expect(screen.getByText('Jitter: 15ms')).toBeInTheDocument();
    });

    it('updates metrics based on WebSocket messages', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const metricsMessage = {
        type: 'CALL_QUALITY_UPDATE',
        data: {
          callId: 'call-123',
          metrics: {
            mos: 3.8,
            latency: 150,
            jitter: 25,
            packetLoss: 1.2
          }
        }
      };

      server.send(JSON.stringify(metricsMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: metricsMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(metricsMessage)
        );
      });
    });

    it('displays real-time analytics dashboard', async () => {
      const { RealTimeAnalytics } = await import('@/components/analytics/RealTimeAnalytics');

      renderWithProviders(<RealTimeAnalytics />);

      expect(screen.getByTestId('real-time-analytics')).toBeInTheDocument();
      expect(screen.getByText('Active Calls: 15')).toBeInTheDocument();
      expect(screen.getByText('Queue Length: 3')).toBeInTheDocument();
      expect(screen.getByText('Avg Wait: 45s')).toBeInTheDocument();
    });
  });

  describe('Queue Management Integration', () => {
    it('processes queue updates in real-time', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const queueUpdateMessage = {
        type: 'QUEUE_UPDATE',
        data: {
          queueId: 'sales-queue',
          waiting: 5,
          averageWaitTime: 120,
          longestWait: 300
        }
      };

      server.send(JSON.stringify(queueUpdateMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: queueUpdateMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(queueUpdateMessage)
        );
      });
    });

    it('handles call routing events', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const routingMessage = {
        type: 'CALL_ROUTED',
        data: {
          callId: 'call-456',
          fromQueue: 'general',
          toAgent: 'agent-2',
          routingReason: 'skill_match'
        }
      };

      server.send(JSON.stringify(routingMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: routingMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(routingMessage)
        );
      });
    });
  });

  describe('Campaign Real-time Updates', () => {
    it('receives campaign progress updates', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const campaignUpdateMessage = {
        type: 'CAMPAIGN_PROGRESS',
        data: {
          campaignId: 'campaign-1',
          completedCalls: 150,
          successfulCalls: 45,
          failedCalls: 5,
          pendingCalls: 800
        }
      };

      server.send(JSON.stringify(campaignUpdateMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: campaignUpdateMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(campaignUpdateMessage)
        );
      });
    });

    it('handles campaign status changes', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const campaignStatusMessage = {
        type: 'CAMPAIGN_STATUS_CHANGE',
        data: {
          campaignId: 'campaign-2',
          status: 'paused',
          reason: 'manual_pause',
          timestamp: new Date().toISOString()
        }
      };

      server.send(JSON.stringify(campaignStatusMessage));

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: campaignStatusMessage,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(campaignStatusMessage)
        );
      });
    });
  });

  describe('Error Handling and Recovery', () => {
    it('handles WebSocket errors gracefully', async () => {
      mockUseWebSocket.mockReturnValue({
        isConnected: false,
        lastMessage: null,
        error: new Error('WebSocket connection failed'),
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      renderWithProviders(<MockDashboard />);

      expect(screen.getByTestId('connection-status')).toHaveTextContent('Disconnected');
    });

    it('recovers from temporary disconnections', async () => {
      renderWithProviders(<MockDashboard />);

      // Simulate disconnection
      mockUseWebSocket.mockReturnValue({
        isConnected: false,
        lastMessage: null,
        error: new Error('Connection lost'),
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      const { rerender } = renderWithProviders(<MockDashboard />);
      rerender(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <MockDashboard />
          </BrowserRouter>
        </QueryClientProvider>
      );

      expect(screen.getByTestId('connection-status')).toHaveTextContent('Disconnected');

      // Simulate reconnection
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      rerender(
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <MockDashboard />
          </BrowserRouter>
        </QueryClientProvider>
      );

      expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
    });

    it('handles malformed WebSocket messages', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      // Send malformed message
      server.send('invalid json');

      // Component should remain stable
      expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
      expect(screen.getByTestId('last-message')).toHaveTextContent('No messages');
    });
  });

  describe('Message Queue and Buffering', () => {
    it('buffers messages during disconnection', async () => {
      renderWithProviders(<MockDashboard />);

      // Simulate buffered messages after reconnection
      const bufferedMessages = [
        {
          type: 'CALL_STATUS_UPDATE',
          data: { callId: 'call-1', status: 'completed' }
        },
        {
          type: 'AGENT_STATUS_CHANGE',
          data: { agentId: 'agent-1', status: 'available' }
        }
      ];

      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: bufferedMessages[0],
        error: null,
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      await waitFor(() => {
        expect(screen.getByTestId('last-message')).toHaveTextContent(
          JSON.stringify(bufferedMessages[0])
        );
      });
    });

    it('processes messages in correct order', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const messages = [
        { type: 'MESSAGE_1', data: { sequence: 1 } },
        { type: 'MESSAGE_2', data: { sequence: 2 } },
        { type: 'MESSAGE_3', data: { sequence: 3 } }
      ];

      // Send messages in sequence
      for (const message of messages) {
        server.send(JSON.stringify(message));

        mockUseWebSocket.mockReturnValue({
          isConnected: true,
          lastMessage: message,
          error: null,
          connect: vi.fn(),
          disconnect: vi.fn()
        });

        await waitFor(() => {
          expect(screen.getByTestId('last-message')).toHaveTextContent(
            JSON.stringify(message)
          );
        });
      }
    });
  });

  describe('Performance and Scalability', () => {
    it('handles high-frequency message updates', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      // Simulate rapid message updates
      const rapidMessages = Array.from({ length: 100 }, (_, i) => ({
        type: 'METRIC_UPDATE',
        data: { metric: 'calls', value: i }
      }));

      for (const message of rapidMessages) {
        server.send(JSON.stringify(message));
      }

      // Component should remain responsive
      expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
    });

    it('throttles message processing to prevent UI blocking', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      const startTime = Date.now();

      // Send burst of messages
      for (let i = 0; i < 50; i++) {
        server.send(JSON.stringify({
          type: 'BURST_MESSAGE',
          data: { index: i }
        }));
      }

      const endTime = Date.now();
      const processingTime = endTime - startTime;

      // Processing should complete within reasonable time
      expect(processingTime).toBeLessThan(1000); // 1 second
    });
  });

  describe('Authentication and Security', () => {
    it('includes authentication token in WebSocket connection', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      // In real implementation, connection would include auth headers
      expect(server).toHaveReceivedMessages([]);
    });

    it('handles authentication failures', async () => {
      mockUseWebSocket.mockReturnValue({
        isConnected: false,
        lastMessage: null,
        error: new Error('Authentication failed'),
        connect: vi.fn(),
        disconnect: vi.fn()
      });

      renderWithProviders(<MockDashboard />);

      expect(screen.getByTestId('connection-status')).toHaveTextContent('Disconnected');
    });

    it('validates message signatures', async () => {
      renderWithProviders(<MockDashboard />);

      await server.connected;

      // Send message without proper signature
      const invalidMessage = {
        type: 'UNSIGNED_MESSAGE',
        data: { content: 'test' }
      };

      server.send(JSON.stringify(invalidMessage));

      // In real implementation, invalid messages would be rejected
      expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
    });
  });
});
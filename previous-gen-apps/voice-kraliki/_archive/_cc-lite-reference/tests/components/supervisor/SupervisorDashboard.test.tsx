import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SupervisorDashboard } from '@/components/supervisor/SupervisorDashboard';
import { useAuth } from '@/contexts/AuthContext';
import { useWebSocket } from '@/hooks/useWebSocket';

// Mock dependencies
vi.mock('@/contexts/AuthContext');
vi.mock('@/hooks/useWebSocket');
vi.mock('@/services/trpc');

// Mock NextUI components
vi.mock('@nextui-org/react', () => ({
  Card: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="card" className={className}>{children}</div>
  ),
  CardBody: ({ children }: { children: React.ReactNode }) => <div data-testid="card-body">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  Button: ({ children, onPress, isDisabled, color, variant, ...props }: any) => (
    <button
      onClick={onPress}
      disabled={isDisabled}
      data-color={color}
      data-variant={variant}
      {...props}
    >
      {children}
    </button>
  ),
  Progress: ({ label, value, ...props }: any) => (
    <div data-testid="progress" data-value={value}>
      <span>{label}</span>
    </div>
  ),
  Chip: ({ children, color }: { children: React.ReactNode; color?: string }) => (
    <span data-testid="chip" data-color={color}>{children}</span>
  ),
  Table: ({ children }: { children: React.ReactNode }) => <table data-testid="table">{children}</table>,
  TableHeader: ({ children }: { children: React.ReactNode }) => <thead data-testid="table-header">{children}</thead>,
  TableColumn: ({ children }: { children: React.ReactNode }) => <th data-testid="table-column">{children}</th>,
  TableBody: ({ children }: { children: React.ReactNode }) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: { children: React.ReactNode }) => <tr data-testid="table-row">{children}</tr>,
  TableCell: ({ children }: { children: React.ReactNode }) => <td data-testid="table-cell">{children}</td>,
  Modal: ({ children, isOpen }: { children: React.ReactNode; isOpen: boolean }) =>
    isOpen ? <div data-testid="modal">{children}</div> : null,
  ModalContent: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-content">{children}</div>,
  ModalHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-header">{children}</div>,
  ModalBody: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-body">{children}</div>,
  ModalFooter: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-footer">{children}</div>,
  Avatar: ({ name }: { name?: string }) => <div data-testid="avatar">{name}</div>,
  Badge: ({ children, color }: { children: React.ReactNode; color?: string }) => (
    <span data-testid="badge" data-color={color}>{children}</span>
  ),
  Select: ({ children, label, onSelectionChange }: any) => (
    <select data-testid="select" data-label={label} onChange={onSelectionChange}>
      {children}
    </select>
  ),
  SelectItem: ({ children, key }: { children: React.ReactNode; key: string }) => (
    <option value={key}>{children}</option>
  ),
  useDisclosure: () => ({
    isOpen: false,
    onOpen: vi.fn(),
    onOpenChange: vi.fn(),
    onClose: vi.fn()
  })
}));

// Mock Heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  PhoneIcon: () => <svg data-testid="phone-icon" />,
  UserGroupIcon: () => <svg data-testid="user-group-icon" />,
  ChartBarIcon: () => <svg data-testid="chart-bar-icon" />,
  ClockIcon: () => <svg data-testid="clock-icon" />,
  EyeIcon: () => <svg data-testid="eye-icon" />,
  PlayIcon: () => <svg data-testid="play-icon" />,
  PauseIcon: () => <svg data-testid="pause-icon" />,
  StopIcon: () => <svg data-testid="stop-icon" />,
  SpeakerWaveIcon: () => <svg data-testid="speaker-icon" />,
  MicrophoneIcon: () => <svg data-testid="microphone-icon" />,
  ExclamationTriangleIcon: () => <svg data-testid="warning-icon" />,
  CheckCircleIcon: () => <svg data-testid="check-circle-icon" />,
  XCircleIcon: () => <svg data-testid="x-circle-icon" />
}));

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;
const mockUseWebSocket = useWebSocket as vi.MockedFunction<typeof useWebSocket>;

const mockSupervisorData = {
  activeCalls: [
    {
      id: 'call-1',
      phoneNumber: '+1234567890',
      status: 'ACTIVE',
      duration: 180,
      agent: 'John Doe',
      agentId: 'agent-1',
      campaign: 'Sales Campaign',
      startTime: new Date(),
      sentiment: 'neutral',
      transcription: 'Hello, how can I help you today?'
    },
    {
      id: 'call-2',
      phoneNumber: '+0987654321',
      status: 'ON_HOLD',
      duration: 95,
      agent: 'Jane Smith',
      agentId: 'agent-2',
      campaign: 'Support Campaign',
      startTime: new Date(),
      sentiment: 'positive',
      transcription: 'Thank you for calling support.'
    }
  ],
  agents: [
    {
      id: 'agent-1',
      name: 'John Doe',
      status: 'busy',
      currentCallId: 'call-1',
      skillLevel: 'senior',
      department: 'sales',
      performance: {
        callsToday: 15,
        avgDuration: 240,
        satisfactionScore: 4.5
      }
    },
    {
      id: 'agent-2',
      name: 'Jane Smith',
      status: 'busy',
      currentCallId: 'call-2',
      skillLevel: 'expert',
      department: 'support',
      performance: {
        callsToday: 22,
        avgDuration: 180,
        satisfactionScore: 4.8
      }
    },
    {
      id: 'agent-3',
      name: 'Bob Wilson',
      status: 'available',
      currentCallId: null,
      skillLevel: 'junior',
      department: 'sales',
      performance: {
        callsToday: 8,
        avgDuration: 300,
        satisfactionScore: 4.2
      }
    }
  ],
  queueStats: {
    waiting: 3,
    averageWaitTime: 45,
    longestWait: 120,
    abandoned: 2
  },
  realTimeMetrics: {
    totalCalls: 45,
    answered: 40,
    missed: 3,
    abandoned: 2,
    avgAnswerTime: 8,
    serviceLevel: 92.5
  }
};

const queryClient = new QueryClient();

describe('SupervisorDashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockUseAuth.mockReturnValue({
      user: {
        id: 'supervisor-1',
        email: 'supervisor@test.com',
        role: 'SUPERVISOR',
        name: 'Test Supervisor'
      },
      isAuthenticated: true,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      refreshAuth: vi.fn(),
      hasRole: vi.fn().mockReturnValue(true),
      hasPermission: vi.fn().mockReturnValue(true),
      canAccessOrganization: vi.fn().mockReturnValue(true)
    });

    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: null,
      error: null,
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    // Mock tRPC calls
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockSupervisorData)
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderSupervisorDashboard = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SupervisorDashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders supervisor dashboard with main sections', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('Supervisor Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Active Calls')).toBeInTheDocument();
    expect(screen.getByText('Agent Status')).toBeInTheDocument();
    expect(screen.getByText('Queue Status')).toBeInTheDocument();
    expect(screen.getByText('Real-time Metrics')).toBeInTheDocument();
  });

  it('displays active calls with correct information', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('ACTIVE')).toBeInTheDocument();
    expect(screen.getByText('Sales Campaign')).toBeInTheDocument();
  });

  it('shows agent status information', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Wilson')).toBeInTheDocument();

    // Check status chips
    expect(screen.getAllByTestId('chip')).toHaveLength(6); // 3 agents × 2 chips each (status + skill)
  });

  it('displays queue statistics', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('3')).toBeInTheDocument(); // Waiting calls
    expect(screen.getByText('45s')).toBeInTheDocument(); // Average wait time
    expect(screen.getByText('2m 0s')).toBeInTheDocument(); // Longest wait
  });

  it('shows real-time metrics', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('45')).toBeInTheDocument(); // Total calls
    expect(screen.getByText('40')).toBeInTheDocument(); // Answered calls
    expect(screen.getByText('92.5%')).toBeInTheDocument(); // Service level
  });

  it('allows call monitoring and intervention', async () => {
    renderSupervisorDashboard();

    const monitorButtons = screen.getAllByTestId('eye-icon');
    expect(monitorButtons).toHaveLength(2); // One for each active call

    fireEvent.click(monitorButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
    });
  });

  it('displays real-time call transcriptions', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('Hello, how can I help you today?')).toBeInTheDocument();
    expect(screen.getByText('Thank you for calling support.')).toBeInTheDocument();
  });

  it('shows sentiment analysis for calls', () => {
    renderSupervisorDashboard();

    // Sentiment should be displayed as colored indicators
    const sentimentChips = screen.getAllByTestId('chip');
    expect(sentimentChips.length).toBeGreaterThan(0);
  });

  it('handles agent status changes', async () => {
    renderSupervisorDashboard();

    const statusSelects = screen.getAllByTestId('select');
    expect(statusSelects.length).toBeGreaterThan(0);

    fireEvent.change(statusSelects[0], { target: { value: 'break' } });

    await waitFor(() => {
      expect(statusSelects[0]).toHaveValue('break');
    });
  });

  it('allows call transfer between agents', async () => {
    renderSupervisorDashboard();

    const transferButtons = screen.getAllByText('Transfer');
    expect(transferButtons.length).toBeGreaterThan(0);

    fireEvent.click(transferButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Transfer Call')).toBeInTheDocument();
    });
  });

  it('displays performance metrics for agents', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('15')).toBeInTheDocument(); // John's calls today
    expect(screen.getByText('22')).toBeInTheDocument(); // Jane's calls today
    expect(screen.getByText('4.5')).toBeInTheDocument(); // John's satisfaction score
    expect(screen.getByText('4.8')).toBeInTheDocument(); // Jane's satisfaction score
  });

  it('shows WebSocket connection status', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('handles WebSocket disconnection gracefully', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      lastMessage: null,
      error: new Error('Connection lost'),
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    renderSupervisorDashboard();

    expect(screen.getByText('OFFLINE')).toBeInTheDocument();
    expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
  });

  it('filters calls by status', async () => {
    renderSupervisorDashboard();

    const statusFilter = screen.getByTestId('select');
    fireEvent.change(statusFilter, { target: { value: 'ACTIVE' } });

    await waitFor(() => {
      // Should only show active calls
      expect(screen.getByText('ACTIVE')).toBeInTheDocument();
      expect(screen.queryByText('ON_HOLD')).not.toBeInTheDocument();
    });
  });

  it('filters agents by department', async () => {
    renderSupervisorDashboard();

    const departmentFilter = screen.getByLabelText('Department Filter');
    fireEvent.change(departmentFilter, { target: { value: 'sales' } });

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Bob Wilson')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('displays call duration in real-time', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('3m 0s')).toBeInTheDocument(); // 180 seconds
    expect(screen.getByText('1m 35s')).toBeInTheDocument(); // 95 seconds
  });

  it('allows emergency call termination', async () => {
    renderSupervisorDashboard();

    const emergencyButtons = screen.getAllByTestId('stop-icon');
    expect(emergencyButtons.length).toBeGreaterThan(0);

    fireEvent.click(emergencyButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Emergency Termination')).toBeInTheDocument();
      expect(screen.getByText('Confirm')).toBeInTheDocument();
    });
  });

  it('shows call recording controls', () => {
    renderSupervisorDashboard();

    expect(screen.getAllByTestId('play-icon')).toHaveLength(2);
    expect(screen.getAllByTestId('pause-icon')).toHaveLength(2);
  });

  it('displays agent skill levels and departments', () => {
    renderSupervisorDashboard();

    expect(screen.getByText('senior')).toBeInTheDocument();
    expect(screen.getByText('expert')).toBeInTheDocument();
    expect(screen.getByText('junior')).toBeInTheDocument();
    expect(screen.getAllByText('sales')).toHaveLength(2);
    expect(screen.getByText('support')).toBeInTheDocument();
  });

  it('handles data refresh on WebSocket updates', async () => {
    const { rerender } = renderSupervisorDashboard();

    // Simulate WebSocket message with updated data
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: {
        type: 'CALL_UPDATE',
        data: { callId: 'call-1', status: 'COMPLETED' }
      },
      error: null,
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    rerender(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <SupervisorDashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      // Should reflect the updated call status
      expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    });
  });

  it('displays error state when data loading fails', () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('API Error'));

    renderSupervisorDashboard();

    expect(screen.getByText('Unable to load supervisor data')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('shows loading state while fetching data', () => {
    global.fetch = vi.fn().mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 1000))
    );

    renderSupervisorDashboard();

    expect(screen.getByText('Loading supervisor dashboard...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });
});
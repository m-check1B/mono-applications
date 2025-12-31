import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AgentStatus } from '@/components/monitoring/AgentStatus';
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
  Button: ({ children, onPress, isDisabled, color, variant, size, ...props }: any) => (
    <button
      onClick={onPress}
      disabled={isDisabled}
      data-color={color}
      data-variant={variant}
      data-size={size}
      {...props}
    >
      {children}
    </button>
  ),
  Chip: ({ children, color, variant, size }: { children: React.ReactNode; color?: string; variant?: string; size?: string }) => (
    <span data-testid="chip" data-color={color} data-variant={variant} data-size={size}>{children}</span>
  ),
  Avatar: ({ name, src, size }: { name?: string; src?: string; size?: string }) => (
    <div data-testid="avatar" data-name={name} data-src={src} data-size={size}>{name}</div>
  ),
  Badge: ({ children, color, content, placement }: { children: React.ReactNode; color?: string; content?: string; placement?: string }) => (
    <span data-testid="badge" data-color={color} data-content={content} data-placement={placement}>{children}</span>
  ),
  Progress: ({ label, value, color, size }: any) => (
    <div data-testid="progress" data-value={value} data-color={color} data-size={size}>
      <span>{label}</span>
    </div>
  ),
  Table: ({ children }: { children: React.ReactNode }) => <table data-testid="table">{children}</table>,
  TableHeader: ({ children }: { children: React.ReactNode }) => <thead data-testid="table-header">{children}</thead>,
  TableColumn: ({ children }: { children: React.ReactNode }) => <th data-testid="table-column">{children}</th>,
  TableBody: ({ children }: { children: React.ReactNode }) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: { children: React.ReactNode }) => <tr data-testid="table-row">{children}</tr>,
  TableCell: ({ children }: { children: React.ReactNode }) => <td data-testid="table-cell">{children}</td>,
  Switch: ({ isSelected, onValueChange, children, size }: any) => (
    <label data-testid="switch" data-size={size}>
      <input
        type="checkbox"
        checked={isSelected}
        onChange={(e) => onValueChange(e.target.checked)}
      />
      {children}
    </label>
  ),
  Select: ({ children, label, placeholder, onSelectionChange, selectedKeys }: any) => (
    <div data-testid="select-wrapper">
      {label && <label>{label}</label>}
      <select
        data-testid="select"
        data-placeholder={placeholder}
        onChange={(e) => onSelectionChange(new Set([e.target.value]))}
        value={selectedKeys ? Array.from(selectedKeys)[0] : ''}
      >
        <option value="">{placeholder}</option>
        {children}
      </select>
    </div>
  ),
  SelectItem: ({ children, key }: { children: React.ReactNode; key: string }) => (
    <option value={key}>{children}</option>
  ),
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="tooltip" title={content}>{children}</div>
  ),
  Modal: ({ children, isOpen }: { children: React.ReactNode; isOpen: boolean }) =>
    isOpen ? <div data-testid="modal">{children}</div> : null,
  ModalContent: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-content">{children}</div>,
  ModalHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-header">{children}</div>,
  ModalBody: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-body">{children}</div>,
  ModalFooter: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-footer">{children}</div>
}));

// Mock Heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  UserIcon: () => <svg data-testid="user-icon" />,
  PhoneIcon: () => <svg data-testid="phone-icon" />,
  ClockIcon: () => <svg data-testid="clock-icon" />,
  ChartBarIcon: () => <svg data-testid="chart-bar-icon" />,
  CheckCircleIcon: () => <svg data-testid="check-circle-icon" />,
  XCircleIcon: () => <svg data-testid="x-circle-icon" />,
  ExclamationTriangleIcon: () => <svg data-testid="warning-icon" />,
  PlayIcon: () => <svg data-testid="play-icon" />,
  PauseIcon: () => <svg data-testid="pause-icon" />,
  StopIcon: () => <svg data-testid="stop-icon" />,
  CogIcon: () => <svg data-testid="cog-icon" />,
  EyeIcon: () => <svg data-testid="eye-icon" />,
  SpeakerWaveIcon: () => <svg data-testid="speaker-icon" />,
  MicrophoneIcon: () => <svg data-testid="microphone-icon" />
}));

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;
const mockUseWebSocket = useWebSocket as vi.MockedFunction<typeof useWebSocket>;

const mockAgentStatusData = {
  agents: [
    {
      id: 'agent-1',
      name: 'John Doe',
      email: 'john.doe@company.com',
      status: 'available',
      department: 'sales',
      skillLevel: 'senior',
      shift: 'morning',
      location: 'New York',
      avatar: '/avatars/john.jpg',
      currentCall: null,
      breakTime: null,
      loginTime: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
      lastActivity: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      stats: {
        callsToday: 15,
        talkTime: 3600, // 1 hour in seconds
        avgDuration: 240, // 4 minutes
        satisfactionScore: 4.5,
        callsAnswered: 14,
        callsMissed: 1,
        transferRate: 5.2,
        holdTime: 45
      },
      performance: {
        daily: { target: 20, achieved: 15 },
        weekly: { target: 100, achieved: 78 },
        monthly: { target: 400, achieved: 312 }
      }
    },
    {
      id: 'agent-2',
      name: 'Jane Smith',
      email: 'jane.smith@company.com',
      status: 'busy',
      department: 'support',
      skillLevel: 'expert',
      shift: 'afternoon',
      location: 'Los Angeles',
      avatar: '/avatars/jane.jpg',
      currentCall: {
        id: 'call-123',
        phoneNumber: '+1234567890',
        startTime: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
        customerName: 'Alice Johnson',
        callType: 'support'
      },
      breakTime: null,
      loginTime: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
      lastActivity: new Date(),
      stats: {
        callsToday: 22,
        talkTime: 4800, // 1.33 hours in seconds
        avgDuration: 218, // 3.6 minutes
        satisfactionScore: 4.8,
        callsAnswered: 22,
        callsMissed: 0,
        transferRate: 2.1,
        holdTime: 23
      },
      performance: {
        daily: { target: 25, achieved: 22 },
        weekly: { target: 125, achieved: 115 },
        monthly: { target: 500, achieved: 445 }
      }
    },
    {
      id: 'agent-3',
      name: 'Bob Wilson',
      email: 'bob.wilson@company.com',
      status: 'break',
      department: 'sales',
      skillLevel: 'junior',
      shift: 'evening',
      location: 'Chicago',
      avatar: '/avatars/bob.jpg',
      currentCall: null,
      breakTime: new Date(Date.now() - 15 * 60 * 1000), // Started break 15 minutes ago
      loginTime: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      lastActivity: new Date(Date.now() - 15 * 60 * 1000),
      stats: {
        callsToday: 8,
        talkTime: 1800, // 0.5 hours in seconds
        avgDuration: 225, // 3.75 minutes
        satisfactionScore: 4.2,
        callsAnswered: 7,
        callsMissed: 1,
        transferRate: 8.5,
        holdTime: 67
      },
      performance: {
        daily: { target: 15, achieved: 8 },
        weekly: { target: 75, achieved: 42 },
        monthly: { target: 300, achieved: 186 }
      }
    },
    {
      id: 'agent-4',
      name: 'Alice Johnson',
      email: 'alice.johnson@company.com',
      status: 'offline',
      department: 'support',
      skillLevel: 'senior',
      shift: 'night',
      location: 'Remote',
      avatar: '/avatars/alice.jpg',
      currentCall: null,
      breakTime: null,
      loginTime: null,
      lastActivity: new Date(Date.now() - 24 * 60 * 60 * 1000), // Yesterday
      stats: {
        callsToday: 0,
        talkTime: 0,
        avgDuration: 0,
        satisfactionScore: 0,
        callsAnswered: 0,
        callsMissed: 0,
        transferRate: 0,
        holdTime: 0
      },
      performance: {
        daily: { target: 20, achieved: 0 },
        weekly: { target: 100, achieved: 85 },
        monthly: { target: 400, achieved: 342 }
      }
    }
  ],
  summary: {
    total: 4,
    available: 1,
    busy: 1,
    onBreak: 1,
    offline: 1,
    avgSatisfaction: 4.4,
    totalCallsToday: 45,
    totalTalkTime: 10200, // 2.83 hours
    activeCallsCount: 1
  }
};

const queryClient = new QueryClient();

describe('AgentStatus Component', () => {
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
      json: () => Promise.resolve(mockAgentStatusData)
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderAgentStatus = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AgentStatus />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders agent status dashboard with main sections', () => {
    renderAgentStatus();

    expect(screen.getByText('Agent Status')).toBeInTheDocument();
    expect(screen.getByText('Team Overview')).toBeInTheDocument();
    expect(screen.getByText('Agent Details')).toBeInTheDocument();
  });

  it('displays team summary statistics', () => {
    renderAgentStatus();

    expect(screen.getByText('Total: 4')).toBeInTheDocument();
    expect(screen.getByText('Available: 1')).toBeInTheDocument();
    expect(screen.getByText('Busy: 1')).toBeInTheDocument();
    expect(screen.getByText('On Break: 1')).toBeInTheDocument();
    expect(screen.getByText('Offline: 1')).toBeInTheDocument();
  });

  it('shows agent cards with basic information', () => {
    renderAgentStatus();

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Bob Wilson')).toBeInTheDocument();
    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
  });

  it('displays agent status with correct styling', () => {
    renderAgentStatus();

    const availableChip = screen.getByText('available');
    const busyChip = screen.getByText('busy');
    const breakChip = screen.getByText('break');
    const offlineChip = screen.getByText('offline');

    expect(availableChip).toBeInTheDocument();
    expect(busyChip).toBeInTheDocument();
    expect(breakChip).toBeInTheDocument();
    expect(offlineChip).toBeInTheDocument();
  });

  it('shows agent skill levels and departments', () => {
    renderAgentStatus();

    expect(screen.getByText('senior')).toBeInTheDocument();
    expect(screen.getByText('expert')).toBeInTheDocument();
    expect(screen.getByText('junior')).toBeInTheDocument();
    expect(screen.getAllByText('sales')).toHaveLength(2);
    expect(screen.getAllByText('support')).toHaveLength(2);
  });

  it('displays current call information for busy agents', () => {
    renderAgentStatus();

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    expect(screen.getByText('10m 0s')).toBeInTheDocument(); // Call duration
  });

  it('shows break time for agents on break', () => {
    renderAgentStatus();

    expect(screen.getByText('Break: 15m')).toBeInTheDocument();
  });

  it('displays agent performance statistics', () => {
    renderAgentStatus();

    expect(screen.getByText('Calls: 15')).toBeInTheDocument();
    expect(screen.getByText('4.5')).toBeInTheDocument(); // Satisfaction score
    expect(screen.getByText('1h 0m')).toBeInTheDocument(); // Talk time
  });

  it('allows filtering agents by status', async () => {
    renderAgentStatus();

    const statusFilter = screen.getByTestId('select');
    fireEvent.change(statusFilter, { target: { value: 'available' } });

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('allows filtering agents by department', async () => {
    renderAgentStatus();

    const departmentFilter = screen.getByLabelText('Department');
    fireEvent.change(departmentFilter, { target: { value: 'sales' } });

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Bob Wilson')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('shows agent avatar and location', () => {
    renderAgentStatus();

    expect(screen.getByText('New York')).toBeInTheDocument();
    expect(screen.getByText('Los Angeles')).toBeInTheDocument();
    expect(screen.getByText('Chicago')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();

    const avatars = screen.getAllByTestId('avatar');
    expect(avatars).toHaveLength(4);
  });

  it('displays login time and last activity', () => {
    renderAgentStatus();

    expect(screen.getByText('Login: 4h ago')).toBeInTheDocument();
    expect(screen.getByText('Last: 5m ago')).toBeInTheDocument();
  });

  it('allows manual status changes for agents', async () => {
    renderAgentStatus();

    const statusButton = screen.getAllByText('Change Status')[0];
    fireEvent.click(statusButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Change Agent Status')).toBeInTheDocument();
    });

    const statusSelect = screen.getByTestId('select');
    fireEvent.change(statusSelect, { target: { value: 'break' } });

    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/agents/agent-1/status'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('shows detailed agent statistics in modal', async () => {
    renderAgentStatus();

    const viewDetailsButtons = screen.getAllByTestId('eye-icon');
    fireEvent.click(viewDetailsButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Agent Details - John Doe')).toBeInTheDocument();
      expect(screen.getByText('Calls Answered: 14')).toBeInTheDocument();
      expect(screen.getByText('Calls Missed: 1')).toBeInTheDocument();
      expect(screen.getByText('Transfer Rate: 5.2%')).toBeInTheDocument();
    });
  });

  it('displays performance progress indicators', () => {
    renderAgentStatus();

    const progressBars = screen.getAllByTestId('progress');
    expect(progressBars.length).toBeGreaterThan(0);

    expect(screen.getByText('75%')).toBeInTheDocument(); // Daily: 15/20
    expect(screen.getByText('78%')).toBeInTheDocument(); // Weekly: 78/100
  });

  it('shows shift information', () => {
    renderAgentStatus();

    expect(screen.getByText('morning')).toBeInTheDocument();
    expect(screen.getByText('afternoon')).toBeInTheDocument();
    expect(screen.getByText('evening')).toBeInTheDocument();
    expect(screen.getByText('night')).toBeInTheDocument();
  });

  it('handles real-time status updates via WebSocket', async () => {
    const { rerender } = renderAgentStatus();

    // Simulate WebSocket message with status update
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: {
        type: 'AGENT_STATUS_UPDATE',
        data: { agentId: 'agent-1', status: 'busy', currentCall: { id: 'call-456' } }
      },
      error: null,
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    rerender(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AgentStatus />
        </BrowserRouter>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('busy')).toBeInTheDocument();
    });
  });

  it('displays WebSocket connection status', () => {
    renderAgentStatus();

    expect(screen.getByText('LIVE')).toBeInTheDocument();
    expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument();
  });

  it('handles WebSocket disconnection gracefully', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      lastMessage: null,
      error: new Error('Connection lost'),
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    renderAgentStatus();

    expect(screen.getByText('OFFLINE')).toBeInTheDocument();
    expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
  });

  it('allows bulk status changes', async () => {
    renderAgentStatus();

    // Select multiple agents
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);
    fireEvent.click(checkboxes[1]);

    await waitFor(() => {
      expect(screen.getByText('Bulk Actions')).toBeInTheDocument();
      expect(screen.getByText('Set Available')).toBeInTheDocument();
      expect(screen.getByText('Set Break')).toBeInTheDocument();
    });
  });

  it('displays agent call history', async () => {
    renderAgentStatus();

    const historyButtons = screen.getAllByText('Call History');
    fireEvent.click(historyButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Call History - John Doe')).toBeInTheDocument();
    });
  });

  it('shows real-time performance metrics', () => {
    renderAgentStatus();

    expect(screen.getByText('Avg Duration: 4m 0s')).toBeInTheDocument();
    expect(screen.getByText('Hold Time: 45s')).toBeInTheDocument();
    expect(screen.getByText('Satisfaction: 4.5/5')).toBeInTheDocument();
  });

  it('allows setting agent skills and preferences', async () => {
    renderAgentStatus();

    const settingsButtons = screen.getAllByTestId('cog-icon');
    fireEvent.click(settingsButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Agent Settings - John Doe')).toBeInTheDocument();
      expect(screen.getByText('Skills')).toBeInTheDocument();
      expect(screen.getByText('Preferences')).toBeInTheDocument();
    });
  });

  it('displays error state when data loading fails', () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('API Error'));

    renderAgentStatus();

    expect(screen.getByText('Unable to load agent status')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('shows loading state while fetching data', () => {
    global.fetch = vi.fn().mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 1000))
    );

    renderAgentStatus();

    expect(screen.getByText('Loading agent status...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });
});
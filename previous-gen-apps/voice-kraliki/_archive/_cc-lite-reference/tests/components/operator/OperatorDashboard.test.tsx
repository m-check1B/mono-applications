import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { OperatorDashboard } from '@/components/OperatorDashboard';
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
  Progress: ({ label, value, color }: any) => (
    <div data-testid="progress" data-value={value} data-color={color}>
      <span>{label}</span>
    </div>
  ),
  Chip: ({ children, color, variant }: { children: React.ReactNode; color?: string; variant?: string }) => (
    <span data-testid="chip" data-color={color} data-variant={variant}>{children}</span>
  ),
  Table: ({ children }: { children: React.ReactNode }) => <table data-testid="table">{children}</table>,
  TableHeader: ({ children }: { children: React.ReactNode }) => <thead data-testid="table-header">{children}</thead>,
  TableColumn: ({ children }: { children: React.ReactNode }) => <th data-testid="table-column">{children}</th>,
  TableBody: ({ children }: { children: React.ReactNode }) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: { children: React.ReactNode }) => <tr data-testid="table-row">{children}</tr>,
  TableCell: ({ children }: { children: React.ReactNode }) => <td data-testid="table-cell">{children}</td>,
  Switch: ({ isSelected, onValueChange, children }: any) => (
    <label data-testid="switch">
      <input
        type="checkbox"
        checked={isSelected}
        onChange={(e) => onValueChange(e.target.checked)}
      />
      {children}
    </label>
  ),
  Avatar: ({ name, src }: { name?: string; src?: string }) => (
    <div data-testid="avatar" data-name={name} data-src={src}>{name}</div>
  ),
  Badge: ({ children, color, content }: { children: React.ReactNode; color?: string; content?: string }) => (
    <span data-testid="badge" data-color={color} data-content={content}>{children}</span>
  ),
  Input: ({ label, placeholder, value, onChange, type }: any) => (
    <div>
      {label && <label>{label}</label>}
      <input
        data-testid="input"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        type={type}
      />
    </div>
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
  PhoneIcon: () => <svg data-testid="phone-icon" />,
  PhoneArrowUpRightIcon: () => <svg data-testid="phone-outgoing-icon" />,
  PhoneArrowDownLeftIcon: () => <svg data-testid="phone-incoming-icon" />,
  PlayIcon: () => <svg data-testid="play-icon" />,
  PauseIcon: () => <svg data-testid="pause-icon" />,
  StopIcon: () => <svg data-testid="stop-icon" />,
  SpeakerWaveIcon: () => <svg data-testid="speaker-icon" />,
  SpeakerXMarkIcon: () => <svg data-testid="speaker-mute-icon" />,
  MicrophoneIcon: () => <svg data-testid="microphone-icon" />,
  UserIcon: () => <svg data-testid="user-icon" />,
  ClockIcon: () => <svg data-testid="clock-icon" />,
  CheckCircleIcon: () => <svg data-testid="check-circle-icon" />,
  XCircleIcon: () => <svg data-testid="x-circle-icon" />,
  ExclamationTriangleIcon: () => <svg data-testid="warning-icon" />,
  ChartBarIcon: () => <svg data-testid="chart-bar-icon" />,
  Cog6ToothIcon: () => <svg data-testid="settings-icon" />
}));

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;
const mockUseWebSocket = useWebSocket as vi.MockedFunction<typeof useWebSocket>;

const mockOperatorData = {
  agent: {
    id: 'agent-1',
    name: 'John Doe',
    status: 'available',
    email: 'john.doe@company.com',
    department: 'sales',
    skillLevel: 'senior',
    currentCallId: null,
    stats: {
      callsToday: 12,
      totalDuration: 2880, // 48 minutes
      avgDuration: 240, // 4 minutes
      satisfactionScore: 4.5,
      callsAnswered: 11,
      callsMissed: 1
    }
  },
  currentCall: null,
  queuedCalls: [
    {
      id: 'queued-1',
      phoneNumber: '+1234567890',
      waitTime: 45,
      priority: 'high',
      campaign: 'Sales Follow-up',
      customerInfo: {
        name: 'Alice Johnson',
        previousCalls: 2,
        lastContact: '2024-01-15'
      }
    },
    {
      id: 'queued-2',
      phoneNumber: '+0987654321',
      waitTime: 23,
      priority: 'normal',
      campaign: 'Product Support',
      customerInfo: {
        name: 'Bob Smith',
        previousCalls: 0,
        lastContact: null
      }
    }
  ],
  recentCalls: [
    {
      id: 'recent-1',
      phoneNumber: '+1122334455',
      status: 'COMPLETED',
      duration: 180,
      startTime: new Date(Date.now() - 300000), // 5 minutes ago
      endTime: new Date(Date.now() - 120000), // 2 minutes ago
      outcome: 'sale',
      notes: 'Customer purchased premium package'
    },
    {
      id: 'recent-2',
      phoneNumber: '+5566778899',
      status: 'MISSED',
      duration: 0,
      startTime: new Date(Date.now() - 600000), // 10 minutes ago
      endTime: null,
      outcome: 'no_answer',
      notes: 'Voicemail left'
    }
  ],
  dailyTargets: {
    calls: 20,
    callsCompleted: 12,
    talkTime: 240, // 4 hours in minutes
    talkTimeCompleted: 48,
    sales: 5,
    salesCompleted: 3
  }
};

const queryClient = new QueryClient();

describe('OperatorDashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockUseAuth.mockReturnValue({
      user: {
        id: 'agent-1',
        email: 'john.doe@company.com',
        role: 'AGENT',
        name: 'John Doe'
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
      json: () => Promise.resolve(mockOperatorData)
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderOperatorDashboard = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <OperatorDashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders operator dashboard with main sections', () => {
    renderOperatorDashboard();

    expect(screen.getByText('Operator Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Agent Status')).toBeInTheDocument();
    expect(screen.getByText('Call Queue')).toBeInTheDocument();
    expect(screen.getByText('Daily Progress')).toBeInTheDocument();
    expect(screen.getByText('Recent Calls')).toBeInTheDocument();
  });

  it('displays agent status controls', () => {
    renderOperatorDashboard();

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Available')).toBeInTheDocument();
    expect(screen.getByTestId('switch')).toBeInTheDocument();
  });

  it('shows call control buttons', () => {
    renderOperatorDashboard();

    expect(screen.getByTestId('phone-icon')).toBeInTheDocument();
    expect(screen.getByText('Answer Next')).toBeInTheDocument();
    expect(screen.getByText('Manual Dial')).toBeInTheDocument();
    expect(screen.getByText('Take Break')).toBeInTheDocument();
  });

  it('displays queued calls with customer information', () => {
    renderOperatorDashboard();

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    expect(screen.getByText('Sales Follow-up')).toBeInTheDocument();
    expect(screen.getByText('45s')).toBeInTheDocument(); // Wait time
  });

  it('shows daily progress tracking', () => {
    renderOperatorDashboard();

    expect(screen.getByText('Calls: 12/20')).toBeInTheDocument();
    expect(screen.getByText('Talk Time: 48/240 min')).toBeInTheDocument();
    expect(screen.getByText('Sales: 3/5')).toBeInTheDocument();
  });

  it('displays recent call history', () => {
    renderOperatorDashboard();

    expect(screen.getByText('+1122334455')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText('3m 0s')).toBeInTheDocument(); // Duration
    expect(screen.getByText('sale')).toBeInTheDocument();
  });

  it('allows agent status changes', async () => {
    renderOperatorDashboard();

    const statusSwitch = screen.getByTestId('switch').querySelector('input');
    expect(statusSwitch).toBeInTheDocument();

    fireEvent.click(statusSwitch!);

    await waitFor(() => {
      expect(statusSwitch).toBeChecked();
    });
  });

  it('handles incoming call simulation', async () => {
    renderOperatorDashboard();

    const answerButton = screen.getByText('Answer Next');
    fireEvent.click(answerButton);

    await waitFor(() => {
      expect(screen.getByText('Incoming Call')).toBeInTheDocument();
      expect(screen.getByText('Answer')).toBeInTheDocument();
      expect(screen.getByText('Decline')).toBeInTheDocument();
    });
  });

  it('opens manual dial modal', async () => {
    renderOperatorDashboard();

    const dialButton = screen.getByText('Manual Dial');
    fireEvent.click(dialButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Manual Dial')).toBeInTheDocument();
      expect(screen.getByTestId('input')).toBeInTheDocument();
    });
  });

  it('displays call statistics in real-time', () => {
    renderOperatorDashboard();

    expect(screen.getByText('12')).toBeInTheDocument(); // Calls today
    expect(screen.getByText('4.5')).toBeInTheDocument(); // Satisfaction score
    expect(screen.getByText('4m 0s')).toBeInTheDocument(); // Average duration
  });

  it('shows priority indicators for queued calls', () => {
    renderOperatorDashboard();

    const priorityChips = screen.getAllByTestId('chip');
    const highPriorityChip = priorityChips.find(chip =>
      chip.textContent === 'high' && chip.getAttribute('data-color') === 'danger'
    );
    expect(highPriorityChip).toBeInTheDocument();
  });

  it('handles break mode toggle', async () => {
    renderOperatorDashboard();

    const breakButton = screen.getByText('Take Break');
    fireEvent.click(breakButton);

    await waitFor(() => {
      expect(screen.getByText('On Break')).toBeInTheDocument();
      expect(screen.getByText('End Break')).toBeInTheDocument();
    });
  });

  it('displays customer history for queued calls', () => {
    renderOperatorDashboard();

    expect(screen.getByText('Previous: 2 calls')).toBeInTheDocument();
    expect(screen.getByText('Last: 2024-01-15')).toBeInTheDocument();
  });

  it('shows call outcome options', async () => {
    renderOperatorDashboard();

    // Simulate being in a call
    mockOperatorData.currentCall = {
      id: 'active-call',
      phoneNumber: '+1111111111',
      startTime: new Date(),
      customerName: 'Test Customer'
    };

    const { rerender } = renderOperatorDashboard();
    rerender(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <OperatorDashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText('End Call')).toBeInTheDocument();

    const endCallButton = screen.getByText('End Call');
    fireEvent.click(endCallButton);

    await waitFor(() => {
      expect(screen.getByText('Call Outcome')).toBeInTheDocument();
      expect(screen.getByText('Sale')).toBeInTheDocument();
      expect(screen.getByText('No Sale')).toBeInTheDocument();
      expect(screen.getByText('Callback')).toBeInTheDocument();
    });
  });

  it('tracks call duration in real-time', () => {
    // Simulate active call
    const activeCallData = {
      ...mockOperatorData,
      currentCall: {
        id: 'active-call',
        phoneNumber: '+1111111111',
        startTime: new Date(Date.now() - 120000), // 2 minutes ago
        customerName: 'Test Customer'
      }
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(activeCallData)
    });

    renderOperatorDashboard();

    expect(screen.getByText('Call Duration: 2m 0s')).toBeInTheDocument();
  });

  it('displays WebSocket connection status', () => {
    renderOperatorDashboard();

    expect(screen.getByText('LIVE')).toBeInTheDocument();
    expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument();
  });

  it('handles WebSocket disconnection', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      lastMessage: null,
      error: new Error('Connection lost'),
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    renderOperatorDashboard();

    expect(screen.getByText('OFFLINE')).toBeInTheDocument();
    expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
  });

  it('shows progress bars for daily targets', () => {
    renderOperatorDashboard();

    const progressBars = screen.getAllByTestId('progress');
    expect(progressBars).toHaveLength(3); // Calls, Talk Time, Sales

    // Check progress values
    expect(screen.getByText('60%')).toBeInTheDocument(); // Calls: 12/20
    expect(screen.getByText('20%')).toBeInTheDocument(); // Talk Time: 48/240
    expect(screen.getByText('60%')).toBeInTheDocument(); // Sales: 3/5
  });

  it('allows adding notes to calls', async () => {
    renderOperatorDashboard();

    const addNotesButton = screen.getByText('Add Notes');
    fireEvent.click(addNotesButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Call Notes')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter call notes...')).toBeInTheDocument();
    });
  });

  it('displays call recording controls during active calls', () => {
    const activeCallData = {
      ...mockOperatorData,
      currentCall: {
        id: 'active-call',
        phoneNumber: '+1111111111',
        startTime: new Date(),
        customerName: 'Test Customer',
        isRecording: true
      }
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(activeCallData)
    });

    renderOperatorDashboard();

    expect(screen.getByTestId('pause-icon')).toBeInTheDocument(); // Recording controls
    expect(screen.getByText('Recording')).toBeInTheDocument();
  });

  it('shows agent performance metrics', () => {
    renderOperatorDashboard();

    expect(screen.getByText('Calls Answered: 11')).toBeInTheDocument();
    expect(screen.getByText('Calls Missed: 1')).toBeInTheDocument();
    expect(screen.getByText('Satisfaction: 4.5/5')).toBeInTheDocument();
  });

  it('handles call transfer functionality', async () => {
    renderOperatorDashboard();

    const transferButton = screen.getByText('Transfer');
    fireEvent.click(transferButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Transfer Call')).toBeInTheDocument();
      expect(screen.getByText('Select Agent')).toBeInTheDocument();
    });
  });

  it('displays error state when data loading fails', () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('API Error'));

    renderOperatorDashboard();

    expect(screen.getByText('Unable to load operator dashboard')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('shows loading state while fetching data', () => {
    global.fetch = vi.fn().mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 1000))
    );

    renderOperatorDashboard();

    expect(screen.getByText('Loading operator dashboard...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });
});
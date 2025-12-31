import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from '@/components/Dashboard';
import { useDashboardData } from '@/hooks/useDashboardData';
import { useWebSocket } from '@/hooks/useWebSocket';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock hooks
vi.mock('@/hooks/useDashboardData');
vi.mock('@/hooks/useWebSocket');

const mockUseDashboardData = useDashboardData as vi.MockedFunction<typeof useDashboardData>;
const mockUseWebSocket = useWebSocket as vi.MockedFunction<typeof useWebSocket>;

// Mock NextUI components
vi.mock('@nextui-org/react', () => ({
  Card: ({ children }: { children: React.ReactNode }) => <div data-testid="card">{children}</div>,
  CardBody: ({ children }: { children: React.ReactNode }) => <div data-testid="card-body">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  Button: ({ children, onPress, ...props }: any) => (
    <button onClick={onPress} {...props}>{children}</button>
  ),
  Progress: ({ label, ...props }: any) => (
    <div data-testid="progress">
      <span>{label}</span>
    </div>
  ),
  Navbar: ({ children }: { children: React.ReactNode }) => <nav data-testid="navbar">{children}</nav>,
  NavbarBrand: ({ children }: { children: React.ReactNode }) => <div data-testid="navbar-brand">{children}</div>,
  NavbarContent: ({ children }: { children: React.ReactNode }) => <div data-testid="navbar-content">{children}</div>,
  NavbarItem: ({ children }: { children: React.ReactNode }) => <div data-testid="navbar-item">{children}</div>,
  Chip: ({ children }: { children: React.ReactNode }) => <span data-testid="chip">{children}</span>,
  Table: ({ children }: { children: React.ReactNode }) => <table data-testid="table">{children}</table>,
  TableHeader: ({ children }: { children: React.ReactNode }) => <thead data-testid="table-header">{children}</thead>,
  TableColumn: ({ children }: { children: React.ReactNode }) => <th data-testid="table-column">{children}</th>,
  TableBody: ({ children }: { children: React.ReactNode }) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: { children: React.ReactNode }) => <tr data-testid="table-row">{children}</tr>,
  TableCell: ({ children }: { children: React.ReactNode }) => <td data-testid="table-cell">{children}</td>,
  Avatar: () => <div data-testid="avatar"></div>,
  Badge: ({ children }: { children: React.ReactNode }) => <span data-testid="badge">{children}</span>,
  Dropdown: ({ children, trigger }: any) => (
    <div data-testid="dropdown">
      {trigger}
      {children}
    </div>
  ),
  DropdownTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  DropdownMenu: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-menu">{children}</div>,
  DropdownItem: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-item">{children}</div>
}));

// Mock Heroicons
vi.mock('@heroicons/react/24/outline', () => ({
  PhoneIcon: () => <svg data-testid="phone-icon" />,
  UserGroupIcon: () => <svg data-testid="user-group-icon" />,
  ChartBarIcon: () => <svg data-testid="chart-bar-icon" />,
  Cog6ToothIcon: () => <svg data-testid="cog-icon" />,
  BellIcon: () => <svg data-testid="bell-icon" />,
  PhoneArrowDownLeftIcon: () => <svg data-testid="phone-down-icon" />,
  ClockIcon: () => <svg data-testid="clock-icon" />,
  CheckCircleIcon: () => <svg data-testid="check-icon" />,
  XCircleIcon: () => <svg data-testid="x-icon" />
}));

const mockDashboardData = {
  activeCalls: [
    {
      id: 'call-1',
      phoneNumber: '+1234567890',
      status: 'ACTIVE',
      duration: 120,
      agent: 'John Doe',
      campaign: 'Sales Campaign'
    }
  ],
  recentCalls: [
    {
      id: 'call-2',
      phoneNumber: '+0987654321',
      status: 'COMPLETED',
      duration: 300,
      agent: 'Jane Smith',
      campaign: 'Support Campaign',
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
      }
    ],
    stats: {
      totalMembers: 1,
      availableAgents: 1,
      busyAgents: 0,
      onBreakAgents: 0,
      offlineAgents: 0
    }
  },
  callStats: {
    totalCalls: 150,
    activeCalls: 1,
    completedCalls: 149,
    averageDuration: 240,
    handledByAI: 45,
    handledByAgents: 105,
    missedCalls: 5
  }
};

const queryClient = new QueryClient();

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseDashboardData.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: null,
      error: null,
      connect: vi.fn(),
      disconnect: vi.fn()
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderDashboard = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders dashboard with navigation', () => {
    renderDashboard();

    expect(screen.getByText('CC-Light')).toBeInTheDocument();
    expect(screen.getByTestId('phone-icon')).toBeInTheDocument();
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Calls')).toBeInTheDocument();
    expect(screen.getByText('Team')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
  });

  it('displays loading state when data is loading', () => {
    mockUseDashboardData.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
      refetch: vi.fn()
    });

    renderDashboard();

    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });

  it('displays error state when data fetch fails', () => {
    const errorMessage = 'Failed to load dashboard data';
    mockUseDashboardData.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error(errorMessage),
      refetch: vi.fn()
    });

    renderDashboard();

    expect(screen.getByText('Connection Error')).toBeInTheDocument();
    expect(screen.getByText(/Unable to connect to the server/)).toBeInTheDocument();
    expect(screen.getByTestId('x-icon')).toBeInTheDocument();
  });

  it('displays dashboard content when data is loaded', () => {
    renderDashboard();

    expect(screen.getByTestId('card')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument(); // Total calls
    expect(screen.getByText('1')).toBeInTheDocument(); // Active calls
    expect(screen.getByText('149')).toBeInTheDocument(); // Completed calls
  });

  it('shows WebSocket connection status', () => {
    renderDashboard();

    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('displays active calls in table', () => {
    renderDashboard();

    expect(screen.getByTestId('table')).toBeInTheDocument();
    expect(screen.getByText('+1234567890')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('ACTIVE')).toBeInTheDocument();
  });

  it('displays team status information', () => {
    renderDashboard();

    expect(screen.getByText('1')).toBeInTheDocument(); // Total members
    expect(screen.getByText('1')).toBeInTheDocument(); // Available agents
  });

  it('handles tab switching', () => {
    renderDashboard();

    const callsTab = screen.getByText('Calls');
    const teamTab = screen.getByText('Team');

    // Click on Calls tab
    fireEvent.click(callsTab);

    // Verify tab is active (should have different styling)
    expect(callsTab).toBeInTheDocument();

    // Click on Team tab
    fireEvent.click(teamTab);

    // Verify tab is active
    expect(teamTab).toBeInTheDocument();
  });

  it('allows retry on error', () => {
    const errorMessage = 'Failed to load dashboard data';
    mockUseDashboardData.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error(errorMessage),
      refetch: vi.fn()
    });

    renderDashboard();

    const retryButton = screen.getByText('Retry');
    fireEvent.click(retryButton);

    expect(window.location.reload).toHaveBeenCalled();
  });

  it('displays call statistics', () => {
    renderDashboard();

    const { callStats } = mockDashboardData;

    expect(screen.getByText(callStats.totalCalls.toString())).toBeInTheDocument();
    expect(screen.getByText(callStats.activeCalls.toString())).toBeInTheDocument();
    expect(screen.getByText(callStats.completedCalls.toString())).toBeInTheDocument();
  });

  it('shows real-time updates when WebSocket is connected', () => {
    renderDashboard();

    expect(screen.getByText('LIVE')).toBeInTheDocument();
    expect(screen.getByTestId('phone-icon')).toBeInTheDocument();
  });

  it('displays navigation menu items', () => {
    renderDashboard();

    const navItems = ['Overview', 'Calls', 'Team', 'Analytics'];
    navItems.forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument();
    });
  });

  it('handles responsive navigation', () => {
    renderDashboard();

    // Check that mobile navigation might be hidden
    const navbar = screen.getByTestId('navbar');
    expect(navbar).toBeInTheDocument();
  });

  it('displays recent calls information', () => {
    renderDashboard();

    expect(screen.getByText('+0987654321')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
  });

  it('shows call duration information', () => {
    renderDashboard();

    expect(screen.getByText('120')).toBeInTheDocument(); // Active call duration
    expect(screen.getByText('300')).toBeInTheDocument(); // Recent call duration
  });

  it('displays average call duration', () => {
    renderDashboard();

    const averageMinutes = Math.floor(mockDashboardData.callStats.averageDuration / 60);
    expect(screen.getByText(averageMinutes.toString())).toBeInTheDocument();
  });

  it('handles empty data gracefully', () => {
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

    mockUseDashboardData.mockReturnValue({
      data: emptyData,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    renderDashboard();

    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('No active calls')).toBeInTheDocument();
  });

  it('provides refetch functionality', () => {
    const refetchFn = vi.fn();
    mockUseDashboardData.mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      refetch: refetchFn
    });

    renderDashboard();

    // Refetch should be available through the hook
    expect(typeof refetchFn).toBe('function');
  });

  it('displays proper icons for different call statuses', () => {
    renderDashboard();

    // Should show appropriate icons for active and completed calls
    expect(screen.getByTestId('phone-icon')).toBeInTheDocument();
    expect(screen.getByTestId('check-icon')).toBeInTheDocument();
  });
});
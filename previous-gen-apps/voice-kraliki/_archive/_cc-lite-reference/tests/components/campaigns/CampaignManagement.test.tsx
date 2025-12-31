import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CampaignManagement } from '@/components/campaigns/CampaignManagement';
import { useAuth } from '@/contexts/AuthContext';

// Mock dependencies
vi.mock('@/contexts/AuthContext');
vi.mock('@/services/trpc');

// Mock NextUI components
vi.mock('@nextui-org/react', () => ({
  Card: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="card" className={className}>{children}</div>
  ),
  CardBody: ({ children }: { children: React.ReactNode }) => <div data-testid="card-body">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  Button: ({ children, onPress, isDisabled, color, variant, size, startContent, endContent, ...props }: any) => (
    <button
      onClick={onPress}
      disabled={isDisabled}
      data-color={color}
      data-variant={variant}
      data-size={size}
      {...props}
    >
      {startContent}
      {children}
      {endContent}
    </button>
  ),
  Input: ({ label, placeholder, value, onChange, type, isRequired, isInvalid, errorMessage }: any) => (
    <div data-testid="input-wrapper">
      {label && <label>{label}</label>}
      <input
        data-testid="input"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        type={type}
        required={isRequired}
        aria-invalid={isInvalid}
      />
      {isInvalid && errorMessage && <span data-testid="error-message">{errorMessage}</span>}
    </div>
  ),
  Textarea: ({ label, placeholder, value, onChange, rows }: any) => (
    <div data-testid="textarea-wrapper">
      {label && <label>{label}</label>}
      <textarea
        data-testid="textarea"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        rows={rows}
      />
    </div>
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
  Table: ({ children }: { children: React.ReactNode }) => <table data-testid="table">{children}</table>,
  TableHeader: ({ children }: { children: React.ReactNode }) => <thead data-testid="table-header">{children}</thead>,
  TableColumn: ({ children }: { children: React.ReactNode }) => <th data-testid="table-column">{children}</th>,
  TableBody: ({ children }: { children: React.ReactNode }) => <tbody data-testid="table-body">{children}</tbody>,
  TableRow: ({ children }: { children: React.ReactNode }) => <tr data-testid="table-row">{children}</tr>,
  TableCell: ({ children }: { children: React.ReactNode }) => <td data-testid="table-cell">{children}</td>,
  Chip: ({ children, color, variant, size }: { children: React.ReactNode; color?: string; variant?: string; size?: string }) => (
    <span data-testid="chip" data-color={color} data-variant={variant} data-size={size}>{children}</span>
  ),
  Progress: ({ label, value, color, size }: any) => (
    <div data-testid="progress" data-value={value} data-color={color} data-size={size}>
      <span>{label}</span>
    </div>
  ),
  Modal: ({ children, isOpen, onOpenChange }: { children: React.ReactNode; isOpen: boolean; onOpenChange?: Function }) => (
    isOpen ? (
      <div data-testid="modal" onClick={() => onOpenChange && onOpenChange(false)}>
        {children}
      </div>
    ) : null
  ),
  ModalContent: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-content">{children}</div>,
  ModalHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-header">{children}</div>,
  ModalBody: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-body">{children}</div>,
  ModalFooter: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-footer">{children}</div>,
  Tabs: ({ children, selectedKey, onSelectionChange }: any) => (
    <div data-testid="tabs" data-selected-key={selectedKey} onClick={() => onSelectionChange && onSelectionChange('tab')}>
      {children}
    </div>
  ),
  Tab: ({ children, key, title }: { children: React.ReactNode; key: string; title: string }) => (
    <div data-testid="tab" data-key={key} data-title={title}>{children}</div>
  ),
  Dropdown: ({ children, trigger }: any) => (
    <div data-testid="dropdown">
      {trigger}
      {children}
    </div>
  ),
  DropdownTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  DropdownMenu: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-menu">{children}</div>,
  DropdownItem: ({ children, key, onPress }: { children: React.ReactNode; key: string; onPress?: Function }) => (
    <div data-testid="dropdown-item" data-key={key} onClick={() => onPress && onPress()}>{children}</div>
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
  PlusIcon: () => <svg data-testid="plus-icon" />,
  PlayIcon: () => <svg data-testid="play-icon" />,
  PauseIcon: () => <svg data-testid="pause-icon" />,
  StopIcon: () => <svg data-testid="stop-icon" />,
  PencilIcon: () => <svg data-testid="pencil-icon" />,
  TrashIcon: () => <svg data-testid="trash-icon" />,
  EyeIcon: () => <svg data-testid="eye-icon" />,
  DocumentArrowUpIcon: () => <svg data-testid="upload-icon" />,
  DocumentArrowDownIcon: () => <svg data-testid="download-icon" />,
  ChartBarIcon: () => <svg data-testid="chart-bar-icon" />,
  ClockIcon: () => <svg data-testid="clock-icon" />,
  PhoneIcon: () => <svg data-testid="phone-icon" />,
  CheckCircleIcon: () => <svg data-testid="check-circle-icon" />,
  XCircleIcon: () => <svg data-testid="x-circle-icon" />,
  ExclamationTriangleIcon: () => <svg data-testid="warning-icon" />
}));

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;

const mockCampaignsData = {
  campaigns: [
    {
      id: 'campaign-1',
      name: 'Q1 Sales Outreach',
      description: 'Quarterly sales campaign targeting new prospects',
      status: 'active',
      type: 'outbound',
      priority: 'high',
      startDate: '2024-01-01',
      endDate: '2024-03-31',
      totalContacts: 1500,
      completedCalls: 450,
      pendingCalls: 1050,
      successRate: 12.5,
      conversionRate: 8.2,
      budget: 50000,
      spent: 18750,
      assignedAgents: ['agent-1', 'agent-2', 'agent-3'],
      settings: {
        maxCallsPerDay: 50,
        callBackDelay: 24,
        voicemailEnabled: true,
        recordingEnabled: true,
        scriptId: 'script-1'
      },
      stats: {
        answered: 360,
        voicemail: 60,
        busy: 20,
        noAnswer: 10,
        sales: 37,
        leadGenerated: 125
      }
    },
    {
      id: 'campaign-2',
      name: 'Customer Support Follow-up',
      description: 'Following up on recent support tickets',
      status: 'paused',
      type: 'inbound',
      priority: 'medium',
      startDate: '2024-01-15',
      endDate: '2024-02-15',
      totalContacts: 800,
      completedCalls: 600,
      pendingCalls: 200,
      successRate: 85.2,
      conversionRate: 92.1,
      budget: 25000,
      spent: 18900,
      assignedAgents: ['agent-2', 'agent-4'],
      settings: {
        maxCallsPerDay: 30,
        callBackDelay: 48,
        voicemailEnabled: false,
        recordingEnabled: true,
        scriptId: 'script-2'
      },
      stats: {
        answered: 510,
        voicemail: 45,
        busy: 30,
        noAnswer: 15,
        sales: 0,
        leadGenerated: 285
      }
    },
    {
      id: 'campaign-3',
      name: 'Product Launch Promotion',
      description: 'Promoting new product features to existing customers',
      status: 'draft',
      type: 'outbound',
      priority: 'low',
      startDate: '2024-02-01',
      endDate: '2024-02-28',
      totalContacts: 2000,
      completedCalls: 0,
      pendingCalls: 2000,
      successRate: 0,
      conversionRate: 0,
      budget: 75000,
      spent: 0,
      assignedAgents: [],
      settings: {
        maxCallsPerDay: 75,
        callBackDelay: 12,
        voicemailEnabled: true,
        recordingEnabled: true,
        scriptId: null
      },
      stats: {
        answered: 0,
        voicemail: 0,
        busy: 0,
        noAnswer: 0,
        sales: 0,
        leadGenerated: 0
      }
    }
  ],
  availableAgents: [
    { id: 'agent-1', name: 'John Doe', status: 'available' },
    { id: 'agent-2', name: 'Jane Smith', status: 'busy' },
    { id: 'agent-3', name: 'Bob Wilson', status: 'available' },
    { id: 'agent-4', name: 'Alice Johnson', status: 'offline' }
  ],
  scripts: [
    { id: 'script-1', name: 'Sales Pitch v2.1', type: 'sales' },
    { id: 'script-2', name: 'Support Follow-up', type: 'support' },
    { id: 'script-3', name: 'Product Demo', type: 'demo' }
  ]
};

const queryClient = new QueryClient();

describe('CampaignManagement Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockUseAuth.mockReturnValue({
      user: {
        id: 'user-1',
        email: 'manager@test.com',
        role: 'ADMIN',
        name: 'Test Manager'
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

    // Mock tRPC calls
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockCampaignsData)
    });
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderCampaignManagement = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CampaignManagement />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders campaign management with main sections', () => {
    renderCampaignManagement();

    expect(screen.getByText('Campaign Management')).toBeInTheDocument();
    expect(screen.getByText('Create Campaign')).toBeInTheDocument();
    expect(screen.getByTestId('table')).toBeInTheDocument();
  });

  it('displays campaigns in table format', () => {
    renderCampaignManagement();

    expect(screen.getByText('Q1 Sales Outreach')).toBeInTheDocument();
    expect(screen.getByText('Customer Support Follow-up')).toBeInTheDocument();
    expect(screen.getByText('Product Launch Promotion')).toBeInTheDocument();
  });

  it('shows campaign status with correct styling', () => {
    renderCampaignManagement();

    const activeChip = screen.getByText('active');
    const pausedChip = screen.getByText('paused');
    const draftChip = screen.getByText('draft');

    expect(activeChip).toBeInTheDocument();
    expect(pausedChip).toBeInTheDocument();
    expect(draftChip).toBeInTheDocument();
  });

  it('displays campaign statistics', () => {
    renderCampaignManagement();

    expect(screen.getByText('1500')).toBeInTheDocument(); // Total contacts
    expect(screen.getByText('450')).toBeInTheDocument(); // Completed calls
    expect(screen.getByText('12.5%')).toBeInTheDocument(); // Success rate
    expect(screen.getByText('8.2%')).toBeInTheDocument(); // Conversion rate
  });

  it('opens create campaign modal', async () => {
    renderCampaignManagement();

    const createButton = screen.getByText('Create Campaign');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Create New Campaign')).toBeInTheDocument();
    });
  });

  it('validates campaign creation form', async () => {
    renderCampaignManagement();

    const createButton = screen.getByText('Create Campaign');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
    });

    const nameInput = screen.getByLabelText('Campaign Name');
    const submitButton = screen.getByText('Create');

    // Try submitting without required fields
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    // Fill required fields
    fireEvent.change(nameInput, { target: { value: 'New Test Campaign' } });

    const descriptionTextarea = screen.getByLabelText('Description');
    fireEvent.change(descriptionTextarea, { target: { value: 'Test description' } });

    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
    });
  });

  it('allows campaign editing', async () => {
    renderCampaignManagement();

    const editButtons = screen.getAllByTestId('pencil-icon');
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Edit Campaign')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Q1 Sales Outreach')).toBeInTheDocument();
    });
  });

  it('handles campaign deletion with confirmation', async () => {
    renderCampaignManagement();

    const deleteButtons = screen.getAllByTestId('trash-icon');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Delete Campaign')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to delete this campaign?')).toBeInTheDocument();
    });

    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/campaigns/campaign-1'),
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  it('displays campaign progress indicators', () => {
    renderCampaignManagement();

    const progressBars = screen.getAllByTestId('progress');
    expect(progressBars.length).toBeGreaterThan(0);

    // Check for progress values
    expect(screen.getByText('30%')).toBeInTheDocument(); // 450/1500 completed
    expect(screen.getByText('75%')).toBeInTheDocument(); // 600/800 completed
  });

  it('filters campaigns by status', async () => {
    renderCampaignManagement();

    const statusFilter = screen.getByTestId('select');
    fireEvent.change(statusFilter, { target: { value: 'active' } });

    await waitFor(() => {
      expect(screen.getByText('Q1 Sales Outreach')).toBeInTheDocument();
      expect(screen.queryByText('Customer Support Follow-up')).not.toBeInTheDocument();
    });
  });

  it('allows campaign start/pause/stop actions', async () => {
    renderCampaignManagement();

    // Test play button for draft campaign
    const playButtons = screen.getAllByTestId('play-icon');
    fireEvent.click(playButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/campaigns/campaign-3/start'),
        expect.objectContaining({ method: 'POST' })
      );
    });

    // Test pause button for active campaign
    const pauseButtons = screen.getAllByTestId('pause-icon');
    fireEvent.click(pauseButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/campaigns/campaign-1/pause'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('shows campaign analytics modal', async () => {
    renderCampaignManagement();

    const analyticsButtons = screen.getAllByTestId('chart-bar-icon');
    fireEvent.click(analyticsButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Campaign Analytics')).toBeInTheDocument();
      expect(screen.getByText('Answered: 360')).toBeInTheDocument();
      expect(screen.getByText('Sales: 37')).toBeInTheDocument();
    });
  });

  it('handles contact list upload', async () => {
    renderCampaignManagement();

    const uploadButtons = screen.getAllByTestId('upload-icon');
    fireEvent.click(uploadButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Upload Contact List')).toBeInTheDocument();
      expect(screen.getByText('Select CSV File')).toBeInTheDocument();
    });

    const fileInput = screen.getByTestId('input');
    const file = new File(['name,phone\nJohn,+1234567890'], 'contacts.csv', { type: 'text/csv' });

    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);

    await waitFor(() => {
      expect(screen.getByText('contacts.csv')).toBeInTheDocument();
    });
  });

  it('displays assigned agents for campaigns', () => {
    renderCampaignManagement();

    expect(screen.getByText('3 agents')).toBeInTheDocument(); // Q1 Sales Outreach
    expect(screen.getByText('2 agents')).toBeInTheDocument(); // Customer Support Follow-up
    expect(screen.getByText('0 agents')).toBeInTheDocument(); // Product Launch Promotion
  });

  it('allows agent assignment to campaigns', async () => {
    renderCampaignManagement();

    const assignAgentButtons = screen.getAllByText('Assign Agents');
    fireEvent.click(assignAgentButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Assign Agents to Campaign')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('shows campaign budget and spending', () => {
    renderCampaignManagement();

    expect(screen.getByText('$50,000')).toBeInTheDocument(); // Budget
    expect(screen.getByText('$18,750')).toBeInTheDocument(); // Spent
    expect(screen.getByText('37.5%')).toBeInTheDocument(); // Budget usage
  });

  it('handles campaign cloning', async () => {
    renderCampaignManagement();

    const cloneButtons = screen.getAllByText('Clone');
    fireEvent.click(cloneButtons[0]);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Clone Campaign')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Q1 Sales Outreach (Copy)')).toBeInTheDocument();
    });
  });

  it('displays campaign priorities with colors', () => {
    renderCampaignManagement();

    const highPriorityChip = screen.getByText('high');
    const mediumPriorityChip = screen.getByText('medium');
    const lowPriorityChip = screen.getByText('low');

    expect(highPriorityChip).toBeInTheDocument();
    expect(mediumPriorityChip).toBeInTheDocument();
    expect(lowPriorityChip).toBeInTheDocument();
  });

  it('shows campaign dates and duration', () => {
    renderCampaignManagement();

    expect(screen.getByText('2024-01-01')).toBeInTheDocument(); // Start date
    expect(screen.getByText('2024-03-31')).toBeInTheDocument(); // End date
  });

  it('handles campaign search and filtering', async () => {
    renderCampaignManagement();

    const searchInput = screen.getByPlaceholderText('Search campaigns...');
    fireEvent.change(searchInput, { target: { value: 'Sales' } });

    await waitFor(() => {
      expect(screen.getByText('Q1 Sales Outreach')).toBeInTheDocument();
      expect(screen.queryByText('Customer Support Follow-up')).not.toBeInTheDocument();
    });
  });

  it('displays campaign type indicators', () => {
    renderCampaignManagement();

    expect(screen.getAllByText('outbound')).toHaveLength(2);
    expect(screen.getByText('inbound')).toBeInTheDocument();
  });

  it('shows real-time campaign updates', async () => {
    renderCampaignManagement();

    // Simulate real-time update
    const updatedData = {
      ...mockCampaignsData,
      campaigns: [
        {
          ...mockCampaignsData.campaigns[0],
          completedCalls: 455,
          stats: {
            ...mockCampaignsData.campaigns[0].stats,
            answered: 365,
            sales: 38
          }
        },
        ...mockCampaignsData.campaigns.slice(1)
      ]
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(updatedData)
    });

    // Trigger refresh
    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(screen.getByText('455')).toBeInTheDocument(); // Updated completed calls
      expect(screen.getByText('38')).toBeInTheDocument(); // Updated sales count
    });
  });

  it('handles bulk campaign operations', async () => {
    renderCampaignManagement();

    // Select multiple campaigns
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);
    fireEvent.click(checkboxes[1]);

    await waitFor(() => {
      expect(screen.getByText('Bulk Actions')).toBeInTheDocument();
      expect(screen.getByText('Start Selected')).toBeInTheDocument();
      expect(screen.getByText('Pause Selected')).toBeInTheDocument();
      expect(screen.getByText('Delete Selected')).toBeInTheDocument();
    });
  });

  it('displays error state when data loading fails', () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('API Error'));

    renderCampaignManagement();

    expect(screen.getByText('Unable to load campaigns')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('shows loading state while fetching data', () => {
    global.fetch = vi.fn().mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 1000))
    );

    renderCampaignManagement();

    expect(screen.getByText('Loading campaigns...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });
});
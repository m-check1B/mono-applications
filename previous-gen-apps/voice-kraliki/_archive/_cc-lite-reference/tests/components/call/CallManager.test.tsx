import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CallManager } from '@/components/call/CallManager';
import { useAuth } from '@/contexts/AuthContext';
import { useWebSocket } from '@/hooks/useWebSocket';

// Mock dependencies
vi.mock('@/contexts/AuthContext');
vi.mock('@/hooks/useWebSocket');
vi.mock('@/services/trpc');

// Mock Twilio Voice SDK
vi.mock('@twilio/voice-sdk', () => ({
  Device: vi.fn().mockImplementation(() => ({
    register: vi.fn(),
    unregister: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    state: 'unregistered',
    calls: [],
    audio: {
      setInputDevice: vi.fn(),
      setOutputDevice: vi.fn(),
      speakerDevices: new Map(),
      ringtoneDevices: new Map()
    }
  })),
  Call: vi.fn().mockImplementation(() => ({
    on: vi.fn(),
    accept: vi.fn(),
    reject: vi.fn(),
    disconnect: vi.fn(),
    mute: vi.fn(),
    sendDigits: vi.fn(),
    status: () => 'pending'
  }))
}));

// Mock NextUI components
vi.mock('@nextui-org/react', () => ({
  Card: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div data-testid="card" className={className}>{children}</div>
  ),
  CardBody: ({ children }: { children: React.ReactNode }) => <div data-testid="card-body">{children}</div>,
  CardHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="card-header">{children}</div>,
  Button: ({ children, onPress, isDisabled, color, variant, size, isIconOnly, ...props }: any) => (
    <button
      onClick={onPress}
      disabled={isDisabled}
      data-color={color}
      data-variant={variant}
      data-size={size}
      data-icon-only={isIconOnly}
      {...props}
    >
      {children}
    </button>
  ),
  Input: ({ label, placeholder, value, onChange, type, startContent, endContent }: any) => (
    <div data-testid="input-wrapper">
      {label && <label>{label}</label>}
      {startContent}
      <input
        data-testid="input"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        type={type}
      />
      {endContent}
    </div>
  ),
  Slider: ({ label, value, onChange, min, max, step }: any) => (
    <div data-testid="slider-wrapper">
      {label && <label>{label}</label>}
      <input
        data-testid="slider"
        type="range"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        min={min}
        max={max}
        step={step}
      />
    </div>
  ),
  Progress: ({ label, value, color, size }: any) => (
    <div data-testid="progress" data-value={value} data-color={color} data-size={size}>
      <span>{label}</span>
    </div>
  ),
  Chip: ({ children, color, variant }: { children: React.ReactNode; color?: string; variant?: string }) => (
    <span data-testid="chip" data-color={color} data-variant={variant}>{children}</span>
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
  Modal: ({ children, isOpen }: { children: React.ReactNode; isOpen: boolean }) =>
    isOpen ? <div data-testid="modal">{children}</div> : null,
  ModalContent: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-content">{children}</div>,
  ModalHeader: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-header">{children}</div>,
  ModalBody: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-body">{children}</div>,
  ModalFooter: ({ children }: { children: React.ReactNode }) => <div data-testid="modal-footer">{children}</div>,
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="tooltip" title={content}>{children}</div>
  ),
  Switch: ({ isSelected, onValueChange, children }: any) => (
    <label data-testid="switch">
      <input
        type="checkbox"
        checked={isSelected}
        onChange={(e) => onValueChange(e.target.checked)}
      />
      {children}
    </label>
  )
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
  NoSymbolIcon: () => <svg data-testid="mute-icon" />,
  ArrowPathIcon: () => <svg data-testid="transfer-icon" />,
  ClockIcon: () => <svg data-testid="clock-icon" />,
  ChatBubbleLeftIcon: () => <svg data-testid="notes-icon" />,
  Cog6ToothIcon: () => <svg data-testid="settings-icon" />,
  SignalIcon: () => <svg data-testid="signal-icon" />,
  XMarkIcon: () => <svg data-testid="x-mark-icon" />,
  CheckIcon: () => <svg data-testid="check-icon" />
}));

const mockUseAuth = useAuth as vi.MockedFunction<typeof useAuth>;
const mockUseWebSocket = useWebSocket as vi.MockedFunction<typeof useWebSocket>;

const mockCallData = {
  currentCall: {
    id: 'call-123',
    phoneNumber: '+1234567890',
    customerName: 'John Customer',
    startTime: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
    status: 'connected',
    direction: 'inbound',
    callSid: 'CA123456789',
    duration: 300, // 5 minutes
    muted: false,
    onHold: false,
    recording: true,
    transferring: false,
    quality: {
      mos: 4.2,
      jitter: 15,
      latency: 120,
      packetLoss: 0.5
    },
    customerInfo: {
      id: 'customer-456',
      name: 'John Customer',
      email: 'john@customer.com',
      previousCalls: 3,
      notes: ['Previous issue with billing', 'Interested in upgrade'],
      tags: ['VIP', 'Technical']
    }
  },
  availableDevices: {
    audio: {
      input: [
        { deviceId: 'default', label: 'Default Microphone' },
        { deviceId: 'mic-1', label: 'USB Microphone' }
      ],
      output: [
        { deviceId: 'default', label: 'Default Speaker' },
        { deviceId: 'speaker-1', label: 'Bluetooth Headset' }
      ]
    }
  },
  callHistory: [
    {
      id: 'call-122',
      phoneNumber: '+1234567890',
      customerName: 'John Customer',
      startTime: new Date(Date.now() - 24 * 60 * 60 * 1000), // Yesterday
      endTime: new Date(Date.now() - 24 * 60 * 60 * 1000 + 10 * 60 * 1000),
      duration: 600,
      outcome: 'resolved',
      notes: 'Issue resolved successfully'
    }
  ],
  agentSettings: {
    autoAnswer: false,
    autoRecord: true,
    preferredInputDevice: 'default',
    preferredOutputDevice: 'default',
    ringtoneVolume: 80,
    micVolume: 85
  }
};

const queryClient = new QueryClient();

describe('CallManager Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockUseAuth.mockReturnValue({
      user: {
        id: 'agent-1',
        email: 'agent@test.com',
        role: 'AGENT',
        name: 'Test Agent'
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
      json: () => Promise.resolve(mockCallData)
    });

    // Mock audio API
    global.navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue({
        getTracks: () => []
      }),
      enumerateDevices: vi.fn().mockResolvedValue([
        { deviceId: 'default', kind: 'audioinput', label: 'Default Microphone' },
        { deviceId: 'mic-1', kind: 'audioinput', label: 'USB Microphone' },
        { deviceId: 'default', kind: 'audiooutput', label: 'Default Speaker' },
        { deviceId: 'speaker-1', kind: 'audiooutput', label: 'Bluetooth Headset' }
      ])
    } as any;
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  const renderCallManager = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <CallManager />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('renders call manager with main controls', () => {
    renderCallManager();

    expect(screen.getByText('Call Manager')).toBeInTheDocument();
    expect(screen.getByTestId('phone-icon')).toBeInTheDocument();
    expect(screen.getByText('Answer')).toBeInTheDocument();
    expect(screen.getByText('Decline')).toBeInTheDocument();
  });

  it('displays active call information', () => {
    renderCallManager();

    expect(screen.getByText('+1234567890')).toBeInTheDocument();
    expect(screen.getByText('John Customer')).toBeInTheDocument();
    expect(screen.getByText('5m 0s')).toBeInTheDocument(); // Call duration
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('shows call control buttons during active call', () => {
    renderCallManager();

    expect(screen.getByTestId('microphone-icon')).toBeInTheDocument(); // Mute
    expect(screen.getByTestId('pause-icon')).toBeInTheDocument(); // Hold
    expect(screen.getByTestId('transfer-icon')).toBeInTheDocument(); // Transfer
    expect(screen.getByTestId('stop-icon')).toBeInTheDocument(); // End call
  });

  it('handles mute/unmute functionality', async () => {
    renderCallManager();

    const muteButton = screen.getByTestId('microphone-icon').parentElement;
    fireEvent.click(muteButton!);

    await waitFor(() => {
      expect(screen.getByTestId('mute-icon')).toBeInTheDocument();
      expect(screen.getByText('Muted')).toBeInTheDocument();
    });

    // Unmute
    fireEvent.click(muteButton!);

    await waitFor(() => {
      expect(screen.getByTestId('microphone-icon')).toBeInTheDocument();
      expect(screen.queryByText('Muted')).not.toBeInTheDocument();
    });
  });

  it('handles hold/unhold functionality', async () => {
    renderCallManager();

    const holdButton = screen.getByTestId('pause-icon').parentElement;
    fireEvent.click(holdButton!);

    await waitFor(() => {
      expect(screen.getByTestId('play-icon')).toBeInTheDocument();
      expect(screen.getByText('On Hold')).toBeInTheDocument();
    });

    // Resume
    fireEvent.click(holdButton!);

    await waitFor(() => {
      expect(screen.getByTestId('pause-icon')).toBeInTheDocument();
      expect(screen.queryByText('On Hold')).not.toBeInTheDocument();
    });
  });

  it('displays call quality indicators', () => {
    renderCallManager();

    expect(screen.getByText('4.2')).toBeInTheDocument(); // MOS score
    expect(screen.getByText('15ms')).toBeInTheDocument(); // Jitter
    expect(screen.getByText('120ms')).toBeInTheDocument(); // Latency
    expect(screen.getByText('0.5%')).toBeInTheDocument(); // Packet loss
  });

  it('shows customer information panel', () => {
    renderCallManager();

    expect(screen.getByText('Customer Info')).toBeInTheDocument();
    expect(screen.getByText('john@customer.com')).toBeInTheDocument();
    expect(screen.getByText('Previous calls: 3')).toBeInTheDocument();
    expect(screen.getByText('VIP')).toBeInTheDocument();
    expect(screen.getByText('Technical')).toBeInTheDocument();
  });

  it('allows adding call notes', async () => {
    renderCallManager();

    const notesButton = screen.getByTestId('notes-icon').parentElement;
    fireEvent.click(notesButton!);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Call Notes')).toBeInTheDocument();
    });

    const notesInput = screen.getByPlaceholderText('Add call notes...');
    fireEvent.change(notesInput, { target: { value: 'Customer inquiry about billing' } });

    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calls/call-123/notes'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('handles call transfer', async () => {
    renderCallManager();

    const transferButton = screen.getByTestId('transfer-icon').parentElement;
    fireEvent.click(transferButton!);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Transfer Call')).toBeInTheDocument();
    });

    const agentSelect = screen.getByTestId('select');
    fireEvent.change(agentSelect, { target: { value: 'agent-2' } });

    const transferConfirmButton = screen.getByText('Transfer');
    fireEvent.click(transferConfirmButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calls/call-123/transfer'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('displays recording status', () => {
    renderCallManager();

    expect(screen.getByText('Recording')).toBeInTheDocument();
    expect(screen.getByTestId('chip')).toHaveAttribute('data-color', 'danger');
  });

  it('handles call termination', async () => {
    renderCallManager();

    const endCallButton = screen.getByTestId('stop-icon').parentElement;
    fireEvent.click(endCallButton!);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('End Call')).toBeInTheDocument();
      expect(screen.getByText('Call Outcome')).toBeInTheDocument();
    });

    const outcomeSelect = screen.getByTestId('select');
    fireEvent.change(outcomeSelect, { target: { value: 'resolved' } });

    const endButton = screen.getByText('End Call');
    fireEvent.click(endButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calls/call-123/end'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('allows DTMF digit input', async () => {
    renderCallManager();

    const dtmfButton = screen.getByText('Keypad');
    fireEvent.click(dtmfButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('DTMF Keypad')).toBeInTheDocument();
    });

    const digitButton = screen.getByText('1');
    fireEvent.click(digitButton);

    await waitFor(() => {
      expect(screen.getByDisplayValue('1')).toBeInTheDocument();
    });

    const sendButton = screen.getByText('Send');
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calls/call-123/dtmf'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ digits: '1' })
        })
      );
    });
  });

  it('shows audio device settings', async () => {
    renderCallManager();

    const settingsButton = screen.getByTestId('settings-icon').parentElement;
    fireEvent.click(settingsButton!);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Audio Settings')).toBeInTheDocument();
      expect(screen.getByText('Input Device')).toBeInTheDocument();
      expect(screen.getByText('Output Device')).toBeInTheDocument();
    });

    const inputSelect = screen.getAllByTestId('select')[0];
    fireEvent.change(inputSelect, { target: { value: 'mic-1' } });

    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/agents/settings'),
        expect.objectContaining({ method: 'PUT' })
      );
    });
  });

  it('displays call timer and updates in real-time', () => {
    renderCallManager();

    expect(screen.getByText('5m 0s')).toBeInTheDocument();

    // Simulate time passing
    vi.advanceTimersByTime(60000); // 1 minute

    expect(screen.getByText('6m 0s')).toBeInTheDocument();
  });

  it('handles incoming call notifications', async () => {
    const incomingCallData = {
      ...mockCallData,
      currentCall: {
        ...mockCallData.currentCall,
        status: 'ringing'
      }
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(incomingCallData)
    });

    renderCallManager();

    expect(screen.getByText('Incoming Call')).toBeInTheDocument();
    expect(screen.getByText('Answer')).toBeInTheDocument();
    expect(screen.getByText('Decline')).toBeInTheDocument();

    const answerButton = screen.getByText('Answer');
    fireEvent.click(answerButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calls/call-123/answer'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });

  it('shows manual dial functionality', async () => {
    const noCallData = {
      ...mockCallData,
      currentCall: null
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(noCallData)
    });

    renderCallManager();

    expect(screen.getByText('Manual Dial')).toBeInTheDocument();

    const dialButton = screen.getByText('Manual Dial');
    fireEvent.click(dialButton);

    await waitFor(() => {
      expect(screen.getByTestId('modal')).toBeInTheDocument();
      expect(screen.getByText('Place Call')).toBeInTheDocument();
    });

    const phoneInput = screen.getByPlaceholderText('Enter phone number');
    fireEvent.change(phoneInput, { target: { value: '+1987654321' } });

    const callButton = screen.getByText('Call');
    fireEvent.click(callButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/calls/dial'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ phoneNumber: '+1987654321' })
        })
      );
    });
  });

  it('displays previous call history', () => {
    renderCallManager();

    expect(screen.getByText('Call History')).toBeInTheDocument();
    expect(screen.getByText('Issue resolved successfully')).toBeInTheDocument();
  });

  it('handles WebSocket call events', async () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: true,
      lastMessage: {
        type: 'CALL_EVENT',
        data: {
          callId: 'call-123',
          event: 'quality_warning',
          quality: { mos: 2.1, jitter: 45 }
        }
      },
      error: null,
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    renderCallManager();

    await waitFor(() => {
      expect(screen.getByText('Poor Connection')).toBeInTheDocument();
      expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
    });
  });

  it('shows volume controls', () => {
    renderCallManager();

    expect(screen.getByTestId('slider')).toBeInTheDocument();
    expect(screen.getByText('Volume')).toBeInTheDocument();

    const volumeSlider = screen.getByTestId('slider');
    fireEvent.change(volumeSlider, { target: { value: '90' } });

    expect(volumeSlider).toHaveValue('90');
  });

  it('displays error state when call fails', () => {
    const errorCallData = {
      ...mockCallData,
      currentCall: {
        ...mockCallData.currentCall,
        status: 'failed',
        error: 'Connection timeout'
      }
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(errorCallData)
    });

    renderCallManager();

    expect(screen.getByText('Call Failed')).toBeInTheDocument();
    expect(screen.getByText('Connection timeout')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('handles WebSocket disconnection during call', () => {
    mockUseWebSocket.mockReturnValue({
      isConnected: false,
      lastMessage: null,
      error: new Error('Connection lost'),
      connect: vi.fn(),
      disconnect: vi.fn()
    });

    renderCallManager();

    expect(screen.getByText('Connection Lost')).toBeInTheDocument();
    expect(screen.getByTestId('warning-icon')).toBeInTheDocument();
  });

  it('shows loading state while initializing call manager', () => {
    global.fetch = vi.fn().mockImplementation(() =>
      new Promise(resolve => setTimeout(resolve, 1000))
    );

    renderCallManager();

    expect(screen.getByText('Initializing call manager...')).toBeInTheDocument();
    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });
});
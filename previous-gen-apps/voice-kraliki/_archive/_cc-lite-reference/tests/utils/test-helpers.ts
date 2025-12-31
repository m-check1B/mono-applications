import { vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

// API Response Mocks
export const createMockApiResponse = <T>(data: T, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data),
  headers: new Map(),
  redirected: false,
  statusText: status >= 200 && status < 300 ? 'OK' : 'Error',
  type: 'basic',
  url: '',
  clone: () => createMockApiResponse(data, status)
});

export const createMockErrorResponse = (error: string, status = 400) => ({
  ok: false,
  status,
  json: async () => ({ error }),
  text: async () => JSON.stringify({ error }),
  headers: new Map(),
  redirected: false,
  statusText: 'Error',
  type: 'basic',
  url: '',
  clone: () => createMockErrorResponse(error, status)
});

// WebSocket Mock
export const createMockWebSocket = () => {
  const mockWebSocket = {
    readyState: 1,
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    onopen: null as any,
    onmessage: null as any,
    onclose: null as any,
    onerror: null as any,
    CONNECTING: 0,
    OPEN: 1,
    CLOSING: 2,
    CLOSED: 3
  };
  return mockWebSocket;
};

// Mock Service Creators
export const createMockAuthService = () => ({
  login: vi.fn(),
  logout: vi.fn(),
  refreshToken: vi.fn(),
  getCurrentUser: vi.fn(),
  hasPermission: vi.fn(),
  hasRole: vi.fn()
});

export const createMockDashboardService = () => ({
  getDashboardData: vi.fn(),
  getCallDetails: vi.fn(),
  getTeamStatus: vi.fn(),
  getCallStats: vi.fn(),
  getRecentCalls: vi.fn()
});

export const createMockWebSocketService = () => ({
  connect: vi.fn(),
  disconnect: vi.fn(),
  sendMessage: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  isConnected: vi.fn(),
  subscribe: vi.fn(),
  unsubscribe: vi.fn()
});

// User Mock Data
export const mockUsers = {
  admin: {
    id: 'admin-123',
    email: 'admin@cc-light.com',
    firstName: 'Admin',
    lastName: 'User',
    role: 'ADMIN' as const,
    status: 'ACTIVE' as const,
    organizationId: 'org-123',
    organization: {
      id: 'org-123',
      name: 'Test Organization',
      domain: 'test.example.com'
    },
    preferences: {
      language: 'en',
      timezone: 'UTC',
      notifications: true,
      autoAnswer: false
    }
  },
  supervisor: {
    id: 'supervisor-123',
    email: 'supervisor@cc-light.com',
    firstName: 'Supervisor',
    lastName: 'User',
    role: 'SUPERVISOR' as const,
    status: 'ACTIVE' as const,
    organizationId: 'org-123',
    organization: {
      id: 'org-123',
      name: 'Test Organization',
      domain: 'test.example.com'
    },
    preferences: {
      language: 'en',
      timezone: 'UTC',
      notifications: true,
      autoAnswer: false
    }
  },
  agent: {
    id: 'agent-123',
    email: 'agent@cc-light.com',
    firstName: 'Agent',
    lastName: 'User',
    role: 'AGENT' as const,
    status: 'ACTIVE' as const,
    organizationId: 'org-123',
    organization: {
      id: 'org-123',
      name: 'Test Organization',
      domain: 'test.example.com'
    },
    preferences: {
      language: 'en',
      timezone: 'UTC',
      notifications: true,
      autoAnswer: true
    }
  }
};

// Call Mock Data
export const mockCalls = {
  active: [
    {
      id: 'call-1',
      phoneNumber: '+1234567890',
      status: 'ACTIVE',
      direction: 'INBOUND',
      duration: 120,
      agent: mockUsers.agent,
      campaign: 'Sales Campaign',
      startTime: new Date(Date.now() - 120000).toISOString(),
      transcript: [],
      confidence: 0
    },
    {
      id: 'call-2',
      phoneNumber: '+0987654321',
      status: 'ACTIVE',
      direction: 'OUTBOUND',
      duration: 85,
      agent: mockUsers.supervisor,
      campaign: 'Support Campaign',
      startTime: new Date(Date.now() - 85000).toISOString(),
      transcript: [],
      confidence: 0
    }
  ],
  completed: [
    {
      id: 'call-3',
      phoneNumber: '+5551234567',
      status: 'COMPLETED',
      direction: 'INBOUND',
      duration: 300,
      agent: mockUsers.agent,
      campaign: 'Sales Campaign',
      startTime: new Date(Date.now() - 300000).toISOString(),
      endTime: new Date(Date.now() - 0).toISOString(),
      transcript: [
        { text: 'Hello, thank you for calling', confidence: 0.95, timestamp: Date.now() - 295000 },
        { text: 'How can I help you today?', confidence: 0.92, timestamp: Date.now() - 290000 }
      ],
      confidence: 0.93
    }
  ],
  missed: [
    {
      id: 'call-4',
      phoneNumber: '+1112223333',
      status: 'MISSED',
      direction: 'INBOUND',
      duration: 0,
      agent: null,
      campaign: 'Support Campaign',
      startTime: new Date(Date.now() - 60000).toISOString(),
      endTime: new Date(Date.now() - 55000).toISOString(),
      transcript: [],
      confidence: 0
    }
  ]
};

// Dashboard Mock Data
export const mockDashboardData = {
  activeCalls: mockCalls.active,
  recentCalls: [...mockCalls.completed, ...mockCalls.missed],
  teamStatus: {
    members: [
      {
        id: mockUsers.agent.id,
        name: `${mockUsers.agent.firstName} ${mockUsers.agent.lastName}`,
        email: mockUsers.agent.email,
        status: 'available' as const,
        activeCall: null,
        skills: ['sales', 'support'],
        lastActivity: new Date().toISOString()
      },
      {
        id: mockUsers.supervisor.id,
        name: `${mockUsers.supervisor.firstName} ${mockUsers.supervisor.lastName}`,
        email: mockUsers.supervisor.email,
        status: 'busy' as const,
        activeCall: mockCalls.active[1].id,
        skills: ['supervision', 'support'],
        lastActivity: new Date().toISOString()
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

// Performance Testing Helpers
export const measurePerformance = async <T>(fn: () => Promise<T>): Promise<{
  result: T;
  duration: number;
  memory: number;
}> => {
  const startTime = performance.now();
  const startMemory = process.memoryUsage().heapUsed;

  const result = await fn();

  const endTime = performance.now();
  const endMemory = process.memoryUsage().heapUsed;

  return {
    result,
    duration: endTime - startTime,
    memory: (endMemory - startMemory) / 1024 / 1024 // MB
  };
};

export const waitForCondition = (
  condition: () => boolean,
  timeout = 5000,
  interval = 100
): Promise<void> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const checkCondition = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Condition not met within timeout'));
      } else {
        setTimeout(checkCondition, interval);
      }
    };

    checkCondition();
  });
};

// React Testing Helpers
export const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
});

export const waitForAsyncAction = () => new Promise(resolve => setTimeout(resolve, 0));

// Event Testing Helpers
export const createMockEvent = (type: string, data = {}) => ({
  preventDefault: vi.fn(),
  stopPropagation: vi.fn(),
  currentTarget: {
    value: '',
    ...data
  },
  target: {
    value: '',
    ...data
  },
  ...data
});

export const simulateFormSubmission = (form: HTMLFormElement) => {
  const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
  form.dispatchEvent(submitEvent);
};

// Mock Intersection Observer
export const setupIntersectionObserverMock = () => {
  const mockIntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  }));

  global.IntersectionObserver = mockIntersectionObserver;

  return mockIntersectionObserver;
};

// Mock Resize Observer
export const setupResizeObserverMock = () => {
  const mockResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  }));

  global.ResizeObserver = mockResizeObserver;

  return mockResizeObserver;
};

// Mock Media Query
export const setupMediaQueryMock = () => {
  const mockMatchMedia = vi.fn().mockImplementation(query => ({
    matches: query.includes('min-width'),
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }));

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: mockMatchMedia
  });

  return mockMatchMedia;
};

// Mock Geolocation
export const setupGeolocationMock = () => {
  const mockGeolocation = {
    getCurrentPosition: vi.fn(),
    watchPosition: vi.fn(),
    clearWatch: vi.fn()
  };

  Object.defineProperty(navigator, 'geolocation', {
    writable: true,
    value: mockGeolocation
  });

  return mockGeolocation;
};

// Animation Testing Helpers
export const advanceTimersByTime = async (ms: number) => {
  vi.advanceTimersByTime(ms);
  await waitForAsyncAction();
};

export const runAllTimersAsync = async () => {
  vi.runAllTimers();
  await waitForAsyncAction();
};

// Component Testing Helpers
export const getTestAttribute = (element: HTMLElement, name: string) => {
  return element.getAttribute(`data-testid`) === name ? element : null;
};

export const findTestAttribute = (container: HTMLElement, name: string) => {
  return container.querySelector(`[data-testid="${name}"]`);
};

// Form Testing Helpers
export const fillForm = async (form: HTMLElement, data: Record<string, string>) => {
  for (const [key, value] of Object.entries(data)) {
    const input = form.querySelector(`[name="${key}"]`) as HTMLInputElement;
    if (input) {
      await act(async () => {
        input.value = value;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }
  }
};

export const submitForm = async (form: HTMLElement) => {
  await act(async () => {
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(submitEvent);
  });
};

// Network Testing Helpers
export const createNetworkError = (message = 'Network error') => {
  return new Error(message);
};

export const createTimeoutError = (message = 'Request timeout') => {
  return new Error(message);
};

// Assertion Helpers
export const expectCalledWith = (mock: vi.Mock, ...expectedArgs: any[]) => {
  expect(mock).toHaveBeenCalledWith(...expectedArgs);
};

export const expectCalledOnce = (mock: vi.Mock) => {
  expect(mock).toHaveBeenCalledTimes(1);
};

export const expectNotCalled = (mock: vi.Mock) => {
  expect(mock).not.toHaveBeenCalled();
};

// Console Mocking Helpers
export const mockConsole = () => {
  const originalConsole = { ...console };
  const mockConsole = {
    log: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
    debug: vi.fn()
  };

  global.console = mockConsole as any;

  const restoreConsole = () => {
    global.console = originalConsole;
  };

  return { mockConsole, restoreConsole };
};

// Storage Mocking Helpers
export const createMockStorage = () => {
  const store: Record<string, string> = {};

  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = String(value);
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
    length: 0,
    key: vi.fn((index: number) => Object.keys(store)[index] || null)
  };
};

export const setupStorageMocks = () => {
  const localStorageMock = createMockStorage();
  const sessionStorageMock = createMockStorage();

  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
  });

  Object.defineProperty(window, 'sessionStorage', {
    value: sessionStorageMock
  });

  return { localStorageMock, sessionStorageMock };
};

// File Upload Testing Helpers
export const createMockFile = (name: string, type: string, size: number) => {
  const file = new File([''], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

export const createMockFileList = (files: File[]) => {
  const fileList = {
    length: files.length,
    item: (index: number) => files[index] || null,
    [Symbol.iterator]: function* () {
      for (const file of files) {
        yield file;
      }
    }
  } as any;

  files.forEach((file, index) => {
    fileList[index] = file;
  });

  return fileList;
};

// Timer Testing Helpers
export const setupTimerMocks = () => {
  vi.useFakeTimers();

  const advanceTimers = (ms: number) => {
    vi.advanceTimersByTime(ms);
  };

  const runAllTimers = () => {
    vi.runAllTimers();
  };

  const restoreTimers = () => {
    vi.useRealTimers();
  };

  return { advanceTimers, runAllTimers, restoreTimers };
};
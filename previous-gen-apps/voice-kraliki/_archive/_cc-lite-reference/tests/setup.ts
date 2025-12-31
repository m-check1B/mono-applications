import { beforeAll, afterAll, beforeEach, afterEach, vi } from 'vitest';
import { PrismaClient, UserRole, UserStatus, CallStatus } from '@prisma/client';
import bcrypt from 'bcrypt';

// Ensure test environment variables are set
if (!process.env.NODE_ENV || process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'beta') {
  process.env.NODE_ENV = 'test';
}
process.env.TESTING = 'true';
process.env.SKIP_PROCESS_EXIT = 'true';

// Vitest overrides process listeners; ensure we return arrays to avoid type errors.
const originalListeners = typeof process.listeners === 'function'
  ? process.listeners.bind(process)
  : undefined;

Object.defineProperty(process, 'listeners', {
  configurable: true,
  enumerable: false,
  writable: true,
  value: (...args: any[]) => (originalListeners ? originalListeners(...args) : [])
});

try {
  Object.defineProperty(bcrypt, 'compare', {
    configurable: true,
    writable: true,
    value: bcrypt.compare.bind(bcrypt)
  });
  Object.defineProperty(bcrypt, 'hash', {
    configurable: true,
    writable: true,
    value: bcrypt.hash.bind(bcrypt)
  });
} catch {
  // Ignore if properties already configurable
}

if (typeof process.setMaxListeners === 'function') {
  process.setMaxListeners(20);
}

let exitSpy: ReturnType<typeof vi.spyOn> | null = null;
try {
  exitSpy = vi.spyOn(process, 'exit').mockImplementation(() => undefined as never);
} catch {
  exitSpy = null;
}

// Global test database client
export const testDb = new PrismaClient({
  datasources: {
    db: {
      url:
        process.env.TEST_DATABASE_URL ||
        process.env.DATABASE_URL ||
        'postgresql://cc_user:cc_password@localhost:5432/cc_light'
    }
  }
});

const skipDbSetup = process.env.SKIP_DB_TEST_SETUP === 'true';
const DEFAULT_ORG_ID = 'test-org';
const DEFAULT_ORG_NAME = 'Test Organization';

// Setup and teardown
beforeAll(async () => {
  if (skipDbSetup) return;
  // Connect to test database
  await testDb.$connect();
  
  // Run migrations
  await testDb.$executeRaw`CREATE SCHEMA IF NOT EXISTS public`;
});

afterAll(async () => {
  if (exitSpy) {
    exitSpy.mockRestore();
  }
  if (originalListeners) {
    (process as any).listeners = originalListeners;
  }

  if (skipDbSetup) return;
  await testDb.$disconnect();
});

beforeEach(async () => {
  if (skipDbSetup) return;
  await testDb.$transaction([
    testDb.callTranscript.deleteMany(),
    testDb.call.deleteMany(),
    testDb.campaignMetric.deleteMany(),
    testDb.campaign.deleteMany(),
    testDb.userSession.deleteMany(),
    testDb.teamMember.deleteMany(),
    testDb.team.deleteMany(),
    testDb.user.deleteMany(),
    testDb.organization.deleteMany(),
  ]);

  await ensureTestOrganization();
});

async function ensureTestOrganization(id: string = DEFAULT_ORG_ID) {
  await testDb.organization.upsert({
    where: { id },
    update: {},
    create: {
      id,
      name: DEFAULT_ORG_NAME,
      domain: `${id}.local`,
      settings: {
        language: 'en',
        timezone: 'UTC',
      },
    },
  });
}

// Test helpers
export const createTestUser = async (overrides: Partial<Parameters<typeof testDb.user.create>[0]['data']> & { password?: string } = {}) => {
  const {
    password = 'password123',
    role = UserRole.AGENT,
    organizationId = DEFAULT_ORG_ID,
    email = 'test@example.com',
    username,
    firstName = 'Test',
    lastName = 'User',
    status = UserStatus.ACTIVE,
    ...rest
  } = overrides as any;

  const resolvedUsername = username || (typeof email === 'string' && email.includes('@')
    ? email.split('@')[0]
    : `testuser_${Date.now()}`);

  await ensureTestOrganization(organizationId);

  const passwordHash = await bcrypt.hash(password, 10);

  return testDb.user.create({
    data: {
      email,
      username: resolvedUsername,
      firstName,
      lastName,
      passwordHash,
      role,
      status,
      organizationId,
      skills: [],
      preferences: {
        language: 'en',
        timezone: 'UTC',
      },
      ...rest,
    },
  });
};

export const createTestCall = async (overrides = {}) => {
  return testDb.call.create({
    data: {
      fromNumber: '+1234567000',
      toNumber: '+1987654321',
      direction: 'INBOUND',
      provider: 'TWILIO',
      organizationId: DEFAULT_ORG_ID,
      startTime: new Date(),
      metadata: {},
      ...overrides,
    } as any,
  });
};

export const createTestCampaign = async (overrides = {}) => {
  const organizationId = (overrides as any).organizationId || DEFAULT_ORG_ID;
  await ensureTestOrganization(organizationId);

  return testDb.campaign.create({
    data: {
      name: 'Test Campaign',
      type: 'OUTBOUND',
      active: true,
      language: 'en',
      instructions: { script: [] },
      tools: {},
      voice: null,
      analytics: {},
      organizationId,
      ...overrides,
    } as any,
  });
};

// Mock services
export const mockDeepgramService = {
  startTranscription: vi.fn(),
  stopTranscription: vi.fn(),
  processAudioStream: vi.fn(),
  synthesizeSpeech: vi.fn(),
  getTranscription: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn(),
  destroy: vi.fn(),
  handleWebSocketConnection: vi.fn(),
  getActiveTranscriptions: vi.fn().mockReturnValue([]),
  streamSpeech: vi.fn()
};

try {
  let mockPid = process.pid;
  Object.defineProperty(process, 'pid', {
    configurable: true,
    get: () => mockPid,
    set: (value: number) => {
      mockPid = value;
    }
  });
} catch {
  // ignore if not configurable
}

export const mockTwilioService = {
  makeCall: vi.fn(),
  endCall: vi.fn(),
  transferCall: vi.fn(),
  holdCall: vi.fn(),
  muteCall: vi.fn(),
  getCallStatus: vi.fn()
};

// Test utilities
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const mockWebSocket = () => {
  return {
    send: vi.fn(),
    close: vi.fn(),
    on: vi.fn(),
    off: vi.fn(),
    readyState: 1,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  };
};

// Mock services for multi-language testing
export const mockLanguageRouter = {
  startSession: vi.fn(),
  endSession: vi.fn(),
  processText: vi.fn(),
  processAudio: vi.fn(),
  synthesizeSpeech: vi.fn(),
  getSessionLanguage: vi.fn(),
  getSessionRoute: vi.fn(),
  setSessionLanguage: vi.fn(),
  switchLanguageRoute: vi.fn(),
  getSessionStats: vi.fn(),
  getActiveSessions: vi.fn().mockReturnValue([]),
  getHealthStatus: vi.fn().mockReturnValue({
    activeSessions: 0,
    deepgramAvailable: true,
    czechTTSAvailable: true
  }),
  updateConfig: vi.fn(),
  destroy: vi.fn(),
  on: vi.fn(),
  emit: vi.fn()
};

export const mockCzechTTSService = {
  synthesize: vi.fn(),
  synthesizeStream: vi.fn(),
  testTTS: vi.fn().mockResolvedValue(true),
  getAvailableVoices: vi.fn().mockReturnValue([]),
  clearCache: vi.fn(),
  getCacheStats: vi.fn().mockReturnValue({ entries: 0, sizeBytes: 0, sizeMB: 0 }),
  destroy: vi.fn(),
  on: vi.fn(),
  emit: vi.fn()
};

// Language detection test helpers
export const createLanguageTestData = (language: 'en' | 'es' | 'cs', length: 'short' | 'medium' | 'long' = 'medium') => {
  const testTexts = {
    en: {
      short: 'Hello there',
      medium: 'Hello, thank you for calling our customer service. How can I help you today?',
      long: 'Hello and welcome to our comprehensive customer service center. Thank you for taking the time to call us today.'
    },
    es: {
      short: 'Hola amigo',
      medium: 'Hola, gracias por llamar a nuestro servicio al cliente. ¿Cómo puedo ayudarte hoy?',
      long: 'Hola y bienvenido a nuestro centro integral de servicio al cliente. Gracias por tomarse el tiempo de llamarnos hoy.'
    },
    cs: {
      short: 'Ahoj příteli',
      medium: 'Dobrý den, děkuji za zavolání do naší zákaznické služby. Jak vám dnes mohu pomoci?',
      long: 'Dobrý den a vítejte v našem komplexním centru zákaznické služby. Děkujeme, že jste si dnes udělali čas na zavolání.'
    }
  };

  return testTexts[language][length];
};

// Performance monitoring helper
export const measurePerformance = async <T>(fn: () => Promise<T>): Promise<{ result: T; duration: number; memory: number }> => {
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

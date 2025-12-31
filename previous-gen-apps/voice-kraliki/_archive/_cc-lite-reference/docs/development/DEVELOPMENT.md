# Voice by Kraliki Developer Guide

> **Complete Developer Onboarding and Development Environment Setup**

## Table of Contents

1. [Quick Start](#quick-start)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [Technology Stack](#technology-stack)
5. [Development Workflow](#development-workflow)
6. [Code Standards](#code-standards)
7. [Testing Strategy](#testing-strategy)
8. [Debugging Guide](#debugging-guide)
9. [API Development](#api-development)
10. [Frontend Development](#frontend-development)
11. [Database Development](#database-development)
12. [Contributing Guidelines](#contributing-guidelines)

## Quick Start

### Prerequisites

**Required Software:**
- **Node.js**: 18.x or higher
- **pnpm**: 8.x or higher (MANDATORY - never use npm/yarn)
- **PostgreSQL**: 15.x or higher
- **Redis**: 7.x or higher
- **Git**: Latest version

```bash
# Install Node.js via nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Install pnpm globally
npm install -g pnpm

# Verify installations
node --version    # Should be 18.x
pnpm --version    # Should be 8.x
```

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/cc-lite.git
cd cc-lite

# 2. Install dependencies (ALWAYS use pnpm)
pnpm install

# 3. Setup environment
cp .env.template .env
# Edit .env with your local configuration

# 4. Setup database
pnpm run db:setup
pnpm run db:migrate
pnpm run db:seed

# 5. Start development servers
pnpm run dev        # Frontend on http://127.0.0.1:3007
pnpm run dev:server # Backend on http://127.0.0.1:3010

# 6. Run tests to verify setup
pnpm test
```

### Test Login

Access the application and login with:
```yaml
Email: test.assistant@stack2025.com
Password: Stack2025!Test@Assistant#Secure$2024
Role: TESTER_UNIVERSAL
```

## Development Environment

### Local Environment Configuration

Create `.env` for local development:

```bash
# ===== DEVELOPMENT CONFIGURATION =====
NODE_ENV=development
PORT=3010
HOST=127.0.0.1
FRONTEND_PORT=3007

# ===== DATABASE (Local) =====
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/cc_lite_dev
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=cc_lite_dev
DB_USER=postgres
DB_PASSWORD=password

# ===== AUTHENTICATION (Development) =====
JWT_SECRET=development_jwt_secret_should_be_changed_in_production
COOKIE_SECRET=development_cookie_secret_change_me
AUTH_ENCRYPTION_KEY=development_encryption_key_32_chars

# ===== REDIS (Local) =====
REDIS_URL=redis://127.0.0.1:6379
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# ===== TELEPHONY (Development/Mock) =====
TELEPHONY_PROVIDER=mock
TELEPHONY_ENABLED=false
MOCK_TELEPHONY=true

# Development Twilio (Optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# ===== AI SERVICES (Development) =====
OPENAI_API_KEY=sk-your-openai-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# ===== DEVELOPMENT SETTINGS =====
SEED_DEMO_USERS=true
ENABLE_DEBUG_LOGGING=true
LOG_LEVEL=debug
METRICS_ENABLED=true
TRACING_ENABLED=true

# ===== DEVELOPMENT TOOLS =====
HOT_RELOAD=true
SOURCE_MAPS=true
TYPESCRIPT_CHECK=true
ESLINT_CHECK=true
```

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "files.associations": {
    "*.tsx": "typescriptreact",
    "*.ts": "typescript"
  },
  "eslint.workingDirectories": ["./"],
  "typescript.updateImportsOnFileMove.enabled": "always",
  "emmet.includeLanguages": {
    "typescript": "html",
    "typescriptreact": "html"
  }
}
```

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Voice by Kraliki Backend",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/server/index.ts",
      "env": {
        "NODE_ENV": "development"
      },
      "runtimeArgs": ["-r", "ts-node/register"],
      "sourceMaps": true,
      "restart": true,
      "protocol": "inspector",
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen"
    },
    {
      "name": "Debug Tests",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/vitest",
      "args": ["run", "--no-coverage"],
      "env": {
        "NODE_ENV": "test"
      },
      "console": "integratedTerminal"
    }
  ]
}
```

### Development Scripts

```json
{
  "scripts": {
    // Development
    "dev": "vite",
    "dev:server": "tsx watch server/index.ts",
    "dev:full": "concurrently \"pnpm dev\" \"pnpm dev:server\"",

    // Database
    "db:setup": "docker compose up -d postgres redis",
    "db:migrate": "prisma migrate dev",
    "db:seed": "prisma db seed",
    "db:reset": "prisma migrate reset --force",
    "db:studio": "prisma studio",

    // Testing
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",

    // Code Quality
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write .",
    "format:check": "prettier --check .",

    // Build
    "build": "tsc && vite build",
    "build:server": "tsc -p server/tsconfig.json",
    "preview": "vite preview"
  }
}
```

## Project Structure

### Directory Overview

```
cc-lite/
├── 📁 src/                     # Frontend source code
│   ├── 📁 components/         # React components
│   │   ├── 📁 dashboard/      # Dashboard components
│   │   ├── 📁 agent/         # Agent interface
│   │   ├── 📁 supervisor/    # Supervisor tools
│   │   ├── 📁 common/        # Shared components
│   │   └── 📁 ui/            # Base UI components
│   ├── 📁 contexts/          # React contexts
│   ├── 📁 hooks/             # Custom hooks
│   ├── 📁 services/          # Frontend services
│   ├── 📁 utils/             # Utility functions
│   ├── 📁 types/             # TypeScript types
│   └── 📁 pages/             # Route components
│
├── 📁 server/                 # Backend source code
│   ├── 📁 trpc/              # tRPC API layer
│   │   ├── 📁 routers/       # Individual route modules
│   │   ├── context.ts        # Request context
│   │   └── router.ts         # Root router
│   ├── 📁 services/          # Business logic
│   ├── 📁 core/              # Core integrations
│   │   ├── 📁 telephony/     # Phone providers
│   │   ├── 📁 ai/            # AI services
│   │   └── 📁 websocket/     # Real-time comms
│   ├── 📁 middleware/        # Server middleware
│   ├── 📁 utils/             # Server utilities
│   └── index.ts              # Server entry point
│
├── 📁 prisma/                # Database layer
│   ├── schema.prisma         # Database schema
│   ├── 📁 migrations/        # Database migrations
│   └── seed.ts               # Database seeding
│
├── 📁 tests/                 # Test suite
│   ├── 📁 e2e/              # End-to-end tests
│   ├── 📁 integration/       # API integration tests
│   ├── 📁 unit/             # Unit tests
│   └── 📁 fixtures/         # Test data
│
├── 📁 docs/                  # Documentation
│   ├── 📁 api/              # API documentation
│   ├── 📁 architecture/     # System design
│   ├── 📁 development/      # Development guides
│   └── 📁 deployment/       # Deployment guides
│
└── 📁 config/                # Configuration files
    ├── 📁 docker/            # Docker configurations
    ├── 📁 nginx/             # Nginx configurations
    └── 📁 monitoring/        # Monitoring configs
```

### Key Files

**Configuration:**
- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite build configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `playwright.config.ts` - E2E testing configuration

**Development:**
- `.env` - Local environment variables
- `.eslintrc.json` - Linting rules
- `.prettierrc` - Code formatting rules
- `.gitignore` - Git ignore patterns

## Technology Stack

### Frontend Technologies

```typescript
// Core Framework
React 18.2.0          // UI library
TypeScript 5.2.0      // Type safety
Vite 5.0.0            // Build tool
React Router 6.8.0    // Client-side routing

// UI Framework
NextUI 2.2.0          // Component library
Tailwind CSS 3.4.0   // Utility-first CSS
Framer Motion 10.16.0 // Animations
Lucide React 0.263.0  // Icons

// State Management
TanStack Query 4.32.0 // Server state
React Context         // Client state
Zustand 4.4.0        // Global state (optional)

// Development Tools
ESLint 8.45.0         // Code linting
Prettier 3.0.0       // Code formatting
Vitest 0.34.0         // Unit testing
Playwright 1.37.0    // E2E testing
```

### Backend Technologies

```typescript
// Core Framework
Fastify 4.25.0        // Web server
tRPC 10.44.0          // Type-safe APIs
TypeScript 5.2.0      // Type safety
Node.js 18.x          // Runtime

// Database
PostgreSQL 15.x       // Primary database
Prisma 5.5.0          // ORM and migrations
Redis 7.x             // Caching and sessions

// Authentication
JWT                   // Token-based auth
bcrypt               // Password hashing
Cookie parsing       // Session management

// Monitoring
Winston 3.10.0       // Logging
Prometheus           // Metrics
OpenTelemetry       // Distributed tracing

// External Integrations
Twilio SDK           // Telephony
OpenAI SDK           // AI services
Deepgram SDK         // Speech processing
```

## Development Workflow

### Feature Development Process

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Implement Feature**
```bash
# Start development servers
pnpm run dev:full

# Create/modify files
# Write tests
# Update documentation
```

3. **Test Implementation**
```bash
# Run all tests
pnpm test

# Run E2E tests
pnpm test:e2e

# Check code quality
pnpm lint
pnpm type-check
```

4. **Create Pull Request**
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### Git Workflow

**Branch Naming:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

**Commit Messages:**
```bash
# Follow conventional commits
feat: add new dashboard component
fix: resolve authentication issue
docs: update API documentation
refactor: improve call management service
test: add unit tests for agent service
```

### Code Review Process

**Before Creating PR:**
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No console.log statements
- [ ] TypeScript strict mode passes

**PR Requirements:**
- [ ] Descriptive title and description
- [ ] Screenshots for UI changes
- [ ] Test coverage maintained
- [ ] No breaking changes (or documented)
- [ ] Security considerations addressed

## Code Standards

### TypeScript Guidelines

```typescript
// ✅ Good: Explicit types
interface User {
  id: string;
  email: string;
  role: UserRole;
  createdAt: Date;
}

const createUser = (data: CreateUserData): Promise<User> => {
  return userService.create(data);
};

// ❌ Bad: Any types
const createUser = (data: any): any => {
  return userService.create(data);
};

// ✅ Good: Proper error handling
const handleApiCall = async (): Promise<Result<User, Error>> => {
  try {
    const user = await api.getUser();
    return { success: true, data: user };
  } catch (error) {
    return { success: false, error: error as Error };
  }
};

// ✅ Good: Strict null checks
const getUserName = (user: User | null): string => {
  return user?.name ?? 'Unknown User';
};
```

### React Component Guidelines

```tsx
// ✅ Good: Functional component with TypeScript
interface CallCardProps {
  call: Call;
  onAnswer: (callId: string) => void;
  onReject: (callId: string) => void;
  className?: string;
}

export const CallCard: React.FC<CallCardProps> = ({
  call,
  onAnswer,
  onReject,
  className
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleAnswer = useCallback(async () => {
    setIsLoading(true);
    try {
      await onAnswer(call.id);
    } finally {
      setIsLoading(false);
    }
  }, [call.id, onAnswer]);

  return (
    <Card className={cn('p-4', className)}>
      <div className="flex justify-between items-center">
        <div>
          <p className="font-medium">{call.phoneNumber}</p>
          <p className="text-sm text-gray-500">{call.duration}</p>
        </div>
        <div className="space-x-2">
          <Button
            onClick={handleAnswer}
            disabled={isLoading}
            color="success"
          >
            Answer
          </Button>
          <Button
            onClick={() => onReject(call.id)}
            disabled={isLoading}
            color="danger"
          >
            Reject
          </Button>
        </div>
      </div>
    </Card>
  );
};
```

### tRPC Router Guidelines

```typescript
// ✅ Good: Proper tRPC router structure
export const callRouter = router({
  list: protectedProcedure
    .input(
      z.object({
        status: z.enum(['ACTIVE', 'QUEUED', 'ENDED']).optional(),
        limit: z.number().min(1).max(100).default(20),
        offset: z.number().min(0).default(0)
      })
    )
    .query(async ({ input, ctx }) => {
      const { user } = ctx;

      return await callService.listCalls({
        userId: user.id,
        ...input
      });
    }),

  answer: protectedProcedure
    .input(z.object({ callId: z.string().uuid() }))
    .mutation(async ({ input, ctx }) => {
      const { user } = ctx;

      return await callService.answerCall(input.callId, user.id);
    })
});

// ❌ Bad: No input validation
export const callRouter = router({
  answer: protectedProcedure
    .mutation(async ({ input, ctx }) => {
      // No input validation, unsafe
      return await callService.answerCall(input.callId, ctx.user.id);
    })
});
```

### Error Handling Standards

```typescript
// ✅ Good: Proper error handling
export class CallService {
  async answerCall(callId: string, agentId: string): Promise<Call> {
    try {
      const call = await this.getCall(callId);

      if (!call) {
        throw new NotFoundError('Call not found');
      }

      if (call.status !== 'QUEUED') {
        throw new BadRequestError('Call is not in a state to be answered');
      }

      return await this.updateCallStatus(callId, 'ACTIVE', agentId);
    } catch (error) {
      logger.error('Failed to answer call', { callId, agentId, error });
      throw error;
    }
  }
}

// ✅ Good: Custom error types
export class NotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class BadRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'BadRequestError';
  }
}
```

## Testing Strategy

### Unit Testing with Vitest

```typescript
// tests/unit/services/CallService.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CallService } from '../../../server/services/CallService';
import { mockCall, mockAgent } from '../../fixtures/call';

describe('CallService', () => {
  let callService: CallService;

  beforeEach(() => {
    callService = new CallService();
  });

  describe('answerCall', () => {
    it('should answer a queued call successfully', async () => {
      // Arrange
      const call = mockCall({ status: 'QUEUED' });
      const agent = mockAgent();

      // Act
      const result = await callService.answerCall(call.id, agent.id);

      // Assert
      expect(result.status).toBe('ACTIVE');
      expect(result.agentId).toBe(agent.id);
    });

    it('should throw error when call is not found', async () => {
      // Arrange
      const nonExistentCallId = 'non-existent-id';
      const agent = mockAgent();

      // Act & Assert
      await expect(
        callService.answerCall(nonExistentCallId, agent.id)
      ).rejects.toThrow('Call not found');
    });
  });
});
```

### Integration Testing

```typescript
// tests/integration/trpc/call.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { createTestContext } from '../../helpers/context';
import { appRouter } from '../../../server/trpc/router';

describe('Call tRPC Router', () => {
  let caller: ReturnType<typeof appRouter.createCaller>;

  beforeEach(async () => {
    const ctx = await createTestContext();
    caller = appRouter.createCaller(ctx);
  });

  it('should list calls for authenticated user', async () => {
    // Act
    const result = await caller.call.list({
      limit: 10,
      offset: 0
    });

    // Assert
    expect(result).toHaveProperty('calls');
    expect(result).toHaveProperty('total');
    expect(Array.isArray(result.calls)).toBe(true);
  });

  it('should require authentication', async () => {
    // Arrange
    const unauthenticatedCaller = appRouter.createCaller({
      user: null
    });

    // Act & Assert
    await expect(
      unauthenticatedCaller.call.list({})
    ).rejects.toThrow('UNAUTHORIZED');
  });
});
```

### E2E Testing with Playwright

```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';
import { loginAsAgent } from '../helpers/auth';

test.describe('Agent Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAgent(page);
  });

  test('should display active calls', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/operator');

    // Check for dashboard elements
    await expect(page.locator('[data-testid="active-calls"]')).toBeVisible();
    await expect(page.locator('[data-testid="call-queue"]')).toBeVisible();
    await expect(page.locator('[data-testid="agent-status"]')).toBeVisible();
  });

  test('should answer incoming call', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/operator');

    // Wait for incoming call
    await page.locator('[data-testid="incoming-call"]').waitFor();

    // Click answer button
    await page.locator('[data-testid="answer-call-btn"]').click();

    // Verify call is answered
    await expect(page.locator('[data-testid="active-call"]')).toBeVisible();
  });
});
```

## Debugging Guide

### Backend Debugging

```typescript
// Enable debug logging
process.env.LOG_LEVEL = 'debug';

// Use debugger statements
const callService = {
  answerCall: async (callId: string) => {
    debugger; // Execution will pause here when debugging

    const call = await this.getCall(callId);
    console.log('Call found:', call); // Temporary debug log

    return call;
  }
};

// Use VS Code debugger
// Set breakpoints in VS Code and run "Debug Voice by Kraliki Backend"
```

### Frontend Debugging

```tsx
// React Developer Tools
// Install React DevTools browser extension

// Debug React hooks
const CallComponent = () => {
  const [calls, setCalls] = useState([]);

  // Debug state changes
  useEffect(() => {
    console.log('Calls updated:', calls);
  }, [calls]);

  // Debug renders
  console.log('Component rendered with:', { calls });

  return <div>...</div>;
};

// Debug tRPC calls
const { data, error, isLoading } = trpc.call.list.useQuery({}, {
  onSuccess: (data) => console.log('tRPC success:', data),
  onError: (error) => console.error('tRPC error:', error)
});
```

### Common Debugging Scenarios

**Database Connection Issues:**
```bash
# Check database status
pnpm run db:status

# Reset database
pnpm run db:reset

# View database logs
docker compose logs postgres
```

**tRPC Type Issues:**
```bash
# Regenerate tRPC types
pnpm run build:server

# Check TypeScript errors
pnpm run type-check
```

**WebSocket Connection Issues:**
```typescript
// Debug WebSocket in browser console
const ws = new WebSocket('ws://localhost:3010/socket.io/');
ws.onopen = () => console.log('Connected');
ws.onmessage = (msg) => console.log('Message:', msg);
ws.onerror = (error) => console.error('Error:', error);
```

## API Development

### Creating New tRPC Routers

1. **Create Router File**
```typescript
// server/trpc/routers/example.ts
import { router, protectedProcedure, publicProcedure } from '../trpc';
import { z } from 'zod';

export const exampleRouter = router({
  list: publicProcedure
    .input(z.object({
      limit: z.number().min(1).max(100).default(10),
      offset: z.number().min(0).default(0)
    }))
    .query(async ({ input }) => {
      // Implementation
      return { items: [], total: 0 };
    }),

  create: protectedProcedure
    .input(z.object({
      name: z.string().min(1),
      description: z.string().optional()
    }))
    .mutation(async ({ input, ctx }) => {
      // Implementation
      return { id: 'new-id', ...input };
    })
});
```

2. **Add to Root Router**
```typescript
// server/trpc/router.ts
import { exampleRouter } from './routers/example';

export const appRouter = router({
  // ... existing routers
  example: exampleRouter
});
```

3. **Use in Frontend**
```typescript
// Frontend usage
const { data, isLoading } = trpc.example.list.useQuery({
  limit: 20,
  offset: 0
});

const createMutation = trpc.example.create.useMutation({
  onSuccess: () => {
    // Invalidate and refetch
    utils.example.list.invalidate();
  }
});
```

### Input Validation Patterns

```typescript
// Common validation schemas
const paginationSchema = z.object({
  limit: z.number().min(1).max(100).default(20),
  offset: z.number().min(0).default(0)
});

const filterSchema = z.object({
  search: z.string().optional(),
  status: z.enum(['ACTIVE', 'INACTIVE']).optional(),
  dateRange: z.object({
    start: z.date(),
    end: z.date()
  }).optional()
});

// Reusable schemas
export const callSchemas = {
  create: z.object({
    phoneNumber: z.string().regex(/^\+[1-9]\d{1,14}$/),
    campaignId: z.string().uuid().optional(),
    metadata: z.record(z.any()).optional()
  }),

  update: z.object({
    id: z.string().uuid(),
    status: z.enum(['QUEUED', 'ACTIVE', 'ENDED']).optional(),
    notes: z.string().max(1000).optional()
  })
};
```

## Frontend Development

### Component Development Patterns

```tsx
// Component with proper TypeScript
interface ComponentProps {
  required: string;
  optional?: number;
  children?: React.ReactNode;
  className?: string;
}

export const ExampleComponent: React.FC<ComponentProps> = ({
  required,
  optional = 0,
  children,
  className
}) => {
  return (
    <div className={cn('base-styles', className)}>
      {children}
    </div>
  );
};

// Custom hooks pattern
const useCallManagement = () => {
  const [activeCall, setActiveCall] = useState<Call | null>(null);

  const answerCall = useCallback(async (callId: string) => {
    try {
      const call = await trpc.call.answer.mutate({ callId });
      setActiveCall(call);
    } catch (error) {
      toast.error('Failed to answer call');
    }
  }, []);

  return {
    activeCall,
    answerCall,
    // ... other methods
  };
};
```

### State Management Patterns

```tsx
// Context pattern
interface CallContextType {
  activeCalls: Call[];
  answerCall: (callId: string) => Promise<void>;
  endCall: (callId: string) => Promise<void>;
}

const CallContext = createContext<CallContextType | undefined>(undefined);

export const CallProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [activeCalls, setActiveCalls] = useState<Call[]>([]);

  const value = {
    activeCalls,
    answerCall,
    endCall
  };

  return (
    <CallContext.Provider value={value}>
      {children}
    </CallContext.Provider>
  );
};

// Hook to use context
export const useCall = () => {
  const context = useContext(CallContext);
  if (!context) {
    throw new Error('useCall must be used within CallProvider');
  }
  return context;
};
```

## Database Development

### Schema Development

```prisma
// prisma/schema.prisma
model Call {
  id          String   @id @default(uuid())
  phoneNumber String
  status      CallStatus @default(QUEUED)
  agentId     String?
  campaignId  String?
  metadata    Json     @default("{}")
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  // Relations
  agent       Agent?   @relation(fields: [agentId], references: [id])
  campaign    Campaign? @relation(fields: [campaignId], references: [id])
  transcripts Transcript[]

  // Indexes
  @@index([status, createdAt])
  @@index([agentId])
  @@map("calls")
}

enum CallStatus {
  QUEUED
  ACTIVE
  ENDED
  FAILED
}
```

### Migration Workflow

```bash
# Create migration
pnpm prisma migrate dev --name add_call_metadata

# Reset database (development only)
pnpm prisma migrate reset

# Apply migrations (production)
pnpm prisma migrate deploy

# Generate Prisma client
pnpm prisma generate
```

### Database Seeding

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Seed users
  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@cc-lite.local' },
    update: {},
    create: {
      email: 'admin@cc-lite.local',
      passwordHash: await hashPassword('admin123'),
      role: 'ADMIN'
    }
  });

  // Seed agents
  await prisma.agent.create({
    data: {
      userId: adminUser.id,
      status: 'OFFLINE',
      capabilities: {
        languages: ['en', 'es'],
        skills: ['sales', 'support']
      }
    }
  });
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

## Contributing Guidelines

### Pull Request Process

1. **Fork & Branch**
   - Fork the repository
   - Create feature branch from `main`
   - Use descriptive branch names

2. **Development**
   - Follow code standards
   - Write comprehensive tests
   - Update documentation
   - Ensure no breaking changes

3. **Testing**
   - All tests must pass
   - Maintain or improve test coverage
   - Test on multiple browsers (E2E)

4. **Code Review**
   - Create detailed PR description
   - Include screenshots for UI changes
   - Address reviewer feedback
   - Squash commits before merge

### Code Quality Checklist

- [ ] TypeScript strict mode passes
- [ ] All tests pass locally
- [ ] ESLint rules followed
- [ ] Code is properly formatted
- [ ] Documentation updated
- [ ] No console.log statements
- [ ] Error handling implemented
- [ ] Accessibility considered
- [ ] Performance optimized

This development guide ensures consistent, high-quality development practices across the Voice by Kraliki project.
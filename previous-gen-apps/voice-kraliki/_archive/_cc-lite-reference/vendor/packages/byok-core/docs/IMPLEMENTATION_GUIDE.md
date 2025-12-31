# BYOK Implementation Guide

Complete guide for implementing the Bring Your Own Keys (BYOK) system in Stack 2025 applications.

## Quick Start

### 1. Installation

```bash
# Install the core BYOK package
pnpm add @stack-2025/byok-core@file:../packages/byok-core

# Optional: Install UI components
pnpm add @stack-2025/byok-ui@file:../packages/byok-ui
```

### 2. Basic Setup

```typescript
import { createBYOKForStack2025 } from '@stack-2025/byok-core';
import { Client } from 'pg';

// Database setup
const postgresClient = new Client({
  connectionString: process.env.DATABASE_URL
});
await postgresClient.connect();

// BYOK system setup
const byokSystem = await createBYOKForStack2025({
  encryptionKey: process.env.BYOK_ENCRYPTION_KEY,
  postgresClient,
  redisClient: redisInstance, // optional
  enabledProviders: ['openai', 'deepgram', 'twilio']
});

// Export for use in your application
export const { manager: byokManager } = byokSystem;
```

### 3. Add Your First Key

```typescript
// Add an OpenAI key
const keyId = await byokManager.addKey({
  userId: 'user_123',
  provider: ProviderType.OPENAI,
  keyData: {
    apiKey: 'sk-...',
    organization: 'org-...' // optional
  },
  alias: 'My OpenAI Key',
  description: 'Production OpenAI key for chat features'
});

console.log('Key added with ID:', keyId);
```

### 4. Use Keys in Your Application

```typescript
// Get key for usage
const key = await byokManager.getActiveKey('user_123', ProviderType.OPENAI);

// Use with OpenAI
const openai = new OpenAI({
  apiKey: key.keyData.apiKey,
  organization: key.keyData.organization
});

const response = await openai.chat.completions.create({
  model: 'gpt-4o-mini',
  messages: [{ role: 'user', content: 'Hello!' }]
});
```

## Architecture Overview

```mermaid
graph TB
    A[Application] --> B[BYOK Manager]
    B --> C[Encryption Service]
    B --> D[Database Layer]
    B --> E[Validation Service]
    B --> F[Fallback Manager]
    
    C --> G[AES-256-GCM]
    D --> H[PostgreSQL]
    E --> I[Provider APIs]
    F --> J[System Keys]
    
    B --> K[Cache Layer]
    K --> L[Redis]
    
    B --> M[Audit Logger]
    M --> N[Audit Database]
```

## Database Setup

### 1. Create Database Schema

```sql
-- Run the complete schema from DATABASE_SCHEMA.md
-- Key tables:
-- - byok_users: User management
-- - byok_keys: Encrypted key storage  
-- - byok_key_usage: Usage tracking
-- - byok_key_validations: Validation results
-- - byok_audit_log: Complete audit trail

\i /path/to/byok-schema.sql
```

### 2. Database Migrations

```typescript
import { DatabaseMigration } from '@stack-2025/byok-core';

const migration = new DatabaseMigration(postgresClient);

// Run all migrations
await migration.runMigrations();

// Check migration status
const status = await migration.getMigrationStatus();
console.log('Migration status:', status);
```

### 3. Database Configuration

```typescript
// Recommended PostgreSQL settings
const dbConfig = {
  // Connection security
  ssl: { rejectUnauthorized: true },
  
  // Performance
  max: 20,              // Connection pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  
  // Security
  application_name: 'byok-service',
  search_path: 'byok,public'
};
```

## Configuration Options

### Environment Variables

```bash
# Required
BYOK_ENCRYPTION_KEY=your-32-char-hex-key
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional - Redis cache
REDIS_URL=redis://localhost:6379

# Optional - Security
BYOK_KEY_ROTATION_DAYS=90
BYOK_AUDIT_RETENTION_DAYS=2555  # 7 years
BYOK_VALIDATION_TIMEOUT=10000   # 10 seconds

# Optional - Features
BYOK_ENABLE_VALIDATION=true
BYOK_ENABLE_FALLBACK=true
BYOK_ENABLE_ANALYTICS=true
```

### Programmatic Configuration

```typescript
const config: BYOKManagerOptions = {
  encryptionKey: process.env.BYOK_ENCRYPTION_KEY!,
  database: {
    client: postgresClient
  },
  cache: {
    redis: {
      client: redisClient
    },
    ttl: 300 // 5 minutes
  },
  validation: {
    enabled: true,
    parallelValidation: true,
    timeout: 10000
  },
  audit: {
    enabled: true,
    retentionDays: 2555 // 7 years for compliance
  },
  fallback: {
    enabled: true,
    systemKeys: {
      [ProviderType.OPENAI]: {
        apiKey: process.env.SYSTEM_OPENAI_KEY
      }
    }
  }
};

const byokManager = new BYOKManager(config);
```

## Provider Integration

### AI Providers

```typescript
import { createBYOKAIIntegration } from '@stack-2025/byok-core';

// Create AI integration
const aiIntegration = createBYOKAIIntegration(byokManager);

// Get AI configuration with BYOK
const aiConfig = await aiIntegration.configFactory.createConfigWithBYOK(
  'user_123',
  {
    fallbackToSystem: true,
    preferredProviders: [ProviderType.OPENAI, ProviderType.ANTHROPIC]
  }
);

// Use with existing AI packages
import { AIRouter } from '@stack-2025/ai-general-core';
const aiRouter = new AIRouter(aiConfig);
```

### Deepgram Integration

```typescript
import { createBYOKDeepgramIntegration } from '@stack-2025/byok-core';

const deepgramIntegration = createBYOKDeepgramIntegration(byokManager);

// Create voice agent configuration
const voiceConfig = await deepgramIntegration.config.createVoiceAgentConfig(
  'user_123',
  {
    listen: { model: 'nova-2-conversational' },
    speak: { model: 'aura-asteria-en' }
  }
);

// Use with Deepgram packages
import { DeepgramVoiceAgent } from '@stack-2025/deepgram-agent-core';
const agent = new DeepgramVoiceAgent(voiceConfig);
```

### Telephony Integration

```typescript
import { createBYOKTelephonyIntegration } from '@stack-2025/byok-core';

const telephonyIntegration = createBYOKTelephonyIntegration(byokManager);

// Create Twilio client
const twilioClient = await telephonyIntegration.config.createTelephonyClient(
  'user_123',
  'twilio',
  {
    capabilities: ['voice', 'sms']
  }
);

// Make a call
const call = await twilioClient.makeCall(
  '+1234567890', // from
  '+0987654321', // to
  'https://yourapp.com/voice-webhook'
);
```

## Middleware Integration

### Express.js Middleware

```typescript
import express from 'express';
import { BYOKAIMiddleware } from '@stack-2025/byok-core';

const app = express();
const aiMiddleware = new BYOKAIMiddleware(byokManager);

// Add BYOK middleware
app.use('/api/ai', aiMiddleware.middleware);
app.use('/api/ai', aiMiddleware.usageMiddleware);

// Use in routes
app.post('/api/ai/chat', async (req, res) => {
  if (req.byokEnabled) {
    // Use BYOK-configured AI
    const response = await processWithAI(req.aiConfig, req.body.message);
    res.json({ response });
  } else {
    res.status(400).json({ error: 'BYOK not configured' });
  }
});
```

### tRPC Integration

```typescript
import { initTRPC } from '@trpc/server';
import { byokMiddleware } from '@stack-2025/byok-core/trpc';

const t = initTRPC.context<Context>().create();

// BYOK middleware
const withBYOK = t.middleware(byokMiddleware(byokManager));

// Protected procedure with BYOK
export const byokRouter = t.router({
  chatWithAI: t.procedure
    .use(withBYOK)
    .input(z.object({ message: z.string() }))
    .mutation(async ({ ctx, input }) => {
      // ctx.byokConfig contains the user's AI configuration
      const response = await ctx.byokConfig.providers.openai.complete(input.message);
      return { response };
    })
});
```

### Next.js App Router

```typescript
// app/api/byok/route.ts
import { NextRequest } from 'next/server';
import { byokManager } from '@/lib/byok';

export async function POST(request: NextRequest) {
  const { userId, provider, keyData } = await request.json();
  
  try {
    const keyId = await byokManager.addKey({
      userId,
      provider,
      keyData,
      environment: Environment.PRODUCTION
    });
    
    return Response.json({ success: true, keyId });
  } catch (error) {
    return Response.json(
      { error: error.message }, 
      { status: 400 }
    );
  }
}
```

## Advanced Features

### Fallback Chains

```typescript
// Configure fallback chain for OpenAI
await byokSystem.fallback.configureFallbackChain(
  'user_123',
  ProviderType.OPENAI,
  Environment.PRODUCTION,
  {
    primaryKeyId: 'key_primary',
    fallbackSequence: ['key_backup1', 'key_backup2'],
    useSystemFallback: true,
    maxRetries: 3,
    retryDelayMs: 1000
  }
);

// Get key with automatic fallback
const result = await byokSystem.fallback.getKeyWithFallback(
  'user_123',
  ProviderType.OPENAI,
  Environment.PRODUCTION
);

console.log('Using key:', result.keyId);
console.log('Was system fallback:', result.wasSystemFallback);
```

### Usage Analytics

```typescript
// Get usage statistics
const analytics = await byokManager.getAnalytics('user_123', {
  timeRange: '30d',
  providers: [ProviderType.OPENAI],
  metrics: ['requests', 'tokens', 'cost'],
  groupBy: 'day'
});

// Create usage alert
await byokSystem.database.createUsageAlert({
  userId: 'user_123',
  alertType: 'cost',
  thresholdValue: 100, // $100
  thresholdPeriod: 'monthly',
  notificationChannels: ['email', 'webhook']
});
```

### Key Validation

```typescript
// Validate single key
const validationResult = await byokManager.testKey('key_123');
console.log('Key valid:', validationResult.isValid);
console.log('Health score:', validationResult.healthScore);

// Validate all user keys
const allResults = await byokManager.validateAllKeys('user_123');
const invalidKeys = allResults.filter(r => !r.isValid);

if (invalidKeys.length > 0) {
  console.log('Invalid keys found:', invalidKeys.map(r => r.keyId));
}

// Schedule periodic validation
const validator = byokSystem.validator;
await validator.schedulePeriodicValidation(3600000); // Every hour
```

## User Interface Integration

### React Components

```typescript
import { BYOKProvider, KeyManagementDashboard } from '@stack-2025/byok-ui';

function App() {
  return (
    <BYOKProvider 
      userId={user.id}
      apiUrl="/api/byok"
      enableAnalytics={true}
    >
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">API Key Management</h1>
        <KeyManagementDashboard />
      </div>
    </BYOKProvider>
  );
}
```

### Individual Components

```typescript
import { AddKeyForm, KeyList, UsageDashboard } from '@stack-2025/byok-ui';

// Add key form
<AddKeyForm 
  provider={ProviderType.OPENAI}
  onKeyAdded={(keyId) => console.log('Added:', keyId)}
  onCancel={() => setShowForm(false)}
/>

// Key listing
<KeyList 
  showHealthStatus={true}
  enableBulkActions={true}
  onKeySelect={(key) => setSelectedKey(key)}
/>

// Usage analytics
<UsageDashboard 
  timeRange="7d"
  showCostBreakdown={true}
  showProviderComparison={true}
/>
```

## Migration from Environment Variables

### Automated Migration

```typescript
import { createMigrationTools } from '@stack-2025/byok-core';

const { analyzer, wizard } = createMigrationTools(byokManager);

// Analyze current environment
const plan = await analyzer.analyzeMigrationOpportunities('user_123', {
  providers: [ProviderType.OPENAI, ProviderType.DEEPGRAM],
  preserveExisting: true
});

// Execute migration
const results = await wizard.startMigration('user_123', {
  autoConfirm: false,
  createBackup: true
});

console.log('Migration completed:', results.successful.length, 'keys migrated');
```

### Manual Migration

```typescript
// Check what's available in environment
const envKeys = {
  openai: process.env.OPENAI_API_KEY,
  deepgram: process.env.DEEPGRAM_API_KEY,
  twilio: {
    accountSid: process.env.TWILIO_ACCOUNT_SID,
    authToken: process.env.TWILIO_AUTH_TOKEN
  }
};

// Migrate to BYOK
for (const [provider, keyData] of Object.entries(envKeys)) {
  if (keyData) {
    await byokManager.addKey({
      userId: 'user_123',
      provider: provider as ProviderType,
      keyData: typeof keyData === 'string' ? { apiKey: keyData } : keyData,
      alias: `Migrated ${provider} key`
    });
  }
}
```

## Testing

### Unit Tests

```typescript
import { BYOKManager, EncryptionService } from '@stack-2025/byok-core';
import { createTestDatabase } from '@stack-2025/byok-core/testing';

describe('BYOK Manager', () => {
  let byokManager: BYOKManager;
  let testDb: any;

  beforeEach(async () => {
    testDb = await createTestDatabase();
    byokManager = new BYOKManager({
      encryptionKey: EncryptionService.generateMasterKey(),
      database: { client: testDb }
    });
  });

  it('should add and retrieve keys', async () => {
    const keyId = await byokManager.addKey({
      userId: 'test-user',
      provider: ProviderType.OPENAI,
      keyData: { apiKey: 'sk-test123' }
    });

    const key = await byokManager.getActiveKey('test-user', ProviderType.OPENAI);
    expect(key.keyData.apiKey).toBe('sk-test123');
  });
});
```

### Integration Tests

```typescript
import { createBYOKForStack2025 } from '@stack-2025/byok-core';

describe('BYOK Integration', () => {
  it('should integrate with AI providers', async () => {
    const byokSystem = await createBYOKForStack2025({
      encryptionKey: testEncryptionKey,
      postgresClient: testDb
    });

    // Add test key
    await byokSystem.manager.addKey({
      userId: 'test-user',
      provider: ProviderType.OPENAI,
      keyData: { apiKey: process.env.TEST_OPENAI_KEY }
    });

    // Test AI integration
    const aiConfig = await createBYOKAIIntegration(byokSystem.manager)
      .configFactory.createConfigWithBYOK('test-user');

    expect(aiConfig.providers.openai).toBeDefined();
    expect(aiConfig.providers.openai.apiKey).toBe(process.env.TEST_OPENAI_KEY);
  });
});
```

## Monitoring & Observability

### Metrics Collection

```typescript
// Custom metrics
import { collectBYOKMetrics } from '@stack-2025/byok-core/metrics';

const metrics = await collectBYOKMetrics(byokManager);

// Example metrics
console.log('Total users:', metrics.users.total);
console.log('Active keys:', metrics.keys.active);
console.log('Validation success rate:', metrics.validation.successRate);
console.log('Average response time:', metrics.performance.averageResponseTime);
```

### Health Checks

```typescript
// Health check endpoint
app.get('/health/byok', async (req, res) => {
  try {
    const health = await validateBYOKHealth(byokSystem);
    res.status(health.status === 'healthy' ? 200 : 503).json(health);
  } catch (error) {
    res.status(503).json({ status: 'unhealthy', error: error.message });
  }
});
```

### Logging

```typescript
import { Logger } from '@stack-2025/logger';

const logger = Logger.create('byok');

// Log key operations
logger.info('Key added', {
  userId: 'user_123',
  provider: ProviderType.OPENAI,
  keyId: 'key_456'
});

// Log validation results
logger.warn('Key validation failed', {
  keyId: 'key_456',
  provider: ProviderType.OPENAI,
  error: 'API key expired'
});
```

## Production Deployment

### Docker Configuration

```dockerfile
FROM node:20-alpine

# Security: Run as non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S byok -u 1001

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY --chown=byok:nodejs . .

USER byok

# Security: Read-only filesystem
VOLUME ["/tmp", "/var/log"]

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: byok-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: byok-service
  template:
    metadata:
      labels:
        app: byok-service
    spec:
      containers:
      - name: byok-service
        image: byok-service:latest
        ports:
        - containerPort: 3000
        env:
        - name: BYOK_ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: byok-secrets
              key: encryption-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: byok-secrets
              key: database-url
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Environment Variables

```bash
# Production environment
export NODE_ENV=production
export BYOK_ENCRYPTION_KEY="$(openssl rand -hex 32)"
export DATABASE_URL="postgresql://user:pass@db:5432/byok"
export REDIS_URL="redis://redis:6379"

# Security
export BYOK_ENABLE_AUDIT=true
export BYOK_AUDIT_RETENTION_DAYS=2555
export BYOK_VALIDATION_TIMEOUT=10000

# Performance  
export BYOK_CACHE_TTL=300
export BYOK_CONNECTION_POOL_SIZE=20
export BYOK_MAX_CONNECTIONS=100
```

## Troubleshooting

### Common Issues

#### Key Validation Failures
```typescript
// Debug validation
const result = await byokManager.testKey('key_123');
if (!result.isValid) {
  console.log('Validation error:', result.errorMessage);
  console.log('Response time:', result.responseTime);
  console.log('Tests run:', result.testsRun);
}

// Check key health
const key = await byokManager.getKeyDetails('key_123');
console.log('Health score:', key?.healthScore);
console.log('Last validated:', key?.lastValidatedAt);
```

#### Performance Issues
```typescript
// Check cache hit rate
const cacheStats = await byokSystem.cache?.getStats();
console.log('Cache hit rate:', cacheStats?.hitRate);

// Monitor database performance
const dbStats = await byokSystem.database.getSystemStats();
console.log('Active connections:', dbStats?.activeConnections);
console.log('Average query time:', dbStats?.averageQueryTime);
```

#### Encryption Errors
```typescript
// Validate encryption key
const encryptionValid = byokSystem.encryption.test();
if (!encryptionValid) {
  console.error('Encryption service failed validation');
}

// Check key rotation status
const rotationStatus = await checkKeyRotationStatus();
console.log('Last rotation:', rotationStatus.lastRotation);
console.log('Next rotation:', rotationStatus.nextRotation);
```

### Debugging Tools

```typescript
// Enable debug logging
process.env.BYOK_DEBUG = 'true';
process.env.BYOK_LOG_LEVEL = 'debug';

// Debug specific operations
const debugManager = byokManager.withDebug(true);
await debugManager.addKey({...}); // Will log detailed information
```

### Support Resources

- **Documentation**: [Stack 2025 BYOK Docs](https://docs.stack2025.com/byok)
- **GitHub Issues**: [Report bugs and request features](https://github.com/stack2025/byok/issues)
- **Community Forum**: [Get help from the community](https://forum.stack2025.com)
- **Professional Support**: support@stack2025.com

---

**Next Steps**:
1. Review the [Security Practices](./SECURITY_PRACTICES.md) guide
2. Check the [API Reference](./API_REFERENCE.md) for detailed method documentation
3. Explore [example implementations](../examples/) in the examples directory
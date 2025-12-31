/**
 * @stack-2025/byok-core - Factory Functions
 * Pre-configured BYOK system setups for common scenarios
 */

import { BYOKManager } from './manager.js';
import { FallbackManager } from './fallback.js';
import { PostgreSQLDatabase } from './database.js';
import { EncryptionService } from './encryption.js';
import { 
  BYOKManagerOptions, 
  ProviderType, 
  Environment,
  BYOKError 
} from './types.js';

/**
 * Complete BYOK system setup
 */
export interface BYOKSystem {
  manager: BYOKManager;
  fallback: FallbackManager;
  database: PostgreSQLDatabase;
  encryption: EncryptionService;
}

/**
 * Create a complete BYOK system with all components
 */
export async function createBYOKSystem(options: {
  encryptionKey: string;
  database: {
    connectionString?: string;
    client?: any;
  };
  redis?: {
    url?: string;
    client?: any;
  };
  systemFallbackKeys?: Partial<Record<ProviderType, any>>;
  validation?: {
    enabled?: boolean;
    timeout?: number;
  };
  audit?: {
    enabled?: boolean;
    retentionDays?: number;
  };
}): Promise<BYOKSystem> {
  
  // Validate encryption key
  if (!options.encryptionKey || options.encryptionKey.length < 32) {
    throw new BYOKError('Encryption key must be at least 32 characters', 'INVALID_ENCRYPTION_KEY');
  }

  // Create database instance
  let database: PostgreSQLDatabase;
  if (options.database.client) {
    database = new PostgreSQLDatabase(options.database.client);
  } else if (options.database.connectionString) {
    // Would need to create client from connection string
    throw new BYOKError('Connection string support not implemented yet', 'NOT_IMPLEMENTED');
  } else {
    throw new BYOKError('Database client or connection string required', 'MISSING_DATABASE');
  }

  await database.connect();

  // Create encryption service
  const encryption = new EncryptionService(options.encryptionKey);

  // Prepare manager options
  const managerOptions: BYOKManagerOptions = {
    encryptionKey: options.encryptionKey,
    database: {
      client: database
    },
    validation: {
      enabled: true,
      parallelValidation: true,
      timeout: 10000,
      ...options.validation
    },
    audit: {
      enabled: true,
      retentionDays: 90,
      ...options.audit
    },
    fallback: {
      enabled: true,
      systemKeys: options.systemFallbackKeys || {}
    }
  };

  // Add cache if Redis is available
  if (options.redis?.client) {
    managerOptions.cache = {
      redis: {
        client: options.redis.client
      },
      ttl: 300 // 5 minutes
    };
  }

  // Create BYOK manager
  const manager = new BYOKManager(managerOptions);

  // Create fallback manager
  const fallback = new FallbackManager(database, manager);

  return {
    manager,
    fallback,
    database,
    encryption
  };
}

/**
 * Create BYOK system specifically configured for Stack 2025
 */
export async function createBYOKForStack2025(options: {
  encryptionKey: string;
  postgresClient: any;
  redisClient?: any;
  enabledProviders?: ProviderType[];
}): Promise<BYOKSystem> {
  
  // Default Stack 2025 provider configuration
  const defaultProviders = [
    ProviderType.OPENAI,
    ProviderType.ANTHROPIC,
    ProviderType.GOOGLE_GEMINI,
    ProviderType.DEEPGRAM,
    ProviderType.TWILIO
  ];

  const enabledProviders = options.enabledProviders || defaultProviders;

  // Create system with Stack 2025 optimized settings
  const system = await createBYOKSystem({
    encryptionKey: options.encryptionKey,
    database: {
      client: options.postgresClient
    },
    redis: options.redisClient ? {
      client: options.redisClient
    } : undefined,
    validation: {
      enabled: true,
      timeout: 15000 // Longer timeout for provider validation
    },
    audit: {
      enabled: true,
      retentionDays: 90 // 3 months retention for compliance
    }
  });

  // Configure fallback chains for each enabled provider
  for (const provider of enabledProviders) {
    try {
      await setupDefaultFallbackChain(system, provider);
    } catch (error) {
      console.warn(`Failed to setup fallback chain for ${provider}:`, error);
    }
  }

  return system;
}

/**
 * Setup development BYOK system with mock data
 */
export async function createBYOKForDevelopment(options: {
  encryptionKey?: string;
  mockProviders?: ProviderType[];
}): Promise<BYOKSystem> {
  
  const encryptionKey = options.encryptionKey || EncryptionService.generateMasterKey();
  
  // This would create a mock database and services for development
  throw new BYOKError('Development setup not implemented yet', 'NOT_IMPLEMENTED');
}

/**
 * Quick setup for single-user scenarios
 */
export async function createPersonalBYOK(options: {
  userId: string;
  encryptionKey: string;
  postgresClient: any;
  initialKeys?: Array<{
    provider: ProviderType;
    keyData: any;
    alias?: string;
  }>;
}): Promise<BYOKSystem> {
  
  const system = await createBYOKSystem({
    encryptionKey: options.encryptionKey,
    database: {
      client: options.postgresClient
    },
    validation: {
      enabled: true,
      timeout: 10000
    },
    audit: {
      enabled: false // Disable audit for personal use
    }
  });

  // Add initial keys if provided
  if (options.initialKeys) {
    for (const keyConfig of options.initialKeys) {
      try {
        await system.manager.addKey({
          userId: options.userId,
          provider: keyConfig.provider,
          keyData: keyConfig.keyData,
          alias: keyConfig.alias,
          environment: Environment.PRODUCTION
        });
      } catch (error) {
        console.warn(`Failed to add initial key for ${keyConfig.provider}:`, error);
      }
    }
  }

  return system;
}

/**
 * Create BYOK system with enterprise features
 */
export async function createEnterpriseBYOK(options: {
  encryptionKey: string;
  postgresClient: any;
  redisClient: any;
  organizationId: string;
  adminUserId: string;
  complianceMode?: boolean;
}): Promise<BYOKSystem> {
  
  const system = await createBYOKSystem({
    encryptionKey: options.encryptionKey,
    database: {
      client: options.postgresClient
    },
    redis: {
      client: options.redisClient
    },
    validation: {
      enabled: true,
      timeout: 20000 // Longer timeout for enterprise
    },
    audit: {
      enabled: true,
      retentionDays: options.complianceMode ? 365 : 90 // 1 year for compliance
    }
  });

  // Setup organization-wide fallback chains
  const enterpriseProviders = [
    ProviderType.OPENAI,
    ProviderType.ANTHROPIC,
    ProviderType.GOOGLE_VERTEX,
    ProviderType.DEEPGRAM,
    ProviderType.TWILIO,
    ProviderType.TELNYX
  ];

  for (const provider of enterpriseProviders) {
    await setupEnterpriseFallbackChain(system, provider, options.organizationId);
  }

  return system;
}

// Helper functions

async function setupDefaultFallbackChain(system: BYOKSystem, provider: ProviderType): Promise<void> {
  // This would setup a basic fallback chain for the provider
  // Implementation would depend on how we want to handle system-level fallbacks
  console.log(`Setting up default fallback chain for ${provider}`);
}

async function setupEnterpriseFallbackChain(
  system: BYOKSystem, 
  provider: ProviderType, 
  organizationId: string
): Promise<void> {
  // This would setup enterprise-grade fallback chains with multiple redundancy levels
  console.log(`Setting up enterprise fallback chain for ${provider} in org ${organizationId}`);
}

/**
 * Utility function to validate BYOK system health
 */
export async function validateBYOKHealth(system: BYOKSystem): Promise<{
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: Array<{
    component: string;
    status: 'pass' | 'fail';
    message?: string;
    responseTime?: number;
  }>;
}> {
  const checks: Array<{
    component: string;
    status: 'pass' | 'fail';
    message?: string;
    responseTime?: number;
  }> = [];

  // Check database connection
  try {
    const start = Date.now();
    const dbHealthy = await system.database.ping();
    const responseTime = Date.now() - start;
    
    checks.push({
      component: 'database',
      status: dbHealthy ? 'pass' : 'fail',
      message: dbHealthy ? 'Database connection OK' : 'Database connection failed',
      responseTime
    });
  } catch (error) {
    checks.push({
      component: 'database',
      status: 'fail',
      message: `Database error: ${error}`
    });
  }

  // Check encryption service
  try {
    const encryptionHealthy = system.encryption.test();
    checks.push({
      component: 'encryption',
      status: encryptionHealthy ? 'pass' : 'fail',
      message: encryptionHealthy ? 'Encryption service OK' : 'Encryption test failed'
    });
  } catch (error) {
    checks.push({
      component: 'encryption',
      status: 'fail',
      message: `Encryption error: ${error}`
    });
  }

  // Determine overall status
  const failedChecks = checks.filter(c => c.status === 'fail').length;
  let status: 'healthy' | 'degraded' | 'unhealthy';
  
  if (failedChecks === 0) {
    status = 'healthy';
  } else if (failedChecks <= checks.length / 2) {
    status = 'degraded';
  } else {
    status = 'unhealthy';
  }

  return { status, checks };
}
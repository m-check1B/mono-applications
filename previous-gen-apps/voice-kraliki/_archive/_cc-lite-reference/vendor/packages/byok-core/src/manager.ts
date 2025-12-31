/**
 * @stack-2025/byok-core - BYOK Manager
 * Main manager class for Bring Your Own Keys functionality
 */

import { 
  BYOKManagerOptions,
  KeyConfig,
  DecryptedKey,
  StoredKey,
  KeyValidationResult,
  KeyUsageStats,
  ProviderType,
  Environment,
  KeyStatus,
  EventType,
  KeyRetrievalOptions,
  KeyListOptions,
  KeyUpdateOptions,
  AnalyticsOptions,
  MigrationPlan,
  BYOKError,
  KeyNotFoundError,
  KeyValidationError,
  PROVIDER_SCHEMAS,
  DEFAULT_CAPABILITIES
} from './types.js';

import { EncryptionService } from './encryption.js';
import { DatabaseInterface } from './database.js';
import { KeyValidator } from './validation.js';
import { CacheService } from './cache.js';
import { AuditLogger } from './audit.js';

/**
 * Main BYOK Manager class
 */
export class BYOKManager {
  private encryption: EncryptionService;
  private database: DatabaseInterface;
  private validator: KeyValidator;
  private cache?: CacheService;
  private audit: AuditLogger;
  private options: BYOKManagerOptions;

  constructor(options: BYOKManagerOptions) {
    this.options = options;
    
    // Initialize encryption service
    this.encryption = new EncryptionService(options.encryptionKey);
    
    // Initialize database
    if (!options.database.client) {
      throw new BYOKError('Database client is required', 'MISSING_DATABASE');
    }
    this.database = options.database.client;
    
    // Initialize validator
    this.validator = new KeyValidator(this.database);
    
    // Initialize cache if configured
    if (options.cache?.redis) {
      this.cache = new CacheService(options.cache.redis.client, options.cache.ttl);
    }
    
    // Initialize audit logger
    this.audit = new AuditLogger(this.database, options.audit);
  }

  /**
   * Add a new API key for a user
   */
  async addKey(keyConfig: KeyConfig): Promise<string> {
    try {
      // Validate the key configuration
      this.validateKeyConfig(keyConfig);
      
      // Validate the key data against provider schema
      await this.validateKeyData(keyConfig.provider, keyConfig.keyData);
      
      // Check for duplicate keys
      const keyHash = this.encryption.generateKeyHash(keyConfig.keyData);
      const existingKey = await this.database.getKeyByHash(keyConfig.userId, keyHash);
      
      if (existingKey) {
        throw new BYOKError('A key with the same data already exists', 'DUPLICATE_KEY');
      }
      
      // Encrypt the key data
      const encryptedData = this.encryption.encrypt(keyConfig.keyData, keyConfig.userId);
      
      // Prepare stored key object
      const storedKey: Omit<StoredKey, 'id' | 'createdAt' | 'updatedAt'> = {
        userId: keyConfig.userId,
        organizationId: keyConfig.organizationId,
        provider: keyConfig.provider,
        alias: keyConfig.alias,
        description: keyConfig.description,
        environment: keyConfig.environment,
        encryptedKeyData: encryptedData.data,
        encryptionNonce: `${encryptedData.nonce}:${encryptedData.salt}`, // Store both nonce and salt
        keyHash,
        metadata: keyConfig.metadata,
        capabilities: keyConfig.capabilities || DEFAULT_CAPABILITIES[keyConfig.provider] || [],
        status: KeyStatus.ACTIVE,
        healthScore: 100,
        usageTracking: true,
        rateLimitConfig: keyConfig.rateLimit || {},
        quotaConfig: keyConfig.quotaConfig || {},
        expiresAt: keyConfig.expiresAt
      };
      
      // Store in database
      const keyId = await this.database.createKey(storedKey);
      
      // Log the creation
      await this.audit.logEvent({
        userId: keyConfig.userId,
        keyId,
        eventType: EventType.CREATE,
        eventAction: 'add_key',
        success: true,
        newValues: {
          provider: keyConfig.provider,
          alias: keyConfig.alias,
          environment: keyConfig.environment
        }
      });
      
      // Validate the key asynchronously
      this.validateKeyAsync(keyId).catch(error => {
        console.warn(`Async key validation failed for ${keyId}:`, error);
      });
      
      return keyId;
      
    } catch (error) {
      await this.audit.logEvent({
        userId: keyConfig.userId,
        eventType: EventType.CREATE,
        eventAction: 'add_key',
        success: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  /**
   * Get an active key for a user and provider
   */
  async getActiveKey(
    userId: string, 
    provider: ProviderType, 
    options: KeyRetrievalOptions = {}
  ): Promise<DecryptedKey> {
    try {
      // Check cache first
      const cacheKey = `byok:user:${userId}:provider:${provider}:env:${options.environment || 'production'}`;
      
      if (this.cache && options.cacheResult !== false) {
        const cached = await this.cache.get(cacheKey);
        if (cached) {
          return cached;
        }
      }
      
      // Get active keys from database
      const keys = await this.database.getUserKeys(userId, {
        provider,
        environment: options.environment,
        status: KeyStatus.ACTIVE,
        includeExpired: false,
        sortBy: 'health_score',
        sortOrder: 'desc',
        limit: 1
      });
      
      if (keys.length === 0) {
        if (options.fallbackToSystem && this.options.fallback?.systemKeys?.[provider]) {
          return this.createSystemFallbackKey(provider, options.environment);
        }
        throw new KeyNotFoundError(`No active key found for provider ${provider}`, provider);
      }
      
      const storedKey = keys[0];
      
      // Validate key if requested
      if (options.validateKey) {
        const validation = await this.validator.validateKey(storedKey);
        if (!validation.isValid) {
          throw new KeyValidationError(
            `Key validation failed: ${validation.errorMessage}`,
            storedKey.id,
            [validation.errorMessage || 'Unknown validation error']
          );
        }
      }
      
      // Decrypt the key
      const decryptedKey = await this.decryptStoredKey(storedKey);
      
      // Cache the result
      if (this.cache && options.cacheResult !== false) {
        await this.cache.set(cacheKey, decryptedKey, 300); // 5 minute cache
      }
      
      // Log usage
      await this.audit.logEvent({
        userId,
        keyId: storedKey.id,
        eventType: EventType.USE,
        eventAction: 'get_active_key',
        success: true
      });
      
      return decryptedKey;
      
    } catch (error) {
      await this.audit.logEvent({
        userId,
        eventType: EventType.USE,
        eventAction: 'get_active_key',
        success: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  /**
   * List keys for a user
   */
  async listKeys(userId: string, options: KeyListOptions = {}): Promise<StoredKey[]> {
    try {
      const keys = await this.database.getUserKeys(userId, options);
      
      await this.audit.logEvent({
        userId,
        eventType: EventType.USE,
        eventAction: 'list_keys',
        success: true,
        additionalData: { count: keys.length, filters: options }
      });
      
      return keys;
      
    } catch (error) {
      await this.audit.logEvent({
        userId,
        eventType: EventType.USE,
        eventAction: 'list_keys',
        success: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  /**
   * Update an existing key
   */
  async updateKey(keyId: string, updates: KeyUpdateOptions): Promise<void> {
    try {
      // Get existing key
      const existingKey = await this.database.getKey(keyId);
      if (!existingKey) {
        throw new KeyNotFoundError(keyId);
      }
      
      // Prepare updates
      const keyUpdates: Partial<StoredKey> = {};
      
      if (updates.alias !== undefined) keyUpdates.alias = updates.alias;
      if (updates.description !== undefined) keyUpdates.description = updates.description;
      if (updates.metadata !== undefined) keyUpdates.metadata = updates.metadata;
      if (updates.capabilities !== undefined) keyUpdates.capabilities = updates.capabilities;
      if (updates.rateLimitConfig !== undefined) keyUpdates.rateLimitConfig = updates.rateLimitConfig;
      if (updates.quotaConfig !== undefined) keyUpdates.quotaConfig = updates.quotaConfig;
      if (updates.expiresAt !== undefined) keyUpdates.expiresAt = updates.expiresAt;
      if (updates.status !== undefined) keyUpdates.status = updates.status;
      
      // Update in database
      await this.database.updateKey(keyId, keyUpdates);
      
      // Clear cache
      if (this.cache) {
        await this.cache.clearUserCache(existingKey.userId);
      }
      
      // Log the update
      await this.audit.logEvent({
        userId: existingKey.userId,
        keyId,
        eventType: EventType.UPDATE,
        eventAction: 'update_key',
        success: true,
        oldValues: {
          alias: existingKey.alias,
          description: existingKey.description,
          status: existingKey.status
        },
        newValues: updates
      });
      
    } catch (error) {
      await this.audit.logEvent({
        keyId,
        eventType: EventType.UPDATE,
        eventAction: 'update_key',
        success: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  /**
   * Delete a key
   */
  async deleteKey(keyId: string): Promise<void> {
    try {
      // Get existing key for audit log
      const existingKey = await this.database.getKey(keyId);
      if (!existingKey) {
        throw new KeyNotFoundError(keyId);
      }
      
      // Delete from database
      await this.database.deleteKey(keyId);
      
      // Clear cache
      if (this.cache) {
        await this.cache.clearUserCache(existingKey.userId);
      }
      
      // Log the deletion
      await this.audit.logEvent({
        userId: existingKey.userId,
        keyId,
        eventType: EventType.DELETE,
        eventAction: 'delete_key',
        success: true,
        oldValues: {
          provider: existingKey.provider,
          alias: existingKey.alias,
          environment: existingKey.environment
        }
      });
      
    } catch (error) {
      await this.audit.logEvent({
        keyId,
        eventType: EventType.DELETE,
        eventAction: 'delete_key',
        success: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  /**
   * Test a key's validity
   */
  async testKey(keyId: string): Promise<KeyValidationResult> {
    try {
      const storedKey = await this.database.getKey(keyId);
      if (!storedKey) {
        throw new KeyNotFoundError(keyId);
      }
      
      const result = await this.validator.validateKey(storedKey);
      
      // Update key status based on validation
      if (!result.isValid && storedKey.status === KeyStatus.ACTIVE) {
        await this.database.updateKey(keyId, {
          status: KeyStatus.INVALID,
          validationError: result.errorMessage,
          healthScore: result.healthScore
        });
      } else if (result.isValid && storedKey.status === KeyStatus.INVALID) {
        await this.database.updateKey(keyId, {
          status: KeyStatus.ACTIVE,
          validationError: undefined,
          healthScore: result.healthScore
        });
      }
      
      // Clear cache if status changed
      if (this.cache) {
        await this.cache.clearUserCache(storedKey.userId);
      }
      
      // Log validation
      await this.audit.logEvent({
        userId: storedKey.userId,
        keyId,
        eventType: EventType.VALIDATE,
        eventAction: 'test_key',
        success: result.isValid,
        errorMessage: result.isValid ? undefined : result.errorMessage,
        additionalData: {
          healthScore: result.healthScore,
          responseTime: result.responseTime
        }
      });
      
      return result;
      
    } catch (error) {
      await this.audit.logEvent({
        keyId,
        eventType: EventType.VALIDATE,
        eventAction: 'test_key',
        success: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  /**
   * Validate all keys for a user
   */
  async validateAllKeys(userId: string): Promise<KeyValidationResult[]> {
    const keys = await this.database.getUserKeys(userId, {
      status: KeyStatus.ACTIVE,
      includeExpired: false
    });
    
    const results: KeyValidationResult[] = [];
    
    // Validate keys in parallel
    const promises = keys.map(key => this.validator.validateKey(key));
    const validationResults = await Promise.allSettled(promises);
    
    for (let i = 0; i < keys.length; i++) {
      const result = validationResults[i];
      const key = keys[i];
      
      if (result.status === 'fulfilled') {
        results.push(result.value);
        
        // Update key status if needed
        if (!result.value.isValid) {
          await this.database.updateKey(key.id, {
            status: KeyStatus.INVALID,
            validationError: result.value.errorMessage,
            healthScore: result.value.healthScore
          });
        }
      } else {
        // Validation failed due to system error
        results.push({
          keyId: key.id,
          isValid: false,
          errorMessage: `Validation system error: ${result.reason}`,
          testResults: {},
          responseTime: 0,
          testsRun: [],
          healthScore: 0
        });
      }
    }
    
    // Clear cache
    if (this.cache) {
      await this.cache.clearUserCache(userId);
    }
    
    return results;
  }

  /**
   * Get usage statistics for a key
   */
  async getUsageStats(keyId: string, timeframe: { start: Date; end: Date }): Promise<KeyUsageStats> {
    return this.database.getUsageStats(keyId, timeframe);
  }

  /**
   * Get analytics for a user
   */
  async getAnalytics(userId: string, options: AnalyticsOptions): Promise<KeyUsageStats[]> {
    return this.database.getUserUsageStats(userId, options);
  }

  /**
   * Plan migration from environment variables
   */
  async planMigration(options: {
    from: 'environment' | 'file' | 'external';
    providers: ProviderType[];
    preserveExisting: boolean;
  }): Promise<MigrationPlan> {
    const plan: MigrationPlan = {
      from: options.from,
      providers: options.providers,
      preserveExisting: options.preserveExisting,
      dryRun: true,
      steps: [],
      estimatedDuration: 0,
      warnings: [],
      errors: []
    };
    
    // Analyze each provider
    for (const provider of options.providers) {
      const step = await this.analyzeMigrationStep(provider, options.from);
      plan.steps.push(step);
      
      if (step.action === 'migrate') {
        plan.estimatedDuration += 30; // 30 seconds per key migration
      }
    }
    
    return plan;
  }

  /**
   * Execute migration plan
   */
  async executeMigration(plan: MigrationPlan): Promise<void> {
    if (plan.dryRun) {
      throw new BYOKError('Cannot execute dry run plan. Set dryRun to false.', 'DRY_RUN_EXECUTION');
    }
    
    for (const step of plan.steps) {
      if (step.action === 'migrate' && step.existingConfig) {
        try {
          // Implementation would add the key from existing config
          console.log(`Migrating ${step.provider} key...`);
          // await this.addKey({...});
        } catch (error) {
          throw new BYOKError(`Migration failed for ${step.provider}: ${error}`, 'MIGRATION_ERROR');
        }
      }
    }
  }

  // Private helper methods

  private validateKeyConfig(keyConfig: KeyConfig): void {
    // Basic validation
    if (!keyConfig.userId) {
      throw new BYOKError('User ID is required', 'INVALID_CONFIG');
    }
    
    if (!keyConfig.provider) {
      throw new BYOKError('Provider is required', 'INVALID_CONFIG');
    }
    
    if (!keyConfig.keyData || Object.keys(keyConfig.keyData).length === 0) {
      throw new BYOKError('Key data is required', 'INVALID_CONFIG');
    }
  }

  private async validateKeyData(provider: ProviderType, keyData: any): Promise<void> {
    const schema = PROVIDER_SCHEMAS[provider];
    if (schema) {
      try {
        schema.parse(keyData);
      } catch (error) {
        throw new KeyValidationError(
          `Invalid key data for ${provider}`,
          'pending',
          [(error as any).errors?.[0]?.message || 'Schema validation failed']
        );
      }
    }
  }

  private async decryptStoredKey(storedKey: StoredKey): Promise<DecryptedKey> {
    try {
      // Parse nonce and salt from stored nonce field
      const [nonce, salt] = storedKey.encryptionNonce.split(':');
      
      const encryptedData = {
        data: storedKey.encryptedKeyData,
        nonce,
        salt
      };
      
      const keyData = this.encryption.decrypt(encryptedData, storedKey.userId);
      
      return {
        id: storedKey.id,
        provider: storedKey.provider,
        keyData,
        metadata: storedKey.metadata,
        capabilities: storedKey.capabilities,
        environment: storedKey.environment,
        healthScore: storedKey.healthScore,
        expiresAt: storedKey.expiresAt
      };
      
    } catch (error) {
      throw new BYOKError(`Failed to decrypt key ${storedKey.id}: ${error}`, 'DECRYPTION_ERROR');
    }
  }

  private async validateKeyAsync(keyId: string): Promise<void> {
    try {
      await this.testKey(keyId);
    } catch (error) {
      console.warn(`Async validation failed for key ${keyId}:`, error);
    }
  }

  private createSystemFallbackKey(provider: ProviderType, environment?: Environment): DecryptedKey {
    const systemKey = this.options.fallback?.systemKeys?.[provider];
    if (!systemKey) {
      throw new KeyNotFoundError(`No system fallback key for ${provider}`, provider);
    }
    
    return {
      id: `system-${provider}`,
      provider,
      keyData: systemKey,
      metadata: { isSystemFallback: true },
      capabilities: DEFAULT_CAPABILITIES[provider] || [],
      environment: environment || Environment.PRODUCTION,
      healthScore: 100
    };
  }

  private async analyzeMigrationStep(provider: ProviderType, from: string) {
    // Implementation would analyze existing configuration
    return {
      provider,
      action: 'skip' as const,
      reason: 'No existing configuration found'
    };
  }
}
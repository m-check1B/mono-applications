/**
 * @stack-2025/byok-core - Fallback Manager
 * Handles failover logic and fallback chains for BYOK keys
 */

import {
  FallbackChain,
  DecryptedKey,
  ProviderType,
  Environment,
  KeyStatus,
  BYOKError,
  KeyNotFoundError
} from './types.js';

import { DatabaseInterface } from './database.js';
import { BYOKManager } from './manager.js';

/**
 * Circuit breaker states
 */
enum CircuitState {
  CLOSED = 'closed',     // Normal operation
  OPEN = 'open',         // Failing, don't try
  HALF_OPEN = 'half_open' // Testing if recovered
}

/**
 * Circuit breaker for key failure tracking
 */
interface CircuitBreaker {
  state: CircuitState;
  failureCount: number;
  lastFailureTime: number;
  successCount: number;
  nextRetryTime: number;
}

/**
 * Fallback execution result
 */
interface FallbackResult {
  key: DecryptedKey;
  keyId: string;
  wasSystemFallback: boolean;
  attemptedKeys: string[];
  failedKeys: Array<{
    keyId: string;
    error: string;
  }>;
  totalAttempts: number;
  executionTime: number;
}

/**
 * Fallback manager for handling key failures and failover
 */
export class FallbackManager {
  private database: DatabaseInterface;
  private byokManager: BYOKManager;
  private circuitBreakers: Map<string, CircuitBreaker> = new Map();

  // Circuit breaker configuration
  private readonly FAILURE_THRESHOLD = 5;
  private readonly RECOVERY_TIMEOUT = 60000; // 1 minute
  private readonly HALF_OPEN_MAX_CALLS = 3;

  constructor(database: DatabaseInterface, byokManager: BYOKManager) {
    this.database = database;
    this.byokManager = byokManager;
  }

  /**
   * Get key with fallback chain execution
   */
  async getKeyWithFallback(
    userId: string,
    provider: ProviderType,
    environment: Environment = Environment.PRODUCTION
  ): Promise<FallbackResult> {
    const startTime = Date.now();
    const attemptedKeys: string[] = [];
    const failedKeys: Array<{ keyId: string; error: string }> = [];

    try {
      // Get fallback chain configuration
      const chain = await this.database.getFallbackChain(userId, provider, environment);
      
      if (chain) {
        return await this.executeChain(chain, attemptedKeys, failedKeys, startTime);
      } else {
        // No chain configured, try default behavior
        return await this.executeDefaultFallback(userId, provider, environment, attemptedKeys, failedKeys, startTime);
      }
    } catch (error) {
      // Return error result
      const executionTime = Date.now() - startTime;
      throw new BYOKError(
        `Fallback chain execution failed: ${error}`,
        'FALLBACK_FAILED',
        {
          provider,
          environment,
          attemptedKeys,
          failedKeys,
          executionTime
        }
      );
    }
  }

  /**
   * Create or update fallback chain
   */
  async configureFallbackChain(
    userId: string,
    provider: ProviderType,
    environment: Environment,
    config: {
      primaryKeyId?: string;
      fallbackSequence: string[];
      useSystemFallback?: boolean;
      maxRetries?: number;
      retryDelayMs?: number;
      chainName?: string;
    }
  ): Promise<string> {
    const existingChain = await this.database.getFallbackChain(userId, provider, environment);

    if (existingChain) {
      // Update existing chain
      await this.database.updateFallbackChain(existingChain.id, {
        primaryKeyId: config.primaryKeyId,
        fallbackSequence: config.fallbackSequence,
        useSystemFallback: config.useSystemFallback ?? true,
        maxRetries: config.maxRetries ?? 3,
        retryDelayMs: config.retryDelayMs ?? 1000,
        chainName: config.chainName
      });
      return existingChain.id;
    } else {
      // Create new chain
      const chainData: Omit<FallbackChain, 'id' | 'createdAt' | 'updatedAt'> = {
        userId,
        provider,
        environment,
        chainName: config.chainName,
        primaryKeyId: config.primaryKeyId,
        fallbackSequence: config.fallbackSequence,
        useSystemFallback: config.useSystemFallback ?? true,
        systemFallbackPriority: 999,
        maxRetries: config.maxRetries ?? 3,
        retryDelayMs: config.retryDelayMs ?? 1000,
        circuitBreakerConfig: this.getDefaultCircuitBreakerConfig()
      };
      
      return await this.database.createFallbackChain(chainData);
    }
  }

  /**
   * Remove fallback chain
   */
  async removeFallbackChain(userId: string, provider: ProviderType, environment: Environment): Promise<void> {
    const chain = await this.database.getFallbackChain(userId, provider, environment);
    if (chain) {
      await this.database.deleteFallbackChain(chain.id);
    }
  }

  /**
   * Get circuit breaker status for a key
   */
  getCircuitBreakerStatus(keyId: string): {
    state: CircuitState;
    failureCount: number;
    isAvailable: boolean;
    nextRetryIn?: number;
  } {
    const breaker = this.circuitBreakers.get(keyId);
    
    if (!breaker) {
      return {
        state: CircuitState.CLOSED,
        failureCount: 0,
        isAvailable: true
      };
    }

    const now = Date.now();
    const isAvailable = breaker.state === CircuitState.CLOSED || 
                       (breaker.state === CircuitState.HALF_OPEN) ||
                       (breaker.state === CircuitState.OPEN && now >= breaker.nextRetryTime);

    return {
      state: breaker.state,
      failureCount: breaker.failureCount,
      isAvailable,
      nextRetryIn: breaker.state === CircuitState.OPEN ? Math.max(0, breaker.nextRetryTime - now) : undefined
    };
  }

  /**
   * Reset circuit breaker for a key
   */
  resetCircuitBreaker(keyId: string): void {
    this.circuitBreakers.delete(keyId);
  }

  // Private methods

  private async executeChain(
    chain: FallbackChain,
    attemptedKeys: string[],
    failedKeys: Array<{ keyId: string; error: string }>,
    startTime: number
  ): Promise<FallbackResult> {
    // Try primary key first
    if (chain.primaryKeyId) {
      try {
        const result = await this.tryKey(chain.primaryKeyId, attemptedKeys, failedKeys);
        if (result) {
          return {
            ...result,
            totalAttempts: attemptedKeys.length,
            executionTime: Date.now() - startTime
          };
        }
      } catch (error) {
        // Primary key failed, continue to fallback sequence
      }
    }

    // Try fallback sequence
    for (const keyId of chain.fallbackSequence) {
      if (attemptedKeys.includes(keyId)) continue; // Skip if already tried

      try {
        const result = await this.tryKey(keyId, attemptedKeys, failedKeys);
        if (result) {
          return {
            ...result,
            totalAttempts: attemptedKeys.length,
            executionTime: Date.now() - startTime
          };
        }
      } catch (error) {
        // Continue to next key in sequence
        await this.delay(chain.retryDelayMs);
      }
    }

    // Try system fallback if configured
    if (chain.useSystemFallback) {
      try {
        const systemKey = await this.getSystemFallbackKey(chain.provider, chain.environment);
        return {
          key: systemKey,
          keyId: `system-${chain.provider}`,
          wasSystemFallback: true,
          attemptedKeys,
          failedKeys,
          totalAttempts: attemptedKeys.length,
          executionTime: Date.now() - startTime
        };
      } catch (error) {
        failedKeys.push({
          keyId: `system-${chain.provider}`,
          error: error instanceof Error ? error.message : 'System fallback failed'
        });
      }
    }

    throw new KeyNotFoundError(`All keys in fallback chain failed`, chain.provider);
  }

  private async executeDefaultFallback(
    userId: string,
    provider: ProviderType,
    environment: Environment,
    attemptedKeys: string[],
    failedKeys: Array<{ keyId: string; error: string }>,
    startTime: number
  ): Promise<FallbackResult> {
    // Get user's keys for this provider
    const keys = await this.database.getUserKeys(userId, {
      provider,
      environment,
      status: KeyStatus.ACTIVE,
      includeExpired: false,
      sortBy: 'health_score',
      sortOrder: 'desc'
    });

    // Try each key in order of health score
    for (const storedKey of keys) {
      try {
        const result = await this.tryKey(storedKey.id, attemptedKeys, failedKeys);
        if (result) {
          return {
            ...result,
            totalAttempts: attemptedKeys.length,
            executionTime: Date.now() - startTime
          };
        }
      } catch (error) {
        // Continue to next key
        await this.delay(1000); // Default delay
      }
    }

    // Try system fallback
    try {
      const systemKey = await this.getSystemFallbackKey(provider, environment);
      return {
        key: systemKey,
        keyId: `system-${provider}`,
        wasSystemFallback: true,
        attemptedKeys,
        failedKeys,
        totalAttempts: attemptedKeys.length,
        executionTime: Date.now() - startTime
      };
    } catch (error) {
      failedKeys.push({
        keyId: `system-${provider}`,
        error: error instanceof Error ? error.message : 'System fallback failed'
      });
    }

    throw new KeyNotFoundError(`No working keys available for provider ${provider}`, provider);
  }

  private async tryKey(
    keyId: string,
    attemptedKeys: string[],
    failedKeys: Array<{ keyId: string; error: string }>
  ): Promise<Partial<FallbackResult> | null> {
    attemptedKeys.push(keyId);

    // Check circuit breaker
    const breakerStatus = this.getCircuitBreakerStatus(keyId);
    if (!breakerStatus.isAvailable) {
      failedKeys.push({
        keyId,
        error: `Circuit breaker ${breakerStatus.state}: not available`
      });
      return null;
    }

    try {
      // Get the key
      const storedKey = await this.database.getKey(keyId);
      if (!storedKey || storedKey.status !== KeyStatus.ACTIVE) {
        throw new Error(`Key not available: status ${storedKey?.status || 'not found'}`);
      }

      // Validate key if in half-open state
      if (breakerStatus.state === CircuitState.HALF_OPEN) {
        const validationResult = await this.byokManager.testKey(keyId);
        if (!validationResult.isValid) {
          throw new Error(`Key validation failed: ${validationResult.errorMessage}`);
        }
      }

      // Get decrypted key (this would need access to the manager's decrypt method)
      // For now, simulate getting the key
      const decryptedKey = await this.getDecryptedKey(storedKey);
      
      // Record success
      this.recordKeySuccess(keyId);

      return {
        key: decryptedKey,
        keyId,
        wasSystemFallback: false
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      failedKeys.push({ keyId, error: errorMessage });
      this.recordKeyFailure(keyId);
      
      return null;
    }
  }

  private async getDecryptedKey(storedKey: any): Promise<DecryptedKey> {
    // This would need to be implemented with access to the encryption service
    // For now, throw an error indicating this needs to be integrated with BYOKManager
    throw new BYOKError('Key decryption not available in fallback manager', 'NOT_IMPLEMENTED');
  }

  private async getSystemFallbackKey(provider: ProviderType, environment: Environment): Promise<DecryptedKey> {
    // This would get system fallback keys from configuration
    throw new BYOKError('System fallback not configured', 'NO_SYSTEM_FALLBACK');
  }

  private recordKeySuccess(keyId: string): void {
    const breaker = this.circuitBreakers.get(keyId);
    if (breaker) {
      breaker.successCount++;
      
      if (breaker.state === CircuitState.HALF_OPEN) {
        if (breaker.successCount >= this.HALF_OPEN_MAX_CALLS) {
          // Reset to closed state
          this.circuitBreakers.delete(keyId);
        }
      }
    }
  }

  private recordKeyFailure(keyId: string): void {
    let breaker = this.circuitBreakers.get(keyId);
    
    if (!breaker) {
      breaker = {
        state: CircuitState.CLOSED,
        failureCount: 0,
        lastFailureTime: 0,
        successCount: 0,
        nextRetryTime: 0
      };
      this.circuitBreakers.set(keyId, breaker);
    }

    breaker.failureCount++;
    breaker.lastFailureTime = Date.now();
    
    if (breaker.failureCount >= this.FAILURE_THRESHOLD) {
      breaker.state = CircuitState.OPEN;
      breaker.nextRetryTime = Date.now() + this.RECOVERY_TIMEOUT;
    }
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getDefaultCircuitBreakerConfig(): Record<string, any> {
    return {
      failureThreshold: this.FAILURE_THRESHOLD,
      recoveryTimeout: this.RECOVERY_TIMEOUT,
      halfOpenMaxCalls: this.HALF_OPEN_MAX_CALLS
    };
  }
}

/**
 * Factory function for creating fallback manager
 */
export function createFallbackManager(
  database: DatabaseInterface,
  byokManager: BYOKManager
): FallbackManager {
  return new FallbackManager(database, byokManager);
}
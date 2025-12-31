/**
 * @stack-2025/byok-core Fallback Service
 * Circuit breaker and fallback management for API keys
 */

import { PrismaClient } from '@prisma/client';
import {
  BYOKProvider,
  FallbackChain,
  KeyStatus,
  BYOKError,
  BYOKErrorCode
} from '../types';

interface CircuitBreakerState {
  failures: number;
  lastFailure?: Date;
  state: 'closed' | 'open' | 'half-open';
  nextRetry?: Date;
}

export class FallbackService {
  private circuitBreakers: Map<string, CircuitBreakerState> = new Map();
  private readonly failureThreshold = 5;
  private readonly resetTimeout = 60000; // 1 minute
  private readonly halfOpenRequests = 3;

  constructor(private prisma: PrismaClient) {}

  /**
   * Get a fallback key for a provider
   */
  async getFallbackKey(
    userId: string,
    provider: BYOKProvider
  ): Promise<string> {
    // Get fallback chain
    const chain = await this.prisma.fallbackChain.findFirst({
      where: {
        userId,
        provider,
        enabled: true
      }
    });

    if (!chain) {
      throw new BYOKError(
        'No fallback chain configured',
        BYOKErrorCode.KEY_NOT_FOUND,
        404
      );
    }

    // Try each fallback key in order
    for (const keyId of chain.fallbackKeyIds) {
      const breaker = this.getCircuitBreaker(keyId);
      
      if (breaker.state === 'open') {
        // Check if we should try half-open
        if (breaker.nextRetry && new Date() >= breaker.nextRetry) {
          breaker.state = 'half-open';
          breaker.failures = 0;
        } else {
          continue; // Skip this key
        }
      }

      try {
        const key = await this.prisma.bYOKKey.findFirst({
          where: {
            id: keyId,
            userId,
            status: KeyStatus.ACTIVE
          }
        });

        if (key) {
          // Reset circuit breaker on success
          this.resetCircuitBreaker(keyId);
          return key.encryptedKey; // Will be decrypted by caller
        }
      } catch (error) {
        this.recordFailure(keyId);
        continue;
      }
    }

    throw new BYOKError(
      'All fallback keys failed',
      BYOKErrorCode.KEY_NOT_FOUND,
      404
    );
  }

  /**
   * Create or update a fallback chain
   */
  async configureFallback(
    userId: string,
    provider: BYOKProvider,
    primaryKeyId: string,
    fallbackKeyIds: string[],
    strategy: 'sequential' | 'load-balance' | 'cost-optimize' = 'sequential'
  ): Promise<FallbackChain> {
    // Validate all keys exist
    const keys = await this.prisma.bYOKKey.findMany({
      where: {
        id: {
          in: [primaryKeyId, ...fallbackKeyIds]
        },
        userId,
        provider
      }
    });

    if (keys.length !== fallbackKeyIds.length + 1) {
      throw new BYOKError(
        'One or more keys not found',
        BYOKErrorCode.KEY_NOT_FOUND,
        404
      );
    }

    // Check for existing chain
    const existing = await this.prisma.fallbackChain.findFirst({
      where: {
        userId,
        provider
      }
    });

    if (existing) {
      // Update existing chain
      return await this.prisma.fallbackChain.update({
        where: { id: existing.id },
        data: {
          primaryKeyId,
          fallbackKeyIds,
          strategy,
          updatedAt: new Date()
        }
      });
    } else {
      // Create new chain
      return await this.prisma.fallbackChain.create({
        data: {
          userId,
          provider,
          primaryKeyId,
          fallbackKeyIds,
          strategy,
          enabled: true,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      });
    }
  }

  /**
   * Get fallback chain for a user and provider
   */
  async getFallbackChain(
    userId: string,
    provider: BYOKProvider
  ): Promise<FallbackChain | null> {
    return await this.prisma.fallbackChain.findFirst({
      where: {
        userId,
        provider
      }
    });
  }

  /**
   * Enable/disable fallback chain
   */
  async toggleFallback(
    userId: string,
    provider: BYOKProvider,
    enabled: boolean
  ): Promise<void> {
    await this.prisma.fallbackChain.updateMany({
      where: {
        userId,
        provider
      },
      data: {
        enabled,
        updatedAt: new Date()
      }
    });
  }

  /**
   * Get circuit breaker state for a key
   */
  private getCircuitBreaker(keyId: string): CircuitBreakerState {
    if (!this.circuitBreakers.has(keyId)) {
      this.circuitBreakers.set(keyId, {
        failures: 0,
        state: 'closed'
      });
    }
    return this.circuitBreakers.get(keyId)!;
  }

  /**
   * Record a failure for circuit breaker
   */
  private recordFailure(keyId: string): void {
    const breaker = this.getCircuitBreaker(keyId);
    breaker.failures++;
    breaker.lastFailure = new Date();

    if (breaker.failures >= this.failureThreshold) {
      breaker.state = 'open';
      breaker.nextRetry = new Date(Date.now() + this.resetTimeout);
    }
  }

  /**
   * Reset circuit breaker after success
   */
  private resetCircuitBreaker(keyId: string): void {
    const breaker = this.getCircuitBreaker(keyId);
    breaker.failures = 0;
    breaker.state = 'closed';
    breaker.lastFailure = undefined;
    breaker.nextRetry = undefined;
  }

  /**
   * Get health status of all circuit breakers
   */
  getCircuitBreakerStatus(): Map<string, CircuitBreakerState> {
    return new Map(this.circuitBreakers);
  }

  /**
   * Reset all circuit breakers
   */
  resetAllCircuitBreakers(): void {
    this.circuitBreakers.clear();
  }

  /**
   * Load balance strategy - select key based on usage
   */
  async loadBalanceSelect(
    keys: string[],
    userId: string
  ): Promise<string> {
    // Get usage stats for each key
    const usageStats = await Promise.all(
      keys.map(async (keyId) => {
        const count = await this.prisma.bYOKUsage.count({
          where: {
            keyId,
            userId,
            timestamp: {
              gte: new Date(Date.now() - 3600000) // Last hour
            }
          }
        });
        return { keyId, usage: count };
      })
    );

    // Select key with lowest usage
    usageStats.sort((a, b) => a.usage - b.usage);
    return usageStats[0].keyId;
  }

  /**
   * Cost optimize strategy - select cheapest key
   */
  async costOptimizeSelect(
    keys: string[],
    userId: string
  ): Promise<string> {
    // Get cost data for each key
    const keyData = await this.prisma.bYOKKey.findMany({
      where: {
        id: { in: keys },
        userId
      }
    });

    // Sort by cost (stored in metadata)
    keyData.sort((a, b) => {
      const costA = (a.metadata as any)?.costPerRequest || 999;
      const costB = (b.metadata as any)?.costPerRequest || 999;
      return costA - costB;
    });

    return keyData[0].id;
  }
}
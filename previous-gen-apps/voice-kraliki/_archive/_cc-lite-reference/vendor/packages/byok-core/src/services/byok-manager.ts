/**
 * @stack-2025/byok-core Main BYOK Manager
 * Core service for managing API keys across all Stack 2025 applications
 */

import { PrismaClient } from '@prisma/client';
import Redis from 'ioredis';
import { 
  BYOKKey, 
  BYOKConfig, 
  BYOKProvider, 
  KeyStatus,
  CreateKeyRequest,
  UpdateKeyRequest,
  KeyValidationResult,
  BYOKUsage,
  FallbackChain,
  AuditLog,
  BYOKError,
  BYOKErrorCode,
  CacheKeys,
  BYOKMetrics
} from '../types';
import { EncryptionService } from './encryption.service';
import { ValidationService } from './validation.service';
import { AuditService } from './audit.service';
import { FallbackService } from './fallback.service';

export class BYOKManager {
  private prisma: PrismaClient;
  private redis?: Redis;
  private encryption: EncryptionService;
  private validation: ValidationService;
  private audit: AuditService;
  private fallback: FallbackService;

  constructor(private config: BYOKConfig) {
    this.prisma = new PrismaClient();
    this.encryption = new EncryptionService(config.encryptionKey);
    this.validation = new ValidationService();
    this.audit = new AuditService(this.prisma);
    this.fallback = new FallbackService(this.prisma);

    if (config.redisUrl && config.cacheEnabled) {
      this.redis = new Redis(config.redisUrl);
    }
  }

  /**
   * Create a new API key
   */
  async createKey(
    userId: string,
    request: CreateKeyRequest
  ): Promise<BYOKKey> {
    try {
      // Validate the API key with the provider
      const validation = await this.validation.validateKey(
        request.provider,
        request.apiKey
      );

      if (!validation.isValid) {
        throw new BYOKError(
          'Invalid API key',
          BYOKErrorCode.INVALID_KEY,
          400,
          validation
        );
      }

      // Encrypt the API key
      const encryptedKey = await this.encryption.encrypt(
        request.apiKey,
        userId
      );

      // Generate key hash for duplicate detection
      const keyHash = await this.encryption.hash(request.apiKey);

      // Check for duplicate keys
      const existingKey = await this.prisma.bYOKKey.findFirst({
        where: {
          userId,
          provider: request.provider,
          keyHash
        }
      });

      if (existingKey) {
        throw new BYOKError(
          'This API key is already registered',
          BYOKErrorCode.INVALID_KEY,
          400
        );
      }

      // Create the key in database
      const key = await this.prisma.bYOKKey.create({
        data: {
          userId,
          provider: request.provider,
          keyName: request.keyName,
          encryptedKey,
          keyHash,
          status: KeyStatus.ACTIVE,
          lastValidated: new Date(),
          validationScore: validation.score,
          expiresAt: request.expiresAt,
          metadata: request.metadata || {}
        }
      });

      // Cache the key if Redis is enabled
      if (this.redis) {
        await this.cacheKey(key);
      }

      // Audit the creation
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'CREATE_KEY',
          resource: 'BYOK_KEY',
          resourceId: key.id,
          success: true,
          metadata: { provider: request.provider }
        });
      }

      return key;
    } catch (error) {
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'CREATE_KEY',
          resource: 'BYOK_KEY',
          resourceId: '',
          success: false,
          errorMessage: error.message,
          metadata: { provider: request.provider }
        });
      }
      throw error;
    }
  }

  /**
   * Get a decrypted API key
   */
  async getKey(
    userId: string,
    keyId: string
  ): Promise<string> {
    try {
      // Try cache first
      if (this.redis) {
        const cached = await this.redis.get(CacheKeys.key(keyId));
        if (cached) {
          const key = JSON.parse(cached) as BYOKKey;
          if (key.userId === userId) {
            return await this.encryption.decrypt(key.encryptedKey, userId);
          }
        }
      }

      // Get from database
      const key = await this.prisma.bYOKKey.findFirst({
        where: {
          id: keyId,
          userId
        }
      });

      if (!key) {
        throw new BYOKError(
          'Key not found',
          BYOKErrorCode.KEY_NOT_FOUND,
          404
        );
      }

      // Check if key is expired
      if (key.expiresAt && key.expiresAt < new Date()) {
        await this.updateKeyStatus(keyId, KeyStatus.EXPIRED);
        throw new BYOKError(
          'Key has expired',
          BYOKErrorCode.INVALID_KEY,
          400
        );
      }

      // Decrypt and return
      return await this.encryption.decrypt(key.encryptedKey, userId);
    } catch (error) {
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'GET_KEY',
          resource: 'BYOK_KEY',
          resourceId: keyId,
          success: false,
          errorMessage: error.message
        });
      }
      throw error;
    }
  }

  /**
   * Get a key for a specific provider with fallback support
   */
  async getProviderKey(
    userId: string,
    provider: BYOKProvider
  ): Promise<string> {
    try {
      // Get primary key
      const primaryKey = await this.prisma.bYOKKey.findFirst({
        where: {
          userId,
          provider,
          status: KeyStatus.ACTIVE
        },
        orderBy: {
          validationScore: 'desc'
        }
      });

      if (primaryKey) {
        try {
          const apiKey = await this.encryption.decrypt(
            primaryKey.encryptedKey,
            userId
          );

          // Track usage
          await this.trackUsage({
            keyId: primaryKey.id,
            userId,
            provider,
            operation: 'GET_KEY',
            success: true
          });

          return apiKey;
        } catch (error) {
          // Try fallback if enabled
          if (this.config.fallbackEnabled) {
            return await this.fallback.getFallbackKey(userId, provider);
          }
          throw error;
        }
      }

      // Try fallback if no primary key
      if (this.config.fallbackEnabled) {
        return await this.fallback.getFallbackKey(userId, provider);
      }

      throw new BYOKError(
        `No active key found for provider ${provider}`,
        BYOKErrorCode.KEY_NOT_FOUND,
        404
      );
    } catch (error) {
      await this.trackUsage({
        keyId: '',
        userId,
        provider,
        operation: 'GET_KEY',
        success: false,
        errorMessage: error.message
      });
      throw error;
    }
  }

  /**
   * Update an API key
   */
  async updateKey(
    userId: string,
    keyId: string,
    request: UpdateKeyRequest
  ): Promise<BYOKKey> {
    try {
      const key = await this.prisma.bYOKKey.findFirst({
        where: {
          id: keyId,
          userId
        }
      });

      if (!key) {
        throw new BYOKError(
          'Key not found',
          BYOKErrorCode.KEY_NOT_FOUND,
          404
        );
      }

      const updateData: any = {};

      // Update API key if provided
      if (request.apiKey) {
        const validation = await this.validation.validateKey(
          key.provider,
          request.apiKey
        );

        if (!validation.isValid) {
          throw new BYOKError(
            'Invalid API key',
            BYOKErrorCode.INVALID_KEY,
            400,
            validation
          );
        }

        updateData.encryptedKey = await this.encryption.encrypt(
          request.apiKey,
          userId
        );
        updateData.keyHash = await this.encryption.hash(request.apiKey);
        updateData.lastValidated = new Date();
        updateData.validationScore = validation.score;
        updateData.status = KeyStatus.ACTIVE;
      }

      // Update other fields
      if (request.keyName) updateData.keyName = request.keyName;
      if (request.expiresAt) updateData.expiresAt = request.expiresAt;
      if (request.metadata) updateData.metadata = request.metadata;

      // Update in database
      const updatedKey = await this.prisma.bYOKKey.update({
        where: { id: keyId },
        data: updateData
      });

      // Update cache
      if (this.redis) {
        await this.cacheKey(updatedKey);
      }

      // Audit the update
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'UPDATE_KEY',
          resource: 'BYOK_KEY',
          resourceId: keyId,
          success: true,
          metadata: { changes: Object.keys(updateData) }
        });
      }

      return updatedKey;
    } catch (error) {
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'UPDATE_KEY',
          resource: 'BYOK_KEY',
          resourceId: keyId,
          success: false,
          errorMessage: error.message
        });
      }
      throw error;
    }
  }

  /**
   * Delete an API key
   */
  async deleteKey(
    userId: string,
    keyId: string
  ): Promise<void> {
    try {
      const key = await this.prisma.bYOKKey.findFirst({
        where: {
          id: keyId,
          userId
        }
      });

      if (!key) {
        throw new BYOKError(
          'Key not found',
          BYOKErrorCode.KEY_NOT_FOUND,
          404
        );
      }

      // Delete from database
      await this.prisma.bYOKKey.delete({
        where: { id: keyId }
      });

      // Remove from cache
      if (this.redis) {
        await this.redis.del(CacheKeys.key(keyId));
        await this.redis.srem(CacheKeys.userKeys(userId), keyId);
      }

      // Audit the deletion
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'DELETE_KEY',
          resource: 'BYOK_KEY',
          resourceId: keyId,
          success: true,
          metadata: { provider: key.provider }
        });
      }
    } catch (error) {
      if (this.config.auditingEnabled) {
        await this.audit.log({
          userId,
          action: 'DELETE_KEY',
          resource: 'BYOK_KEY',
          resourceId: keyId,
          success: false,
          errorMessage: error.message
        });
      }
      throw error;
    }
  }

  /**
   * List all keys for a user
   */
  async listKeys(userId: string): Promise<BYOKKey[]> {
    try {
      // Try cache first
      if (this.redis) {
        const keyIds = await this.redis.smembers(CacheKeys.userKeys(userId));
        if (keyIds.length > 0) {
          const keys = await Promise.all(
            keyIds.map(async (keyId) => {
              const cached = await this.redis!.get(CacheKeys.key(keyId));
              return cached ? JSON.parse(cached) : null;
            })
          );
          const validKeys = keys.filter(Boolean) as BYOKKey[];
          if (validKeys.length === keyIds.length) {
            return validKeys;
          }
        }
      }

      // Get from database
      const keys = await this.prisma.bYOKKey.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' }
      });

      // Cache the keys
      if (this.redis) {
        await Promise.all(keys.map(key => this.cacheKey(key)));
      }

      return keys;
    } catch (error) {
      throw new BYOKError(
        'Failed to list keys',
        BYOKErrorCode.PROVIDER_ERROR,
        500,
        error
      );
    }
  }

  /**
   * Validate all keys for a user
   */
  async validateUserKeys(userId: string): Promise<Map<string, KeyValidationResult>> {
    const keys = await this.listKeys(userId);
    const results = new Map<string, KeyValidationResult>();

    for (const key of keys) {
      try {
        const decryptedKey = await this.encryption.decrypt(
          key.encryptedKey,
          userId
        );
        const validation = await this.validation.validateKey(
          key.provider,
          decryptedKey
        );

        // Update key status based on validation
        if (validation.status !== key.status) {
          await this.updateKeyStatus(key.id, validation.status);
        }

        results.set(key.id, validation);
      } catch (error) {
        results.set(key.id, {
          isValid: false,
          status: KeyStatus.INVALID,
          score: 0,
          message: error.message
        });
      }
    }

    return results;
  }

  /**
   * Get usage statistics
   */
  async getUsageStats(
    userId: string,
    startDate: Date,
    endDate: Date
  ): Promise<BYOKUsage[]> {
    return await this.prisma.bYOKUsage.findMany({
      where: {
        userId,
        timestamp: {
          gte: startDate,
          lte: endDate
        }
      },
      orderBy: { timestamp: 'desc' }
    });
  }

  /**
   * Get metrics
   */
  async getMetrics(): Promise<BYOKMetrics> {
    const [
      totalKeys,
      activeKeys,
      invalidKeys,
      totalRequests,
      successfulRequests,
      providerCounts
    ] = await Promise.all([
      this.prisma.bYOKKey.count(),
      this.prisma.bYOKKey.count({ where: { status: KeyStatus.ACTIVE } }),
      this.prisma.bYOKKey.count({ where: { status: KeyStatus.INVALID } }),
      this.prisma.bYOKUsage.count(),
      this.prisma.bYOKUsage.count({ where: { success: true } }),
      this.prisma.bYOKKey.groupBy({
        by: ['provider'],
        _count: true
      })
    ]);

    const providerBreakdown = providerCounts.reduce((acc, curr) => {
      acc[curr.provider as BYOKProvider] = curr._count;
      return acc;
    }, {} as Record<BYOKProvider, number>);

    // Calculate cache hit rate if Redis is enabled
    let cacheHitRate = 0;
    if (this.redis) {
      const info = await this.redis.info('stats');
      const hits = parseInt(info.match(/keyspace_hits:(\d+)/)?.[1] || '0');
      const misses = parseInt(info.match(/keyspace_misses:(\d+)/)?.[1] || '0');
      cacheHitRate = hits / (hits + misses) || 0;
    }

    return {
      totalKeys,
      activeKeys,
      invalidKeys,
      totalRequests,
      successfulRequests,
      failedRequests: totalRequests - successfulRequests,
      averageResponseTime: 0, // TODO: Implement response time tracking
      cacheHitRate,
      validationSuccessRate: successfulRequests / totalRequests || 0,
      providerBreakdown
    };
  }

  /**
   * Helper: Cache a key
   */
  private async cacheKey(key: BYOKKey): Promise<void> {
    if (!this.redis) return;

    const ttl = this.config.cacheTTL || 3600;
    await this.redis.setex(
      CacheKeys.key(key.id),
      ttl,
      JSON.stringify(key)
    );
    await this.redis.sadd(CacheKeys.userKeys(key.userId), key.id);
  }

  /**
   * Helper: Update key status
   */
  private async updateKeyStatus(
    keyId: string,
    status: KeyStatus
  ): Promise<void> {
    await this.prisma.bYOKKey.update({
      where: { id: keyId },
      data: { status }
    });

    if (this.redis) {
      await this.redis.del(CacheKeys.key(keyId));
    }
  }

  /**
   * Helper: Track usage
   */
  private async trackUsage(usage: Omit<BYOKUsage, 'id' | 'timestamp'>): Promise<void> {
    await this.prisma.bYOKUsage.create({
      data: {
        ...usage,
        timestamp: new Date()
      }
    });
  }

  /**
   * Cleanup resources
   */
  async cleanup(): Promise<void> {
    await this.prisma.$disconnect();
    if (this.redis) {
      this.redis.disconnect();
    }
  }
}
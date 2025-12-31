/**
 * @stack-2025/byok-core - Cache Service
 * Caching layer for BYOK operations using Redis
 */

import { DecryptedKey, BYOKError } from './types.js';

/**
 * Cache service for BYOK operations
 */
export class CacheService {
  private redis: any;
  private defaultTTL: number;

  constructor(redisClient: any, defaultTTL: number = 300) {
    this.redis = redisClient;
    this.defaultTTL = defaultTTL; // 5 minutes default
  }

  /**
   * Get cached key
   */
  async get(key: string): Promise<DecryptedKey | null> {
    try {
      const cached = await this.redis.get(key);
      if (cached) {
        return JSON.parse(cached);
      }
      return null;
    } catch (error) {
      console.warn('Cache get error:', error);
      return null; // Fail gracefully
    }
  }

  /**
   * Set cached key
   */
  async set(key: string, value: DecryptedKey, ttl?: number): Promise<void> {
    try {
      await this.redis.setEx(
        key,
        ttl || this.defaultTTL,
        JSON.stringify(value)
      );
    } catch (error) {
      console.warn('Cache set error:', error);
      // Don't throw - caching is optional
    }
  }

  /**
   * Delete cached key
   */
  async del(key: string): Promise<void> {
    try {
      await this.redis.del(key);
    } catch (error) {
      console.warn('Cache delete error:', error);
    }
  }

  /**
   * Clear all cached keys for a user
   */
  async clearUserCache(userId: string): Promise<void> {
    try {
      const pattern = `byok:user:${userId}:*`;
      const keys = await this.redis.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
      }
    } catch (error) {
      console.warn('Cache clear user error:', error);
    }
  }

  /**
   * Clear all BYOK cache
   */
  async clearAll(): Promise<void> {
    try {
      const pattern = 'byok:*';
      const keys = await this.redis.keys(pattern);
      if (keys.length > 0) {
        await this.redis.del(...keys);
      }
    } catch (error) {
      console.warn('Cache clear all error:', error);
    }
  }
}
/**
 * @stack-2025/byok-core - Database Operations
 * Database abstraction layer for BYOK system
 */

import { 
  StoredKey, 
  KeyUsageStats, 
  KeyValidationResult, 
  FallbackChain, 
  UsageAlert, 
  AuditLogEntry, 
  ProviderConfig,
  ProviderType,
  KeyStatus,
  Environment,
  EventType,
  KeyListOptions,
  AnalyticsOptions,
  BYOKError
} from './types.js';

/**
 * Database interface for BYOK operations
 */
export interface DatabaseInterface {
  // Connection management
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  ping(): Promise<boolean>;

  // User management
  createUser(userId: string, organizationId?: string): Promise<void>;
  getUser(userId: string): Promise<{ id: string; userId: string; organizationId?: string } | null>;
  
  // Key operations
  createKey(key: Omit<StoredKey, 'id' | 'createdAt' | 'updatedAt'>): Promise<string>;
  getKey(keyId: string): Promise<StoredKey | null>;
  getKeyByHash(userId: string, keyHash: string): Promise<StoredKey | null>;
  getUserKeys(userId: string, options?: KeyListOptions): Promise<StoredKey[]>;
  updateKey(keyId: string, updates: Partial<StoredKey>): Promise<void>;
  deleteKey(keyId: string): Promise<void>;
  
  // Key validation
  createValidation(validation: Omit<KeyValidationResult, 'keyId'>): Promise<void>;
  getLatestValidation(keyId: string): Promise<KeyValidationResult | null>;
  getValidationHistory(keyId: string, limit?: number): Promise<KeyValidationResult[]>;
  
  // Usage tracking
  recordUsage(usage: {
    keyId: string;
    requestsCount: number;
    tokensConsumed: number;
    costUsd: number;
    operation: string;
    modelUsed?: string;
    success: boolean;
    errorCode?: string;
    responseTimeMs?: number;
    dataProcessedBytes?: number;
  }): Promise<void>;
  getUsageStats(keyId: string, timeframe: { start: Date; end: Date }): Promise<KeyUsageStats>;
  getUserUsageStats(userId: string, options: AnalyticsOptions): Promise<KeyUsageStats[]>;
  
  // Fallback chains
  createFallbackChain(chain: Omit<FallbackChain, 'id' | 'createdAt' | 'updatedAt'>): Promise<string>;
  getFallbackChain(userId: string, provider: ProviderType, environment: Environment): Promise<FallbackChain | null>;
  updateFallbackChain(chainId: string, updates: Partial<FallbackChain>): Promise<void>;
  deleteFallbackChain(chainId: string): Promise<void>;
  
  // Usage alerts
  createUsageAlert(alert: Omit<UsageAlert, 'id' | 'createdAt' | 'updatedAt'>): Promise<string>;
  getUserAlerts(userId: string): Promise<UsageAlert[]>;
  updateAlert(alertId: string, updates: Partial<UsageAlert>): Promise<void>;
  deleteAlert(alertId: string): Promise<void>;
  getTriggeredAlerts(userId: string): Promise<UsageAlert[]>;
  
  // Audit logging
  logEvent(entry: Omit<AuditLogEntry, 'id' | 'eventTimestamp'>): Promise<void>;
  getAuditLog(filters: {
    userId?: string;
    keyId?: string;
    eventType?: EventType;
    startDate?: Date;
    endDate?: Date;
    limit?: number;
    offset?: number;
  }): Promise<AuditLogEntry[]>;
  
  // Provider configurations
  getProviderConfigs(providerType?: ProviderType): Promise<ProviderConfig[]>;
  getProviderConfig(providerType: ProviderType, service?: string): Promise<ProviderConfig | null>;
  
  // Analytics and reporting
  getSystemStats(): Promise<{
    totalUsers: number;
    totalKeys: number;
    activeKeys: number;
    keysByProvider: Record<ProviderType, number>;
    dailyUsage: number;
    monthlyUsage: number;
  }>;
  
  // Cleanup operations
  cleanupExpiredKeys(): Promise<number>;
  cleanupOldUsageData(retentionDays: number): Promise<number>;
  cleanupAuditLogs(retentionDays: number): Promise<number>;
}

/**
 * PostgreSQL implementation of the database interface
 */
export class PostgreSQLDatabase implements DatabaseInterface {
  private client: any;
  private connected = false;

  constructor(client: any) {
    this.client = client;
  }

  async connect(): Promise<void> {
    try {
      if (!this.connected) {
        await this.client.connect();
        this.connected = true;
      }
    } catch (error) {
      throw new BYOKError(`Database connection failed: ${error}`, 'DB_CONNECTION_ERROR');
    }
  }

  async disconnect(): Promise<void> {
    try {
      if (this.connected) {
        await this.client.end();
        this.connected = false;
      }
    } catch (error) {
      throw new BYOKError(`Database disconnection failed: ${error}`, 'DB_DISCONNECTION_ERROR');
    }
  }

  async ping(): Promise<boolean> {
    try {
      await this.client.query('SELECT 1');
      return true;
    } catch {
      return false;
    }
  }

  async createUser(userId: string, organizationId?: string): Promise<void> {
    const query = `
      INSERT INTO byok_users (user_id, organization_id, encryption_key_hash)
      VALUES ($1, $2, $3)
      ON CONFLICT (user_id) DO NOTHING
    `;
    
    // Generate a unique encryption key hash for this user
    const crypto = await import('node:crypto');
    const keyHash = crypto.createHash('sha256').update(userId).digest('hex');
    
    try {
      await this.client.query(query, [userId, organizationId, keyHash]);
    } catch (error) {
      throw new BYOKError(`Failed to create user: ${error}`, 'DB_CREATE_USER_ERROR');
    }
  }

  async getUser(userId: string): Promise<{ id: string; userId: string; organizationId?: string } | null> {
    const query = `
      SELECT id, user_id, organization_id 
      FROM byok_users 
      WHERE user_id = $1
    `;
    
    try {
      const result = await this.client.query(query, [userId]);
      return result.rows[0] || null;
    } catch (error) {
      throw new BYOKError(`Failed to get user: ${error}`, 'DB_GET_USER_ERROR');
    }
  }

  async createKey(key: Omit<StoredKey, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
    // First ensure user exists
    await this.createUser(key.userId, key.organizationId);
    
    // Get user's internal ID
    const user = await this.getUser(key.userId);
    if (!user) {
      throw new BYOKError(`User not found: ${key.userId}`, 'USER_NOT_FOUND');
    }

    const query = `
      INSERT INTO byok_keys (
        user_id, provider_type, provider_service, alias, description, environment,
        encrypted_key_data, encryption_nonce, key_hash, metadata, capabilities,
        status, health_score, usage_tracking, rate_limit_config, quota_config, expires_at
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
      RETURNING id
    `;
    
    try {
      const result = await this.client.query(query, [
        user.id,
        key.provider,
        key.providerService,
        key.alias,
        key.description,
        key.environment,
        key.encryptedKeyData,
        key.encryptionNonce,
        key.keyHash,
        JSON.stringify(key.metadata),
        JSON.stringify(key.capabilities),
        key.status,
        key.healthScore,
        key.usageTracking,
        JSON.stringify(key.rateLimitConfig),
        JSON.stringify(key.quotaConfig),
        key.expiresAt
      ]);
      
      return result.rows[0].id;
    } catch (error) {
      if ((error as any).code === '23505') { // Unique violation
        throw new BYOKError('Duplicate key detected', 'DUPLICATE_KEY');
      }
      throw new BYOKError(`Failed to create key: ${error}`, 'DB_CREATE_KEY_ERROR');
    }
  }

  async getKey(keyId: string): Promise<StoredKey | null> {
    const query = `
      SELECT k.*, u.user_id, u.organization_id
      FROM byok_keys k
      JOIN byok_users u ON k.user_id = u.id
      WHERE k.id = $1
    `;
    
    try {
      const result = await this.client.query(query, [keyId]);
      if (!result.rows[0]) return null;
      
      return this.mapRowToStoredKey(result.rows[0]);
    } catch (error) {
      throw new BYOKError(`Failed to get key: ${error}`, 'DB_GET_KEY_ERROR');
    }
  }

  async getKeyByHash(userId: string, keyHash: string): Promise<StoredKey | null> {
    const query = `
      SELECT k.*, u.user_id, u.organization_id
      FROM byok_keys k
      JOIN byok_users u ON k.user_id = u.id
      WHERE u.user_id = $1 AND k.key_hash = $2
    `;
    
    try {
      const result = await this.client.query(query, [userId, keyHash]);
      if (!result.rows[0]) return null;
      
      return this.mapRowToStoredKey(result.rows[0]);
    } catch (error) {
      throw new BYOKError(`Failed to get key by hash: ${error}`, 'DB_GET_KEY_BY_HASH_ERROR');
    }
  }

  async getUserKeys(userId: string, options: KeyListOptions = {}): Promise<StoredKey[]> {
    let query = `
      SELECT k.*, u.user_id, u.organization_id
      FROM byok_keys k
      JOIN byok_users u ON k.user_id = u.id
      WHERE u.user_id = $1
    `;
    
    const params: any[] = [userId];
    let paramIndex = 2;
    
    // Add filters
    if (options.provider) {
      query += ` AND k.provider_type = $${paramIndex}`;
      params.push(options.provider);
      paramIndex++;
    }
    
    if (options.environment) {
      query += ` AND k.environment = $${paramIndex}`;
      params.push(options.environment);
      paramIndex++;
    }
    
    if (options.status) {
      query += ` AND k.status = $${paramIndex}`;
      params.push(options.status);
      paramIndex++;
    }
    
    if (!options.includeExpired) {
      query += ` AND (k.expires_at IS NULL OR k.expires_at > NOW())`;
    }
    
    // Add sorting
    const sortBy = options.sortBy || 'created_at';
    const sortOrder = options.sortOrder || 'desc';
    query += ` ORDER BY k.${sortBy} ${sortOrder}`;
    
    // Add pagination
    if (options.limit) {
      query += ` LIMIT $${paramIndex}`;
      params.push(options.limit);
      paramIndex++;
    }
    
    if (options.offset) {
      query += ` OFFSET $${paramIndex}`;
      params.push(options.offset);
    }
    
    try {
      const result = await this.client.query(query, params);
      return result.rows.map((row: any) => this.mapRowToStoredKey(row));
    } catch (error) {
      throw new BYOKError(`Failed to get user keys: ${error}`, 'DB_GET_USER_KEYS_ERROR');
    }
  }

  async updateKey(keyId: string, updates: Partial<StoredKey>): Promise<void> {
    const setClauses: string[] = [];
    const params: any[] = [];
    let paramIndex = 1;
    
    // Build SET clauses dynamically
    for (const [key, value] of Object.entries(updates)) {
      if (value !== undefined) {
        let columnName = key;
        // Convert camelCase to snake_case
        columnName = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
        
        if (key === 'metadata' || key === 'capabilities' || key === 'rateLimitConfig' || key === 'quotaConfig') {
          setClauses.push(`${columnName} = $${paramIndex}`);
          params.push(JSON.stringify(value));
        } else {
          setClauses.push(`${columnName} = $${paramIndex}`);
          params.push(value);
        }
        paramIndex++;
      }
    }
    
    if (setClauses.length === 0) return;
    
    // Always update the updated_at timestamp
    setClauses.push(`updated_at = NOW()`);
    
    const query = `
      UPDATE byok_keys 
      SET ${setClauses.join(', ')}
      WHERE id = $${paramIndex}
    `;
    params.push(keyId);
    
    try {
      await this.client.query(query, params);
    } catch (error) {
      throw new BYOKError(`Failed to update key: ${error}`, 'DB_UPDATE_KEY_ERROR');
    }
  }

  async deleteKey(keyId: string): Promise<void> {
    const query = 'DELETE FROM byok_keys WHERE id = $1';
    
    try {
      await this.client.query(query, [keyId]);
    } catch (error) {
      throw new BYOKError(`Failed to delete key: ${error}`, 'DB_DELETE_KEY_ERROR');
    }
  }

  // Helper method to map database row to StoredKey object
  private mapRowToStoredKey(row: any): StoredKey {
    return {
      id: row.id,
      userId: row.user_id,
      organizationId: row.organization_id,
      provider: row.provider_type,
      providerService: row.provider_service,
      alias: row.alias,
      description: row.description,
      environment: row.environment,
      encryptedKeyData: row.encrypted_key_data,
      encryptionNonce: row.encryption_nonce,
      keyHash: row.key_hash,
      metadata: typeof row.metadata === 'string' ? JSON.parse(row.metadata) : row.metadata,
      capabilities: typeof row.capabilities === 'string' ? JSON.parse(row.capabilities) : row.capabilities,
      status: row.status,
      lastValidatedAt: row.last_validated_at,
      validationError: row.validation_error,
      healthScore: row.health_score,
      usageTracking: row.usage_tracking,
      rateLimitConfig: typeof row.rate_limit_config === 'string' ? JSON.parse(row.rate_limit_config) : row.rate_limit_config,
      quotaConfig: typeof row.quota_config === 'string' ? JSON.parse(row.quota_config) : row.quota_config,
      expiresAt: row.expires_at,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    };
  }

  // Implement remaining methods...
  async createValidation(validation: Omit<KeyValidationResult, 'keyId'>): Promise<void> {
    // Implementation for validation records
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getLatestValidation(keyId: string): Promise<KeyValidationResult | null> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getValidationHistory(keyId: string, limit?: number): Promise<KeyValidationResult[]> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async recordUsage(usage: any): Promise<void> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getUsageStats(keyId: string, timeframe: { start: Date; end: Date }): Promise<KeyUsageStats> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getUserUsageStats(userId: string, options: AnalyticsOptions): Promise<KeyUsageStats[]> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async createFallbackChain(chain: Omit<FallbackChain, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getFallbackChain(userId: string, provider: ProviderType, environment: Environment): Promise<FallbackChain | null> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async updateFallbackChain(chainId: string, updates: Partial<FallbackChain>): Promise<void> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async deleteFallbackChain(chainId: string): Promise<void> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async createUsageAlert(alert: Omit<UsageAlert, 'id' | 'createdAt' | 'updatedAt'>): Promise<string> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getUserAlerts(userId: string): Promise<UsageAlert[]> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async updateAlert(alertId: string, updates: Partial<UsageAlert>): Promise<void> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async deleteAlert(alertId: string): Promise<void> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getTriggeredAlerts(userId: string): Promise<UsageAlert[]> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async logEvent(entry: Omit<AuditLogEntry, 'id' | 'eventTimestamp'>): Promise<void> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getAuditLog(filters: any): Promise<AuditLogEntry[]> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getProviderConfigs(providerType?: ProviderType): Promise<ProviderConfig[]> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getProviderConfig(providerType: ProviderType, service?: string): Promise<ProviderConfig | null> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async getSystemStats(): Promise<any> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async cleanupExpiredKeys(): Promise<number> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async cleanupOldUsageData(retentionDays: number): Promise<number> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }

  async cleanupAuditLogs(retentionDays: number): Promise<number> {
    throw new BYOKError('Method not implemented yet', 'NOT_IMPLEMENTED');
  }
}

/**
 * Factory function for creating database instances
 */
export function createDatabase(
  type: 'postgresql' | 'sqlite' | 'mock',
  config: any
): DatabaseInterface {
  switch (type) {
    case 'postgresql':
      return new PostgreSQLDatabase(config.client);
    case 'sqlite':
      throw new BYOKError('SQLite implementation not available yet', 'NOT_IMPLEMENTED');
    case 'mock':
      throw new BYOKError('Mock implementation not available yet', 'NOT_IMPLEMENTED');
    default:
      throw new BYOKError(`Unsupported database type: ${type}`, 'INVALID_DATABASE_TYPE');
  }
}
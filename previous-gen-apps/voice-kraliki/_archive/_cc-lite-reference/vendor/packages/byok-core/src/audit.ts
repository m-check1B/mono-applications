/**
 * @stack-2025/byok-core - Audit Logger
 * Comprehensive audit logging for BYOK operations
 */

import { 
  AuditLogEntry,
  EventType,
  BYOKError
} from './types.js';

import { DatabaseInterface } from './database.js';

/**
 * Audit configuration
 */
export interface AuditConfig {
  enabled?: boolean;
  retentionDays?: number;
  includeRequestData?: boolean;
  includeResponseData?: boolean;
  logLevel?: 'minimal' | 'standard' | 'detailed';
}

/**
 * Audit logger service
 */
export class AuditLogger {
  private database: DatabaseInterface;
  private config: AuditConfig;

  constructor(database: DatabaseInterface, config?: AuditConfig) {
    this.database = database;
    this.config = {
      enabled: true,
      retentionDays: 90,
      includeRequestData: false,
      includeResponseData: false,
      logLevel: 'standard',
      ...config
    };
  }

  /**
   * Log an event
   */
  async logEvent(event: Partial<AuditLogEntry>): Promise<void> {
    if (!this.config.enabled) return;

    try {
      // Extract request context if available
      const context = this.extractRequestContext();
      
      const logEntry: Omit<AuditLogEntry, 'id' | 'eventTimestamp'> = {
        userId: event.userId,
        keyId: event.keyId,
        eventType: event.eventType || EventType.USE,
        eventAction: event.eventAction || 'unknown',
        ipAddress: context.ipAddress,
        userAgent: context.userAgent,
        sessionId: context.sessionId,
        requestId: context.requestId,
        oldValues: this.sanitizeData(event.oldValues),
        newValues: this.sanitizeData(event.newValues),
        success: event.success ?? true,
        errorMessage: event.errorMessage,
        additionalData: this.sanitizeData(event.additionalData || {})
      };

      // Filter data based on log level
      if (this.config.logLevel === 'minimal') {
        delete logEntry.oldValues;
        delete logEntry.newValues;
        delete logEntry.additionalData;
      } else if (this.config.logLevel === 'standard') {
        // Remove sensitive data
        logEntry.oldValues = this.removeSensitiveFields(logEntry.oldValues);
        logEntry.newValues = this.removeSensitiveFields(logEntry.newValues);
      }

      await this.database.logEvent(logEntry);

    } catch (error) {
      // Log audit failures to console but don't throw
      console.error('Audit logging failed:', error);
    }
  }

  /**
   * Log key creation
   */
  async logKeyCreated(userId: string, keyId: string, provider: string, alias?: string): Promise<void> {
    await this.logEvent({
      userId,
      keyId,
      eventType: EventType.CREATE,
      eventAction: 'create_key',
      success: true,
      newValues: {
        provider,
        alias,
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Log key usage
   */
  async logKeyUsed(userId: string, keyId: string, operation: string, success: boolean, error?: string): Promise<void> {
    await this.logEvent({
      userId,
      keyId,
      eventType: EventType.USE,
      eventAction: `use_key_${operation}`,
      success,
      errorMessage: error,
      additionalData: {
        operation,
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Log key validation
   */
  async logKeyValidated(userId: string, keyId: string, isValid: boolean, error?: string): Promise<void> {
    await this.logEvent({
      userId,
      keyId,
      eventType: EventType.VALIDATE,
      eventAction: 'validate_key',
      success: isValid,
      errorMessage: error,
      additionalData: {
        validationResult: isValid ? 'passed' : 'failed',
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Log security events
   */
  async logSecurityEvent(
    type: 'unauthorized_access' | 'suspicious_activity' | 'rate_limit_exceeded',
    details: Record<string, any>
  ): Promise<void> {
    await this.logEvent({
      eventType: EventType.USE, // Use generic event type
      eventAction: `security_${type}`,
      success: false,
      errorMessage: `Security event: ${type}`,
      additionalData: {
        securityEventType: type,
        ...this.sanitizeData(details),
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Get audit trail for a user
   */
  async getAuditTrail(
    userId: string,
    options?: {
      eventType?: EventType;
      keyId?: string;
      startDate?: Date;
      endDate?: Date;
      limit?: number;
      offset?: number;
    }
  ): Promise<AuditLogEntry[]> {
    return this.database.getAuditLog({
      userId,
      ...options
    });
  }

  /**
   * Get audit trail for a key
   */
  async getKeyAuditTrail(
    keyId: string,
    options?: {
      eventType?: EventType;
      startDate?: Date;
      endDate?: Date;
      limit?: number;
    }
  ): Promise<AuditLogEntry[]> {
    return this.database.getAuditLog({
      keyId,
      ...options
    });
  }

  /**
   * Generate audit report
   */
  async generateReport(
    options: {
      userId?: string;
      startDate: Date;
      endDate: Date;
      eventTypes?: EventType[];
    }
  ): Promise<{
    summary: {
      totalEvents: number;
      successfulEvents: number;
      failedEvents: number;
      eventsByType: Record<EventType, number>;
    };
    events: AuditLogEntry[];
    timeRange: {
      start: Date;
      end: Date;
    };
  }> {
    const events = await this.database.getAuditLog({
      userId: options.userId,
      startDate: options.startDate,
      endDate: options.endDate,
      limit: 10000 // Large limit for report
    });

    // Filter by event types if specified
    const filteredEvents = options.eventTypes 
      ? events.filter(e => options.eventTypes!.includes(e.eventType))
      : events;

    // Calculate summary
    const summary = {
      totalEvents: filteredEvents.length,
      successfulEvents: filteredEvents.filter(e => e.success).length,
      failedEvents: filteredEvents.filter(e => !e.success).length,
      eventsByType: {} as Record<EventType, number>
    };

    // Count events by type
    for (const eventType of Object.values(EventType)) {
      summary.eventsByType[eventType] = filteredEvents.filter(e => e.eventType === eventType).length;
    }

    return {
      summary,
      events: filteredEvents,
      timeRange: {
        start: options.startDate,
        end: options.endDate
      }
    };
  }

  /**
   * Cleanup old audit logs
   */
  async cleanup(): Promise<number> {
    if (!this.config.retentionDays) return 0;
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - this.config.retentionDays);
    
    return this.database.cleanupAuditLogs(this.config.retentionDays);
  }

  // Private helper methods

  private extractRequestContext(): {
    ipAddress?: string;
    userAgent?: string;
    sessionId?: string;
    requestId?: string;
  } {
    // In a real implementation, this would extract context from request headers
    // For now, return empty context
    return {};
  }

  private sanitizeData(data: any): any {
    if (!data) return data;
    
    // Remove or mask sensitive fields
    const sensitiveFields = [
      'password', 'apiKey', 'secret', 'token', 'key',
      'authorization', 'auth', 'credential', 'private'
    ];
    
    if (typeof data === 'object') {
      const sanitized = { ...data };
      
      for (const key in sanitized) {
        const lowerKey = key.toLowerCase();
        
        if (sensitiveFields.some(field => lowerKey.includes(field))) {
          // Mask sensitive data
          if (typeof sanitized[key] === 'string') {
            sanitized[key] = this.maskString(sanitized[key]);
          } else {
            sanitized[key] = '[REDACTED]';
          }
        } else if (typeof sanitized[key] === 'object') {
          sanitized[key] = this.sanitizeData(sanitized[key]);
        }
      }
      
      return sanitized;
    }
    
    return data;
  }

  private removeSensitiveFields(data: any): any {
    if (!data) return data;
    
    const sensitiveFields = [
      'apiKey', 'secret', 'token', 'password', 'credential',
      'encryptedKeyData', 'encryptionNonce', 'keyHash'
    ];
    
    if (typeof data === 'object') {
      const cleaned = { ...data };
      
      for (const field of sensitiveFields) {
        if (field in cleaned) {
          delete cleaned[field];
        }
      }
      
      return cleaned;
    }
    
    return data;
  }

  private maskString(str: string): string {
    if (str.length <= 8) {
      return '*'.repeat(str.length);
    }
    
    // Show first 3 and last 3 characters
    return str.substring(0, 3) + '*'.repeat(str.length - 6) + str.substring(str.length - 3);
  }
}
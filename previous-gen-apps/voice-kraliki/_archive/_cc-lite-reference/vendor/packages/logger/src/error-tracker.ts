/**
 * Stack 2025 Error Tracking
 */

import { ErrorDetails, LogContext } from './types.js';

export interface ErrorStats {
  total: number;
  byType: Record<string, number>;
  byCode: Record<string, number>;
  recent: ErrorRecord[];
  topErrors: Array<{ error: string; count: number }>;
}

export interface ErrorRecord {
  timestamp: Date;
  error: ErrorDetails;
  context?: LogContext;
  frequency: number;
}

export class ErrorTracker {
  private errors: Map<string, ErrorRecord> = new Map();
  private errorCounts: Map<string, number> = new Map();
  private recentErrors: ErrorRecord[] = [];
  private maxRecentErrors = 100;

  track(error: Error | any, context?: LogContext): void {
    const errorDetails = this.extractErrorDetails(error);
    const errorKey = this.generateErrorKey(errorDetails);
    
    // Update error count
    const count = (this.errorCounts.get(errorKey) || 0) + 1;
    this.errorCounts.set(errorKey, count);
    
    // Create or update error record
    const record: ErrorRecord = {
      timestamp: new Date(),
      error: errorDetails,
      context,
      frequency: count
    };
    
    this.errors.set(errorKey, record);
    
    // Add to recent errors
    this.recentErrors.unshift(record);
    if (this.recentErrors.length > this.maxRecentErrors) {
      this.recentErrors.pop();
    }
  }

  private extractErrorDetails(error: Error | any): ErrorDetails {
    if (error instanceof Error) {
      return {
        name: error.name,
        message: error.message,
        stack: error.stack,
        code: (error as any).code,
        statusCode: (error as any).statusCode,
        cause: (error as any).cause,
        metadata: (error as any).metadata
      };
    }
    
    // Handle non-Error objects
    return {
      name: 'UnknownError',
      message: String(error),
      metadata: typeof error === 'object' ? error : undefined
    };
  }

  private generateErrorKey(error: ErrorDetails): string {
    return `${error.name}:${error.message}:${error.code || 'NO_CODE'}`;
  }

  getStats(): ErrorStats {
    const byType: Record<string, number> = {};
    const byCode: Record<string, number> = {};
    
    for (const [key, record] of this.errors) {
      const { error } = record;
      
      // Count by type
      byType[error.name] = (byType[error.name] || 0) + record.frequency;
      
      // Count by code
      if (error.code) {
        byCode[error.code] = (byCode[error.code] || 0) + record.frequency;
      }
    }
    
    // Get top errors
    const topErrors = Array.from(this.errorCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([error, count]) => ({ error, count }));
    
    return {
      total: Array.from(this.errorCounts.values()).reduce((sum, count) => sum + count, 0),
      byType,
      byCode,
      recent: this.recentErrors.slice(0, 10),
      topErrors
    };
  }

  getError(errorKey: string): ErrorRecord | undefined {
    return this.errors.get(errorKey);
  }

  clear(): void {
    this.errors.clear();
    this.errorCounts.clear();
    this.recentErrors = [];
  }

  // Get errors by time range
  getErrorsByTimeRange(startTime: Date, endTime: Date): ErrorRecord[] {
    return this.recentErrors.filter(record => 
      record.timestamp >= startTime && record.timestamp <= endTime
    );
  }

  // Get errors by type
  getErrorsByType(errorType: string): ErrorRecord[] {
    return Array.from(this.errors.values()).filter(record => 
      record.error.name === errorType
    );
  }

  // Export errors for analysis
  exportErrors(): string {
    const data = {
      stats: this.getStats(),
      errors: Array.from(this.errors.values())
    };
    return JSON.stringify(data, null, 2);
  }
}
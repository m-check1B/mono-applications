/**
 * @stack-2025/byok-core Audit Service
 * Security audit logging for BYOK operations
 */

import { PrismaClient } from '@prisma/client';
import { AuditLog } from '../types';

export class AuditService {
  constructor(private prisma: PrismaClient) {}

  /**
   * Log an audit event
   */
  async log(entry: Omit<AuditLog, 'id' | 'timestamp'>): Promise<void> {
    try {
      await this.prisma.auditLog.create({
        data: {
          ...entry,
          timestamp: new Date()
        }
      });
    } catch (error) {
      // Log to console if database logging fails
      console.error('[AUDIT] Failed to log:', entry, error);
    }
  }

  /**
   * Query audit logs
   */
  async query(
    filters: {
      userId?: string;
      action?: string;
      resource?: string;
      startDate?: Date;
      endDate?: Date;
      success?: boolean;
    },
    limit: number = 100
  ): Promise<AuditLog[]> {
    const where: any = {};

    if (filters.userId) where.userId = filters.userId;
    if (filters.action) where.action = filters.action;
    if (filters.resource) where.resource = filters.resource;
    if (filters.success !== undefined) where.success = filters.success;

    if (filters.startDate || filters.endDate) {
      where.timestamp = {};
      if (filters.startDate) where.timestamp.gte = filters.startDate;
      if (filters.endDate) where.timestamp.lte = filters.endDate;
    }

    return await this.prisma.auditLog.findMany({
      where,
      orderBy: { timestamp: 'desc' },
      take: limit
    });
  }

  /**
   * Generate audit report
   */
  async generateReport(
    userId: string,
    startDate: Date,
    endDate: Date
  ): Promise<{
    summary: {
      totalActions: number;
      successfulActions: number;
      failedActions: number;
      uniqueResources: number;
    };
    actionBreakdown: Record<string, number>;
    resourceBreakdown: Record<string, number>;
    failureReasons: string[];
  }> {
    const logs = await this.query(
      { userId, startDate, endDate },
      10000
    );

    const actionBreakdown: Record<string, number> = {};
    const resourceBreakdown: Record<string, number> = {};
    const failureReasons: string[] = [];

    logs.forEach(log => {
      // Count actions
      actionBreakdown[log.action] = (actionBreakdown[log.action] || 0) + 1;

      // Count resources
      resourceBreakdown[log.resource] = (resourceBreakdown[log.resource] || 0) + 1;

      // Collect failure reasons
      if (!log.success && log.errorMessage) {
        failureReasons.push(log.errorMessage);
      }
    });

    return {
      summary: {
        totalActions: logs.length,
        successfulActions: logs.filter(l => l.success).length,
        failedActions: logs.filter(l => !l.success).length,
        uniqueResources: Object.keys(resourceBreakdown).length
      },
      actionBreakdown,
      resourceBreakdown,
      failureReasons: [...new Set(failureReasons)]
    };
  }

  /**
   * Clean up old audit logs
   */
  async cleanup(retentionDays: number = 90): Promise<number> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

    const result = await this.prisma.auditLog.deleteMany({
      where: {
        timestamp: {
          lt: cutoffDate
        }
      }
    });

    return result.count;
  }
}
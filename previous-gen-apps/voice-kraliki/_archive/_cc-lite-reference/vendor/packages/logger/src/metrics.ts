/**
 * Stack 2025 Metrics Collection
 */

import { LogMetrics } from './types.js';

export class MetricsCollector {
  private totalLogs = 0;
  private errorCount = 0;
  private warnCount = 0;
  private infoCount = 0;
  private debugCount = 0;
  private startTime = Date.now();
  private memorySnapshots: number[] = [];
  private cpuSnapshots: number[] = [];

  incrementError(): void {
    this.totalLogs++;
    this.errorCount++;
  }

  incrementWarn(): void {
    this.totalLogs++;
    this.warnCount++;
  }

  incrementInfo(): void {
    this.totalLogs++;
    this.infoCount++;
  }

  incrementDebug(): void {
    this.totalLogs++;
    this.debugCount++;
  }

  captureMemory(): void {
    const usage = process.memoryUsage();
    this.memorySnapshots.push(usage.heapUsed);
    
    // Keep only last 100 snapshots
    if (this.memorySnapshots.length > 100) {
      this.memorySnapshots.shift();
    }
  }

  captureCPU(): void {
    const usage = process.cpuUsage();
    const totalUsage = (usage.user + usage.system) / 1000000; // Convert to seconds
    this.cpuSnapshots.push(totalUsage);
    
    // Keep only last 100 snapshots
    if (this.cpuSnapshots.length > 100) {
      this.cpuSnapshots.shift();
    }
  }

  getMetrics(): LogMetrics {
    this.captureMemory();
    this.captureCPU();
    
    const peakMemoryUsage = this.memorySnapshots.length > 0
      ? Math.max(...this.memorySnapshots)
      : undefined;
    
    const averageCPU = this.cpuSnapshots.length > 0
      ? this.cpuSnapshots.reduce((sum, cpu) => sum + cpu, 0) / this.cpuSnapshots.length
      : undefined;
    
    const uptime = Date.now() - this.startTime;
    const averageResponseTime = this.totalLogs > 0 ? uptime / this.totalLogs : undefined;
    
    return {
      totalLogs: this.totalLogs,
      errorCount: this.errorCount,
      warnCount: this.warnCount,
      infoCount: this.infoCount,
      debugCount: this.debugCount,
      averageResponseTime,
      peakMemoryUsage,
      cpuUsage: averageCPU
    };
  }

  reset(): void {
    this.totalLogs = 0;
    this.errorCount = 0;
    this.warnCount = 0;
    this.infoCount = 0;
    this.debugCount = 0;
    this.memorySnapshots = [];
    this.cpuSnapshots = [];
    this.startTime = Date.now();
  }

  // Get rate metrics
  getRates(): {
    logsPerSecond: number;
    errorsPerSecond: number;
    warnsPerSecond: number;
  } {
    const uptimeSeconds = (Date.now() - this.startTime) / 1000;
    
    return {
      logsPerSecond: this.totalLogs / uptimeSeconds,
      errorsPerSecond: this.errorCount / uptimeSeconds,
      warnsPerSecond: this.warnCount / uptimeSeconds
    };
  }

  // Get health status
  getHealthStatus(): {
    status: 'healthy' | 'warning' | 'critical';
    issues: string[];
  } {
    const issues: string[] = [];
    let status: 'healthy' | 'warning' | 'critical' = 'healthy';
    
    const errorRate = this.errorCount / Math.max(1, this.totalLogs);
    const peakMemory = Math.max(...this.memorySnapshots, 0);
    
    // Check error rate
    if (errorRate > 0.1) {
      issues.push(`High error rate: ${(errorRate * 100).toFixed(2)}%`);
      status = 'critical';
    } else if (errorRate > 0.05) {
      issues.push(`Elevated error rate: ${(errorRate * 100).toFixed(2)}%`);
      status = 'warning';
    }
    
    // Check memory usage (threshold: 1GB)
    if (peakMemory > 1024 * 1024 * 1024) {
      issues.push(`High memory usage: ${(peakMemory / 1024 / 1024 / 1024).toFixed(2)}GB`);
      status = status === 'critical' ? 'critical' : 'warning';
    }
    
    // Check logs per second (threshold: 1000)
    const rates = this.getRates();
    if (rates.logsPerSecond > 1000) {
      issues.push(`High log volume: ${rates.logsPerSecond.toFixed(2)} logs/sec`);
      status = status === 'critical' ? 'critical' : 'warning';
    }
    
    return { status, issues };
  }
}

// Export singleton metrics collector
export const metrics = new MetricsCollector();
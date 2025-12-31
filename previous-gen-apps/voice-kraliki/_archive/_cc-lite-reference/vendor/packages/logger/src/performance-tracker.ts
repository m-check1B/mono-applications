/**
 * Stack 2025 Performance Tracking
 */

import { PerformanceMetrics } from './types.js';

export interface PerformanceStats {
  operations: Map<string, OperationStats>;
  slowest: PerformanceMetrics[];
  fastest: PerformanceMetrics[];
  recent: PerformanceMetrics[];
  averageResponseTime: number;
  p50: number;
  p95: number;
  p99: number;
}

export interface OperationStats {
  name: string;
  count: number;
  totalDuration: number;
  averageDuration: number;
  minDuration: number;
  maxDuration: number;
  successCount: number;
  failureCount: number;
  successRate: number;
}

export class PerformanceTracker {
  private metrics: PerformanceMetrics[] = [];
  private operationStats: Map<string, OperationStats> = new Map();
  private timers: Map<string, number> = new Map();
  private maxMetrics = 1000;

  startTimer(operation: string): () => number {
    const startTime = Date.now();
    const timerId = `${operation}-${startTime}-${Math.random()}`;
    this.timers.set(timerId, startTime);
    
    return () => {
      const endTime = Date.now();
      const duration = endTime - startTime;
      this.timers.delete(timerId);
      
      this.track({
        operation,
        duration,
        startTime: new Date(startTime),
        endTime: new Date(endTime),
        success: true
      });
      
      return duration;
    };
  }

  track(metrics: PerformanceMetrics): void {
    // Add to metrics array
    this.metrics.push(metrics);
    if (this.metrics.length > this.maxMetrics) {
      this.metrics.shift();
    }
    
    // Update operation stats
    const stats = this.operationStats.get(metrics.operation) || {
      name: metrics.operation,
      count: 0,
      totalDuration: 0,
      averageDuration: 0,
      minDuration: Infinity,
      maxDuration: 0,
      successCount: 0,
      failureCount: 0,
      successRate: 0
    };
    
    stats.count++;
    stats.totalDuration += metrics.duration;
    stats.averageDuration = stats.totalDuration / stats.count;
    stats.minDuration = Math.min(stats.minDuration, metrics.duration);
    stats.maxDuration = Math.max(stats.maxDuration, metrics.duration);
    
    if (metrics.success) {
      stats.successCount++;
    } else {
      stats.failureCount++;
    }
    
    stats.successRate = (stats.successCount / stats.count) * 100;
    
    this.operationStats.set(metrics.operation, stats);
  }

  getStats(): PerformanceStats {
    const durations = this.metrics.map(m => m.duration).sort((a, b) => a - b);
    const recent = this.metrics.slice(-10);
    const slowest = [...this.metrics].sort((a, b) => b.duration - a.duration).slice(0, 10);
    const fastest = [...this.metrics].sort((a, b) => a.duration - b.duration).slice(0, 10);
    
    const averageResponseTime = durations.length > 0
      ? durations.reduce((sum, d) => sum + d, 0) / durations.length
      : 0;
    
    const p50 = this.percentile(durations, 50);
    const p95 = this.percentile(durations, 95);
    const p99 = this.percentile(durations, 99);
    
    return {
      operations: this.operationStats,
      slowest,
      fastest,
      recent,
      averageResponseTime,
      p50,
      p95,
      p99
    };
  }

  private percentile(sortedArray: number[], percentile: number): number {
    if (sortedArray.length === 0) return 0;
    const index = Math.ceil((percentile / 100) * sortedArray.length) - 1;
    return sortedArray[Math.max(0, index)];
  }

  getOperationStats(operation: string): OperationStats | undefined {
    return this.operationStats.get(operation);
  }

  clear(): void {
    this.metrics = [];
    this.operationStats.clear();
    this.timers.clear();
  }

  // Get metrics by time range
  getMetricsByTimeRange(startTime: Date, endTime: Date): PerformanceMetrics[] {
    return this.metrics.filter(metric => 
      metric.startTime >= startTime && metric.endTime <= endTime
    );
  }

  // Get slow operations above threshold
  getSlowOperations(thresholdMs: number): PerformanceMetrics[] {
    return this.metrics.filter(metric => metric.duration > thresholdMs);
  }

  // Export metrics for analysis
  exportMetrics(): string {
    const data = {
      stats: this.getStats(),
      metrics: this.metrics,
      operations: Array.from(this.operationStats.values())
    };
    return JSON.stringify(data, null, 2);
  }
}
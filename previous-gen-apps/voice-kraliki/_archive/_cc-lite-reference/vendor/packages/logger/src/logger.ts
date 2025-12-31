/**
 * Stack 2025 Core Logger Implementation
 */

import winston from 'winston';
import { LogLevel, LogContext, LoggerConfig, LogEntry } from './types.js';
import { createTransports } from './transports.js';
import { createFormats } from './formatters.js';
import { ErrorTracker } from './error-tracker.js';
import { PerformanceTracker } from './performance-tracker.js';
import { MetricsCollector } from './metrics.js';

export class Stack2025Logger {
  private winston: winston.Logger;
  private config: LoggerConfig;
  private context: LogContext;
  private errorTracker: ErrorTracker;
  private performanceTracker: PerformanceTracker;
  private metricsCollector: MetricsCollector;

  constructor(config: LoggerConfig) {
    this.config = this.validateConfig(config);
    this.context = this.buildContext(config);
    
    // Initialize trackers
    this.errorTracker = new ErrorTracker();
    this.performanceTracker = new PerformanceTracker();
    this.metricsCollector = new MetricsCollector();

    // Create Winston logger
    this.winston = winston.createLogger({
      level: config.level || LogLevel.INFO,
      format: createFormats(config),
      transports: createTransports(config),
      defaultMeta: this.context,
      exitOnError: config.exitOnError ?? false,
      handleExceptions: config.handleExceptions ?? true,
      handleRejections: config.handleRejections ?? true,
      silent: config.silent ?? false
    });
  }

  private validateConfig(config: LoggerConfig): LoggerConfig {
    if (!config.service) {
      throw new Error('Logger service name is required');
    }
    return {
      ...config,
      level: config.level || LogLevel.INFO,
      environment: config.environment || process.env.NODE_ENV || 'development',
      version: config.version || process.env.APP_VERSION || '1.0.0',
      consoleEnabled: config.consoleEnabled ?? true,
      fileEnabled: config.fileEnabled ?? true,
      format: config.format || 'json',
      colorize: config.colorize ?? true,
      dirname: config.dirname || './logs'
    };
  }

  private buildContext(config: LoggerConfig): LogContext {
    return {
      service: config.service,
      environment: config.environment,
      version: config.version,
      hostname: process.env.HOSTNAME || 'localhost',
      pid: process.pid,
      ...config.metadata
    };
  }

  // Core logging methods
  error(message: string, error?: Error | any, context?: LogContext): void {
    this.metricsCollector.incrementError();
    if (error) {
      this.errorTracker.track(error, context);
    }
    this.winston.error(message, { error, ...context });
  }

  warn(message: string, data?: any, context?: LogContext): void {
    this.metricsCollector.incrementWarn();
    this.winston.warn(message, { data, ...context });
  }

  info(message: string, data?: any, context?: LogContext): void {
    this.metricsCollector.incrementInfo();
    this.winston.info(message, { data, ...context });
  }

  http(message: string, data?: any, context?: LogContext): void {
    this.winston.http(message, { data, ...context });
  }

  verbose(message: string, data?: any, context?: LogContext): void {
    this.winston.verbose(message, { data, ...context });
  }

  debug(message: string, data?: any, context?: LogContext): void {
    this.metricsCollector.incrementDebug();
    this.winston.debug(message, { data, ...context });
  }

  silly(message: string, data?: any, context?: LogContext): void {
    this.winston.silly(message, { data, ...context });
  }

  // Performance tracking
  startTimer(operation: string): () => void {
    return this.performanceTracker.startTimer(operation);
  }

  async trackAsync<T>(
    operation: string,
    fn: () => Promise<T>,
    context?: LogContext
  ): Promise<T> {
    const endTimer = this.startTimer(operation);
    try {
      const result = await fn();
      const duration = endTimer();
      this.info(`${operation} completed`, { duration }, context);
      return result;
    } catch (error) {
      const duration = endTimer();
      this.error(`${operation} failed`, error as Error, { ...context, duration });
      throw error;
    }
  }

  // Child logger with additional context
  child(context: LogContext): Stack2025Logger {
    const childConfig = {
      ...this.config,
      metadata: { ...this.context, ...context }
    };
    return new Stack2025Logger(childConfig);
  }

  // Get metrics
  getMetrics() {
    return {
      logs: this.metricsCollector.getMetrics(),
      errors: this.errorTracker.getStats(),
      performance: this.performanceTracker.getStats()
    };
  }

  // Flush logs
  async flush(): Promise<void> {
    return new Promise((resolve) => {
      this.winston.end(() => resolve());
    });
  }

  // Update log level dynamically
  setLevel(level: LogLevel): void {
    this.winston.level = level;
  }

  // Add custom transport
  addTransport(transport: winston.transport): void {
    this.winston.add(transport);
  }

  // Remove transport
  removeTransport(transport: winston.transport): void {
    this.winston.remove(transport);
  }

  // Clear all transports
  clearTransports(): void {
    this.winston.clear();
  }
}

// Default logger instance
let defaultLogger: Stack2025Logger | null = null;

export function createLogger(config: LoggerConfig): Stack2025Logger {
  const logger = new Stack2025Logger(config);
  if (!defaultLogger) {
    defaultLogger = logger;
  }
  return logger;
}

export const logger = {
  error: (message: string, error?: Error, context?: LogContext) => {
    if (!defaultLogger) {
      console.error('Logger not initialized. Call createLogger first.');
      console.error(message, error);
      return;
    }
    defaultLogger.error(message, error, context);
  },
  warn: (message: string, data?: any, context?: LogContext) => {
    if (!defaultLogger) {
      console.warn('Logger not initialized. Call createLogger first.');
      console.warn(message, data);
      return;
    }
    defaultLogger.warn(message, data, context);
  },
  info: (message: string, data?: any, context?: LogContext) => {
    if (!defaultLogger) {
      console.info('Logger not initialized. Call createLogger first.');
      console.info(message, data);
      return;
    }
    defaultLogger.info(message, data, context);
  },
  debug: (message: string, data?: any, context?: LogContext) => {
    if (!defaultLogger) {
      console.debug('Logger not initialized. Call createLogger first.');
      console.debug(message, data);
      return;
    }
    defaultLogger.debug(message, data, context);
  },
  http: (message: string, data?: any, context?: LogContext) => {
    if (!defaultLogger) return;
    defaultLogger.http(message, data, context);
  },
  verbose: (message: string, data?: any, context?: LogContext) => {
    if (!defaultLogger) return;
    defaultLogger.verbose(message, data, context);
  },
  silly: (message: string, data?: any, context?: LogContext) => {
    if (!defaultLogger) return;
    defaultLogger.silly(message, data, context);
  },
  startTimer: (operation: string) => {
    if (!defaultLogger) {
      return () => 0;
    }
    return defaultLogger.startTimer(operation);
  },
  trackAsync: async <T>(
    operation: string,
    fn: () => Promise<T>,
    context?: LogContext
  ): Promise<T> => {
    if (!defaultLogger) {
      return fn();
    }
    return defaultLogger.trackAsync(operation, fn, context);
  },
  child: (context: LogContext) => {
    if (!defaultLogger) {
      throw new Error('Logger not initialized. Call createLogger first.');
    }
    return defaultLogger.child(context);
  },
  getMetrics: () => {
    if (!defaultLogger) {
      return null;
    }
    return defaultLogger.getMetrics();
  }
};
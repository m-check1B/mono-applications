/**
 * Stack 2025 Logger Types
 */

export enum LogLevel {
  ERROR = 'error',
  WARN = 'warn',
  INFO = 'info',
  HTTP = 'http',
  VERBOSE = 'verbose',
  DEBUG = 'debug',
  SILLY = 'silly'
}

export interface LogContext {
  service?: string;
  userId?: string;
  sessionId?: string;
  requestId?: string;
  traceId?: string;
  spanId?: string;
  environment?: string;
  version?: string;
  hostname?: string;
  pid?: number;
  [key: string]: any;
}

export interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: Date;
  context?: LogContext;
  error?: Error;
  data?: any;
  duration?: number;
  tags?: string[];
}

export interface LoggerConfig {
  service: string;
  level?: LogLevel;
  environment?: string;
  version?: string;
  consoleEnabled?: boolean;
  fileEnabled?: boolean;
  remoteEnabled?: boolean;
  rotateFiles?: boolean;
  maxFiles?: string;
  maxSize?: string;
  datePattern?: string;
  dirname?: string;
  filename?: string;
  errorFile?: string;
  combinedFile?: string;
  format?: 'json' | 'pretty' | 'simple';
  colorize?: boolean;
  handleExceptions?: boolean;
  handleRejections?: boolean;
  exitOnError?: boolean;
  silent?: boolean;
  metadata?: LogContext;
  remoteUrl?: string;
  remoteApiKey?: string;
  sampling?: {
    enabled: boolean;
    rate: number;
  };
  redaction?: {
    enabled: boolean;
    paths: string[];
    keywords: string[];
  };
}

export interface LogMetrics {
  totalLogs: number;
  errorCount: number;
  warnCount: number;
  infoCount: number;
  debugCount: number;
  averageResponseTime?: number;
  peakMemoryUsage?: number;
  cpuUsage?: number;
}

export interface ErrorDetails {
  name: string;
  message: string;
  stack?: string;
  code?: string;
  statusCode?: number;
  cause?: any;
  metadata?: Record<string, any>;
}

export interface PerformanceMetrics {
  operation: string;
  duration: number;
  startTime: Date;
  endTime: Date;
  success: boolean;
  metadata?: Record<string, any>;
}
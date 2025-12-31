/**
 * Stack 2025 Logger Transports
 */

import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import { LoggerConfig } from './types.js';
import path from 'path';
import fs from 'fs';

// Ensure log directory exists
function ensureLogDirectory(dirname: string): void {
  if (!fs.existsSync(dirname)) {
    fs.mkdirSync(dirname, { recursive: true });
  }
}

// Console transport factory
function createConsoleTransport(config: LoggerConfig): winston.transport {
  return new winston.transports.Console({
    level: config.level,
    format: winston.format.combine(
      winston.format.colorize({ all: config.colorize }),
      winston.format.simple()
    )
  });
}

// File transport factory
function createFileTransport(config: LoggerConfig): winston.transport[] {
  const transports: winston.transport[] = [];
  const dirname = config.dirname || './logs';
  
  ensureLogDirectory(dirname);
  
  // Error file transport
  if (config.errorFile !== undefined) {
    transports.push(new winston.transports.File({
      filename: path.join(dirname, config.errorFile || 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }));
  }
  
  // Combined file transport
  if (config.combinedFile !== undefined) {
    transports.push(new winston.transports.File({
      filename: path.join(dirname, config.combinedFile || 'combined.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }));
  }
  
  return transports;
}

// Rotating file transport factory
function createRotatingFileTransport(config: LoggerConfig): winston.transport[] {
  const transports: winston.transport[] = [];
  const dirname = config.dirname || './logs';
  
  ensureLogDirectory(dirname);
  
  // Rotating error file
  transports.push(new DailyRotateFile({
    filename: path.join(dirname, '%DATE%-error.log'),
    datePattern: config.datePattern || 'YYYY-MM-DD',
    level: 'error',
    maxSize: config.maxSize || '20m',
    maxFiles: config.maxFiles || '14d',
    zippedArchive: true
  }));
  
  // Rotating combined file
  transports.push(new DailyRotateFile({
    filename: path.join(dirname, '%DATE%-combined.log'),
    datePattern: config.datePattern || 'YYYY-MM-DD',
    maxSize: config.maxSize || '20m',
    maxFiles: config.maxFiles || '14d',
    zippedArchive: true
  }));
  
  // Rotating application file
  transports.push(new DailyRotateFile({
    filename: path.join(dirname, `%DATE%-${config.service}.log`),
    datePattern: config.datePattern || 'YYYY-MM-DD',
    maxSize: config.maxSize || '20m',
    maxFiles: config.maxFiles || '14d',
    zippedArchive: true,
    format: winston.format.json()
  }));
  
  return transports;
}

// HTTP transport for remote logging
function createHttpTransport(config: LoggerConfig): winston.transport | null {
  if (!config.remoteUrl) return null;
  
  return new winston.transports.Http({
    host: new URL(config.remoteUrl).hostname,
    port: parseInt(new URL(config.remoteUrl).port) || 443,
    path: new URL(config.remoteUrl).pathname,
    ssl: new URL(config.remoteUrl).protocol === 'https:',
    headers: config.remoteApiKey ? {
      'Authorization': `Bearer ${config.remoteApiKey}`
    } : undefined
  });
}

// Stream transport for custom outputs
export class StreamTransport extends winston.transports.Stream {
  constructor(stream: NodeJS.WritableStream) {
    super({ stream });
  }
}

// Memory transport for testing
export class MemoryTransport extends winston.transports.Stream {
  logs: any[] = [];
  
  log(info: any, callback: () => void): void {
    this.logs.push(info);
    callback();
  }
  
  clear(): void {
    this.logs = [];
  }
  
  getLogs(): any[] {
    return this.logs;
  }
}

// Create all transports based on config
export function createTransports(config: LoggerConfig): winston.transport[] {
  const transports: winston.transport[] = [];
  
  // Console transport
  if (config.consoleEnabled !== false) {
    transports.push(createConsoleTransport(config));
  }
  
  // File transports
  if (config.fileEnabled !== false) {
    if (config.rotateFiles) {
      transports.push(...createRotatingFileTransport(config));
    } else {
      transports.push(...createFileTransport(config));
    }
  }
  
  // Remote transport
  if (config.remoteEnabled && config.remoteUrl) {
    const httpTransport = createHttpTransport(config);
    if (httpTransport) {
      transports.push(httpTransport);
    }
  }
  
  return transports;
}

// Export transport constructors for custom use
export const transports = {
  Console: winston.transports.Console,
  File: winston.transports.File,
  Http: winston.transports.Http,
  Stream: StreamTransport,
  Memory: MemoryTransport,
  DailyRotateFile,
  create: createTransports
};
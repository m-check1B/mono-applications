/**
 * Stack 2025 Logger Formatters
 */

import winston from 'winston';
import chalk from 'chalk';
import { LoggerConfig } from './types.js';

const { combine, timestamp, errors, printf, json, colorize, metadata, align } = winston.format;

// Color scheme for different log levels
const levelColors = {
  error: chalk.red,
  warn: chalk.yellow,
  info: chalk.cyan,
  http: chalk.magenta,
  verbose: chalk.blue,
  debug: chalk.gray,
  silly: chalk.white
};

// Pretty print format for development
const prettyFormat = printf(({ level, message, timestamp, service, ...meta }) => {
  const coloredLevel = levelColors[level as keyof typeof levelColors]?.(level.toUpperCase()) || level;
  const serviceName = service ? chalk.green(`[${service}]`) : '';
  
  let output = `${chalk.gray(timestamp)} ${coloredLevel} ${serviceName} ${message}`;
  
  // Add metadata if present
  if (meta && Object.keys(meta).length > 0) {
    const metaStr = JSON.stringify(meta, null, 2);
    output += `\n${chalk.gray(metaStr)}`;
  }
  
  return output;
});

// Simple format for production logs
const simpleFormat = printf(({ level, message, timestamp, service, ...meta }) => {
  let output = `${timestamp} [${level.toUpperCase()}] [${service}] ${message}`;
  
  if (meta && Object.keys(meta).length > 0) {
    output += ` | ${JSON.stringify(meta)}`;
  }
  
  return output;
});

// JSON format with metadata extraction
const jsonFormat = combine(
  metadata({ fillWith: ['service', 'environment', 'version'] }),
  json()
);

// Redaction formatter to remove sensitive data
const redactFormat = winston.format((info) => {
  const sensitiveFields = ['password', 'token', 'apiKey', 'secret', 'authorization', 'cookie'];
  
  const redact = (obj: any): any => {
    if (!obj || typeof obj !== 'object') return obj;
    
    const result = Array.isArray(obj) ? [...obj] : { ...obj };
    
    for (const key in result) {
      if (sensitiveFields.some(field => key.toLowerCase().includes(field))) {
        result[key] = '[REDACTED]';
      } else if (typeof result[key] === 'object') {
        result[key] = redact(result[key]);
      }
    }
    
    return result;
  };
  
  return redact(info);
})();

// Error formatter with stack trace
const errorFormat = errors({ stack: true });

// Create combined format based on config
export function createFormats(config: LoggerConfig): any {
  const formats: any[] = [
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    errorFormat
  ];
  
  // Add redaction if enabled
  if (config.redaction?.enabled) {
    formats.push(redactFormat);
  }
  
  // Choose output format
  switch (config.format) {
    case 'pretty':
      if (config.colorize) {
        formats.push(colorize({ all: true }));
      }
      formats.push(prettyFormat);
      break;
    case 'simple':
      formats.push(simpleFormat);
      break;
    case 'json':
    default:
      formats.push(jsonFormat);
      break;
  }
  
  return combine(...formats);
}

// Export individual formatters for custom use
export const formatters = {
  pretty: prettyFormat,
  simple: simpleFormat,
  json: jsonFormat,
  redact: redactFormat,
  error: errorFormat,
  timestamp: timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
  colorize: colorize({ all: true }),
  combine: (...formats: any[]) => combine(...formats)
};
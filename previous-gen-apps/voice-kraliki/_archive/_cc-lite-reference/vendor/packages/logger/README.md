# @stack-2025/logger

Production-ready logging system for the Stack 2025 ecosystem. A comprehensive logging solution with error tracking, performance monitoring, and built-in middleware for all major frameworks.

## Features

- 🚀 **Production Ready**: Battle-tested logging with Winston
- 📊 **Performance Tracking**: Built-in performance metrics and monitoring
- 🐛 **Error Tracking**: Comprehensive error tracking and analysis
- 🔄 **Log Rotation**: Automatic log rotation with compression
- 🎨 **Multiple Formats**: JSON, pretty print, and simple formats
- 🔒 **Security**: Automatic redaction of sensitive data
- 📡 **Remote Logging**: Support for remote log aggregation
- 🔌 **Framework Integration**: Middleware for Express, Fastify, tRPC, WebSocket, GraphQL
- 📈 **Metrics Collection**: Real-time metrics and health monitoring
- 🎯 **Contextual Logging**: Child loggers with inherited context

## Installation

```bash
pnpm add @stack-2025/logger
```

## Quick Start

```typescript
import { createLogger, logger } from '@stack-2025/logger';

// Initialize logger
const appLogger = createLogger({
  service: 'my-app',
  level: 'info',
  environment: 'production',
  format: 'json',
  rotateFiles: true
});

// Use logger
logger.info('Application started');
logger.error('Something went wrong', new Error('Database connection failed'));
logger.debug('Debug information', { userId: 123, action: 'login' });
```

## Configuration

```typescript
import { createLogger, LogLevel } from '@stack-2025/logger';

const logger = createLogger({
  // Required
  service: 'my-service',
  
  // Optional
  level: LogLevel.INFO,
  environment: 'production',
  version: '1.0.0',
  
  // Console output
  consoleEnabled: true,
  colorize: true,
  
  // File output
  fileEnabled: true,
  rotateFiles: true,
  dirname: './logs',
  maxFiles: '14d',
  maxSize: '20m',
  
  // Output format
  format: 'json', // 'json' | 'pretty' | 'simple'
  
  // Remote logging
  remoteEnabled: false,
  remoteUrl: 'https://logs.example.com',
  remoteApiKey: 'your-api-key',
  
  // Security
  redaction: {
    enabled: true,
    paths: ['password', 'token', 'apiKey'],
    keywords: ['secret', 'credential']
  },
  
  // Error handling
  handleExceptions: true,
  handleRejections: true,
  exitOnError: false
});
```

## Framework Integration

### Express

```typescript
import express from 'express';
import { createLogger, middleware } from '@stack-2025/logger';

const app = express();
const logger = createLogger({ service: 'express-app' });

// Add logging middleware
app.use(middleware.express(logger));

app.get('/', (req, res) => {
  // Logger available on request
  req.logger.info('Home page accessed');
  res.send('Hello World');
});
```

### Fastify

```typescript
import fastify from 'fastify';
import { createLogger, middleware } from '@stack-2025/logger';

const app = fastify();
const logger = createLogger({ service: 'fastify-app' });

// Register logging plugin
app.register(middleware.fastify(logger));

app.get('/', async (request, reply) => {
  request.logger.info('Home page accessed');
  return { hello: 'world' };
});
```

### tRPC

```typescript
import { initTRPC } from '@trpc/server';
import { createLogger, middleware } from '@stack-2025/logger';

const logger = createLogger({ service: 'trpc-api' });
const t = initTRPC.create();

// Add logging middleware
const loggedProcedure = t.procedure.use(middleware.trpc(logger));

export const appRouter = t.router({
  hello: loggedProcedure.query(({ ctx }) => {
    ctx.logger.info('Hello query executed');
    return 'world';
  })
});
```

### WebSocket (Socket.io)

```typescript
import { Server } from 'socket.io';
import { createLogger, middleware } from '@stack-2025/logger';

const io = new Server();
const logger = createLogger({ service: 'websocket-server' });

// Add logging middleware
io.use(middleware.websocket(logger));

io.on('connection', (socket) => {
  socket.logger.info('Client connected');
  
  socket.on('message', (data) => {
    socket.logger.debug('Message received', data);
  });
});
```

## Performance Tracking

```typescript
import { logger } from '@stack-2025/logger';

// Manual timing
const endTimer = logger.startTimer('database-query');
// ... perform operation ...
const duration = endTimer(); // Logs automatically

// Async tracking
const result = await logger.trackAsync('api-call', async () => {
  return await fetch('https://api.example.com/data');
});

// Get performance metrics
const metrics = logger.getMetrics();
console.log(metrics.performance);
```

## Error Tracking

```typescript
import { logger } from '@stack-2025/logger';

try {
  // ... some operation ...
} catch (error) {
  logger.error('Operation failed', error, {
    userId: 123,
    operation: 'data-sync'
  });
}

// Get error statistics
const metrics = logger.getMetrics();
console.log(metrics.errors);
```

## Child Loggers

```typescript
import { logger } from '@stack-2025/logger';

// Create child logger with additional context
const userLogger = logger.child({
  userId: 123,
  sessionId: 'abc-123'
});

userLogger.info('User action'); // Includes userId and sessionId
```

## Metrics and Monitoring

```typescript
import { logger } from '@stack-2025/logger';

// Get comprehensive metrics
const metrics = logger.getMetrics();

console.log({
  logs: metrics.logs,           // Log counts by level
  errors: metrics.errors,        // Error statistics
  performance: metrics.performance // Performance metrics
});

// Example output:
{
  logs: {
    totalLogs: 1523,
    errorCount: 12,
    warnCount: 45,
    infoCount: 892,
    debugCount: 574,
    averageResponseTime: 125,
    peakMemoryUsage: 134217728,
    cpuUsage: 0.15
  },
  errors: {
    total: 12,
    byType: { TypeError: 5, ReferenceError: 7 },
    topErrors: [{ error: 'Database timeout', count: 8 }]
  },
  performance: {
    averageResponseTime: 125,
    p50: 100,
    p95: 450,
    p99: 800
  }
}
```

## Log Formats

### JSON Format (Default)
```json
{
  "level": "info",
  "message": "User logged in",
  "timestamp": "2025-08-23 10:30:45.123",
  "service": "auth-service",
  "userId": 123,
  "sessionId": "abc-123"
}
```

### Pretty Format (Development)
```
2025-08-23 10:30:45.123 INFO [auth-service] User logged in
{
  "userId": 123,
  "sessionId": "abc-123"
}
```

### Simple Format
```
2025-08-23 10:30:45.123 [INFO] [auth-service] User logged in | {"userId":123,"sessionId":"abc-123"}
```

## Best Practices

1. **Always initialize logger at startup**
```typescript
// app.ts
import { createLogger } from '@stack-2025/logger';

const logger = createLogger({
  service: process.env.SERVICE_NAME || 'my-app'
});

// Export for use in other modules
export { logger };
```

2. **Use appropriate log levels**
```typescript
logger.error('Critical error', error);  // System errors
logger.warn('Deprecation warning');     // Warnings
logger.info('User registered');         // Important events
logger.http('GET /api/users');         // HTTP logs
logger.debug('Cache miss', { key });   // Debug info
```

3. **Add context to logs**
```typescript
logger.info('Order processed', {
  orderId: 12345,
  userId: 678,
  amount: 99.99,
  currency: 'USD'
});
```

4. **Use child loggers for request context**
```typescript
app.use((req, res, next) => {
  req.logger = logger.child({
    requestId: req.id,
    userId: req.user?.id
  });
  next();
});
```

5. **Track performance of critical operations**
```typescript
await logger.trackAsync('database-transaction', async () => {
  await db.beginTransaction();
  await db.insert(data);
  await db.commit();
});
```

## Environment Variables

```bash
# Log level
LOG_LEVEL=info

# Environment
NODE_ENV=production

# Application version
APP_VERSION=1.0.0

# Remote logging
REMOTE_LOG_URL=https://logs.example.com
REMOTE_LOG_API_KEY=your-api-key
```

## Testing

```typescript
import { createLogger, transports } from '@stack-2025/logger';

// Use memory transport for testing
const memoryTransport = new transports.Memory();
const testLogger = createLogger({
  service: 'test',
  consoleEnabled: false,
  fileEnabled: false
});

testLogger.addTransport(memoryTransport);

// Run tests
testLogger.info('Test message');

// Assert logs
const logs = memoryTransport.getLogs();
expect(logs[0].message).toBe('Test message');
```

## Migration from console.log

```typescript
// Before
console.log('User logged in', userId);
console.error('Error:', error);

// After
import { logger } from '@stack-2025/logger';

logger.info('User logged in', { userId });
logger.error('Error occurred', error);
```

## License

MIT

## Support

For issues and questions, please open an issue in the Stack 2025 repository.
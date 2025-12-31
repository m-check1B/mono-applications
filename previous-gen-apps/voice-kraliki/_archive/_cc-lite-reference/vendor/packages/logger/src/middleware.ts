/**
 * Stack 2025 Logger Middleware for Express/Fastify
 */

import { Stack2025Logger } from './logger.js';
import { LogContext } from './types.js';

// Express middleware
export function expressMiddleware(logger: Stack2025Logger) {
  return (req: any, res: any, next: any) => {
    const startTime = Date.now();
    const requestId = req.headers['x-request-id'] || generateRequestId();
    
    // Add request ID to request object
    req.requestId = requestId;
    
    // Create child logger with request context
    const requestLogger = logger.child({
      requestId,
      method: req.method,
      url: req.url,
      ip: req.ip || req.connection.remoteAddress,
      userAgent: req.headers['user-agent']
    });
    
    // Attach logger to request
    req.logger = requestLogger;
    
    // Log request
    requestLogger.http('Incoming request', {
      headers: req.headers,
      query: req.query,
      params: req.params
    });
    
    // Capture response
    const originalSend = res.send;
    res.send = function(data: any) {
      res.send = originalSend;
      const duration = Date.now() - startTime;
      
      // Log response
      requestLogger.http('Request completed', {
        statusCode: res.statusCode,
        duration,
        responseSize: data ? data.length : 0
      });
      
      return res.send(data);
    };
    
    next();
  };
}

// Fastify plugin
export function fastifyPlugin(logger: Stack2025Logger) {
  return async function(fastify: any, options: any) {
    // Request hook
    fastify.addHook('onRequest', async (request: any, reply: any) => {
      const requestId = request.headers['x-request-id'] || generateRequestId();
      request.requestId = requestId;
      
      // Create child logger
      const requestLogger = logger.child({
        requestId,
        method: request.method,
        url: request.url,
        ip: request.ip,
        userAgent: request.headers['user-agent']
      });
      
      request.logger = requestLogger;
      
      // Log request
      requestLogger.http('Incoming request', {
        headers: request.headers,
        query: request.query,
        params: request.params
      });
    });
    
    // Response hook
    fastify.addHook('onResponse', async (request: any, reply: any) => {
      const duration = reply.getResponseTime();
      
      request.logger.http('Request completed', {
        statusCode: reply.statusCode,
        duration
      });
    });
    
    // Error hook
    fastify.addHook('onError', async (request: any, reply: any, error: Error) => {
      request.logger.error('Request error', error, {
        statusCode: reply.statusCode
      });
    });
  };
}

// tRPC middleware
export function trpcMiddleware(logger: Stack2025Logger) {
  return ({ ctx, next, path, type }: any) => {
    const startTime = Date.now();
    const requestId = generateRequestId();
    
    // Create child logger
    const requestLogger = logger.child({
      requestId,
      path,
      type,
      userId: ctx?.user?.id
    });
    
    // Log RPC call
    requestLogger.debug('tRPC call started', { path, type });
    
    return next({
      ctx: {
        ...ctx,
        logger: requestLogger,
        requestId
      }
    }).then((result: any) => {
      const duration = Date.now() - startTime;
      requestLogger.debug('tRPC call completed', { path, duration });
      return result;
    }).catch((error: any) => {
      const duration = Date.now() - startTime;
      requestLogger.error('tRPC call failed', error, { path, duration });
      throw error;
    });
  };
}

// WebSocket middleware
export function websocketMiddleware(logger: Stack2025Logger) {
  return (socket: any, next: any) => {
    const sessionId = socket.id || generateRequestId();
    
    // Create child logger
    const socketLogger = logger.child({
      sessionId,
      transport: socket.conn.transport.name,
      address: socket.handshake.address
    });
    
    // Attach logger to socket
    socket.logger = socketLogger;
    
    // Log connection
    socketLogger.info('WebSocket connected', {
      query: socket.handshake.query,
      headers: socket.handshake.headers
    });
    
    // Log disconnection
    socket.on('disconnect', (reason: string) => {
      socketLogger.info('WebSocket disconnected', { reason });
    });
    
    // Log errors
    socket.on('error', (error: Error) => {
      socketLogger.error('WebSocket error', error);
    });
    
    next();
  };
}

// GraphQL middleware
export function graphqlMiddleware(logger: Stack2025Logger) {
  return {
    requestDidStart() {
      return {
        willSendResponse(requestContext: any) {
          const { request, response } = requestContext;
          const requestId = request.http.headers.get('x-request-id') || generateRequestId();
          
          // Create child logger
          const requestLogger = logger.child({
            requestId,
            operationName: request.operationName,
            query: request.query,
            variables: request.variables
          });
          
          // Log based on response
          if (response.errors) {
            requestLogger.error('GraphQL errors', response.errors);
          } else {
            requestLogger.debug('GraphQL query completed', {
              operationName: request.operationName
            });
          }
        }
      };
    }
  };
}

// Helper function to generate request ID
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Export middleware collection
export const middleware = {
  express: expressMiddleware,
  fastify: fastifyPlugin,
  trpc: trpcMiddleware,
  websocket: websocketMiddleware,
  graphql: graphqlMiddleware
};
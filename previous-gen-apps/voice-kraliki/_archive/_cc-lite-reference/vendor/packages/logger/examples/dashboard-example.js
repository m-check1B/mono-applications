/**
 * Example: How to use the Stack 2025 Logger Dashboard
 */

import { createLogger, createDashboard } from '@stack-2025/logger';

// Create a logger instance
const logger = createLogger({
  service: 'my-app',
  level: 'debug',
  format: 'pretty'
});

// Create and start the dashboard
const dashboard = createDashboard({
  port: 9090,
  host: '127.0.0.1',
  logger: logger
});

async function start() {
  await dashboard.start();
  console.log('Dashboard running at http://127.0.0.1:9090');
  
  // Generate some example logs
  setInterval(() => {
    logger.info('Regular info message', { timestamp: Date.now() });
  }, 5000);
  
  setInterval(() => {
    logger.debug('Debug data', { 
      cpu: process.cpuUsage(),
      memory: process.memoryUsage()
    });
  }, 10000);
  
  // Simulate occasional errors
  setInterval(() => {
    if (Math.random() > 0.8) {
      logger.error('Random error occurred', new Error('Something went wrong'));
    }
  }, 15000);
  
  // Simulate warnings
  setInterval(() => {
    if (Math.random() > 0.7) {
      logger.warn('Performance warning', { 
        responseTime: Math.floor(Math.random() * 1000)
      });
    }
  }, 8000);
}

start().catch(console.error);

// Graceful shutdown
process.on('SIGINT', async () => {
  logger.info('Shutting down dashboard...');
  await dashboard.stop();
  process.exit(0);
});
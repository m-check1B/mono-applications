#!/usr/bin/env node
/**
 * Test Stack 2025 Logger Dashboard
 */

import { createLogger, createDashboard } from '../dist/index.js';

console.log('🚀 Starting Stack 2025 Logger Dashboard Test...\n');

// Create a logger instance
const logger = createLogger({
  service: 'test-dashboard',
  level: 'debug',
  format: 'pretty',
  colorize: true,
  rotateFiles: true
});

// Create and start the dashboard
const dashboard = createDashboard({
  port: 9090,
  host: '127.0.0.1',
  logger: logger
});

async function start() {
  try {
    await dashboard.start();
    console.log('✅ Dashboard started successfully!');
    console.log('📊 View at: http://127.0.0.1:9090\n');
    
    // Generate various types of logs
    console.log('Generating test logs...\n');
    
    // Regular info logs
    setInterval(() => {
      logger.info('Regular heartbeat', { 
        timestamp: Date.now(),
        status: 'healthy',
        uptime: process.uptime()
      });
    }, 3000);
    
    // Debug logs
    setInterval(() => {
      logger.debug('System metrics', { 
        cpu: process.cpuUsage(),
        memory: process.memoryUsage(),
        platform: process.platform
      });
    }, 5000);
    
    // Simulate warnings
    setInterval(() => {
      if (Math.random() > 0.7) {
        logger.warn('High memory usage detected', { 
          usage: Math.floor(Math.random() * 100),
          threshold: 80
        });
      }
    }, 8000);
    
    // Simulate errors
    setInterval(() => {
      if (Math.random() > 0.8) {
        const errors = [
          'Database connection timeout',
          'API rate limit exceeded',
          'File not found',
          'Permission denied'
        ];
        const error = errors[Math.floor(Math.random() * errors.length)];
        logger.error(error, new Error(error), {
          code: 'ERR_' + Math.floor(Math.random() * 1000)
        });
      }
    }, 10000);
    
    // Performance tracking
    setInterval(async () => {
      await logger.trackAsync('api-call', async () => {
        const delay = Math.floor(Math.random() * 200) + 50;
        await new Promise(resolve => setTimeout(resolve, delay));
        return { success: true, responseTime: delay };
      });
    }, 4000);
    
    console.log('Dashboard is running. Press Ctrl+C to stop.\n');
    
  } catch (error) {
    console.error('Failed to start dashboard:', error);
    process.exit(1);
  }
}

// Handle shutdown
process.on('SIGINT', async () => {
  console.log('\n📛 Shutting down dashboard...');
  await dashboard.stop();
  logger.info('Dashboard stopped');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await dashboard.stop();
  process.exit(0);
});

// Start the dashboard
start().catch(console.error);
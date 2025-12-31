/**
 * PM2 Ecosystem Configuration for Voice by Kraliki
 * Production-ready process management
 *
 * Start: pm2 start ecosystem.config.cjs --env production
 * Monitor: pm2 monit
 * Logs: pm2 logs
 * Restart: pm2 restart all
 */

module.exports = {
  apps: [
    {
      // Main Application Server (Frontend + Backend)
      name: 'cc-lite-server',
      script: 'pnpm',
      args: 'start:backend:production',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 2, // Use cluster mode for availability
      exec_mode: 'cluster',

      // Environment variables
      env: {
        NODE_ENV: 'development',
        PORT: 3010,
        FRONTEND_PORT: 3007,
        HOST: '127.0.0.1'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3010,
        FRONTEND_PORT: 3007,
        HOST: '0.0.0.0'
      },

      // Resource management
      max_memory_restart: '1G',
      max_restarts: 10,
      min_uptime: '10s',

      // Restart strategies
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', 'logs', '.git'],

      // Logging
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_file: './logs/pm2-combined.log',
      merge_logs: true,

      // Advanced features
      listen_timeout: 10000,
      kill_timeout: 5000,
      wait_ready: true,
      shutdown_with_message: true,

      // Health monitoring
      instance_var: 'INSTANCE_ID',

      // Post-deploy hooks
      post_update: ['pnpm install', 'pnpm prisma generate', 'pnpm build']
    },

    {
      // Campaign Worker (Background Jobs)
      name: 'cc-lite-campaign-worker',
      script: 'pnpm',
      args: 'start:worker',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 1,
      exec_mode: 'fork',

      env: {
        NODE_ENV: 'development',
        WORKER_TYPE: 'campaign'
      },
      env_production: {
        NODE_ENV: 'production',
        WORKER_TYPE: 'campaign'
      },

      max_memory_restart: '512M',
      autorestart: true,
      watch: false,

      error_file: './logs/worker-error.log',
      out_file: './logs/worker-out.log',
      merge_logs: true
    }
  ],

  // Deployment configuration
  deploy: {
    production: {
      user: 'adminmatej',
      host: ['localhost'],
      ref: 'origin/main',
      repo: 'https://github.com/yourusername/cc-lite.git',
      path: '/home/adminmatej/github/apps/cc-lite',

      // Pre-deploy: prepare environment
      'pre-deploy-local': 'echo "Starting deployment..."',

      // Post-deploy: install deps, migrate DB, restart
      'post-deploy': 'pnpm install && pnpm prisma migrate deploy && pnpm build && pm2 reload ecosystem.config.cjs --env production && pm2 save',

      // Post-setup: initial setup
      'pre-setup': 'mkdir -p logs uploads',

      // Environment variables
      env: {
        NODE_ENV: 'production'
      }
    },

    staging: {
      user: 'adminmatej',
      host: ['localhost'],
      ref: 'origin/develop',
      repo: 'https://github.com/yourusername/cc-lite.git',
      path: '/home/adminmatej/github/apps/cc-lite-staging',

      'post-deploy': 'pnpm install && pnpm prisma migrate deploy && pnpm build && pm2 reload ecosystem.config.cjs --env staging && pm2 save',

      env: {
        NODE_ENV: 'staging'
      }
    }
  }
};
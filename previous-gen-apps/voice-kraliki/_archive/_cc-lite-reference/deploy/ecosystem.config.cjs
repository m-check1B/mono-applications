// PM2 Production Configuration for CC-Light
// ========================================
// Usage:
//   Development: pm2 start ecosystem.config.cjs --env development
//   Production:  pm2 start ecosystem.config.cjs --env production
//   Staging:     pm2 start ecosystem.config.cjs --env staging

const path = require('node:path');

const appCwd = path.resolve(__dirname);

module.exports = {
  apps: [
    {
      // Main Backend API Server
      name: 'cc-light-server',
      script: 'dist/server/index.js',
      cwd: appCwd,
      interpreter: 'node',
      node_args: [
        '--enable-source-maps',
        '--max-old-space-size=512',  // Optimize memory usage
        '--unhandled-rejections=strict'
      ],
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '512M',

      // Environment Variables
      env: {
        NODE_ENV: 'development',
        PORT: 3900,
        HOST: '127.0.0.1',
        PM2_PROCESS_NAME: 'cc-light-server'
      },
      env_staging: {
        NODE_ENV: 'staging',
        PORT: 3900,
        HOST: '127.0.0.1',
        PM2_PROCESS_NAME: 'cc-light-server',
        DEBUG: 'cc-light:*'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3900,
        HOST: '127.0.0.1',
        PM2_PROCESS_NAME: 'cc-light-server'
      },

      // Logging Configuration
      error_file: './logs/server-error.log',
      out_file: './logs/server-out.log',
      merge_logs: true,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      log_type: 'json',

      // Auto-restart Configuration
      autorestart: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,

      // Health Check Configuration
      health_check_http: true,
      health_check_path: '/health',
      health_check_interval: 30000,  // 30 seconds
      health_check_timeout: 5000,    // 5 seconds
      health_check_grace_period: 60000, // 1 minute

      // Advanced Configuration
      kill_timeout: 5000,
      wait_ready: true,
      listen_timeout: 8000,

      // Source maps for better debugging
      source_map_support: true,

      // Process management
      ignore_watch: [
        "node_modules",
        "logs",
        "dist/client",
        "*.log"
      ],

      // Environment file loading
      env_file: '.env',

      // Cron-style restart (optional - restart every day at 2 AM in production)
      cron_restart: process.env.NODE_ENV === 'production' ? '0 2 * * *' : undefined
    },

    {
      // Campaign Worker Process
      name: 'cc-light-campaign-worker',
      script: 'dist/server/jobs/campaign-worker.js',
      cwd: appCwd,
      interpreter: 'node',
      node_args: [
        '--enable-source-maps',
        '--max-old-space-size=256'
      ],
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '256M',

      // Environment Variables
      env: {
        NODE_ENV: 'development',
        PM2_PROCESS_NAME: 'cc-light-campaign-worker',
        WORKER_TYPE: 'campaign'
      },
      env_staging: {
        NODE_ENV: 'staging',
        PM2_PROCESS_NAME: 'cc-light-campaign-worker',
        WORKER_TYPE: 'campaign',
        DEBUG: 'cc-light:worker:*'
      },
      env_production: {
        NODE_ENV: 'production',
        PM2_PROCESS_NAME: 'cc-light-campaign-worker',
        WORKER_TYPE: 'campaign'
      },

      // Logging Configuration
      error_file: './logs/worker-error.log',
      out_file: './logs/worker-out.log',
      merge_logs: true,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      log_type: 'json',

      // Auto-restart Configuration
      autorestart: true,
      min_uptime: '5s',
      max_restarts: 15,
      restart_delay: 2000,

      // Advanced Configuration
      kill_timeout: 3000,

      // Source maps for better debugging
      source_map_support: true,

      // Cron job mode - run every 5 minutes in development, every hour in production
      cron_restart: process.env.NODE_ENV === 'production' ? '0 * * * *' : '*/5 * * * *',

      // Environment file loading
      env_file: '.env'
    }
  ],

  // PM2 Deploy Configuration (optional)
  deploy: {
    production: {
      user: 'node',
      host: ['server1.example.com', 'server2.example.com'],
      ref: 'origin/main',
      repo: 'git@github.com:username/cc-light.git',
      path: '/var/www/cc-light',
      'post-deploy': 'pnpm install && pnpm build && pm2 reload ecosystem.config.cjs --env production',
      'pre-setup': 'git clone git@github.com:username/cc-light.git /var/www/cc-light'
    },
    staging: {
      user: 'node',
      host: 'staging.example.com',
      ref: 'origin/develop',
      repo: 'git@github.com:username/cc-light.git',
      path: '/var/www/cc-light-staging',
      'post-deploy': 'pnpm install && pnpm build && pm2 reload ecosystem.config.cjs --env staging'
    }
  }
};
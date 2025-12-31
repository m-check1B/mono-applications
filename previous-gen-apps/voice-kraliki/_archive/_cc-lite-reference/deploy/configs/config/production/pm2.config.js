module.exports = {
  apps: [
    {
      name: 'cc-lite',
      script: 'dist/server.js',
      instances: 'max',
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PORT: 3900,
        HOST: '127.0.0.1'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3900,
        HOST: '127.0.0.1'
      },
      // Auto-restart configuration
      autorestart: true,
      watch: false,
      ignore_watch: [
        'node_modules',
        'logs',
        'dist',
        '.git'
      ],
      // Resource limits
      max_memory_restart: '1G',
      max_cpu_restart: '90%',

      // Logging
      log_file: '/var/log/cc-lite/pm2.log',
      out_file: '/var/log/cc-lite/out.log',
      error_file: '/var/log/cc-lite/error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

      // Time configuration
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 4000,

      // Cluster mode configuration
      wait_ready: true,
      listen_timeout: 10000,
      kill_timeout: 1600,

      // Environment variables
      merge_logs: true,
      source_map_support: false,

      // Monitoring
      monitoring: true,
      metrics: {
        network: true,
        v8: true,
        metrics: {
          rate: 1,
          max_elements: 120
        }
      }
    },
    {
      name: 'cc-lite-worker',
      script: 'dist/worker.js',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        WORKER_TYPE: 'background'
      },
      env_production: {
        NODE_ENV: 'production',
        WORKER_TYPE: 'background'
      },
      autorestart: true,
      max_memory_restart: '512M',
      log_file: '/var/log/cc-lite/worker.log',
      out_file: '/var/log/cc-lite/worker-out.log',
      error_file: '/var/log/cc-lite/worker-error.log'
    }
  ],

  // Deployment configuration
  deploy: {
    production: {
      user: 'deploy',
      host: ['localhost'],
      ref: 'origin/main',
      repo: 'git@github.com:your-org/cc-lite.git',
      path: '/var/www/cc-lite',
      'post-setup': 'npm install',
      'post-deploy': 'npm run build && pm2 reload ecosystem.config.js --env production',
      'pre-deploy-local': 'echo "Starting deployment..."',
      'post-deploy-local': 'echo "Deployment completed"'
    }
  }
};

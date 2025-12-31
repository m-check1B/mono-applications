module.exports = {
  apps: [
    {
      name: 'cc-lite-server',
      script: 'pnpm',
      args: 'dev:server',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 3010
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3010
      }
    },
    {
      name: 'cc-lite-campaign-worker',
      script: 'pnpm',
      args: 'tsx server/workers/campaign-worker.ts',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development'
      },
      env_production: {
        NODE_ENV: 'production'
      },
      error_file: './logs/campaign-worker-error.log',
      out_file: './logs/campaign-worker-out.log',
      log_file: './logs/campaign-worker-combined.log',
      time: true
    }
  ]
};
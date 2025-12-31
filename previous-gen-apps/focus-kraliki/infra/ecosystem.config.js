
module.exports = {
  apps: [
    {
      name: 'focus-kraliki-backend',
      cwd: './backend',
      script: 'bash',
      args: '-lc "if [ \"$NODE_ENV\" = production ]; then pnpm start; else pnpm dev; fi"',
      instances: 2, // PM2 cluster mode with 2 instances
      exec_mode: 'cluster',
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3017,
        HOST: '127.0.0.1',
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_file: './logs/backend-combined.log',
      time: true,
      merge_logs: true,
      // Health check configuration
      min_uptime: '10s',
      max_restarts: 10,
      autorestart: true,
    },
    {
      name: 'focus-kraliki-frontend',
      cwd: './frontend',
      script: 'bash',
      args: '-lc "if [ \"$NODE_ENV\" = production ]; then pnpm preview --host 127.0.0.1 --port 5175; else pnpm dev; fi"',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        NODE_ENV: 'development',
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 5175,
        HOST: '127.0.0.1',
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_file: './logs/frontend-combined.log',
      time: true,
    },
  ],

  // Deploy configuration for different environments
  deploy: {
    staging: {
      user: 'deploy',
      host: 'staging.focus.verduona.dev',
      ref: 'origin/develop',
      repo: 'git@github.com:focus-kraliki/focus-kraliki.git',
      path: '/var/www/focus-kraliki-staging',
      'pre-deploy': 'git fetch --all',
      'post-deploy': 'pnpm install && pnpm build && pm2 reload ecosystem.config.js --env staging',
      env: {
        NODE_ENV: 'staging',
      }
    },
    production: {
      user: 'deploy',
      host: 'focus.verduona.dev',
      ref: 'origin/main',
      repo: 'git@github.com:focus-kraliki/focus-kraliki.git',
      path: '/var/www/focus-kraliki',
      'pre-deploy': 'git fetch --all',
      'post-deploy': 'pnpm install && pnpm build && pm2 reload ecosystem.config.js --env production',
      'post-setup': 'pnpm install && pnpm build',
      env: {
        NODE_ENV: 'production',
      }
    }
  }
};

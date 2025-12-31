// PM2 Configuration for operator-demo-2026
// This configuration manages both frontend and backend services

module.exports = {
  apps: [
    {
      // Backend Service (FastAPI)
      name: 'operator-demo-backend',
      script: 'uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000 --reload',
      cwd: './backend',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 8000
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 8000,
        reload: false
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_file: './logs/backend-combined.log',
      time: true
    },
    {
      // Frontend Service (SvelteKit)
      name: 'operator-demo-frontend',
      script: 'npm',
      args: 'run preview',
      cwd: './frontend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        PORT: 5173,
        PUBLIC_BACKEND_URL: 'http://localhost:8000'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
        PUBLIC_BACKEND_URL: 'https://api.your-domain.com'
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_file: './logs/frontend-combined.log',
      time: true
    }
  ],

  // Deploy configuration (optional)
  deploy: {
    production: {
      user: 'adminmatej',
      host: 'your-server.com',
      ref: 'origin/develop',
      repo: 'https://github.com/m-check1B/operator-demo-2026.git',
      path: '/home/adminmatej/apps/operator-demo-2026',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-deploy-local': '',
      env: {
        NODE_ENV: 'production'
      }
    }
  }
};
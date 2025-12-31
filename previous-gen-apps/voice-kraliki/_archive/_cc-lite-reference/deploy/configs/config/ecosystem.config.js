// PM2 Ecosystem Configuration for CC-Light
// ========================================
// Optimized configuration for production deployment with subdomain support
// Usage: pm2 start config/ecosystem.config.js --env production

export default {
  apps: [
    {
      // Backend API Server (cc-lite-api)
      name: 'cc-lite-api',
      script: 'pnpm',
      args: 'start:server:production',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 3900,
        HOST: '127.0.0.1'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3900,
        HOST: '127.0.0.1', // Security: Bind to localhost only
        TELEPHONY_ENABLED: false,
        TELEPHONY_PROVIDER: 'twilio',
        OPENAI_LLM_MODEL: 'gpt-5',
        
        // Subdomain configuration
        FRONTEND_URL: 'https://app.cc-lite',
        API_BASE_URL: 'https://api.cc-lite',
        WEBHOOK_BASE_URL: 'https://api.cc-lite',
        
        // Multi-Language Configuration
        ENABLE_LANGUAGE_DETECTION: true,
        DEFAULT_LANGUAGE: 'en',
        SUPPORTED_LANGUAGES: 'en,es,cs',
        LANGUAGE_AUTO_DETECTION_THRESHOLD: 0.85,
        LANGUAGE_FALLBACK_ON_ERROR: true,
        
        // Czech Language Settings
        CZECH_LANGUAGE_ENABLED: true,
        CZECH_DEFAULT_DIALECT: 'cs-CZ',
        CZECH_STT_MODEL: 'nova-2-general',
        CZECH_TTS_PROVIDER: 'elevenlabs',
        CZECH_VOICE_MODEL: 'kamila-cs',
        CZECH_TTS_CACHE_ENABLED: true,
        CZECH_TTS_MAX_CACHE_SIZE: 100,
        
        // Spanish Language Settings
        SPANISH_LANGUAGE_ENABLED: true,
        SPANISH_DEFAULT_DIALECT: 'es-ES',
        SPANISH_STT_MODEL: 'nova-2-general',
        SPANISH_TTS_PROVIDER: 'deepgram',
        SPANISH_VOICE_MODEL: 'aura-2-nestor-es',
        SPANISH_DEFAULT_ACCENT: 'es-ES',
        SPANISH_FALLBACK_ACCENT: 'es-LA',
        
        // English Language Settings
        ENGLISH_LANGUAGE_ENABLED: true,
        ENGLISH_DEFAULT_DIALECT: 'en-US',
        ENGLISH_STT_MODEL: 'nova-2-general',
        ENGLISH_TTS_PROVIDER: 'deepgram',
        ENGLISH_VOICE_MODEL: 'aura-2-luna-en',
        
        // Voice Routing & Performance
        VOICE_ROUTING_ENABLED: true,
        VOICE_ROUTING_CACHE_TTL: 7200,
        VOICE_ROUTING_FALLBACK_ENABLED: true,
        LANGUAGE_CACHE_ENABLED: true,
        LANGUAGE_CACHE_TTL: 3600,
        TTS_CACHE_ENABLED: true,
        TTS_CACHE_MAX_SIZE: 500,
        STT_CACHE_ENABLED: true,
        STT_CACHE_TTL: 1800,
        
        // Performance Settings
        NODE_OPTIONS: '--max-old-space-size=2048',
        UV_THREADPOOL_SIZE: 16,
        
        // Security & Monitoring
        LOG_LEVEL: 'warn',
        LOG_FORMAT: 'json',
        MONITORING_ENABLED: true,
        HEALTH_CHECK_ENABLED: true,
        METRICS_COLLECTION_ENABLED: true,
        RATE_LIMIT_ENABLED: true,
        RATE_LIMIT_WINDOW_MS: 900000,
        RATE_LIMIT_MAX_REQUESTS: 50,
        
        // Bug Reporting
        APP_ENV: 'production'
      },
      error_file: '/var/log/cc-lite/api-error.log',
      out_file: '/var/log/cc-lite/api-out.log',
      merge_logs: true,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Auto-restart configuration
      autorestart: true,
      min_uptime: '10s',
      max_restarts: 10,
      
      // Health check
      health_check: {
        interval: 30000,
        timeout: 10000,
        max_failures: 5
      }
    },
    
    {
      // Frontend Vite Server (cc-lite-frontend)
      name: 'cc-lite-frontend',
      script: 'pnpm',
      args: 'preview',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        PORT: 5174,
        HOST: '127.0.0.1'
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 5174,
        HOST: '127.0.0.1', // Security: Bind to localhost only
        
        // Subdomain configuration for frontend
        VITE_API_BASE_URL: 'https://api.cc-lite',
        VITE_APP_BASE_URL: 'https://app.cc-lite',
        VITE_WEBHOOK_BASE_URL: 'https://api.cc-lite',
        
        // OpenAI Configuration
        OPENAI_LLM_MODEL: 'gpt-5',
        
        // Frontend Multi-Language Support
        VITE_DEFAULT_LANGUAGE: 'en',
        VITE_SUPPORTED_LANGUAGES: 'en,es,cs',
        VITE_ENABLE_LANGUAGE_DETECTION: true,
        VITE_APP_ENV: 'production',
        
        // Performance Settings for Frontend
        NODE_OPTIONS: '--max-old-space-size=1024'
      },
      error_file: '/var/log/cc-lite/frontend-error.log',
      out_file: '/var/log/cc-lite/frontend-out.log',
      merge_logs: true,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Auto-restart configuration
      autorestart: true,
      min_uptime: '10s',
      max_restarts: 10
    },
    
    {
      // Campaign Worker (autonomous runs)
      name: 'cc-lite-campaign-worker',
      script: 'pnpm',
      args: 'tsx server/jobs/campaign-worker.ts',
      cwd: '/home/adminmatej/github/apps/cc-lite',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'development',
        WORKER_HEARTBEAT_MS: 30000
      },
      env_production: {
        NODE_ENV: 'production',
        WORKER_HEARTBEAT_MS: 60000,
        HOST: '127.0.0.1',
        API_BASE_URL: 'https://api.cc-lite'
      },
      error_file: '/var/log/cc-lite/worker-error.log',
      out_file: '/var/log/cc-lite/worker-out.log',
      merge_logs: true,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Auto-restart configuration
      autorestart: true,
      min_uptime: '10s',
      max_restarts: 5
    },
    
    {
      // Database Backup Cron Job
      name: 'cc-lite-backup',
      script: '/home/adminmatej/github/apps/cc-lite/scripts/backup.sh',
      instances: 1,
      exec_mode: 'fork',
      cron_restart: '0 2 * * *', // Daily at 2 AM
      autorestart: false,
      watch: false,
      error_file: '/var/log/cc-lite/backup-error.log',
      out_file: '/var/log/cc-lite/backup-out.log',
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    
    {
      // Health Check Monitor
      name: 'cc-lite-monitor',
      script: '/home/adminmatej/github/apps/cc-lite/scripts/health-check.js',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '200M',
      env: {
        CHECK_INTERVAL: 60000, // Check every minute
        API_ENDPOINT: 'http://127.0.0.1:3900/health',
        FRONTEND_ENDPOINT: 'http://127.0.0.1:5174',
        ALERT_EMAIL: 'admin@yourdomain.com',
        SLACK_WEBHOOK: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
      },
      env_production: {
        CHECK_INTERVAL: 30000, // Check every 30 seconds in production
        API_ENDPOINT: 'https://api.cc-lite/health',
        FRONTEND_ENDPOINT: 'https://app.cc-lite',
        ALERT_EMAIL: 'admin@yourdomain.com'
      },
      error_file: '/var/log/cc-lite/monitor-error.log',
      out_file: '/var/log/cc-lite/monitor-out.log',
      merge_logs: true,
      time: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ],
  
  // Deploy configuration
  deploy: {
    production: {
      user: 'adminmatej',
      host: ['api.cc-lite', 'app.cc-lite'],
      ref: 'origin/main',
      repo: 'git@github.com:yourdomain/cc-lite.git',
      path: '/home/adminmatej/github/apps/cc-lite',
      'pre-deploy-local': 'pnpm test && pnpm build',
      'post-deploy': 'pnpm install --frozen-lockfile && pnpm build && pm2 reload config/ecosystem.config.js --env production',
      'pre-setup': 'mkdir -p /var/log/cc-lite',
      env: {
        NODE_ENV: 'production'
      }
    }
  }
};

// PM2 Commands Reference:
// =======================
// Start all apps: pm2 start config/ecosystem.config.js --env production
// Stop all apps: pm2 stop config/ecosystem.config.js
// Restart all apps: pm2 restart config/ecosystem.config.js
// Reload with zero downtime: pm2 reload config/ecosystem.config.js
// View logs: pm2 logs
// Monitor: pm2 monit
// Save current process list: pm2 save
// Auto-start on boot: pm2 startup
// Delete all apps: pm2 delete config/ecosystem.config.js
//
// Individual app management:
// pm2 start cc-lite-api --env production
// pm2 start cc-lite-frontend --env production
// pm2 restart cc-lite-api
// pm2 logs cc-lite-api

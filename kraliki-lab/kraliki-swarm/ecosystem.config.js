// Kraliki PM2 Ecosystem Configuration
// Location: /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/
//
// Start: pm2 start ecosystem.config.js
// Stop:  pm2 stop all
// Logs:  pm2 logs
//
// Architecture: 4 independent CLI watchdogs (claude, opencode, gemini, codex)
// Each CLI runs its own orchestrator. No coupling. If one fails, others work.

const fs = require('fs');
const path = require('path');

const KRALIKI_DIR = path.resolve(__dirname);
const APPS_DIR = path.resolve(KRALIKI_DIR, '..');
const APPS_ROOT = ['beta', 'kraliki-lab'].includes(path.basename(APPS_DIR))
  ? path.resolve(APPS_DIR, '..')
  : APPS_DIR;
const GITHUB_DIR = path.resolve(APPS_ROOT, '..');
const LOGS_DIR = path.join(KRALIKI_DIR, 'logs');
const SECRETS_DIR = path.join(GITHUB_DIR, 'secrets');
const TOOLS_DIR = path.join(GITHUB_DIR, 'tools');
const AGENT_BOARD_DIR = path.join(APPS_DIR, 'services', 'agent-board', 'backend');
const RECALL_DIR = path.join(APPS_DIR, 'services', 'recall-kraliki', 'backend');

// Load secrets from files
const LINEAR_API_KEY = fs.existsSync(`${SECRETS_DIR}/linear_api_key.txt`)
  ? fs.readFileSync(`${SECRETS_DIR}/linear_api_key.txt`, 'utf8').trim()
  : '';

module.exports = {
  apps: [
    // ===================
    // WATCHDOGS - Independent per-CLI (4 parallel streams)
    // ===================
    {
      name: 'kraliki-watchdog-claude',
      script: `${KRALIKI_DIR}/agents/watchdog_cli.py`,
      args: 'claude',
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 60000,
      error_file: `${LOGS_DIR}/control/watchdog-claude-error.log`,
      out_file: `${LOGS_DIR}/control/watchdog-claude-out.log`,
      merge_logs: true,
      time: true
    },
    {
      name: 'kraliki-watchdog-opencode',
      script: `${KRALIKI_DIR}/agents/watchdog_cli.py`,
      args: 'opencode',
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 60000,
      error_file: `${LOGS_DIR}/control/watchdog-opencode-error.log`,
      out_file: `${LOGS_DIR}/control/watchdog-opencode-out.log`,
      merge_logs: true,
      time: true,
      env: {
        LINEAR_API_KEY: LINEAR_API_KEY
      }
    },
    {
      name: 'kraliki-watchdog-gemini',
      script: `${KRALIKI_DIR}/agents/watchdog_cli.py`,
      args: 'gemini',
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 60000,
      error_file: `${LOGS_DIR}/control/watchdog-gemini-error.log`,
      out_file: `${LOGS_DIR}/control/watchdog-gemini-out.log`,
      merge_logs: true,
      time: true
    },
    {
      name: 'kraliki-watchdog-codex',
      script: `${KRALIKI_DIR}/agents/watchdog_cli.py`,
      args: 'codex',
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 60000,
      error_file: `${LOGS_DIR}/control/watchdog-codex-error.log`,
      out_file: `${LOGS_DIR}/control/watchdog-codex-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // HEALTH MONITOR - System health checks
    // ===================
    {
      name: 'kraliki-health',
      script: `${KRALIKI_DIR}/control/health-monitor.py`,
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 30000,
      error_file: `${LOGS_DIR}/control/health-error.log`,
      out_file: `${LOGS_DIR}/control/health-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // AGENT MONITOR - Tracks agent completion and triggers hooks (VD-477)
    // ===================
    {
      name: 'kraliki-agent-monitor',
      script: `${KRALIKI_DIR}/control/agent_monitor.py`,
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 10000,
      error_file: `${LOGS_DIR}/control/agent-monitor-error.log`,
      out_file: `${LOGS_DIR}/control/agent-monitor-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // STATS COLLECTOR - Hourly metrics
    // ===================
    {
      name: 'kraliki-stats',
      script: `${KRALIKI_DIR}/control/stats-collector.py`,
      interpreter: '/usr/bin/python3',
      cwd: GITHUB_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 60000,
      error_file: `${LOGS_DIR}/control/stats-error.log`,
      out_file: `${LOGS_DIR}/control/stats-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // DASHBOARD - Web UI (Kraliki Unified)
    // ===================
    {
      name: 'kraliki-swarm-dashboard',
      script: 'server.js',
      interpreter: 'node',
      cwd: path.join(KRALIKI_DIR, 'dashboard'),
      env: {
        HOST: '172.17.0.1',  // SECURITY: Bind to docker0 bridge only - Traefik accesses via host.docker.internal
        PORT: '8099',
        ORIGIN: 'https://kraliki.verduona.dev',
        KRALIKI_DIR: KRALIKI_DIR,
        // Zitadel OAuth Configuration
        ZITADEL_DOMAIN: 'identity.verduona.dev',
        ZITADEL_CLIENT_ID: '289758876994011392@kraliki',
        ZITADEL_CLIENT_SECRET: '3HM6fI6Hep6pJp8lW4n9OT5gp84wq1mGw9SIiQaRGrggQBqT2ZcvdD5qp2iKlHOa',
        // Local Development Fallback Auth
        LOCAL_AUTH_EMAIL: 'matej.havlin@gmail.com',
        LOCAL_AUTH_PASSWORD: 'Testing2026!!!',
        LOCAL_AUTH_NAME: 'Matej Havlin',
        // Integration URLs - Docker container IPs (updated dynamically)
        FOCUS_URL: 'http://172.21.0.12:3017',  // Focus by Kraliki backend
        SPEAK_URL: 'http://speak-kraliki-backend:8000',  // Speak by Kraliki backend
        LEARN_URL: 'http://127.0.0.1:8030'  // Learn by Kraliki backend
      },
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/control/dashboard-error.log`,
      out_file: `${LOGS_DIR}/control/dashboard-out.log`,
      merge_logs: true,
      time: true
    },
    {
      name: 'kraliki-swarm-dashboard-local',
      script: 'build/index.js',
      interpreter: 'node',
      cwd: path.join(KRALIKI_DIR, 'dashboard'),
      env: {
        HOST: '127.0.0.1',  // Local-only loopback for direct access and VS Code port forward
        PORT: '8099',
        ORIGIN: 'https://kraliki.verduona.dev',
        KRALIKI_DIR: KRALIKI_DIR,
        // Integration URLs - Docker container IPs (updated dynamically)
        FOCUS_URL: 'http://172.21.0.12:3017',  // Focus by Kraliki backend
        SPEAK_URL: 'http://speak-kraliki-backend:8000',  // Speak by Kraliki backend
        LEARN_URL: 'http://127.0.0.1:8030'  // Learn by Kraliki backend
      },
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/control/dashboard-local-error.log`,
      out_file: `${LOGS_DIR}/control/dashboard-local-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // WINDMILL API - Workflow engine (replaces n8n)
    // ===================
    {
      name: 'kraliki-windmill-api',
      script: `${KRALIKI_DIR}/integrations/windmill_api.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      env: {
        WINDMILL_URL: 'http://127.0.0.1:8100'
      },
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/integrations/windmill-api-error.log`,
      out_file: `${LOGS_DIR}/integrations/windmill-api-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // COMM HUB - Agent-to-agent messaging (REST) - localhost
    // ===================
    {
      name: 'kraliki-comm',
      script: `${KRALIKI_DIR}/comm/hub.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/control/comm-error.log`,
      out_file: `${LOGS_DIR}/control/comm-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // COMM HUB ZT - Agent messaging via ZeroTier (for Mac)
    // ===================
    {
      name: 'kraliki-comm-zt',
      script: `${KRALIKI_DIR}/comm/hub.py`,
      args: '--host 10.204.242.82 --port 8198',
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/control/comm-zt-error.log`,
      out_file: `${LOGS_DIR}/control/comm-zt-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // COMM WS - Real-time WebSocket messaging
    // ===================
    {
      name: 'kraliki-comm-ws',
      script: `${KRALIKI_DIR}/comm/ws_hub.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/control/comm-ws-error.log`,
      out_file: `${LOGS_DIR}/control/comm-ws-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // MESSAGE POLLER - Linear message bridge for external agents
    // ===================
    {
      name: 'kraliki-msg-poller',
      script: `${KRALIKI_DIR}/comm/message_poller.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 30000,  // 30s delay on restart
      error_file: `${LOGS_DIR}/control/msg-poller-error.log`,
      out_file: `${LOGS_DIR}/control/msg-poller-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // LINEAR SYNC - Dashboard Data Sync
    // ===================
    {
      name: 'kraliki-linear-sync',
      script: `${KRALIKI_DIR}/integrations/linear_sync.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 60000,
      error_file: `${LOGS_DIR}/integrations/linear-sync-error.log`,
      out_file: `${LOGS_DIR}/integrations/linear-sync-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // AGENT BOARD - Social Layer (Backend) - Internal tool, not a product
    // ===================
    {
      name: 'kraliki-agent-board',
      script: path.join(AGENT_BOARD_DIR, '.venv', 'bin', 'uvicorn'),
      args: 'app.main:app --host 127.0.0.1 --port 3021',
      cwd: AGENT_BOARD_DIR,
      interpreter: 'none',
      env: {
        PORT: '3021',
        API_HOST: '127.0.0.1'
      },
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/integrations/agent-board-error.log`,
      out_file: `${LOGS_DIR}/integrations/agent-board-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // RECALL - Long-term Memory (Backend)
    // ===================
    {
      name: 'kraliki-recall',
      script: path.join(RECALL_DIR, '.venv', 'bin', 'uvicorn'),
      args: 'app.main:app --host 127.0.0.1 --port 3020',
      cwd: RECALL_DIR,
      interpreter: 'none',
      env: {
        PORT: '3020',
        API_HOST: '127.0.0.1'
      },
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/integrations/recall-error.log`,
      out_file: `${LOGS_DIR}/integrations/recall-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // EVENTS BRIDGE - Kraliki <-> platform-2026 events-core integration
    // ===================
    {
      name: 'kraliki-events-bridge',
      script: `${KRALIKI_DIR}/integrations/events_bridge.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      env: {
        KRALIKI_COMM_URL: 'http://127.0.0.1:8199',
        RABBITMQ_URL: ''  // Empty = InMemory, set for RabbitMQ
      },
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 20000,
      min_uptime: '30s',
      max_memory_restart: '500M',
      error_file: `${LOGS_DIR}/integrations/events-bridge-error.log`,
      out_file: `${LOGS_DIR}/integrations/events-bridge-out.log`,
      merge_logs: true,
      time: true
    },

    // ===================
    // TELEGRAM NOTIFY BOT - @kraliki_dev_bot for CEO notifications
    // MOVED TO DOCKER: websites/docker-compose.yml (kraliki-telegram-bot)
    // Container needed for proper Traefik routing
    // ===================

    // ===================
    // KRALIKI MCP SERVER - Admin API for Claude Code
    // ===================
    {
      name: 'kraliki-mcp',
      script: `${KRALIKI_DIR}/mcp/server.py`,
      interpreter: '/usr/bin/python3',
      cwd: KRALIKI_DIR,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      error_file: `${LOGS_DIR}/control/mcp-error.log`,
      out_file: `${LOGS_DIR}/control/mcp-out.log`,
      merge_logs: true,
      time: true
    },
  ]
};

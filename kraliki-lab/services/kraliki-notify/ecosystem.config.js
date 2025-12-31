module.exports = {
  apps: [{
    name: 'kraliki-telegram-bot',
    script: '.venv/bin/uvicorn',
    // Bind to Docker bridge IP (172.17.0.1) for Traefik access
    // NOT 0.0.0.0 (security) and NOT 127.0.0.1 (Docker can't reach)
    args: 'app.main:app --host 172.17.0.1 --port 8097',
    cwd: '/home/adminmatej/github/applications/kraliki-lab/services/kraliki-notify',
    interpreter: 'none',
    // Load .env file automatically
    env_file: '.env'
  }]
};

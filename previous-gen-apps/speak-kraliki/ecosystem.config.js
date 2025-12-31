module.exports = {
  apps: [
    {
      name: 'speak-kraliki-backend',
      cwd: '/home/adminmatej/github/applications/speak-kraliki/backend',
      script: '.venv/bin/uvicorn',
      // Bind to localhost only (internet-connected dev server)
      args: 'app.main:app --host 127.0.0.1 --port 8020',
      interpreter: 'none',
      env: {
        PATH: '/home/adminmatej/github/applications/speak-kraliki/backend/.venv/bin:' + process.env.PATH
      },
      restart_delay: 3000,
      max_restarts: 5,
      autorestart: true
    },
    {
      name: 'speak-kraliki-frontend',
      cwd: '/home/adminmatej/github/applications/speak-kraliki/frontend',
      script: 'npm',
      // Bind to localhost only (internet-connected dev server)
      args: 'run dev -- --host 127.0.0.1 --port 5175',
      interpreter: 'none',
      restart_delay: 3000,
      max_restarts: 5,
      autorestart: true
    }
  ]
};

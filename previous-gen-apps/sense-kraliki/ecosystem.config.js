module.exports = {
  apps: [
    {
      name: "sense-kraliki-bot",
      script: ".venv/bin/python",
      args: "-m app.main",
      cwd: "/home/adminmatej/github/applications/sense-kraliki",
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
    },
  ],
};

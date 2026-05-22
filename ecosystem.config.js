module.exports = {
  apps: [
    {
      name: "telegram-gateway",
      script: "pipenv",
      args: "run start-telegram",
      interpreter: "none",
      cwd: __dirname,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      watch: false,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
  ],
};

# Developer Quickstart (Security)

1. Copy `.env.example` to `.env` and set secrets.
2. Start dependencies: `pnpm dev:services` (Postgres + Redis).
3. Run DB setup: `node scripts/setup-database.js`.
4. Start backend: `pnpm dev:server` and frontend: `pnpm dev`.

Security notes:
- Do not commit secrets.
- Use Docker secrets in production.


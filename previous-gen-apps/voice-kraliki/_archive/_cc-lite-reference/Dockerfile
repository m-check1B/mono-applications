# Voice by Kraliki production Dockerfile (monorepo structure)
# Alpha/Beta-ready: runs backend via tsx and serves built frontend

FROM node:20-alpine

RUN apk add --no-cache bash curl python3 make g++
WORKDIR /app

# Enable pnpm
RUN corepack enable && corepack prepare pnpm@9 --activate

# Install dependencies
COPY pnpm-lock.yaml package.json ./
COPY prisma ./prisma
COPY vendor ./vendor
COPY backend ./backend
COPY frontend ./frontend

RUN pnpm install --frozen-lockfile

# Install frontend dependencies and build
WORKDIR /app/frontend
RUN pnpm install --frozen-lockfile
WORKDIR /app

# Generate Prisma client and build
RUN pnpm prisma generate && pnpm build

# Runtime
ENV NODE_ENV=production
ENV HOST=0.0.0.0
EXPOSE 3010 3007

COPY scripts/start.sh ./scripts/start.sh
RUN chmod +x ./scripts/start.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3010/health || exit 1

CMD ["./scripts/start.sh"]


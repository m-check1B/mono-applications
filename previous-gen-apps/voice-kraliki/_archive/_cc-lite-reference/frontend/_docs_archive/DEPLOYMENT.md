# SvelteKit UI Deployment Guide

## 🚀 Running Locally

### Prerequisites
- Node.js >= 20
- pnpm >= 8
- Backend running on port 3010

### Development
```bash
# Install dependencies
pnpm install

# Start dev server (port 5173)
pnpm dev
```

### Production Build
```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

---

## 🐳 Docker Deployment (Recommended)

### Option 1: Standalone Container
```dockerfile
# Dockerfile
FROM node:20-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source
COPY . .

# Build
RUN pnpm build

# Expose port
EXPOSE 5173

# Start
CMD ["pnpm", "preview", "--host", "0.0.0.0", "--port", "5173"]
```

Build and run:
```bash
docker build -t cc-lite-ui .
docker run -p 5173:5173 --env-file .env cc-lite-ui
```

### Option 2: Docker Compose (with backend)
```yaml
# docker compose.yml (in cc-lite root)
version: '3.8'

services:
  backend:
    build: ./server
    ports:
      - "127.0.0.1:3010:3010"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      # ... other backend env vars
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./sveltekit-ui
    ports:
      - "127.0.0.1:5173:5173"
    environment:
      VITE_API_URL: http://backend:3010
      VITE_WS_URL: ws://backend:3010/ws

  postgres:
    image: postgres:16
    # ... postgres config

  redis:
    image: redis:7-alpine
    # ... redis config
```

Run:
```bash
docker compose up -d
```

---

## 🌐 Nginx Reverse Proxy

### Development (A/B Testing)
Run both React and SvelteKit, switch via Nginx:

```nginx
# /etc/nginx/sites-available/cc-lite
upstream react_frontend {
    server 127.0.0.1:3007;
}

upstream svelte_frontend {
    server 127.0.0.1:5173;
}

server {
    listen 80;
    server_name cc-lite.local;

    # Route 50% to React, 50% to SvelteKit
    location / {
        # Use cookie to maintain sticky sessions
        if ($cookie_frontend = "svelte") {
            proxy_pass http://svelte_frontend;
        }

        if ($cookie_frontend = "react") {
            proxy_pass http://react_frontend;
        }

        # Random split for new users
        set $backend react_frontend;
        if ($request_id ~ "[0-4]") {
            set $backend svelte_frontend;
            add_header Set-Cookie "frontend=svelte; Path=/";
        }
        if ($request_id ~ "[5-9]") {
            set $backend react_frontend;
            add_header Set-Cookie "frontend=react; Path=/";
        }

        proxy_pass http://$backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API (same for both)
    location /trpc {
        proxy_pass http://127.0.0.1:3010;
        proxy_set_header Host $host;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:3010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Production (SvelteKit Only)
```nginx
server {
    listen 80;
    server_name cc-lite.production.com;

    # SvelteKit frontend
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /trpc {
        proxy_pass http://127.0.0.1:3010;
        proxy_set_header Host $host;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:3010;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## ⚙️ Environment Variables

### Development (.env)
```bash
VITE_API_URL=http://127.0.0.1:3010
VITE_WS_URL=ws://127.0.0.1:3010/ws
```

### Production (.env.production)
```bash
VITE_API_URL=https://api.cc-lite.com
VITE_WS_URL=wss://api.cc-lite.com/ws
```

---

## 📊 A/B Testing Strategy

### Phase 1: Parallel Deployment (Week 1)
- Run both React and SvelteKit
- 10% traffic to SvelteKit
- Monitor errors, performance

### Phase 2: Gradual Rollout (Week 2)
- Increase to 50% traffic
- Collect user feedback
- Compare metrics

### Phase 3: Full Cutover (Week 3)
- 100% traffic to SvelteKit
- Keep React as backup
- Monitor for 1 week

### Phase 4: Deprecation (Week 4)
- Archive React codebase
- Remove old dependencies
- Update documentation

---

## 🔍 Monitoring

### Metrics to Track
- **Performance**:
  - First Contentful Paint (FCP)
  - Time to Interactive (TTI)
  - Lighthouse score
- **Usage**:
  - Active users (React vs SvelteKit)
  - Error rates
  - User session duration
- **Business**:
  - Conversion rates
  - Feature adoption
  - User satisfaction

### Tools
- **Google Analytics**: Track page views, user flows
- **Sentry**: Error monitoring
- **Lighthouse CI**: Performance regression testing

---

## 🐛 Rollback Plan

If SvelteKit has critical issues:

1. **Immediate**: Switch Nginx config to 100% React
   ```bash
   # Edit nginx config
   sudo nano /etc/nginx/sites-available/cc-lite
   # Change proxy_pass to react_frontend
   sudo nginx -t
   sudo systemctl reload nginx
   ```

2. **Investigate**: Check logs, Sentry errors

3. **Fix**: Deploy hotfix to SvelteKit

4. **Gradual Re-rollout**: Start at 10% again

---

## 📦 Build Optimization

### Vite Config
```typescript
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte'],
          trpc: ['@trpc/client', '@tanstack/svelte-query'],
        },
      },
    },
  },
});
```

---

## 🚀 Production Checklist

- [ ] Environment variables set
- [ ] Backend running and healthy
- [ ] Database migrated
- [ ] Redis connected
- [ ] WebSocket working
- [ ] SSL certificates configured
- [ ] Nginx config tested
- [ ] Error monitoring active (Sentry)
- [ ] Analytics tracking (GA)
- [ ] E2E tests passing
- [ ] Performance benchmarks meet targets
- [ ] Rollback plan documented

---

## 📞 Support

**Issues**: Check logs in:
- Frontend: Browser DevTools Console
- Backend: `pnpm dev:server` logs
- Nginx: `/var/log/nginx/error.log`

**Questions**: See main project README.md

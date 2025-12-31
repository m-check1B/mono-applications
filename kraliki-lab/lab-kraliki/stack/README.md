# Lab by Kraliki - Docker Stack

Docker deployment configuration for Lab by Kraliki (Lab by Kraliki).

## Quick Start

```bash
# Navigate to stack directory
cd stack/

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start services
docker compose up -d

# Check status
docker compose ps
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Infinity | 127.0.0.1:7997 | Embedding & reranking |
| Qdrant | 127.0.0.1:6333 | Vector database |
| Traefik | 127.0.0.1:8080 | Reverse proxy |
| Traefik Dashboard | 127.0.0.1:8081 | Service monitoring |

## Security

All ports are bound to `127.0.0.1` (localhost only).

Access services via:
- SSH tunnel: `ssh -L 7997:localhost:7997 user@server`
- VS Code Remote: Automatic port forwarding

## Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f [service]

# Update images
docker compose pull
docker compose up -d

# Check health
curl http://localhost:7997/health  # Infinity
curl http://localhost:6333/healthz # Qdrant
```

## Files

- `docker-compose.yml` - Service definitions
- `.env.example` - Environment template
- `Dockerfile` - Base image (for custom builds)
- `.dockerignore` - Build exclusions

## Volumes

Data persists in Docker volumes:
- `magic-box-qdrant-storage` - Vector database
- `magic-box-infinity-cache` - Model cache

Backup: `docker run --rm -v magic-box-qdrant-storage:/data -v $(pwd):/backup ubuntu tar cvf /backup/qdrant-backup.tar /data`

# Voice by Kraliki Docker Infrastructure

## Production

The production stack now lives in `infra/docker/production.yml`. To deploy:

```bash
docker compose -f infra/docker/production.yml up -d
```

- Secrets referenced in the compose file must exist (`cc_lite_*`).
- All old compose variants under `deploy/docker/` have been removed.
- CI/CD pipelines and scripts should reference the new path.

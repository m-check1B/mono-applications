# Docker Deployment Policy

Production deployments MUST use Docker with the consolidated compose file:

- infra/docker/production.yml

Context and rationale: DOCKER_CONSOLIDATION_SUMMARY.md

For local development of dependencies only, use:

- docker compose.dev.yml (development)


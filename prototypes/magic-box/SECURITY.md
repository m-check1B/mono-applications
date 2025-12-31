# Security Policy

## Supported Versions

Currently, only the latest version of Magic Box is supported for security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Magic Box seriously. If you believe you've found a security vulnerability, please report it to us as soon as possible.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please send an email to security@verduona.dev.

### What to include:
- A description of the vulnerability.
- Steps to reproduce the issue.
- Potential impact of the vulnerability.
- Any suggested fixes or mitigations.

### What to expect:
- We will acknowledge receipt of your report within 48 hours.
- We will provide a timeline for addressing the issue.
- We will keep you updated on our progress.

## Data Handling Practices

Magic Box is designed with privacy and data sovereignty in mind:

- **Self-Hosted Infrastructure**: All AI orchestration runs on customer-controlled infrastructure
- **No Verduona Data Collection**: No data, prompts, or outputs are sent to Verduona servers
- **API Key Protection**: Customer API keys stored locally in environment variables, never transmitted
- **Isolated Containers**: Each AI service runs in isolated Docker containers
- **Local Services**: All services bind to localhost (127.0.0.1) to prevent external access
- **Environment Variable Security**: Secrets are never committed to code repositories
- **Data Retention**: Customer maintains full control over data retention and deletion

### AI Service Integration

Magic Box orchestrates requests to third-party AI services (Anthropic Claude, Google Gemini, OpenAI Codex):
- Customer provides their own API keys
- API keys are stored locally and never shared with Verduona
- Prompts and responses flow directly between Magic Box and the AI service
- Verduona has no visibility into AI interactions

## Compliance Information

### GDPR Compliance

Magic Box is designed to support GDPR compliance requirements:

- **Data Sovereignty**: All data remains on customer infrastructure within the jurisdiction of the customer's choosing
- **Data Controller**: Customer acts as the data controller for all data processed through Magic Box
- **No Cross-Border Transfers**: No data is transferred outside of the customer's chosen infrastructure
- **Data Access**: Customer maintains full control and access to all data
- **Right to Deletion**: Customers can delete all data at any time by removing their deployment

### Data Residency

- All processing occurs on customer-controlled infrastructure
- No data is processed or stored on Verduona infrastructure
- Customer chooses the geographic location of their deployment
- Data residency requirements can be met by deploying in the customer's preferred region

### Third-Party Services

When using AI services through Magic Box:

- Customer is responsible for ensuring compliance with the third-party AI service's terms of service
- Customer should review the data handling policies of AI service providers (Anthropic, Google, OpenAI)
- Magic Box does not modify or intercept data sent to AI services

### Security Audits

For security audits or compliance reviews, customers can:

1. Review the open-source code in this repository
2. Inspect the Docker containers and services running on their infrastructure
3. Monitor network traffic to verify data flows
4. Review environment variable configurations

## Security Best Practices

This application follows security best practices:

- **API Security**: CLIProxyAPI with API key authentication
- **Infrastructure**: Traefik reverse proxy with TLS termination
- **Data Protection**: Secrets stored in environment variables, never in code
- **Network**: All services bound to localhost only (127.0.0.1)
- **Containerization**: Docker isolation for all services
- **Regular Updates**: Keep Docker images and dependencies updated
- **Monitoring**: Monitor logs for suspicious activity

Thank you for helping keep Magic Box secure!

# Security Policy

## Supported Versions

Currently, only the latest version of Voice by Kraliki is supported for security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Voice by Kraliki seriously. If you believe you've found a security vulnerability, please report it to us as soon as possible.

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

## Security Best Practices

This application follows security best practices:

- **Authentication**: Ed25519 JWT tokens with short expiration
- **Data Protection**: Call recordings encrypted at rest
- **API Security**: Rate limiting and input validation
- **Infrastructure**: All services bound to localhost only (127.0.0.1)
- **Telephony**: Secure SIP/WebRTC connections

Thank you for helping keep Voice by Kraliki secure!

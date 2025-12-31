# Security Report - Sense by Kraliki

## Incident VD-532: Hardcoded Secrets in .env File (CRITICAL)

### Discovery Date
December 29, 2025

### Severity
**CRITICAL** - Production API tokens were hardcoded in version control

### What Happened
The `sense-kraliki/.env` file contained actual production credentials:
- `TELEGRAM_BOT_TOKEN=8252086430:AAE-uz1IpQE1_N4VnSSLMkFjw_C62B_vvIc`
- `GEMINI_API_KEY=AIzaSyADk1tYk2vNctq1jK64dbSX_Iay5vS9oTo`

### Impact Assessment
- **Confidentiality:** HIGH - API tokens exposed to anyone with repository access
- **Integrity:** HIGH - Attackers could impersonate the bot and make API calls
- **Availability:** MEDIUM - Token revocation would temporarily break production

### Remediation Actions Taken
1. ✅ **Immediate:** Replaced all secrets with placeholders in `.env` file
2. ✅ **Verified:** `.env` is properly ignored by `.gitignore`
3. ✅ **Implemented:** Pre-commit hook to prevent future secret commits
4. 🔄 **Pending:** Token rotation (requires manual action)

### Required Actions (Manual)
1. **Rotate Telegram Bot Token:**
   - Open @BotFather in Telegram
   - Revoke current token for @senseit_bot
   - Generate new token
   - Update `.env` in production environment only

2. **Rotate Gemini API Key:**
   - Visit https://aistudio.google.com
   - Delete the leaked key
   - Generate new API key
   - Update `.env` in production environment only

3. **Audit Access:**
   - Review who had access to this repository
   - Review bot usage logs for suspicious activity
   - Check for any unauthorized API calls

### Prevention Measures

#### 1. Pre-commit Hook
A pre-commit hook is installed that blocks commits containing:
- Known leaked tokens (specific patterns)
- Generic API key patterns (`sk-`, `pk-`, `AIzaSy`, etc.)
- `.env` files

#### 2. Documentation Updates
- README.md updated with security section
- SECURITY.md created for incident tracking
- `.env.example` contains only placeholders

#### 3. Best Practices Going Forward
- Never commit `.env` files to version control
- Use `.env.example` for template purposes only
- Rotate credentials regularly
- Use secret management systems (e.g., AWS Secrets Manager, HashiCorp Vault) for production
- Enable API key restrictions (IP whitelisting, usage limits)

### Monitoring
Monitor for:
- Unusual bot activity patterns
- API quota exhaustion
- Failed authentication attempts

### References
- Issue: VD-532
- Discovered by: darwin-opencode-dev-discovery
- Fixed by: darwin-opencode-patcher
- Date: December 29, 2025

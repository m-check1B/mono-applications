# Focus by Kraliki Privacy Policy

**Last Updated:** November 16, 2025
**Effective Date:** November 16, 2025

## Overview

Focus by Kraliki is committed to protecting your privacy and giving you control over your data. This privacy policy explains how we collect, use, store, and protect your information.

**TL;DR:**
- You own your data, always
- We never train AI models on your content
- BYOK (Bring Your Own Key) gives you complete control
- You can export all your data anytime
- Feature toggles let you disable AI processing

---

## 1. Information We Collect

### 1.1 Account Information
- Email address (required for login)
- Full name (optional)
- Password (hashed with bcrypt, never stored in plain text)
- Google account ID (if you sign in with Google)

### 1.2 Usage Data
- Tasks, projects, and knowledge items you create
- Time entries and productivity metrics
- Voice recordings (if voice transcription is enabled)
- AI conversation history
- Shadow Work analysis results

### 1.3 Technical Data
- IP address (for security and fraud prevention)
- Browser type and version
- Device information
- Session logs

---

## 2. How We Use Your Information

### 2.1 Core Functionality
- **Task Management:** Store and organize your tasks, projects, and deadlines
- **AI Features:** Process requests through AI services (OpenRouter, Google Gemini)
- **Voice Transcription:** Convert voice input to text (if enabled)
- **Analytics:** Generate insights about your productivity patterns

### 2.2 Service Improvements
- Monitor service performance and reliability
- Detect and prevent abuse or security issues
- Aggregate anonymized usage statistics (no personal data)

### 2.3 Communications
- Send transactional emails (password resets, billing updates)
- Notify you about important product updates (optional)
- Respond to support requests

---

## 3. Third-Party Services

Focus by Kraliki uses the following third-party services to provide AI features:

### 3.1 OpenRouter (Default AI Provider)
- **What we send:** Your natural language prompts, task data, conversation history
- **Purpose:** Process AI requests for task parsing, scheduling, and insights
- **Data retention:** According to OpenRouter's privacy policy
- **Your control:** Use BYOK to process through your own API key
- **Policy:** https://openrouter.ai/privacy

### 3.2 Google Gemini (File Search)
- **What we send:** Knowledge item content, voice transcripts (if enabled)
- **Purpose:** Semantic search over your knowledge base
- **Data retention:** Stored in Google's File Search service
- **Your control:** Disable Gemini File Search in Settings → Privacy & Features
- **Policy:** https://ai.google.dev/gemini-api/terms

### 3.3 Deepgram (Voice Transcription)
- **What we send:** Audio recordings of your voice
- **Purpose:** Convert speech to text for task creation
- **Data retention:** Real-time processing, not stored after transcription
- **Your control:** Disable Voice Transcription in Settings
- **Policy:** https://deepgram.com/privacy

### 3.4 Stripe (Payment Processing)
- **What we send:** Billing information, payment details
- **Purpose:** Process subscription payments
- **Data retention:** According to Stripe's policy
- **Policy:** https://stripe.com/privacy

---

## 4. Data Control & Privacy Features

### 4.1 BYOK (Bring Your Own Key)

You can use your own API keys to process AI requests:

**Benefits:**
- ✅ Your data goes directly to your AI provider account
- ✅ We never see or store your AI requests
- ✅ Unlimited AI usage without upgrading to Premium
- ✅ Complete audit trail in your provider dashboard

**Supported Providers:**
- OpenRouter (for general AI tasks)
- Google Gemini (optional, for File Search)

**Setup:** Settings → API Keys → Add OpenRouter Key

### 4.2 Feature Toggles

Control which AI features can process your data:

| Feature | What It Does | Data Sent To |
|---------|-------------|--------------|
| **Gemini File Search** | Semantic search over knowledge | Google Gemini |
| **II-Agent Assistance** | Complex workflow automation | OpenRouter/Your BYOK key |
| **Voice Transcription** | Speech-to-text for tasks | Deepgram |

**How to disable:** Settings → Privacy & Features → Toggle off any feature

### 4.3 Data Export

Download all your data anytime:

- Tasks, projects, time entries (CSV/JSON)
- Knowledge items and notes
- AI conversation history
- Shadow Work analysis results

**Access:** Settings → Export Data (coming soon)

### 4.4 Data Deletion

Request complete account deletion:

- All your data is permanently deleted within 30 days
- Backups are purged within 90 days
- Third-party services (Gemini, OpenRouter) retain according to their policies

**How to delete:** Settings → Security → Delete Account

---

## 5. Data Storage & Security

### 5.1 Storage Location
- **Primary database:** PostgreSQL hosted on secure servers
- **Backups:** Encrypted daily backups, 30-day retention
- **File storage:** Secure cloud storage with encryption at rest

### 5.2 Encryption
- **In transit:** TLS 1.3 encryption for all connections
- **At rest:** AES-256 encryption for database and files
- **Passwords:** Bcrypt hashing with salt (industry standard)

### 5.3 Access Controls
- **Authentication:** JWT tokens with 7-day expiry
- **Authorization:** Role-based access control (RBAC)
- **Workspace isolation:** Organization-scoped data separation
- **Admin access:** Minimal team access, logged and audited

### 5.4 Security Practices
- Regular security audits and penetration testing
- Dependency scanning for vulnerabilities
- Incident response plan in place
- SOC 2 Type II compliance (in progress)

---

## 6. What We DO NOT Do

### 6.1 We Never:
- ❌ Train AI models on your personal data
- ❌ Sell your data to third parties
- ❌ Share your data without explicit consent
- ❌ Use your content for marketing or advertising
- ❌ Store credit card details (handled by Stripe)

### 6.2 AI Training Policy

**Focus by Kraliki does NOT train models on user data. Here's our contractual guarantee:**

- OpenRouter: Set `no_training: true` on all requests
- Google Gemini: Uses File Search API, not training pipeline
- Your content is ONLY used to answer YOUR queries

**Exception:** Anonymized, aggregated usage statistics (e.g., "80% of users create tasks via voice") may be used for product improvement. No personal data or content is included.

---

## 7. Compliance & Regulations

### 7.1 GDPR (European Users)

If you're in the EU, you have additional rights:

- **Right to Access:** Request all data we have about you
- **Right to Rectification:** Correct inaccurate data
- **Right to Erasure:** Request account deletion ("right to be forgotten")
- **Right to Portability:** Download your data in machine-readable format
- **Right to Object:** Opt out of certain processing (e.g., analytics)

**Contact for GDPR requests:** privacy@focus_kraliki.com

### 7.2 CCPA (California Users)

California residents have the right to:

- Know what personal information we collect
- Delete personal information
- Opt out of "sale" of personal information (we don't sell data)
- Non-discrimination for exercising privacy rights

**Contact for CCPA requests:** privacy@focus_kraliki.com

### 7.3 Data Processing Agreements

For enterprise customers, we offer:

- Data Processing Addendum (DPA)
- Business Associate Agreement (BAA) for HIPAA compliance
- Custom data retention policies

**Contact:** enterprise@focus_kraliki.com

---

## 8. Cookies & Tracking

### 8.1 Essential Cookies
- Authentication token (required for login)
- Session management (required for functionality)
- Security tokens (CSRF protection)

### 8.2 Optional Cookies
- Analytics cookies (if you consent)
- Preference cookies (theme, language)

**How to manage:** Browser settings → Cookies → Block third-party cookies

### 8.3 Analytics

We use minimal, privacy-respecting analytics:

- **What we track:** Page views, feature usage, error rates
- **What we DON'T track:** Individual user behavior, personal content
- **Tools:** Self-hosted analytics (no Google Analytics)
- **Opt out:** Settings → Privacy → Disable Analytics

---

## 9. Children's Privacy

Focus by Kraliki is not intended for users under 13 years old. We do not knowingly collect information from children. If you believe a child has created an account, please contact us at privacy@focus_kraliki.com.

---

## 10. Changes to This Policy

We may update this privacy policy to reflect:

- Changes in our services or features
- Legal or regulatory requirements
- User feedback and best practices

**Notification:**
- Email notification for material changes
- 30-day notice before changes take effect
- Continued use implies acceptance

**Version history:** Available at /privacy/changelog

---

## 11. Contact Us

### Privacy Questions
- **Email:** privacy@focus_kraliki.com
- **Response time:** Within 5 business days

### Data Subject Requests
For GDPR/CCPA requests:
- **Portal:** /privacy/requests
- **Email:** dpo@focus_kraliki.com (Data Protection Officer)
- **Response time:** Within 30 days

### Security Issues
For security vulnerabilities:
- **Email:** security@focus_kraliki.com
- **Responsible disclosure:** security@focus_kraliki.com
- **Bug bounty program:** Coming soon

---

## 12. Summary Table

| Question | Answer |
|----------|--------|
| **Who owns the data?** | You do, always |
| **Can I export my data?** | Yes, anytime in Settings |
| **Do you train AI on my data?** | Never |
| **Can I use my own API keys?** | Yes, BYOK supported |
| **How long is data retained?** | Until you delete your account |
| **Can I disable AI features?** | Yes, Settings → Privacy & Features |
| **Who has access to my data?** | Only you and minimal team admins |
| **Is data encrypted?** | Yes, in transit (TLS) and at rest (AES-256) |
| **Do you sell data?** | Never |
| **GDPR compliant?** | Yes |
| **CCPA compliant?** | Yes |
| **SOC 2 certified?** | In progress |

---

## 13. Transparency Commitment

Focus by Kraliki is committed to transparency:

- **Open source:** Core features are open source (GitHub)
- **Public roadmap:** See what we're building at /roadmap
- **Privacy reports:** Annual transparency reports
- **Third-party audits:** SOC 2 reports available on request

**Trust, but verify.** We welcome audits and feedback.

---

**Last Updated:** November 16, 2025
**Effective Date:** November 16, 2025
**Version:** 2.0

---

**Have questions?** Contact us at privacy@focus_kraliki.com or visit /docs/privacy-faq

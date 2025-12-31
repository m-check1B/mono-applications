"""Real-time agent assistance service for AI-first call center.

This service provides intelligent agent coaching with:
- Suggested responses in real-time
- Knowledge base integration
- Compliance checking
- Performance coaching
- Context-aware guidance
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AssistanceType(str, Enum):
    """Types of agent assistance."""
    SUGGESTED_RESPONSE = "suggested_response"
    KNOWLEDGE_ARTICLE = "knowledge_article"
    COMPLIANCE_WARNING = "compliance_warning"
    PERFORMANCE_TIP = "performance_tip"
    ESCALATION_GUIDE = "escalation_guide"


class AssistancePriority(str, Enum):
    """Priority levels for assistance."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AssistanceSuggestion(BaseModel):
    """An assistance suggestion for the agent."""
    id: str
    session_id: UUID
    type: AssistanceType
    priority: AssistancePriority
    title: str
    content: str
    confidence: float  # 0-1
    timestamp: datetime
    context: dict = {}

    class Config:
        json_schema_extra = {
            "example": {
                "id": "assist_123",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "suggested_response",
                "priority": "medium",
                "title": "Billing Issue Resolution",
                "content": "I understand your concern about the billing discrepancy. Let me review your account right away and get this resolved for you.",
                "confidence": 0.87,
                "timestamp": "2025-10-12T12:00:00Z",
                "context": {
                    "customer_sentiment": "frustrated",
                    "topic": "billing"
                }
            }
        }


class KnowledgeArticle(BaseModel):
    """Knowledge base article."""
    id: str
    title: str
    summary: str
    content: str
    category: str
    tags: list[str]
    relevance_score: float


class AssistanceConfig(BaseModel):
    """Configuration for agent assistance."""
    enable_suggestions: bool = True
    enable_knowledge_base: bool = True
    enable_compliance: bool = True
    enable_coaching: bool = True
    suggestion_threshold: float = 0.6  # Min confidence for suggestions
    max_suggestions: int = 3


class AgentAssistanceService:
    """Real-time agent assistance service.

    Provides intelligent suggestions, knowledge articles, and coaching
    to help agents perform better during customer interactions.
    """

    def __init__(self):
        """Initialize agent assistance service."""
        self._active_sessions: dict[UUID, AssistanceConfig] = {}
        self._suggestion_history: dict[UUID, list[AssistanceSuggestion]] = {}
        self._knowledge_base: dict[str, KnowledgeArticle] = {}
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Load knowledge base articles."""
        # Comprehensive knowledge base covering all major categories
        # In production, load from database or external KB system
        self._knowledge_base = {
            # BILLING ARTICLES (10 articles)
            "billing_001": KnowledgeArticle(
                id="billing_001",
                title="Billing Discrepancy Resolution",
                summary="How to handle billing discrepancies",
                content="When a customer reports a billing discrepancy, first verify their account details and review the complete billing history. Check for any promotional credits, discounts, or special rates that may apply. If an error is confirmed, apply the appropriate credit or refund immediately. Always document the resolution in the customer's account notes and provide a clear explanation of what caused the discrepancy and how it was resolved.",
                category="Billing",
                tags=["billing", "credit", "refund", "discrepancy", "account"],
                relevance_score=90
            ),
            "billing_002": KnowledgeArticle(
                id="billing_002",
                title="How to Update Payment Method",
                summary="Guide for updating customer payment information",
                content="To update a payment method, navigate to Account Settings > Billing > Payment Methods. Click 'Add Payment Method' to add a new credit card, debit card, or bank account. Customers can set a default payment method that will be used for all future billing cycles. Changes take effect immediately, and the system will automatically use the new method for the next billing date. Previous payment methods can be removed after confirming a new default is set.",
                category="Billing",
                tags=["payment", "credit card", "billing", "account", "update", "payment method"],
                relevance_score=85
            ),
            "billing_003": KnowledgeArticle(
                id="billing_003",
                title="Refund Processing Procedures",
                summary="How to process customer refunds",
                content="Refunds can be processed for eligible charges within 30 days of the billing date. To initiate a refund, verify the customer's identity and the reason for the refund request. Check if the service was used and to what extent. Full refunds are available for unused services, while partial refunds may apply for partial usage. Process the refund through the billing system and provide the customer with a confirmation number. Refunds typically appear in the customer's account within 5-7 business days.",
                category="Billing",
                tags=["refund", "billing", "payment", "credit", "reimbursement", "money back"],
                relevance_score=88
            ),
            "billing_004": KnowledgeArticle(
                id="billing_004",
                title="Subscription Plan Changes",
                summary="How to upgrade or downgrade customer subscription plans",
                content="Customers can change their subscription plan at any time. Upgrades take effect immediately with prorated charges for the remainder of the billing cycle. Downgrades typically take effect at the start of the next billing cycle to ensure the customer receives the full value of their current plan. When processing a plan change, review the feature differences with the customer and confirm they understand any changes in pricing, features, or service limits. Document the change and send a confirmation email.",
                category="Billing",
                tags=["subscription", "plan", "upgrade", "downgrade", "billing", "pricing"],
                relevance_score=87
            ),
            "billing_005": KnowledgeArticle(
                id="billing_005",
                title="Invoice and Receipt Requests",
                summary="How to provide invoices and receipts to customers",
                content="Customers can access all invoices and receipts through their account dashboard under Billing > Invoice History. Each invoice includes a detailed breakdown of charges, payment method used, and transaction date. For custom invoices or additional documentation, agents can generate PDF invoices directly from the billing system. Invoices can be emailed directly to the customer or to a designated billing contact. Historical invoices are available for up to 7 years.",
                category="Billing",
                tags=["invoice", "receipt", "billing", "documentation", "payment history", "records"],
                relevance_score=82
            ),
            "billing_006": KnowledgeArticle(
                id="billing_006",
                title="Failed Payment Recovery",
                summary="Steps to resolve failed payment transactions",
                content="When a payment fails, the system automatically retries the charge up to three times over a 10-day period. Common causes include insufficient funds, expired cards, or incorrect billing information. Contact the customer promptly to update payment information and avoid service interruption. If the payment continues to fail, the account may be placed on hold. Work with the customer to verify their payment details, update the payment method, and manually retry the transaction if needed.",
                category="Billing",
                tags=["payment", "failed", "declined", "billing", "credit card", "error"],
                relevance_score=86
            ),
            "billing_007": KnowledgeArticle(
                id="billing_007",
                title="Billing Cycle and Due Dates",
                summary="Understanding billing cycles and payment due dates",
                content="Billing cycles run on a monthly basis from the subscription start date. Invoices are generated 5 days before the due date and sent via email. Payment is automatically processed on the due date using the default payment method. Customers can view their next billing date in their account dashboard. If a payment fails, the customer has a 10-day grace period to update payment information before service is interrupted. Billing cycles can only be changed by contacting customer support.",
                category="Billing",
                tags=["billing cycle", "due date", "payment", "schedule", "monthly", "invoice date"],
                relevance_score=84
            ),
            "billing_008": KnowledgeArticle(
                id="billing_008",
                title="Promotional Credits and Discounts",
                summary="How to apply and manage promotional credits",
                content="Promotional credits are automatically applied to eligible accounts at checkout or billing time. Credits appear as line items on invoices and reduce the total amount charged. Credits typically have expiration dates and specific usage terms. To apply a promotional code, customers can enter it in the billing section or during checkout. Expired credits cannot be reinstated. Agents can verify available credits in the customer's account under Billing > Credits and view the expiration dates and applicable services.",
                category="Billing",
                tags=["promo", "discount", "credit", "coupon", "promotional code", "savings"],
                relevance_score=83
            ),
            "billing_009": KnowledgeArticle(
                id="billing_009",
                title="Tax and International Billing",
                summary="Handling taxes and international payment issues",
                content="Tax calculations vary by customer location and service type. Sales tax, VAT, or GST may apply based on local regulations. International customers may see charges in their local currency with exchange rates applied at the time of billing. For business customers, tax exemption certificates can be uploaded to the account to avoid applicable taxes. All tax documentation is included on invoices. International payment methods may require additional verification for fraud prevention.",
                category="Billing",
                tags=["tax", "VAT", "international", "currency", "billing", "exchange rate"],
                relevance_score=81
            ),
            "billing_010": KnowledgeArticle(
                id="billing_010",
                title="Account Cancellation and Final Billing",
                summary="Process for canceling accounts and final charges",
                content="Account cancellations can be initiated at any time through the account dashboard or by contacting support. Upon cancellation, customers are billed for usage through the cancellation date. Any prepaid amounts for unused services are refunded automatically. The final invoice is generated within 48 hours of cancellation and includes all outstanding charges. Customers have 30 days to download their data before the account is permanently deleted. Cancellation confirmations are sent via email and include the final invoice.",
                category="Billing",
                tags=["cancellation", "cancel", "billing", "final bill", "refund", "close account"],
                relevance_score=85
            ),

            # TECHNICAL SUPPORT ARTICLES (15 articles)
            "technical_001": KnowledgeArticle(
                id="technical_001",
                title="Connection Issues Troubleshooting",
                summary="Steps to resolve connection problems",
                content="Connection issues are often caused by network problems, firewall settings, or service outages. Start by checking the customer's internet connection and verifying they can access other websites. Ask them to restart their modem and router by unplugging for 30 seconds. Check for any service status alerts in the system. If the issue persists, verify firewall settings aren't blocking the service and ensure the customer's software is up to date. For persistent issues, escalate to technical support with detailed logs.",
                category="Technical Support",
                tags=["technical", "connectivity", "troubleshooting", "connection", "internet", "network"],
                relevance_score=92
            ),
            "technical_002": KnowledgeArticle(
                id="technical_002",
                title="Initial Account Setup and Configuration",
                summary="Step-by-step guide for new account setup",
                content="New account setup begins with email verification followed by profile completion. Guide customers through selecting their subscription plan, configuring notification preferences, and setting up their profile. Walk them through the dashboard layout and key features. Ensure they set up two-factor authentication for security. For business accounts, help configure team members, roles, and permissions. Provide links to getting started guides and video tutorials. Confirm all settings are saved before completing the setup process.",
                category="Technical Support",
                tags=["setup", "configuration", "new account", "onboarding", "getting started", "initial"],
                relevance_score=88
            ),
            "technical_003": KnowledgeArticle(
                id="technical_003",
                title="Mobile App Installation and Setup",
                summary="Guide for installing and configuring mobile applications",
                content="The mobile app is available for iOS and Android devices. Direct customers to download from the App Store or Google Play Store. After installation, they can log in using their existing credentials. The app will sync with their account automatically. Walk through enabling push notifications for important alerts. Show them how to access key features from the mobile interface. For sync issues, try logging out and back in. The app requires iOS 14+ or Android 8+ and an active internet connection.",
                category="Technical Support",
                tags=["mobile", "app", "installation", "setup", "iOS", "Android", "smartphone"],
                relevance_score=85
            ),
            "technical_004": KnowledgeArticle(
                id="technical_004",
                title="API Integration Support",
                summary="How to integrate and troubleshoot API connections",
                content="API integration requires generating API keys from the account dashboard under Developer Settings. Provide customers with the API documentation link and code samples. Common integration issues include incorrect authentication headers, rate limiting, and malformed requests. Verify the customer is using the correct API endpoint and version. Check their rate limits in the system. For authentication errors, regenerate API keys. All API requests should use HTTPS and include proper error handling. Debug logs can be accessed in the developer portal.",
                category="Technical Support",
                tags=["API", "integration", "developer", "technical", "authentication", "webhook"],
                relevance_score=87
            ),
            "technical_005": KnowledgeArticle(
                id="technical_005",
                title="Browser Compatibility and Cache Issues",
                summary="Resolving browser-related technical problems",
                content="The platform supports the latest versions of Chrome, Firefox, Safari, and Edge. If customers experience display issues or functionality problems, first ask them to clear their browser cache and cookies. Hard refresh the page using Ctrl+F5 or Cmd+Shift+R. Try accessing the site in an incognito or private browsing window to rule out extension conflicts. Ensure JavaScript is enabled and pop-up blockers aren't interfering. If issues persist, test with a different browser to isolate the problem.",
                category="Technical Support",
                tags=["browser", "cache", "technical", "display", "Chrome", "Firefox", "compatibility"],
                relevance_score=84
            ),
            "technical_006": KnowledgeArticle(
                id="technical_006",
                title="Data Import and Export Procedures",
                summary="How to import and export customer data",
                content="Data can be imported via CSV, JSON, or Excel files through the Data Import tool in account settings. The system validates data format and shows preview before importing. For large datasets, use the bulk import API. Data exports are available in multiple formats and can be scheduled for automatic generation. Exports include all account data or specific datasets based on filters. Large exports are processed asynchronously and delivered via email link. All data operations are logged for audit purposes.",
                category="Technical Support",
                tags=["import", "export", "data", "CSV", "migration", "backup", "transfer"],
                relevance_score=86
            ),
            "technical_007": KnowledgeArticle(
                id="technical_007",
                title="Performance Optimization Tips",
                summary="How to optimize system performance",
                content="To improve performance, start by reviewing the customer's current usage patterns and resource allocation. Large datasets should be paginated, and unnecessary features should be disabled. Optimize database queries by using appropriate filters and indexes. Enable caching where possible. For API users, implement request batching and use webhooks instead of polling. Monitor performance metrics in the dashboard and set up alerts for anomalies. Consider upgrading to a higher-tier plan if consistently hitting resource limits.",
                category="Technical Support",
                tags=["performance", "optimization", "speed", "slow", "technical", "efficiency"],
                relevance_score=83
            ),
            "technical_008": KnowledgeArticle(
                id="technical_008",
                title="Webhook Configuration and Testing",
                summary="Setting up and troubleshooting webhooks",
                content="Webhooks enable real-time event notifications to external systems. Configure webhooks in the Developer Settings section by providing an endpoint URL and selecting event types. The system sends POST requests with JSON payloads. Implement signature verification for security. Test webhooks using the test mode before going live. Common issues include endpoint timeouts, certificate errors, and incorrect response codes. Webhook delivery history and retry attempts are logged in the dashboard. Failed webhooks retry up to 5 times with exponential backoff.",
                category="Technical Support",
                tags=["webhook", "integration", "API", "events", "notifications", "developer"],
                relevance_score=88
            ),
            "technical_009": KnowledgeArticle(
                id="technical_009",
                title="Third-Party Integration Setup",
                summary="Connecting with third-party services and tools",
                content="The platform integrates with numerous third-party services including CRM systems, payment processors, and communication tools. Access integrations from the Apps & Integrations section. Each integration has specific setup instructions and required credentials. Use OAuth for secure authentication when available. After connecting, configure data sync settings and field mappings. Test the integration thoroughly before going live. Monitor integration health in the dashboard and check logs for any sync errors or failures.",
                category="Technical Support",
                tags=["integration", "third-party", "CRM", "apps", "connect", "sync"],
                relevance_score=85
            ),
            "technical_010": KnowledgeArticle(
                id="technical_010",
                title="Error Code Reference Guide",
                summary="Understanding and resolving common error codes",
                content="Error codes help identify specific issues. 4xx errors indicate client-side problems like invalid input or authentication failures. 5xx errors indicate server-side issues. Error 401: Authentication required - check API keys. Error 403: Insufficient permissions - verify account access. Error 404: Resource not found - verify the resource ID. Error 429: Rate limit exceeded - implement backoff strategy. Error 500: Server error - retry the request or contact support. All error responses include detailed messages and documentation links.",
                category="Technical Support",
                tags=["error", "troubleshooting", "technical", "error code", "debugging", "problem"],
                relevance_score=89
            ),
            "technical_011": KnowledgeArticle(
                id="technical_011",
                title="Security Best Practices",
                summary="Implementing security best practices",
                content="Security starts with strong passwords and two-factor authentication. Never share API keys or credentials. Rotate API keys regularly and immediately revoke compromised keys. Use IP whitelisting for API access when possible. Monitor account activity logs for suspicious behavior. Enable audit logging for all critical operations. Keep software and dependencies up to date. Implement proper access controls and principle of least privilege. Encrypt sensitive data at rest and in transit. Report any security concerns immediately to the security team.",
                category="Technical Support",
                tags=["security", "authentication", "2FA", "password", "access", "protection"],
                relevance_score=91
            ),
            "technical_012": KnowledgeArticle(
                id="technical_012",
                title="Backup and Disaster Recovery",
                summary="Data backup procedures and recovery options",
                content="All customer data is automatically backed up daily with multiple redundant copies. Backups are retained for 30 days for standard accounts and 90 days for premium accounts. Customers can manually trigger on-demand backups before major changes. To restore data, contact support with the desired restore point. Point-in-time recovery is available for the past 7 days. Disaster recovery procedures ensure 99.9% uptime with automatic failover to backup systems. Test restores regularly to verify backup integrity.",
                category="Technical Support",
                tags=["backup", "recovery", "disaster", "restore", "data protection", "redundancy"],
                relevance_score=86
            ),
            "technical_013": KnowledgeArticle(
                id="technical_013",
                title="System Status and Planned Maintenance",
                summary="Checking system status and maintenance schedules",
                content="Check real-time system status at status.example.com for service health, incident reports, and scheduled maintenance. Customers can subscribe to status updates via email, SMS, or RSS feed. Planned maintenance is announced at least 7 days in advance and typically scheduled during off-peak hours. During maintenance, some features may be temporarily unavailable. The status page shows historical uptime data and incident post-mortems. For critical issues, major incident notifications are sent immediately to all affected customers.",
                category="Technical Support",
                tags=["status", "maintenance", "downtime", "outage", "availability", "service health"],
                relevance_score=87
            ),
            "technical_014": KnowledgeArticle(
                id="technical_014",
                title="Custom Domain Configuration",
                summary="Setting up custom domains and SSL certificates",
                content="Custom domains can be configured for branded experiences. Add the domain in account settings and verify ownership via DNS records. Update DNS settings with the provided CNAME or A records. SSL certificates are automatically provisioned via Let's Encrypt. Domain propagation can take up to 48 hours. Verify the domain is working correctly using the validation tool. For subdomain routing, configure additional DNS records. Premium accounts can use custom SSL certificates. Contact support for wildcard domain setup.",
                category="Technical Support",
                tags=["domain", "DNS", "SSL", "custom", "configuration", "certificate", "HTTPS"],
                relevance_score=82
            ),
            "technical_015": KnowledgeArticle(
                id="technical_015",
                title="Rate Limiting and Usage Quotas",
                summary="Understanding API rate limits and account quotas",
                content="Rate limits prevent abuse and ensure fair usage. Standard accounts have 1000 API requests per hour. Premium accounts have 10000 requests per hour. Rate limit information is included in response headers. When limits are exceeded, requests return a 429 status code. Implement exponential backoff to handle rate limiting gracefully. Usage quotas apply to storage, bandwidth, and compute resources. Monitor usage in the account dashboard and set up alerts before reaching limits. Contact sales to increase quotas or upgrade plans.",
                category="Technical Support",
                tags=["rate limit", "quota", "API", "usage", "throttling", "limits"],
                relevance_score=84
            ),

            # ACCOUNT MANAGEMENT ARTICLES (10 articles)
            "account_001": KnowledgeArticle(
                id="account_001",
                title="Profile Settings and Customization",
                summary="How to update profile information and preferences",
                content="Profile settings can be accessed from the account menu in the top right corner. Update personal information including name, email, phone number, and profile picture. Set your timezone for accurate timestamps and scheduling. Configure language preferences for the interface. Update job title and department for team organization. Changes to email addresses require verification via confirmation link. Profile information is used for personalization and communication. Keep profile information current to ensure accurate account management.",
                category="Account Management",
                tags=["profile", "settings", "account", "preferences", "customization", "personal"],
                relevance_score=85
            ),
            "account_002": KnowledgeArticle(
                id="account_002",
                title="Two-Factor Authentication Setup",
                summary="Enabling and managing two-factor authentication",
                content="Two-factor authentication (2FA) adds an extra security layer to account access. Enable 2FA in Security Settings using an authenticator app like Google Authenticator or Authy. Scan the QR code or enter the setup key manually. Save the backup codes in a secure location for account recovery. Once enabled, login requires both password and time-based code. For SMS-based 2FA, verify your phone number first. Disable 2FA temporarily only if necessary and re-enable immediately. Contact support if locked out of account.",
                category="Account Management",
                tags=["2FA", "security", "authentication", "two-factor", "account protection", "login"],
                relevance_score=92
            ),
            "account_003": KnowledgeArticle(
                id="account_003",
                title="Notification Preferences",
                summary="Configuring email and push notifications",
                content="Customize notification preferences in Settings > Notifications. Choose which events trigger email notifications, such as billing updates, security alerts, or system notifications. Configure push notification settings for the mobile app. Set quiet hours to pause non-critical notifications during specific times. Create custom notification rules based on priority levels. Unsubscribe from marketing emails separately in the email footer. Critical security and billing notifications cannot be disabled. Notification settings apply across all devices and can be updated anytime.",
                category="Account Management",
                tags=["notifications", "email", "alerts", "preferences", "settings", "push"],
                relevance_score=84
            ),
            "account_004": KnowledgeArticle(
                id="account_004",
                title="Password Reset and Account Recovery",
                summary="Steps to reset password or recover locked accounts",
                content="Reset passwords using the 'Forgot Password' link on the login page. Enter the email address associated with the account to receive a reset link. Click the link within 1 hour to set a new password. For locked accounts after multiple failed login attempts, wait 30 minutes or use the password reset process. If unable to access email, contact support with account verification details. Use backup codes for 2FA account recovery. For compromised accounts, immediately reset password and review recent activity logs.",
                category="Account Management",
                tags=["password", "reset", "recovery", "locked", "forgot", "account access"],
                relevance_score=88
            ),
            "account_005": KnowledgeArticle(
                id="account_005",
                title="Team Member Management",
                summary="Adding and managing team members and roles",
                content="Add team members in Account Settings > Team Management. Send invitations via email with a specified role. Available roles include Admin, Member, and Viewer with different permission levels. Admins can manage billing and team settings. Members can access all features but not administrative functions. Viewers have read-only access. Remove team members or change roles as needed. Team member activity is logged for audit purposes. Each team member needs their own account and cannot share credentials.",
                category="Account Management",
                tags=["team", "users", "members", "roles", "permissions", "collaboration", "access"],
                relevance_score=86
            ),
            "account_006": KnowledgeArticle(
                id="account_006",
                title="Account Activity and Audit Logs",
                summary="Reviewing account activity and security logs",
                content="Access audit logs in Security Settings > Activity Log to review all account actions. Logs include login attempts, setting changes, API calls, and administrative actions. Filter logs by date range, user, or action type. Export logs for compliance or security review. Failed login attempts are highlighted for security monitoring. Activity logs are retained for 90 days for standard accounts and 365 days for enterprise accounts. Set up alerts for suspicious activity such as login from new locations or multiple failed attempts.",
                category="Account Management",
                tags=["activity", "audit", "logs", "security", "monitoring", "history"],
                relevance_score=87
            ),
            "account_007": KnowledgeArticle(
                id="account_007",
                title="Data Privacy and GDPR Compliance",
                summary="Managing data privacy settings and rights",
                content="Customers have rights to access, modify, and delete their personal data. Submit data access requests through Privacy Settings > Data Rights. Receive a complete copy of stored data within 30 days. Request data deletion for account closure or privacy reasons. Opt out of data processing for marketing purposes. Review the privacy policy for detailed information on data handling. For GDPR-related inquiries, contact the data protection officer. All data handling complies with GDPR, CCPA, and other privacy regulations.",
                category="Account Management",
                tags=["privacy", "GDPR", "data protection", "compliance", "personal data", "rights"],
                relevance_score=83
            ),
            "account_008": KnowledgeArticle(
                id="account_008",
                title="Session Management and Device Security",
                summary="Managing active sessions and connected devices",
                content="View all active sessions in Security Settings > Active Sessions. See device type, location, IP address, and last activity for each session. Remotely sign out of suspicious sessions or unused devices. The system automatically logs out inactive sessions after 24 hours. Enable setting to log out of all devices when password is changed. Review login history to identify unauthorized access attempts. Limit active sessions to trusted devices only. Use the mobile app's biometric authentication for added security.",
                category="Account Management",
                tags=["session", "device", "security", "logout", "active", "connected"],
                relevance_score=85
            ),
            "account_009": KnowledgeArticle(
                id="account_009",
                title="Account Transfer and Ownership",
                summary="Transferring account ownership to another user",
                content="Transfer account ownership in Settings > Account Transfer. Only account owners can initiate transfers. The new owner must have an existing account and accept the transfer request. All data, settings, and billing information transfer to the new owner. The previous owner loses all access unless added as a team member. Transfers cannot be reversed without support intervention. For business accounts, verify authorization documentation. Complete any outstanding billing before transfer. Transfer confirmation is sent to both parties.",
                category="Account Management",
                tags=["transfer", "ownership", "account", "change owner", "handover"],
                relevance_score=81
            ),
            "account_010": KnowledgeArticle(
                id="account_010",
                title="Account Deletion and Data Retention",
                summary="Permanently deleting accounts and data",
                content="Account deletion is permanent and cannot be undone. Before deleting, download any needed data using the export tool. Cancel active subscriptions to avoid future charges. Submit deletion request in Settings > Delete Account. A confirmation email is sent with a 7-day grace period. During the grace period, reactivate the account by logging in. After the grace period, all data is permanently deleted including backups. Some data may be retained for legal compliance purposes for up to 90 days. Usernames cannot be reused after deletion.",
                category="Account Management",
                tags=["deletion", "delete account", "remove", "close", "deactivate", "permanent"],
                relevance_score=86
            ),

            # PRODUCT FEATURES ARTICLES (10 articles)
            "product_001": KnowledgeArticle(
                id="product_001",
                title="AI-Powered Call Routing",
                summary="How AI routes calls to the best available agent",
                content="The AI call routing system analyzes incoming calls in real-time based on customer data, call history, and agent skills. Machine learning algorithms match customers with the most qualified agent for their specific needs. The system considers factors like language preference, technical expertise, and past interaction history. Priority routing is available for VIP customers. Call routing reduces wait times by 40% and improves first-call resolution rates. Admins can set custom routing rules and priorities. Review routing analytics in the dashboard to optimize performance.",
                category="Product Features",
                tags=["AI", "routing", "calls", "intelligent", "automation", "agents"],
                relevance_score=90
            ),
            "product_002": KnowledgeArticle(
                id="product_002",
                title="Real-Time Transcription Service",
                summary="Live call transcription and recording features",
                content="Real-time transcription converts voice calls to text instantly during conversations. Transcripts are displayed in the agent dashboard and saved for future reference. The system supports over 30 languages with high accuracy. Transcripts include speaker identification, timestamps, and confidence scores. Use transcripts for quality assurance, training, and compliance. Search historical transcripts by keyword or customer. Recording features require customer consent based on local regulations. Transcripts are stored securely and encrypted at rest.",
                category="Product Features",
                tags=["transcription", "recording", "calls", "voice", "speech-to-text", "AI"],
                relevance_score=89
            ),
            "product_003": KnowledgeArticle(
                id="product_003",
                title="Sentiment Analysis and Mood Detection",
                summary="AI-powered customer sentiment tracking",
                content="Sentiment analysis uses natural language processing to detect customer emotions in real-time. The system identifies positive, negative, or neutral sentiment with confidence scores. Visual indicators alert agents to frustrated customers requiring special attention. Sentiment trends are tracked over time to identify systemic issues. Managers can view sentiment analytics across all calls to measure customer satisfaction. The AI detects urgency levels and suggests appropriate responses. Sentiment data integrates with CRM systems for comprehensive customer profiles.",
                category="Product Features",
                tags=["sentiment", "analysis", "emotion", "AI", "mood", "customer satisfaction"],
                relevance_score=88
            ),
            "product_004": KnowledgeArticle(
                id="product_004",
                title="Automated Quality Assurance Scoring",
                summary="AI-driven call quality evaluation",
                content="Quality assurance scoring automatically evaluates every call based on customizable criteria. The AI assesses greeting quality, problem resolution, empathy, and call handling procedures. Scores are calculated immediately after calls end with detailed breakdowns. Agents receive feedback on areas for improvement. Supervisors can review flagged calls and provide coaching. Custom scoring rubrics can be created for different call types. Historical scores track agent performance over time. The system identifies top performers and those needing additional training.",
                category="Product Features",
                tags=["quality", "scoring", "QA", "evaluation", "performance", "AI"],
                relevance_score=87
            ),
            "product_005": KnowledgeArticle(
                id="product_005",
                title="Telephony Integration Options",
                summary="Connecting phone systems and carriers",
                content="The platform integrates with major telephony providers including Twilio, Vonage, and traditional PBX systems. Integration supports inbound and outbound calling, SMS, and conferencing. Configure phone numbers, call forwarding, and voicemail through the admin panel. SIP trunking is available for enterprise deployments. WebRTC technology enables browser-based calling without additional hardware. Call quality monitoring tools identify network issues. Failover and redundancy ensure high availability. Support for international numbers in over 100 countries.",
                category="Product Features",
                tags=["telephony", "phone", "integration", "calling", "SIP", "VoIP"],
                relevance_score=86
            ),
            "product_006": KnowledgeArticle(
                id="product_006",
                title="Advanced Analytics Dashboard",
                summary="Comprehensive reporting and analytics tools",
                content="The analytics dashboard provides real-time and historical insights into call center operations. Key metrics include call volume, average handle time, first-call resolution, and customer satisfaction scores. Create custom reports with drag-and-drop widgets. Schedule automated report delivery via email. Drill down into individual agent performance or team statistics. Compare metrics across time periods to identify trends. Export data in CSV or PDF formats. Set up alerts for metric thresholds. Analytics data is updated in real-time for up-to-the-minute insights.",
                category="Product Features",
                tags=["analytics", "reporting", "dashboard", "metrics", "statistics", "insights"],
                relevance_score=91
            ),
            "product_007": KnowledgeArticle(
                id="product_007",
                title="Intelligent Call Queuing",
                summary="Smart queue management and wait time optimization",
                content="Intelligent queuing uses AI to optimize wait times and call distribution. Customers are positioned in queue based on priority, issue complexity, and expected wait time. Real-time announcements inform callers of their position and estimated wait. Callback options allow customers to hang up and receive a call when an agent is available. Queue analytics identify peak times and staffing needs. Overflow routing redirects calls during high volume periods. VIP customers can have priority queue access. Music and messaging can be customized during wait times.",
                category="Product Features",
                tags=["queue", "waiting", "hold", "call management", "distribution", "IVR"],
                relevance_score=85
            ),
            "product_008": KnowledgeArticle(
                id="product_008",
                title="Omnichannel Communication Hub",
                summary="Unified interface for phone, email, chat, and social media",
                content="The omnichannel hub consolidates all customer communications in one interface. Agents can handle calls, emails, live chat, SMS, and social media messages from a single dashboard. Customer history is unified across all channels for consistent experiences. Conversations can be transferred seamlessly between channels. Automated channel routing directs inquiries to the most appropriate medium. Response templates speed up common replies. Channel analytics show volume and performance by communication type. Customers can switch channels mid-conversation without repeating information.",
                category="Product Features",
                tags=["omnichannel", "multichannel", "chat", "email", "social media", "unified"],
                relevance_score=89
            ),
            "product_009": KnowledgeArticle(
                id="product_009",
                title="Agent Coaching and Training Tools",
                summary="Built-in tools for agent development and coaching",
                content="Coaching tools help managers develop agent skills with targeted feedback. Review recorded calls with annotation and comments. Create training playlists from exemplary calls. Agents can self-assess performance using scorecards. Schedule coaching sessions and track improvement over time. Gamification features include leaderboards and achievement badges. Skill gap analysis identifies training needs across the team. Library of training materials and best practice guides. Certification programs for skill validation. Peer coaching features enable knowledge sharing among agents.",
                category="Product Features",
                tags=["coaching", "training", "development", "learning", "agents", "performance"],
                relevance_score=84
            ),
            "product_010": KnowledgeArticle(
                id="product_010",
                title="CRM Integration and Data Sync",
                summary="Connecting with Salesforce, HubSpot, and other CRMs",
                content="Native integrations with major CRM platforms including Salesforce, HubSpot, Zendesk, and Microsoft Dynamics. Bi-directional data sync keeps customer information up to date across systems. Call logs, transcripts, and recordings automatically attach to CRM records. Click-to-dial from CRM contacts. Custom field mapping ensures data flows correctly. Screen pop displays CRM records when calls arrive. Automated case creation for support tickets. Sync frequency and field selection are fully configurable. Troubleshoot sync issues using integration logs and diagnostics.",
                category="Product Features",
                tags=["CRM", "integration", "Salesforce", "sync", "data", "HubSpot"],
                relevance_score=90
            ),

            # POLICIES ARTICLES (5 articles)
            "policy_001": KnowledgeArticle(
                id="policy_001",
                title="Terms of Service Overview",
                summary="Key points from the terms of service agreement",
                content="The terms of service govern the use of the platform and define rights and responsibilities. Key provisions include acceptable use policies, service availability guarantees, and limitation of liability. Users must be 18 years or older and provide accurate information. Prohibited activities include illegal use, harassment, and attempts to compromise security. The company reserves the right to suspend accounts for violations. Service level agreements specify uptime commitments and remedies. Terms may be updated with notice to users. Continued use after changes constitutes acceptance of updated terms.",
                category="Policies",
                tags=["terms", "service", "agreement", "legal", "policy", "TOS"],
                relevance_score=82
            ),
            "policy_002": KnowledgeArticle(
                id="policy_002",
                title="Privacy Policy and Data Handling",
                summary="How customer data is collected, used, and protected",
                content="The privacy policy explains data collection, usage, and protection practices. Personal information is collected only for service delivery and improvement. Data is encrypted in transit and at rest using industry standards. Information is never sold to third parties. Data sharing occurs only with service providers under strict agreements. Users can access, modify, or delete their data at any time. Cookie usage and tracking is disclosed transparently. Compliance with GDPR, CCPA, and other privacy regulations is maintained. Contact the privacy team for questions or concerns.",
                category="Policies",
                tags=["privacy", "policy", "data", "GDPR", "protection", "personal information"],
                relevance_score=85
            ),
            "policy_003": KnowledgeArticle(
                id="policy_003",
                title="Data Retention and Deletion Policy",
                summary="How long data is retained and deletion procedures",
                content="Data retention periods vary by data type and regulatory requirements. Call recordings are retained for 90 days for standard accounts and up to 7 years for enterprise accounts. Transcripts and logs are kept for 1 year by default. Deleted data is permanently removed after a 30-day recovery period. Backups are retained according to the backup schedule. Some data may be retained longer for legal compliance or dispute resolution. Customers can request early deletion of specific data. Automated deletion processes run regularly to enforce retention policies.",
                category="Policies",
                tags=["retention", "deletion", "data", "policy", "storage", "compliance"],
                relevance_score=83
            ),
            "policy_004": KnowledgeArticle(
                id="policy_004",
                title="Compliance and Regulatory Standards",
                summary="Industry compliance certifications and standards",
                content="The platform maintains compliance with industry standards including SOC 2 Type II, HIPAA, PCI DSS, and GDPR. Regular third-party audits verify security and compliance controls. Call recording complies with federal and state regulations requiring customer consent. Data centers are certified for physical and logical security. Penetration testing and vulnerability assessments are conducted quarterly. Business continuity and disaster recovery plans are tested annually. Compliance documentation is available for customer audits. Contact the compliance team for specific certification questions.",
                category="Policies",
                tags=["compliance", "regulatory", "standards", "HIPAA", "SOC 2", "certification"],
                relevance_score=84
            ),
            "policy_005": KnowledgeArticle(
                id="policy_005",
                title="Acceptable Use Policy",
                summary="Guidelines for appropriate platform usage",
                content="The acceptable use policy defines prohibited activities and usage guidelines. Users must not engage in illegal activities, harassment, or spam. Attempts to compromise security or circumvent access controls are strictly forbidden. Excessive resource usage that impacts other users is not permitted. Content must not infringe intellectual property rights or contain malware. Users are responsible for maintaining the security of their accounts. Violations may result in account suspension or termination. Report policy violations to the abuse team. The policy is enforced to ensure a safe and reliable service for all users.",
                category="Policies",
                tags=["acceptable use", "policy", "prohibited", "guidelines", "rules", "violations"],
                relevance_score=81
            ),

            # TROUBLESHOOTING ARTICLES (5 additional articles)
            "troubleshoot_001": KnowledgeArticle(
                id="troubleshoot_001",
                title="Audio Quality Issues",
                summary="Resolving poor call audio quality problems",
                content="Audio quality issues can stem from network problems, hardware issues, or configuration errors. Check the customer's internet connection speed and stability - minimum 1 Mbps required for voice calls. Verify microphone and speaker settings in their device. Close bandwidth-heavy applications during calls. Use a wired connection instead of Wi-Fi when possible. Check for firewall or VPN interference. Test with different devices or headsets to isolate hardware issues. Review call quality metrics in the dashboard to identify patterns. Enable QoS settings on the router for voice traffic prioritization.",
                category="Troubleshooting",
                tags=["audio", "quality", "sound", "call", "voice", "troubleshooting", "technical"],
                relevance_score=88
            ),
            "troubleshoot_002": KnowledgeArticle(
                id="troubleshoot_002",
                title="Login and Authentication Problems",
                summary="Fixing issues with logging in to the account",
                content="Login problems can occur due to incorrect credentials, browser issues, or account status. Verify the email and password are correct - passwords are case-sensitive. Clear browser cache and cookies then try again. Disable browser extensions that might interfere with login. Check if the account is locked due to multiple failed attempts - wait 30 minutes or reset password. For 2FA issues, ensure the device clock is synchronized correctly. Try a different browser or incognito mode. Verify the account email is confirmed. Contact support if account is suspended or requires manual verification.",
                category="Troubleshooting",
                tags=["login", "authentication", "access", "password", "troubleshooting", "error"],
                relevance_score=87
            ),
            "troubleshoot_003": KnowledgeArticle(
                id="troubleshoot_003",
                title="Data Sync and Refresh Issues",
                summary="Resolving data synchronization problems",
                content="Data sync issues can prevent updates from appearing across devices or integrations. Force a manual refresh by clicking the refresh button or pressing F5. Check internet connectivity - sync requires a stable connection. Verify no browser extensions are blocking sync requests. Clear application cache in settings. Log out and back in to reinitiate sync. For integration sync issues, check the integration status and reconnect if necessary. Review sync logs for error messages. Large datasets may take time to sync - be patient. Contact support if sync has been failing for over 24 hours.",
                category="Troubleshooting",
                tags=["sync", "synchronization", "refresh", "data", "update", "troubleshooting"],
                relevance_score=85
            ),
            "troubleshoot_004": KnowledgeArticle(
                id="troubleshoot_004",
                title="Mobile App Crashes and Freezing",
                summary="Fixing mobile application stability issues",
                content="Mobile app crashes can be caused by outdated software, memory issues, or corrupted data. Ensure the app is updated to the latest version from the app store. Restart the device to clear memory and temporary issues. Clear the app cache in device settings. Uninstall and reinstall the app if problems persist - login credentials will be saved. Close other apps running in the background. Check device storage - low storage can cause instability. Verify the device meets minimum system requirements. Review app permissions and grant necessary access. Report persistent crashes with device model and OS version.",
                category="Troubleshooting",
                tags=["mobile", "app", "crash", "freeze", "troubleshooting", "iOS", "Android"],
                relevance_score=86
            ),
            "troubleshoot_005": KnowledgeArticle(
                id="troubleshoot_005",
                title="Notification Delivery Problems",
                summary="Troubleshooting missing or delayed notifications",
                content="Notification issues can prevent important alerts from reaching users. Verify notifications are enabled in account settings and device settings. Check that the email address or phone number is correct and verified. Look for notifications in spam or junk folders. Disable battery optimization for the app on mobile devices. Check if Do Not Disturb mode is enabled. Ensure push notification permissions are granted. Test notification delivery using the test notification feature. Review notification rules and filters that might be blocking certain types. For email notifications, whitelist the sender domain. Allow up to 15 minutes for delivery during high volume periods.",
                category="Troubleshooting",
                tags=["notifications", "alerts", "email", "push", "delivery", "troubleshooting"],
                relevance_score=84
            )
        }

    async def start_assistance(
        self,
        session_id: UUID,
        config: AssistanceConfig
    ) -> None:
        """Start providing assistance for a session.

        Args:
            session_id: Session identifier
            config: Assistance configuration
        """
        self._active_sessions[session_id] = config
        self._suggestion_history[session_id] = []
        logger.info(f"Started agent assistance for session {session_id}")

    async def stop_assistance(self, session_id: UUID) -> None:
        """Stop providing assistance for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        logger.info(f"Stopped agent assistance for session {session_id}")

    async def analyze_conversation(
        self,
        session_id: UUID,
        transcript: str,
        current_context: dict
    ) -> list[AssistanceSuggestion]:
        """Analyze conversation and provide assistance suggestions.

        Args:
            session_id: Session identifier
            transcript: Current conversation transcript
            current_context: Current conversation context

        Returns:
            List of assistance suggestions
        """
        config = self._active_sessions.get(session_id)
        if not config:
            return []

        suggestions = []

        if config.enable_suggestions:
            response_suggestions = await self._generate_response_suggestions(
                session_id, transcript, current_context
            )
            suggestions.extend(response_suggestions)

        if config.enable_knowledge_base:
            kb_suggestions = await self._search_knowledge_base(
                session_id, transcript, current_context
            )
            suggestions.extend(kb_suggestions)

        if config.enable_compliance:
            compliance_warnings = await self._check_compliance(
                session_id, transcript, current_context
            )
            suggestions.extend(compliance_warnings)

        if config.enable_coaching:
            coaching_tips = await self._generate_coaching_tips(
                session_id, transcript, current_context
            )
            suggestions.extend(coaching_tips)

        # Filter by confidence threshold
        filtered_suggestions = [
            s for s in suggestions
            if s.confidence >= config.suggestion_threshold
        ]

        # Limit to max suggestions
        filtered_suggestions.sort(key=lambda x: (x.priority.value, -x.confidence))
        filtered_suggestions = filtered_suggestions[:config.max_suggestions]

        # Store in history
        if session_id not in self._suggestion_history:
            self._suggestion_history[session_id] = []
        self._suggestion_history[session_id].extend(filtered_suggestions)

        return filtered_suggestions

    async def _generate_response_suggestions(
        self,
        session_id: UUID,
        transcript: str,
        context: dict
    ) -> list[AssistanceSuggestion]:
        """Generate suggested responses.

        Args:
            session_id: Session identifier
            transcript: Conversation transcript
            context: Current context

        Returns:
            List of response suggestions
        """
        suggestions = []

        # Analyze last customer message
        lines = [l for l in transcript.split('\n') if l.strip()]
        if not lines:
            return suggestions

        last_customer_message = ""
        for line in reversed(lines):
            if line.startswith('CUSTOMER:'):
                last_customer_message = line.replace('CUSTOMER:', '').strip()
                break

        if not last_customer_message:
            return suggestions

        # Generate contextual suggestions
        message_lower = last_customer_message.lower()

        if "billing" in message_lower or "charge" in message_lower:
            suggestions.append(AssistanceSuggestion(
                id=f"resp_{len(self._suggestion_history.get(session_id, []))}",
                session_id=session_id,
                type=AssistanceType.SUGGESTED_RESPONSE,
                priority=AssistancePriority.MEDIUM,
                title="Billing Inquiry Response",
                content="I understand your concern about the billing. Let me review your account details right away to help resolve this.",
                confidence=0.85,
                timestamp=datetime.now(UTC),
                context={"topic": "billing"}
            ))

        elif "problem" in message_lower or "issue" in message_lower:
            suggestions.append(AssistanceSuggestion(
                id=f"resp_{len(self._suggestion_history.get(session_id, []))}",
                session_id=session_id,
                type=AssistanceType.SUGGESTED_RESPONSE,
                priority=AssistancePriority.MEDIUM,
                title="Problem Acknowledgment",
                content="I apologize for the inconvenience you're experiencing. I'm here to help get this resolved for you quickly.",
                confidence=0.82,
                timestamp=datetime.now(UTC),
                context={"topic": "problem_solving"}
            ))

        return suggestions

    async def _search_knowledge_base(
        self,
        session_id: UUID,
        transcript: str,
        context: dict
    ) -> list[AssistanceSuggestion]:
        """Search knowledge base for relevant articles.

        Args:
            session_id: Session identifier
            transcript: Conversation transcript
            context: Current context

        Returns:
            List of knowledge base suggestions
        """
        suggestions = []
        transcript_lower = transcript.lower()

        # Simple keyword matching
        # In production, use vector search or semantic matching
        for article_id, article in self._knowledge_base.items():
            relevance = 0.0

            for tag in article.tags:
                if tag in transcript_lower:
                    relevance += 0.3

            if article.category in transcript_lower:
                relevance += 0.4

            if relevance > 0.5:
                suggestions.append(AssistanceSuggestion(
                    id=f"kb_{article_id}",
                    session_id=session_id,
                    type=AssistanceType.KNOWLEDGE_ARTICLE,
                    priority=AssistancePriority.LOW,
                    title=article.title,
                    content=article.summary,
                    confidence=min(relevance, 1.0),
                    timestamp=datetime.now(UTC),
                    context={"article_id": article_id, "category": article.category}
                ))

        return suggestions

    async def _check_compliance(
        self,
        session_id: UUID,
        transcript: str,
        context: dict
    ) -> list[AssistanceSuggestion]:
        """Check for compliance issues.

        Args:
            session_id: Session identifier
            transcript: Conversation transcript
            context: Current context

        Returns:
            List of compliance warnings
        """
        suggestions = []
        transcript_lower = transcript.lower()

        # Check for potential compliance issues
        restricted_phrases = [
            "guarantee",
            "promise",
            "always",
            "never"
        ]

        for phrase in restricted_phrases:
            if phrase in transcript_lower:
                suggestions.append(AssistanceSuggestion(
                    id=f"comp_{len(suggestions)}",
                    session_id=session_id,
                    type=AssistanceType.COMPLIANCE_WARNING,
                    priority=AssistancePriority.URGENT,
                    title="Compliance Alert",
                    content=f"Avoid using absolute terms like '{phrase}'. Use qualified language instead.",
                    confidence=1.0,
                    timestamp=datetime.now(UTC),
                    context={"detected_phrase": phrase}
                ))

        return suggestions

    async def _generate_coaching_tips(
        self,
        session_id: UUID,
        transcript: str,
        context: dict
    ) -> list[AssistanceSuggestion]:
        """Generate performance coaching tips.

        Args:
            session_id: Session identifier
            transcript: Conversation transcript
            context: Current context

        Returns:
            List of coaching tips
        """
        suggestions = []

        # Analyze agent's communication style
        agent_lines = [l for l in transcript.split('\n') if l.startswith('AGENT:')]

        if len(agent_lines) > 3:
            # Check for empathy phrases
            empathy_phrases = ["understand", "apologize", "appreciate"]
            has_empathy = any(
                any(phrase in line.lower() for phrase in empathy_phrases)
                for line in agent_lines
            )

            if not has_empathy:
                suggestions.append(AssistanceSuggestion(
                    id=f"coach_{len(suggestions)}",
                    session_id=session_id,
                    type=AssistanceType.PERFORMANCE_TIP,
                    priority=AssistancePriority.LOW,
                    title="Empathy Tip",
                    content="Consider adding empathy phrases like 'I understand' or 'I appreciate' to build rapport.",
                    confidence=0.75,
                    timestamp=datetime.now(UTC),
                    context={"tip_category": "empathy"}
                ))

        return suggestions

    def get_suggestion_history(
        self,
        session_id: UUID,
        limit: int | None = None
    ) -> list[AssistanceSuggestion]:
        """Get suggestion history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestions
        """
        history = self._suggestion_history.get(session_id, [])

        if limit:
            return history[-limit:]

        return history


# Singleton instance
_agent_assistance_service: AgentAssistanceService | None = None


def get_agent_assistance_service() -> AgentAssistanceService:
    """Get singleton agent assistance service instance.

    Returns:
        AgentAssistanceService instance
    """
    global _agent_assistance_service
    if _agent_assistance_service is None:
        _agent_assistance_service = AgentAssistanceService()
    return _agent_assistance_service

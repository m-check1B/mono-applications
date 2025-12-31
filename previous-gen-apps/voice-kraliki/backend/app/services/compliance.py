"""
Compliance and Consent Management Service

Handles regional compliance requirements for:
- Recording consent capture and management
- Data retention policies by region
- GDPR/CCPA compliance features
- Audit logging for compliance events
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

class Region(str, Enum):
    """Supported regions with specific compliance requirements"""
    US = "us"           # United States - minimal restrictions
    EU = "eu"           # European Union - GDPR
    UK = "uk"           # United Kingdom - UK GDPR
    CA = "ca"           # Canada - PIPEDA
    AU = "au"           # Australia - Privacy Act
    APAC = "apac"       # Asia Pacific - varies by country

class ConsentType(str, Enum):
    """Types of consent that can be captured"""
    RECORDING = "recording"
    TRANSCRIPTION = "transcription"
    AI_PROCESSING = "ai_processing"
    DATA_STORAGE = "data_storage"
    MARKETING = "marketing"
    ANALYTICS = "analytics"

class ConsentStatus(str, Enum):
    """Consent status values"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

@dataclass
class ConsentRecord:
    """Record of consent captured from a customer"""
    id: str
    session_id: str
    customer_phone: str
    region: Region
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: datetime | None = None
    denied_at: datetime | None = None
    withdrawn_at: datetime | None = None
    expires_at: datetime | None = None
    method: str = "verbal"  # verbal, written, electronic
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        # Convert string dates to datetime objects
        for field in ['granted_at', 'denied_at', 'withdrawn_at', 'expires_at']:
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, datetime.fromisoformat(value))

@dataclass
class RetentionPolicy:
    """Data retention policy for a specific region and data type"""
    region: Region
    data_type: str
    retention_days: int
    auto_delete: bool = True
    requires_consent: bool = True
    anonymize_after_retention: bool = False

@dataclass
class ComplianceEvent:
    """Audit log entry for compliance-related events"""
    id: str
    event_type: str
    session_id: str
    customer_phone: str
    region: Region
    timestamp: datetime
    details: dict[str, Any]
    user_id: str | None = None

    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)

class ComplianceService:
    """Service for managing compliance and consent"""

    def __init__(self):
        self.consent_records: dict[str, ConsentRecord] = {}
        self.compliance_events: list[ComplianceEvent] = []
        self.retention_policies: dict[str, RetentionPolicy] = {}
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """Initialize default retention policies by region"""
        # GDPR (EU) - strictest policies
        self.retention_policies["eu_recording"] = RetentionPolicy(
            region=Region.EU,
            data_type="recording",
            retention_days=30,
            requires_consent=True,
            anonymize_after_retention=True
        )
        self.retention_policies["eu_transcript"] = RetentionPolicy(
            region=Region.EU,
            data_type="transcript",
            retention_days=90,
            requires_consent=True,
            anonymize_after_retention=True
        )

        # US - more lenient policies
        self.retention_policies["us_recording"] = RetentionPolicy(
            region=Region.US,
            data_type="recording",
            retention_days=365,
            requires_consent=True,
            anonymize_after_retention=False
        )
        self.retention_policies["us_transcript"] = RetentionPolicy(
            region=Region.US,
            data_type="transcript",
            retention_days=730,
            requires_consent=True,
            anonymize_after_retention=False
        )

        # UK - similar to EU but with some differences
        self.retention_policies["uk_recording"] = RetentionPolicy(
            region=Region.UK,
            data_type="recording",
            retention_days=60,
            requires_consent=True,
            anonymize_after_retention=True
        )

        # Canada - PIPEDA requirements
        self.retention_policies["ca_recording"] = RetentionPolicy(
            region=Region.CA,
            data_type="recording",
            retention_days=180,
            requires_consent=True,
            anonymize_after_retention=True
        )

    def detect_region_from_phone(self, phone_number: str) -> Region:
        """Detect region from phone number"""
        # Simple country code detection
        if phone_number.startswith('+1'):
            return Region.US
        elif phone_number.startswith('+44'):
            return Region.UK
        elif any(phone_number.startswith(f'+{code}') for code in ['33', '49', '31', '34', '39', '41']):
            return Region.EU
        elif phone_number.startswith('+61'):
            return Region.AU
        elif phone_number.startswith('+1'):
            # Could be Canada, need more sophisticated detection
            # For now, default to US
            return Region.US
        else:
            # Default to US for unknown numbers
            return Region.US

    def capture_consent(self,
                       session_id: str,
                       customer_phone: str,
                       consent_type: ConsentType,
                       status: ConsentStatus,
                       method: str = "verbal",
                       ip_address: str | None = None,
                       user_agent: str | None = None,
                       metadata: dict[str, Any] | None = None) -> str:
        """Capture consent for a specific type"""

        region = self.detect_region_from_phone(customer_phone)
        consent_id = str(uuid4())

        now = datetime.now(UTC)

        consent_record = ConsentRecord(
            id=consent_id,
            session_id=session_id,
            customer_phone=customer_phone,
            region=region,
            consent_type=consent_type,
            status=status,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )

        # Set timestamps based on status
        if status == ConsentStatus.GRANTED:
            consent_record.granted_at = now
            # Set expiration for certain consent types
            if consent_type == ConsentType.MARKETING:
                consent_record.expires_at = now + timedelta(days=365)
        elif status == ConsentStatus.DENIED:
            consent_record.denied_at = now
        elif status == ConsentStatus.WITHDRAWN:
            consent_record.withdrawn_at = now

        self.consent_records[consent_id] = consent_record

        # Log compliance event
        self._log_compliance_event(
            event_type="consent_captured",
            session_id=session_id,
            customer_phone=customer_phone,
            region=region,
            details={
                "consent_id": consent_id,
                "consent_type": consent_type.value,
                "status": status.value,
                "method": method
            }
        )

        logger.info(f"Consent captured: {consent_type.value} = {status.value} for {customer_phone}")
        return consent_id

    def check_consent(self,
                     customer_phone: str,
                     consent_type: ConsentType,
                     session_id: str | None = None) -> bool:
        """Check if valid consent exists for a customer and consent type"""

        region = self.detect_region_from_phone(customer_phone)

        # Find the most recent consent record for this customer and type
        relevant_consents = [
            record for record in self.consent_records.values()
            if record.customer_phone == customer_phone
            and record.consent_type == consent_type
        ]

        if not relevant_consents:
            # No consent found
            self._log_compliance_event(
                event_type="consent_check_failed",
                session_id=session_id or "unknown",
                customer_phone=customer_phone,
                region=region,
                details={
                    "consent_type": consent_type.value,
                    "reason": "no_consent_found"
                }
            )
            return False

        # Sort by granted/denied timestamp (most recent first)
        relevant_consents.sort(
            key=lambda x: (x.granted_at or x.denied_at or x.withdrawn_at or datetime.min),
            reverse=True
        )

        latest_consent = relevant_consents[0]

        # Check if consent is still valid
        if latest_consent.status == ConsentStatus.GRANTED:
            if latest_consent.expires_at and latest_consent.expires_at < datetime.now(UTC):
                # Consent has expired
                self._log_compliance_event(
                    event_type="consent_expired",
                    session_id=session_id or "unknown",
                    customer_phone=customer_phone,
                    region=region,
                    details={
                        "consent_id": latest_consent.id,
                        "consent_type": consent_type.value,
                        "expired_at": latest_consent.expires_at.isoformat()
                    }
                )
                return False
            return True
        elif latest_consent.status == ConsentStatus.WITHDRAWN:
            return False
        else:
            return False

    def withdraw_consent(self,
                        consent_id: str,
                        session_id: str | None = None) -> bool:
        """Withdraw previously granted consent"""

        if consent_id not in self.consent_records:
            return False

        consent_record = self.consent_records[consent_id]
        consent_record.status = ConsentStatus.WITHDRAWN
        consent_record.withdrawn_at = datetime.now(UTC)

        self._log_compliance_event(
            event_type="consent_withdrawn",
            session_id=session_id or "unknown",
            customer_phone=consent_record.customer_phone,
            region=consent_record.region,
            details={
                "consent_id": consent_id,
                "consent_type": consent_record.consent_type.value
            }
        )

        logger.info(f"Consent withdrawn: {consent_id}")
        return True

    def get_retention_policy(self, region: Region, data_type: str) -> RetentionPolicy | None:
        """Get retention policy for a region and data type"""
        policy_key = f"{region.value}_{data_type}"
        return self.retention_policies.get(policy_key)

    def check_retention_compliance(self,
                                  customer_phone: str,
                                  data_type: str,
                                  created_at: datetime) -> bool:
        """Check if data can still be retained based on retention policies"""

        region = self.detect_region_from_phone(customer_phone)
        policy = self.get_retention_policy(region, data_type)

        if not policy:
            # No policy found, assume safe to retain
            return True

        # Check if data has exceeded retention period
        age_days = (datetime.now(UTC) - created_at).days
        return age_days <= policy.retention_days

    def schedule_data_deletion(self,
                              customer_phone: str,
                              data_type: str,
                              data_id: str,
                              created_at: datetime) -> datetime | None:
        """Schedule data for deletion based on retention policies"""

        region = self.detect_region_from_phone(customer_phone)
        policy = self.get_retention_policy(region, data_type)

        if not policy or not policy.auto_delete:
            return None

        # Calculate deletion date
        deletion_date = created_at + timedelta(days=policy.retention_days)

        self._log_compliance_event(
            event_type="data_deletion_scheduled",
            session_id="system",
            customer_phone=customer_phone,
            region=region,
            details={
                "data_type": data_type,
                "data_id": data_id,
                "deletion_date": deletion_date.isoformat(),
                "retention_days": policy.retention_days
            }
        )

        return deletion_date

    def get_consent_records(self,
                           customer_phone: str | None = None,
                           session_id: str | None = None,
                           consent_type: ConsentType | None = None) -> list[ConsentRecord]:
        """Get consent records with optional filtering"""

        records = list(self.consent_records.values())

        if customer_phone:
            records = [r for r in records if r.customer_phone == customer_phone]

        if session_id:
            records = [r for r in records if r.session_id == session_id]

        if consent_type:
            records = [r for r in records if r.consent_type == consent_type]

        return records

    def get_compliance_events(self,
                             customer_phone: str | None = None,
                             session_id: str | None = None,
                             event_type: str | None = None,
                             limit: int = 100) -> list[ComplianceEvent]:
        """Get compliance events with optional filtering"""

        events = self.compliance_events

        if customer_phone:
            events = [e for e in events if e.customer_phone == customer_phone]

        if session_id:
            events = [e for e in events if e.session_id == session_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by timestamp (most recent first) and limit
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]

    def _log_compliance_event(self,
                             event_type: str,
                             session_id: str,
                             customer_phone: str,
                             region: Region,
                             details: dict[str, Any]):
        """Log a compliance event for audit purposes"""

        event = ComplianceEvent(
            id=str(uuid4()),
            event_type=event_type,
            session_id=session_id,
            customer_phone=customer_phone,
            region=region,
            timestamp=datetime.now(UTC),
            details=details
        )

        self.compliance_events.append(event)

        # Keep only recent events (last 10000)
        if len(self.compliance_events) > 10000:
            self.compliance_events = self.compliance_events[-10000:]

    def export_compliance_data(self,
                              customer_phone: str,
                              format: str = "json") -> dict[str, Any]:
        """Export all compliance data for a customer (GDPR right to access)"""

        consent_records = self.get_consent_records(customer_phone=customer_phone)
        compliance_events = self.get_compliance_events(customer_phone=customer_phone)

        export_data = {
            "customer_phone": customer_phone,
            "export_date": datetime.now(UTC).isoformat(),
            "consent_records": [asdict(record) for record in consent_records],
            "compliance_events": [asdict(event) for event in compliance_events],
            "retention_policies": []
        }

        # Add relevant retention policies
        region = self.detect_region_from_phone(customer_phone)
        for policy_key, policy in self.retention_policies.items():
            if policy.region == region:
                export_data["retention_policies"].append(asdict(policy))

        return export_data

    def delete_customer_data(self, customer_phone: str) -> bool:
        """Delete all compliance data for a customer (GDPR right to be forgotten)"""

        # Delete consent records
        consent_to_delete = [
            consent_id for consent_id, record in self.consent_records.items()
            if record.customer_phone == customer_phone
        ]

        for consent_id in consent_to_delete:
            del self.consent_records[consent_id]

        # Log the deletion
        region = self.detect_region_from_phone(customer_phone)
        self._log_compliance_event(
            event_type="customer_data_deleted",
            session_id="system",
            customer_phone=customer_phone,
            region=region,
            details={
                "deleted_consent_records": len(consent_to_delete)
            }
        )

        logger.info(f"Deleted compliance data for customer: {customer_phone}")
        return True

# Global instance
compliance_service = ComplianceService()

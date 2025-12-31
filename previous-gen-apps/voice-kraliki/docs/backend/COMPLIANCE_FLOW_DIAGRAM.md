# Compliance Integration Flow Diagram

## Outbound Call Flow with Compliance Checks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        POST /api/v1/telephony/outbound                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Validate Request                                                         │
│     - from_number, to_number                                                 │
│     - telephony_provider (twilio/telnyx)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. CHECK RECORDING CONSENT (Lines 208-220)                                  │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │ compliance_service.check_consent(                                │    │
│     │     customer_phone=request.to_number,                            │    │
│     │     consent_type=ConsentType.RECORDING                           │    │
│     │ )                                                                 │    │
│     └─────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│     ┌─────────────────┐                           ┌─────────────────┐       │
│     │  Has Consent?   │──── YES ─────────────────▶│ Status: GRANTED │       │
│     └─────────────────┘                           └─────────────────┘       │
│            │                                              │                  │
│           NO                                              │                  │
│            │                                              │                  │
│            ▼                                              │                  │
│     ┌─────────────────┐                                  │                  │
│     │ Status: DENIED  │                                  │                  │
│     │ (Warning logged)│                                  │                  │
│     └─────────────────┘                                  │                  │
│            │                                              │                  │
│            └──────────────────┬───────────────────────────┘                  │
│                               │                                              │
└───────────────────────────────┼──────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Create Session with Metadata (Lines 222-235)                             │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │ metadata = {                                                     │    │
│     │     "from_number": from_number,                                  │    │
│     │     "to_number": request.to_number,                              │    │
│     │     "recording_consent": recording_consent_status,   ◄── NEW!   │    │
│     │     "compliance_checked": True,                      ◄── NEW!   │    │
│     │     **request.metadata                                           │    │
│     │ }                                                                 │    │
│     └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Start Session & Initiate Call                                            │
│     - session_manager.start_session()                                        │
│     - adapter.setup_call()                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Return Response                                                           │
│     {                                                                         │
│       "status": "accepted",                                                  │
│       "session_id": "...",                                                   │
│       "call_sid": "...",                                                     │
│       "recording_consent": "granted|denied"  ◄── Tracked in metadata        │
│     }                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Compliance Service Integration Points

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPLIANCE SERVICE FEATURES                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Consent Management                                                        │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │ • check_consent(phone, consent_type)                             │    │
│     │   └─▶ Returns: True/False                                        │    │
│     │   └─▶ Logs: Compliance event for audit                           │    │
│     │                                                                   │    │
│     │ • capture_consent(session_id, phone, consent_type, status)       │    │
│     │   └─▶ Creates: Consent record with timestamp                     │    │
│     │   └─▶ Logs: Consent capture event                                │    │
│     │                                                                   │    │
│     │ • withdraw_consent(consent_id)                                   │    │
│     │   └─▶ Updates: Status to WITHDRAWN                               │    │
│     │   └─▶ Logs: Consent withdrawal event                             │    │
│     └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Regional Compliance                                                       │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │ Phone Number        Region      Retention Policy                 │    │
│     │ ──────────────────────────────────────────────────────────────  │    │
│     │ +1 XXX XXX XXXX  →  US       →  365 days (recordings)           │    │
│     │ +44 XXXX XXXXXX  →  UK       →  60 days (recordings)            │    │
│     │ +33 X XX XX XX   →  EU       →  30 days (GDPR strict)           │    │
│     │ +61 X XXXX XXXX  →  AU       →  180 days (Privacy Act)          │    │
│     └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Audit Trail                                                               │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │ Event Type              Timestamp           Details              │    │
│     │ ──────────────────────────────────────────────────────────────  │    │
│     │ consent_check_failed    2025-10-14 18:40    No consent found    │    │
│     │ consent_captured        2025-10-14 18:41    Recording: granted  │    │
│     │ consent_check_passed    2025-10-14 18:42    Valid consent       │    │
│     │ consent_withdrawn       2025-10-14 19:00    User request        │    │
│     └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Decision Flow for Recording Consent

```
                            Check Consent
                                  │
                  ┌───────────────┴───────────────┐
                  │                               │
              ✅ FOUND                        ❌ NOT FOUND
                  │                               │
         ┌────────┴────────┐                     │
         │                 │                     │
    GRANTED          DENIED/WITHDRAWN            │
         │                 │                     │
         │                 └──────┬──────────────┘
         │                        │
         │                        ▼
         │              ┌─────────────────────┐
         │              │  WARNING LOGGED     │
         │              │  Status: "denied"   │
         │              │  Call: PROCEEDS     │
         │              └─────────────────────┘
         │                        │
         ▼                        │
┌─────────────────────┐          │
│  INFO LOGGED        │          │
│  Status: "granted"  │          │
│  Call: PROCEEDS     │          │
└─────────────────────┘          │
         │                        │
         └──────┬─────────────────┘
                │
                ▼
        ┌───────────────────┐
        │ Session Metadata: │
        │ - recording_consent: "granted" | "denied"
        │ - compliance_checked: true
        └───────────────────┘
                │
                ▼
        ┌───────────────────┐
        │  Call Continues   │
        │  with appropriate │
        │  recording policy │
        └───────────────────┘
```

## Key Benefits

1. **Non-Breaking**: Calls proceed regardless of consent status
2. **Auditable**: All consent checks logged with timestamps
3. **Regional Compliance**: Automatic region detection and policy application
4. **Flexible**: Easy to add strict mode or additional consent types
5. **Transparent**: Clear metadata tracking throughout call lifecycle

## Future Enhancements

- Add strict mode (block calls without consent)
- Integrate with IVR for real-time consent capture
- Add consent expiration handling
- Implement automatic data deletion based on retention policies
- Add GDPR export and right-to-be-forgotten endpoints

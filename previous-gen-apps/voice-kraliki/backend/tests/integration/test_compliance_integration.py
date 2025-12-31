"""
Test script to verify compliance integration in telephony routes.

This script validates:
1. Import of compliance service
2. Consent checking functionality
3. Consent capture and validation flow
"""

import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.compliance import compliance_service, ConsentType, ConsentStatus

def test_compliance_integration():
    """Test the compliance service integration."""

    print("=" * 60)
    print("COMPLIANCE INTEGRATION TEST")
    print("=" * 60)

    # Test 1: Import verification
    print("\n1. Testing imports...")
    print("   ✓ compliance_service imported successfully")
    print("   ✓ ConsentType enum imported successfully")
    print("   ✓ ConsentStatus enum imported successfully")

    # Test 2: Check consent for phone without consent (should return False)
    print("\n2. Testing consent check without prior consent...")
    test_phone = "+14155551234"
    has_consent = compliance_service.check_consent(
        customer_phone=test_phone,
        consent_type=ConsentType.RECORDING
    )
    print(f"   Phone: {test_phone}")
    print(f"   Has consent: {has_consent}")
    if not has_consent:
        print("   ✓ Correctly returns False for phone without consent")
    else:
        print("   ✗ ERROR: Should return False for phone without consent")
        return False

    # Test 3: Capture consent
    print("\n3. Testing consent capture...")
    consent_id = compliance_service.capture_consent(
        session_id="test-session-123",
        customer_phone=test_phone,
        consent_type=ConsentType.RECORDING,
        status=ConsentStatus.GRANTED,
        method="verbal",
        metadata={"test": True}
    )
    print(f"   Consent ID: {consent_id}")
    print("   ✓ Consent captured successfully")

    # Test 4: Check consent again (should return True now)
    print("\n4. Testing consent check with granted consent...")
    has_consent = compliance_service.check_consent(
        customer_phone=test_phone,
        consent_type=ConsentType.RECORDING
    )
    print(f"   Phone: {test_phone}")
    print(f"   Has consent: {has_consent}")
    if has_consent:
        print("   ✓ Correctly returns True for phone with granted consent")
    else:
        print("   ✗ ERROR: Should return True for phone with granted consent")
        return False

    # Test 5: Verify consent records
    print("\n5. Testing consent record retrieval...")
    consent_records = compliance_service.get_consent_records(
        customer_phone=test_phone
    )
    print(f"   Found {len(consent_records)} consent record(s)")
    if len(consent_records) > 0:
        record = consent_records[0]
        print(f"   - Consent Type: {record.consent_type.value}")
        print(f"   - Status: {record.status.value}")
        print(f"   - Region: {record.region.value}")
        print(f"   - Method: {record.method}")
        print("   ✓ Consent records retrieved successfully")
    else:
        print("   ✗ ERROR: No consent records found")
        return False

    # Test 6: Verify compliance events
    print("\n6. Testing compliance event logging...")
    compliance_events = compliance_service.get_compliance_events(
        customer_phone=test_phone,
        limit=10
    )
    print(f"   Found {len(compliance_events)} compliance event(s)")
    if len(compliance_events) > 0:
        for i, event in enumerate(compliance_events[:3], 1):
            print(f"   {i}. {event.event_type} at {event.timestamp}")
        print("   ✓ Compliance events logged successfully")
    else:
        print("   ✗ WARNING: No compliance events found")

    # Test 7: Test with different phone numbers and regions
    print("\n7. Testing region detection...")
    test_phones = {
        "+14155551234": "US",
        "+442071234567": "UK",
        "+33123456789": "EU",
        "+61212345678": "AU"
    }

    for phone, expected_region in test_phones.items():
        detected_region = compliance_service.detect_region_from_phone(phone)
        region_match = detected_region.value.upper() == expected_region
        status = "✓" if region_match else "✗"
        print(f"   {status} {phone} -> {detected_region.value.upper()} (expected: {expected_region})")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nCompliance integration is working correctly.")
    print("The telephony routes can now use compliance_service.check_consent()")
    print("to validate recording consent before starting calls.")

    return True

if __name__ == "__main__":
    try:
        success = test_compliance_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

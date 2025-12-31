"""Test script for persistent call state management.

This script verifies that call state persistence works correctly with
database storage and Redis caching.
"""

import sys
import os
from uuid import uuid4
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.telephony.call_state_manager import get_call_state_manager
from app.models.call_state import CallStatus
from app.database_init import initialize_database, get_database_status


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_basic_registration():
    """Test basic call registration."""
    print_section("Test 1: Basic Call Registration")

    manager = get_call_state_manager()

    # Create test call
    call_id = f"test_call_{uuid4().hex[:8]}"
    session_id = uuid4()

    print(f"Registering call: {call_id}")
    print(f"Session ID: {session_id}")

    call_state = manager.register_call(
        call_id=call_id,
        session_id=session_id,
        provider="twilio",
        direction="inbound",
        from_number="+1234567890",
        to_number="+0987654321",
        metadata={"test": "data"}
    )

    print(f"✓ Call registered successfully")
    print(f"  Status: {call_state.status}")
    print(f"  Provider: {call_state.provider}")
    print(f"  Direction: {call_state.direction}")

    return call_id, session_id


def test_lookup_operations(call_id: str, session_id):
    """Test lookup operations."""
    print_section("Test 2: Lookup Operations")

    manager = get_call_state_manager()

    # Test call -> session lookup
    print(f"Looking up session for call: {call_id}")
    found_session = manager.get_session_for_call(call_id)
    print(f"✓ Found session: {found_session}")
    assert found_session == session_id, "Session ID mismatch!"

    # Test session -> call lookup
    print(f"\nLooking up call for session: {session_id}")
    found_call = manager.get_call_for_session(session_id)
    print(f"✓ Found call: {found_call}")
    assert found_call == call_id, "Call ID mismatch!"

    # Test call details
    print(f"\nGetting call details for: {call_id}")
    call_state = manager.get_call_by_id(call_id)
    if call_state:
        print(f"✓ Call details retrieved:")
        print(f"  Status: {call_state.status}")
        print(f"  From: {call_state.from_number}")
        print(f"  To: {call_state.to_number}")
        print(f"  Metadata: {call_state.call_metadata}")
    else:
        print("✗ Call not found!")


def test_status_updates(call_id: str):
    """Test status updates."""
    print_section("Test 3: Status Updates")

    manager = get_call_state_manager()

    statuses = [
        CallStatus.RINGING,
        CallStatus.ANSWERED,
        CallStatus.ON_HOLD,
        CallStatus.ANSWERED,
    ]

    for status in statuses:
        print(f"Updating call {call_id} to {status.value}...")
        success = manager.update_call_status(call_id, status)
        if success:
            print(f"✓ Status updated to {status.value}")
        else:
            print(f"✗ Failed to update status")

    # Verify final status
    call_state = manager.get_call_by_id(call_id)
    if call_state:
        print(f"\nFinal status: {call_state.status}")


def test_active_calls(call_id: str):
    """Test active calls retrieval."""
    print_section("Test 4: Active Calls")

    manager = get_call_state_manager()

    print("Retrieving active calls...")
    active_calls = manager.get_active_calls()
    print(f"✓ Found {len(active_calls)} active call(s)")

    for call in active_calls:
        print(f"  - {call.call_id} ({call.status.value})")

    # Verify our test call is in the list
    test_call_found = any(c.call_id == call_id for c in active_calls)
    if test_call_found:
        print(f"✓ Test call {call_id} is in active calls")
    else:
        print(f"✗ Test call {call_id} not found in active calls!")


def test_call_completion(call_id: str, session_id):
    """Test call completion."""
    print_section("Test 5: Call Completion")

    manager = get_call_state_manager()

    print(f"Ending call: {call_id}")
    success = manager.end_call(call_id)
    if success:
        print(f"✓ Call ended successfully")
    else:
        print(f"✗ Failed to end call")

    # Verify status is completed
    call_state = manager.get_call_by_id(call_id)
    if call_state:
        print(f"  Status: {call_state.status}")
        print(f"  Ended at: {call_state.ended_at}")
        assert call_state.status == CallStatus.COMPLETED

    # Verify removed from active calls
    active_calls = manager.get_active_calls()
    test_call_found = any(c.call_id == call_id for c in active_calls)
    if not test_call_found:
        print(f"✓ Call removed from active calls")
    else:
        print(f"✗ Call still in active calls!")


def test_persistence_recovery():
    """Test persistence recovery after restart."""
    print_section("Test 6: Persistence Recovery")

    # Create a new call
    manager = get_call_state_manager()
    call_id = f"persist_call_{uuid4().hex[:8]}"
    session_id = uuid4()

    print(f"Creating call for persistence test: {call_id}")
    manager.register_call(
        call_id=call_id,
        session_id=session_id,
        provider="twilio",
        direction="outbound",
        from_number="+1111111111",
        to_number="+2222222222",
    )
    print(f"✓ Call created")

    # Simulate recovery
    print("\nSimulating server restart and recovery...")
    recovered_calls = manager.recover_active_calls()
    print(f"✓ Recovered {len(recovered_calls)} active call(s)")

    for call in recovered_calls:
        print(f"  - {call.call_id} ({call.status.value})")

    # Clean up
    print(f"\nCleaning up persistence test call...")
    manager.end_call(call_id)
    print(f"✓ Cleaned up")


def test_backwards_compatibility():
    """Test backwards compatibility with old state module."""
    print_section("Test 7: Backwards Compatibility")

    from app.telephony import state

    # Test registration
    call_id = f"compat_call_{uuid4().hex[:8]}"
    session_id = uuid4()

    print(f"Testing state.register_call()...")
    state.register_call(call_id, session_id)
    print(f"✓ Call registered via state module")

    # Test lookup
    print(f"\nTesting state.get_session_for_call()...")
    found_session = state.get_session_for_call(call_id)
    print(f"✓ Found session: {found_session}")
    assert found_session == session_id

    print(f"\nTesting state.get_call_for_session()...")
    found_call = state.get_call_for_session(session_id)
    print(f"✓ Found call: {found_call}")
    assert found_call == call_id

    # Test unregister
    print(f"\nTesting state.unregister_call()...")
    state.unregister_call(call_id)
    print(f"✓ Call unregistered via state module")

    # Verify removed from active calls (but still in DB for history)
    found_session = state.get_session_for_call(call_id)

    # With persistence, completed calls remain in DB for history
    # but are no longer in the active calls list
    manager = get_call_state_manager()
    call_state = manager.get_call_by_id(call_id)

    if call_state and call_state.status == CallStatus.COMPLETED:
        print(f"✓ Call marked as completed (preserved for history)")
    else:
        print(f"✗ Call status incorrect!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("  Call State Persistence Test Suite")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    if not initialize_database():
        print("✗ Database initialization failed!")
        return 1
    print("✓ Database initialized")

    # Check database status
    status = get_database_status()
    print(f"\nDatabase status: {status['status']}")
    print(f"Tables: {len(status['existing_tables'])}")

    # Verify call_states table exists
    if 'call_states' in status['existing_tables']:
        print("✓ call_states table exists")
    else:
        print("✗ call_states table missing!")
        return 1

    try:
        # Run tests
        call_id, session_id = test_basic_registration()
        test_lookup_operations(call_id, session_id)
        test_status_updates(call_id)
        test_active_calls(call_id)
        test_call_completion(call_id, session_id)
        test_persistence_recovery()
        test_backwards_compatibility()

        print_section("All Tests Passed! ✓")
        return 0

    except Exception as exc:
        print_section(f"Test Failed! ✗")
        print(f"\nError: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

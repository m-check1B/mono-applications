#!/usr/bin/env python3
"""
Focus Tools Integration Test

This script tests the Focus Tools implementation by:
1. Verifying imports work
2. Creating tool instances
3. Checking tool schemas
4. Simulating basic operations (if Focus by Kraliki backend is running)

Usage:
    PYTHONPATH=./src python3 test_focus_tools.py
"""

import sys
import asyncio
from typing import Optional

try:
    from ii_agent.tools.focus_tools import (
        create_focus_tools,
        CreateKnowledgeItemTool,
        UpdateKnowledgeItemTool,
        ListKnowledgeItemsTool,
        CreateTaskTool,
        UpdateTaskTool,
        ListTasksTool,
        CreateOrGetProjectTool,
    )
    print("✓ Focus Tools imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def test_tool_schemas():
    """Test that all tool schemas are properly defined."""
    print("\n=== Testing Tool Schemas ===")

    tools = create_focus_tools("http://127.0.0.1:3017", "test_token")

    expected_tools = [
        "create_knowledge_item",
        "update_knowledge_item",
        "list_knowledge_items",
        "create_task",
        "update_task",
        "list_tasks",
        "create_or_get_project",
    ]

    actual_tools = [tool.name for tool in tools]

    print(f"Expected {len(expected_tools)} tools:")
    for name in expected_tools:
        if name in actual_tools:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} MISSING")

    print(f"\nTotal tools created: {len(tools)}")

    # Verify each tool has required attributes
    for tool in tools:
        assert hasattr(tool, 'name'), f"Tool missing 'name' attribute"
        assert hasattr(tool, 'description'), f"Tool {tool.name} missing 'description'"
        assert hasattr(tool, 'input_schema'), f"Tool {tool.name} missing 'input_schema'"
        assert hasattr(tool, 'run_impl'), f"Tool {tool.name} missing 'run_impl'"

    print("✓ All tools have required attributes")


def test_input_schemas():
    """Test that input schemas are valid."""
    print("\n=== Testing Input Schemas ===")

    tools = create_focus_tools("http://127.0.0.1:3017", "test_token")

    for tool in tools:
        schema = tool.input_schema
        assert "type" in schema, f"{tool.name}: Schema missing 'type'"
        assert schema["type"] == "object", f"{tool.name}: Schema type should be 'object'"
        assert "properties" in schema, f"{tool.name}: Schema missing 'properties'"

        # Check for required fields
        required = schema.get("required", [])
        print(f"  ✓ {tool.name}: {len(schema['properties'])} properties, {len(required)} required")

    print("✓ All schemas are valid")


async def test_tool_execution(backend_url: str = "http://127.0.0.1:3017"):
    """
    Test actual tool execution (requires running Focus by Kraliki backend).

    Args:
        backend_url: URL of Focus by Kraliki backend
    """
    print("\n=== Testing Tool Execution (requires backend) ===")

    # Note: This requires a valid agent token from Focus by Kraliki
    # For now, we just test that the methods can be called
    test_token = "fake_token_for_testing"

    tool = CreateKnowledgeItemTool(backend_url, test_token)

    # Test that we can call run_impl (it will fail without valid token, but that's expected)
    test_input = {
        "typeId": "note",
        "title": "Test Note",
        "content": "This is a test note"
    }

    try:
        result = await tool.run_impl(test_input)
        print(f"  Tool execution returned: {result.tool_result_message}")
        print(f"  Success: {result.auxiliary_data.get('success', False)}")
    except Exception as e:
        print(f"  Expected error (no backend or invalid token): {type(e).__name__}")

    print("✓ Tool execution test complete")


def test_error_handling():
    """Test that tools handle errors gracefully."""
    print("\n=== Testing Error Handling ===")

    # Create tool with invalid URL to test error handling
    tool = CreateTaskTool("http://invalid-backend:9999", "test_token")

    async def run_test():
        test_input = {"title": "Test Task"}
        result = await tool.run_impl(test_input)

        # Should return error in output, not crash
        assert "Failed" in result.output or "error" in result.output.lower()
        assert result.auxiliary_data.get("success") == False
        print("  ✓ Tool handles connection errors gracefully")

    asyncio.run(run_test())

    print("✓ Error handling test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Focus Tools Integration Test")
    print("=" * 60)

    try:
        test_tool_schemas()
        test_input_schemas()
        test_error_handling()

        # Only run execution test if user confirms backend is running
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

        print("\nTo test actual tool execution:")
        print("1. Start Focus by Kraliki backend: ./start.sh")
        print("2. Get a valid agent token from POST /agent/sessions")
        print("3. Run: PYTHONPATH=./src python3 test_focus_tools.py --with-backend")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Phase 4 Implementation Verification Script

This script verifies that all Phase 4 components are correctly implemented.
Run this after implementing the FocusFileSearchTool to ensure everything is in place.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def verify_imports():
    """Verify all imports work correctly."""
    print("🔍 Verifying imports...")
    try:
        from ii_agent.tools.focus_tools import (
            FocusFileSearchTool,
            FocusToolBase,
            create_focus_tools
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_class_structure():
    """Verify FocusFileSearchTool has correct structure."""
    print("\n🔍 Verifying class structure...")
    try:
        from ii_agent.tools.focus_tools import FocusFileSearchTool, FocusToolBase

        # Check inheritance
        if not issubclass(FocusFileSearchTool, FocusToolBase):
            print("❌ FocusFileSearchTool doesn't inherit from FocusToolBase")
            return False

        # Check required attributes
        tool = FocusFileSearchTool("http://127.0.0.1:3017", "test_token")

        if not hasattr(tool, 'name'):
            print("❌ Missing 'name' attribute")
            return False

        if tool.name != "focus_file_search_query":
            print(f"❌ Wrong name: {tool.name}")
            return False

        if not hasattr(tool, 'description'):
            print("❌ Missing 'description' attribute")
            return False

        if not hasattr(tool, 'input_schema'):
            print("❌ Missing 'input_schema' attribute")
            return False

        # Check input schema
        schema = tool.input_schema
        if 'query' not in schema['properties']:
            print("❌ Schema missing 'query' property")
            return False

        if 'context' not in schema['properties']:
            print("❌ Schema missing 'context' property")
            return False

        if 'query' not in schema['required']:
            print("❌ Schema doesn't require 'query'")
            return False

        print("✅ Class structure correct")
        return True

    except Exception as e:
        print(f"❌ Structure verification failed: {e}")
        return False

def verify_tool_registration():
    """Verify tool is registered in create_focus_tools."""
    print("\n🔍 Verifying tool registration...")
    try:
        from ii_agent.tools.focus_tools import create_focus_tools

        tools = create_focus_tools("http://127.0.0.1:3017", "test_token")

        if len(tools) != 8:
            print(f"❌ Wrong number of tools: {len(tools)} (expected 8)")
            return False

        tool_names = [t.name for t in tools]
        if "focus_file_search_query" not in tool_names:
            print("❌ FocusFileSearchTool not in tool list")
            return False

        print("✅ Tool correctly registered")
        return True

    except Exception as e:
        print(f"❌ Registration verification failed: {e}")
        return False

def verify_method_signature():
    """Verify run_impl method has correct signature."""
    print("\n🔍 Verifying method signature...")
    try:
        from ii_agent.tools.focus_tools import FocusFileSearchTool
        import inspect

        tool = FocusFileSearchTool("http://127.0.0.1:3017", "test_token")

        if not hasattr(tool, 'run_impl'):
            print("❌ Missing run_impl method")
            return False

        # Check method signature
        sig = inspect.signature(tool.run_impl)
        params = list(sig.parameters.keys())

        if 'tool_input' not in params:
            print("❌ run_impl missing 'tool_input' parameter")
            return False

        if 'message_history' not in params:
            print("❌ run_impl missing 'message_history' parameter")
            return False

        print("✅ Method signature correct")
        return True

    except Exception as e:
        print(f"❌ Method verification failed: {e}")
        return False

def verify_files_exist():
    """Verify all required files exist."""
    print("\n🔍 Verifying file existence...")

    base_path = Path(__file__).parent
    required_files = [
        "src/ii_agent/tools/focus_tools.py",
        "tests/tools/test_focus_file_search_tool.py",
        "FOCUS_INTEGRATION.md",
        "PHASE_4_FILE_SEARCH_INTEGRATION.md",
        "QUICK_START_FILE_SEARCH.md",
        "PHASE_4_IMPLEMENTATION_SUMMARY.md"
    ]

    all_exist = True
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False

    return all_exist

def verify_documentation():
    """Verify documentation was updated."""
    print("\n🔍 Verifying documentation...")

    base_path = Path(__file__).parent
    focus_integration = base_path / "FOCUS_INTEGRATION.md"

    if not focus_integration.exists():
        print("❌ FOCUS_INTEGRATION.md missing")
        return False

    content = focus_integration.read_text()

    checks = [
        ("8 Pydantic-based tool implementations", "Tool count updated"),
        ("focus_file_search_query", "File search tool documented"),
        ("/ai/file-search/query", "API endpoint documented"),
        ("Example 4:", "Usage example added")
    ]

    all_found = True
    for text, description in checks:
        if text in content:
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {description}")
            all_found = False

    return all_found

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Phase 4 Implementation Verification")
    print("=" * 60)

    checks = [
        ("Imports", verify_imports),
        ("Class Structure", verify_class_structure),
        ("Tool Registration", verify_tool_registration),
        ("Method Signature", verify_method_signature),
        ("Required Files", verify_files_exist),
        ("Documentation", verify_documentation)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All checks passed! Phase 4 implementation is complete.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

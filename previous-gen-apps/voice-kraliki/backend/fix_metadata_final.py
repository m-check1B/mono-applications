#!/usr/bin/env python3
"""
Final fix for all metadata column syntax issues.
"""
import re
from pathlib import Path

def fix_file(filepath):
    """Fix metadata column syntax in a file"""
    content = filepath.read_text()
    original = content
    
    # Fix all patterns of incomplete Column definitions
    # Pattern: Column("metadata", JSON, default=dict... without closing )
    
    fixes = [
        # Add missing closing paren when nullable=False with no comment
        (r'Column\("metadata", JSON, default=dict, nullable=False\s*\n', 
         r'Column("metadata", JSON, default=dict, nullable=False)\n'),
        
        # Add missing closing paren with comment
        (r'Column\("metadata", JSON, default=dict, nullable=False, comment="([^"]+)"\s*\n',
         r'Column("metadata", JSON, default=dict, nullable=False, comment="\1")\n'),
        
        # Add missing closing paren when just default=dict with comment
        (r'Column\("metadata", JSON, default=dict\s+(#[^\n]+)\n',
         r'Column("metadata", JSON, default=dict)  \1\n'),
        
        # Add missing closing paren when just default=dict
        (r'Column\("metadata", JSON, default=dict\s*\n',
         r'Column("metadata", JSON, default=dict)\n'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        filepath.write_text(content)
        return True
    return False

def main():
    models_dir = Path("app/models")
    
    # Files that need fixing
    files = [
        "ai_insights.py",
        "analytics.py",
        "call_state.py",
        "provider.py",
        "session.py",
        "supervisor.py",
    ]
    
    for filename in files:
        filepath = models_dir / filename
        if not filepath.exists():
            continue
        
        print(f"Processing {filename}...")
        if fix_file(filepath):
            print(f"  ✓ Fixed {filename}")
        else:
            print(f"  - No changes for {filename}")

if __name__ == "__main__":
    main()

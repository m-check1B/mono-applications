#!/usr/bin/env python3
"""
Fix remaining metadata column syntax issues.
"""
import re
from pathlib import Path

def fix_column_syntax(content):
    """Fix broken Column syntax patterns"""
    # Pattern 1: Fix duplicate JSON parameters
    # From: Column("metadata", JSON, (JSON, default=...))
    # To: Column("metadata", JSON, default=...)
    pattern1 = r'Column\("metadata", JSON, \(JSON, (default=dict.*?)\)\)'
    replacement1 = r'Column("metadata", JSON, \1)'
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Fix without closing paren on multiline
    pattern2 = r'Column\("metadata", JSON, \(JSON, (default=dict.*?)\)'
    replacement2 = r'Column("metadata", JSON, \1'
    content = re.sub(pattern2, replacement2, content)
    
    return content

def main():
    models_dir = Path("app/models")
    
    # List of files that need fixing
    files_to_fix = [
        "ai_insights.py",
        "call_state.py",
        "provider.py",
        "session.py",
        "supervisor.py"
    ]
    
    for filename in files_to_fix:
        py_file = models_dir / filename
        if not py_file.exists():
            continue
            
        print(f"Processing {filename}...")
        content = py_file.read_text()
        
        fixed_content = fix_column_syntax(content)
        
        if content != fixed_content:
            py_file.write_text(fixed_content)
            print(f"  Fixed {filename}")
        else:
            print(f"  No changes needed for {filename}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fix metadata column name conflicts in SQLAlchemy models.
"""
import re
from pathlib import Path

def fix_metadata_column(content):
    """Fix metadata = Column(...) to custom_metadata = Column("metadata", ...)"""
    # Pattern to match: metadata = Column(JSON, default=dict, ...)
    # or metadata = Column(JSON, default=dict)
    # Replace with: custom_metadata = Column("metadata", JSON, default=dict, ...)
    
    # This regex captures the full Column() call
    pattern = r'(\s+)custom_metadata = Column\("metadata", JSON, \(JSON, (default=dict.*?)\)'
    replacement = r'\1custom_metadata = Column("metadata", JSON, \2)'
    content = re.sub(pattern, replacement, content)
    
    return content

def main():
    models_dir = Path("app/models")
    
    for py_file in models_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        print(f"Processing {py_file.name}...")
        content = py_file.read_text()
        
        # Fix broken syntax from previous sed command
        fixed_content = fix_metadata_column(content)
        
        if content != fixed_content:
            py_file.write_text(fixed_content)
            print(f"  Fixed {py_file.name}")

if __name__ == "__main__":
    main()

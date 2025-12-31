import os
import re

def find_silent_exceptions(root_dir):
    pattern = re.compile(r'except\s+.*?:(\s*#.*)*\n\s*(pass|return\s+None|print\(.*?\))\s*(\n|$)', re.MULTILINE)
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = list(pattern.finditer(content))
                        if matches:
                            print(f"\nExample silent exceptions in {filepath}:")
                            for m in matches:
                                print(f"  Line {content.count(chr(10), 0, m.start()) + 1}: {m.group(0).strip()}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    find_silent_exceptions("app")

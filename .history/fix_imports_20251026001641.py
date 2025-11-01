#!/usr/bin/env python3
"""
Quick fix to remove local import re statements from database.py
"""

import os

def fix_database_file():
    file_path = "database.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic lines
    content = content.replace('                                import re\n', '')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed database.py - removed local 'import re' statements")

if __name__ == "__main__":
    fix_database_file()